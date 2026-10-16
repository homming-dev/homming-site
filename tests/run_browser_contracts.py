"""Replay the site's synthetic privacy fixture in an isolated local Chromium context."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

SITE = Path(__file__).resolve().parents[1]
GOLDEN = Path("experiments/tasks/golden-v1.json")


class HarnessError(Exception):
    def __init__(self, code, case_id=None, observed_count=None):
        self.details = {"code": code}
        if case_id is not None:
            self.details["case_id"] = case_id
        if observed_count is not None:
            self.details["observed_count"] = observed_count
        super().__init__(code)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def inside(path, directory):
    return path == directory or directory in path.parents


def local_file(root, name):
    path = (root / name).resolve()
    if not inside(path, root) or not path.is_file():
        raise HarnessError("invalid_local_fixture_path")
    return path


def output_directory(value, site):
    path = Path(value).expanduser().resolve()
    if any(inside(path, root) for root in (SITE, site)):
        raise HarnessError("output_must_be_outside_source_repositories")
    if any((parent / ".git").exists() for parent in (path, *path.parents)):
        raise HarnessError("output_must_be_outside_git_repositories")
    if path.exists():
        raise HarnessError("output_directory_already_exists")
    path.mkdir(parents=True)
    return path


def inject_fault(source, fault, case_id):
    if fault["kind"] != "throw_before_signup_listener_installation":
        raise HarnessError("unsupported_fault_kind", case_id)
    target, message = fault["target_inline_script_contains"], fault["message"]
    if not isinstance(target, str) or not target or not isinstance(message, str):
        raise HarnessError("invalid_fault_configuration", case_id)
    scripts = list(
        re.finditer(r"<script\b([^>]*)>([\s\S]*?)</script\s*>", source, re.IGNORECASE)
    )
    matches = [
        m
        for m in scripts
        if not re.search(r"\bsrc\s*=", m[1], re.IGNORECASE) and target in m[2]
    ]
    if len(matches) != 1:
        raise HarnessError("fault_target_not_unique", case_id, len(matches))
    match = matches[0]
    # JSON string quoting prevents fixture text from becoming executable source.
    literal = json.dumps(message).replace("<", "\\u003c")
    return (
        source[: match.start(2)]
        + "throw new Error("
        + literal
        + ");\n"
        + source[match.start(2) :]
    )


def load_suite(site, hashes):
    golden_path = local_file(site, GOLDEN)
    golden_bytes = golden_path.read_bytes()
    hashes["golden_sha256"] = digest(golden_bytes)
    golden = json.loads(golden_bytes)
    fixture_path = local_file(site, golden["fixture"])
    fixture_bytes = fixture_path.read_bytes()
    hashes["fixture_sha256"] = digest(fixture_bytes)
    hashes["source_sha256"] = {}
    fixture = json.loads(fixture_bytes)
    if (
        golden.get("kind") != "static_site_browser_contract_registry"
        or fixture.get("kind") != "static_site_browser_fixture"
    ):
        raise HarnessError("unsupported_fixture_kind")
    cases = fixture["cases"]
    if (
        not cases
        or [c["id"] for c in cases] != golden["case_ids"]
        or len({c["id"] for c in cases}) != len(cases)
    ):
        raise HarnessError("case_registry_mismatch")
    prepared, sources = [], {}
    for case in cases:
        identity = case["id"]
        page_url = urlsplit(case["page"])
        if (
            page_url.scheme
            or page_url.netloc
            or page_url.path.startswith("/")
            or not page_url.path.endswith(".html")
        ):
            raise HarnessError("case_page_must_be_local_html", identity)
        path = local_file(site, unquote(page_url.path))
        source_bytes = path.read_bytes()
        sources[str(path.relative_to(site))] = source_bytes
        hashes["source_sha256"][str(path.relative_to(site))] = digest(source_bytes)
        if type(case["browser"]["javascript_enabled"]) is not bool:
            raise HarnessError("invalid_javascript_setting", identity)
        data, expected = case["synthetic_input"], case["expected"]
        if (
            not isinstance(data["email"], str)
            or not isinstance(data["role"], str)
            or type(data["consent"]) is not bool
        ):
            raise HarnessError("invalid_synthetic_input", identity)
        if case["trigger"] not in ("submit_button", "email_enter"):
            raise HarnessError("unsupported_trigger", identity)
        if (
            expected["form_accepts_input"] is not False
            or expected["native_submission_possible"] is not False
            or expected["signup_post_count"] != 0
            or expected["synthetic_email_absent_from_url"] is not True
            or not isinstance(expected["forbidden_url_query_keys"], list)
            or not expected["forbidden_url_query_keys"]
            or not all(isinstance(k, str) for k in expected["forbidden_url_query_keys"])
        ):
            raise HarnessError("unsupported_privacy_contract_expectation", identity)
        fault = case["fault"]
        if fault and not case["browser"]["javascript_enabled"]:
            raise HarnessError("fault_requires_javascript", identity)
        body = inject_fault(source_bytes.decode(), fault, identity) if fault else None
        prepared.append((case, page_url.path, body))
    return prepared, sources, {golden_path: golden_bytes, fixture_path: fixture_bytes}


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass  # Never log URLs, query values or request bodies.


@contextmanager
def local_server(site):
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), partial(QuietHandler, directory=str(site))
    )
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        yield "http://127.0.0.1:" + str(server.server_port)
    finally:
        server.shutdown()
        server.server_close()
        worker.join()


def run_case(
    browser, origin, case, page_path, fault_body, blocked_hosts, timeout_error
):
    context = browser.new_context(
        java_script_enabled=case["browser"]["javascript_enabled"],
        reduced_motion="reduce",
        service_workers="block",
        accept_downloads=False,
    )
    navigation_urls, signup_posts, errors = [], [], []
    injected = 0
    origin_parts = urlsplit(origin)

    def route(request_route):
        nonlocal injected
        request = request_route.request
        parts = urlsplit(request.url)
        if request.method == "POST" and parts.path.rstrip("/") == "/api/signup":
            signup_posts.append(True)
        is_local = (parts.scheme, parts.netloc) == (
            origin_parts.scheme,
            origin_parts.netloc,
        )
        if not is_local:
            if parts.hostname:
                blocked_hosts.add(parts.hostname)
            request_route.abort()
            return
        if request.method not in ("GET", "HEAD"):
            request_route.abort()
            return
        if request.is_navigation_request():
            navigation_urls.append(request.url)
            if (
                fault_body is not None
                and parts.path == "/" + page_path
                and injected == 0
            ):
                injected += 1
                request_route.fulfill(
                    status=200, content_type="text/html; charset=utf-8", body=fault_body
                )
                return
        request_route.continue_()

    context.route("**/*", route)
    # WebSockets are not used by this site. Close them without connecting upstream.
    if hasattr(context, "route_web_socket"):
        context.route_web_socket("**/*", lambda socket: socket.close())
    page = context.new_page()
    page.set_default_timeout(3000)
    page.on("pageerror", lambda error: errors.append(str(error)))
    try:
        page.goto(origin + "/" + case["page"], wait_until="domcontentloaded")
        email = page.locator('input[type="email"]')
        roles = page.locator('input[name="role"]')
        consent = page.locator('input[name="consent"]')
        submit = page.locator("#send")
        if (
            email.count() != 1
            or consent.count() != 1
            or submit.count() != 1
            or roles.count() == 0
        ):
            raise HarnessError("required_control_not_unique", case["id"])
        disabled = {
            "email": email.is_disabled(),
            "roles": all(roles.nth(i).is_disabled() for i in range(roles.count())),
            "consent": consent.is_disabled(),
            "submit": submit.is_disabled(),
        }
        values = case["synthetic_input"]
        role = page.locator(
            'input[name="role"][value=' + json.dumps(values["role"]) + "]"
        )
        if role.count() != 1:
            raise HarnessError("fixture_role_not_unique", case["id"])
        if not disabled["email"]:
            email.fill(values["email"])
        if not role.is_disabled():
            role.locator("..").click()
        if not disabled["consent"]:
            consent.set_checked(values["consent"])
        if case["trigger"] == "submit_button":
            try:
                submit.click(timeout=350 if disabled["submit"] else 3000)
            except timeout_error:
                if not disabled["submit"]:
                    raise HarnessError("enabled_submit_action_timed_out", case["id"])
        else:
            # A disabled target cannot take focus, including for an Enter submission.
            try:
                email.press("Enter", timeout=350 if disabled["email"] else 3000)
            except timeout_error:
                if not disabled["email"]:
                    raise HarnessError("enabled_enter_action_timed_out", case["id"])
        page.wait_for_timeout(200)
        expected = case["expected"]
        forbidden = set(expected["forbidden_url_query_keys"])
        urls = navigation_urls + [page.url]
        forbidden_keys = sorted(
            {
                key
                for url in urls
                for key in parse_qs(urlsplit(url).query)
                if key in forbidden
            }
        )
        email_absent = all(
            values["email"].casefold() not in unquote(url).casefold() for url in urls
        )
        faults = case["fault"]
        matching_errors = (
            sum(error == faults["message"] for error in errors) if faults else 0
        )
        failure_observed = (
            (injected == 1 and matching_errors == 1 and len(errors) == 1)
            if faults
            else not errors
        )
        observed = {
            "form_accepts_input": not all(
                disabled[key] for key in ("email", "roles", "consent")
            ),
            "native_submission_possible": not disabled["email"]
            or not disabled["submit"]
            or len(navigation_urls) > 1,
            "signup_post_count": len(signup_posts),
            "forbidden_navigation_query_keys": forbidden_keys,
            "synthetic_email_absent_from_url": email_absent,
            "controls_disabled": disabled,
            "navigation_count": len(navigation_urls),
            "fault_injection_count": injected,
            "expected_initialization_error_count": matching_errors,
            "browser_error_count": len(errors),
        }
        checks = {
            "form_accepts_input": observed["form_accepts_input"]
            == expected["form_accepts_input"],
            "native_submission_possible": observed["native_submission_possible"]
            == expected["native_submission_possible"],
            "signup_post_count": observed["signup_post_count"]
            == expected["signup_post_count"],
            "forbidden_url_query_keys": not forbidden_keys,
            "synthetic_email_absent_from_url": email_absent
            == expected["synthetic_email_absent_from_url"],
            "input_and_submit_disabled": all(disabled.values()),
            "initialization_failure_observed": failure_observed,
        }
        return {
            "id": case["id"],
            "passed": all(checks.values()),
            "checks": checks,
            "observed": observed,
        }
    finally:
        context.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--browser-executable",
        required=True,
        type=Path,
        help="Existing Chromium executable; no download or installation is attempted",
    )
    parser.add_argument(
        "--out-dir",
        required=True,
        help="New result directory outside every Git repository",
    )
    parser.add_argument(
        "--site-root",
        type=Path,
        default=SITE,
        help="Local site copy containing the golden registry and fixture (default: this checkout)",
    )
    args = parser.parse_args()
    site = args.site_root.expanduser().resolve()
    report = {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "harness_error",
        "results": [],
        "browser_version": None,
        "blocked_external_hostnames": [],
        "external_network_sent": False,
        "live_signup_sent": False,
        "success_response_simulated": False,
        "model_evaluation": False,
        "hashes": {"runner_sha256": digest(Path(__file__).read_bytes())},
    }
    out = None
    blocked = set()
    browser_error_type = RuntimeError
    try:
        out = output_directory(args.out_dir, site)
        prepared, sources, inputs = load_suite(site, report["hashes"])
        executable = args.browser_executable.expanduser().resolve()
        if not executable.is_file():
            raise HarnessError("browser_executable_missing")
        try:
            from playwright.sync_api import Error as BrowserError
            from playwright.sync_api import TimeoutError as BrowserTimeout
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise HarnessError(
                "playwright_not_installed_in_selected_interpreter"
            ) from None
        browser_error_type = BrowserError
        with local_server(site) as origin, sync_playwright() as runtime:
            browser = runtime.chromium.launch(
                headless=True,
                executable_path=str(executable),
                args=[
                    "--disable-background-networking",
                    "--disable-component-update",
                    "--disable-sync",
                ],
            )
            try:
                report["browser_version"] = browser.version
                for case, page_path, body in prepared:
                    report["results"].append(
                        run_case(
                            browser,
                            origin,
                            case,
                            page_path,
                            body,
                            blocked,
                            BrowserTimeout,
                        )
                    )
            finally:
                browser.close()
        report["blocked_external_hostnames"] = sorted(blocked)
        if any(path.read_bytes() != data for path, data in inputs.items()) or any(
            local_file(site, name).read_bytes() != data
            for name, data in sources.items()
        ):
            raise HarnessError("source_or_fixture_changed_during_run")
        report["passed"] = sum(result["passed"] for result in report["results"])
        report["total"] = len(prepared)
        report["status"] = (
            "passed" if report["passed"] == report["total"] else "contract_failed"
        )
    except HarnessError as error:
        report["harness_error"] = error.details
    except (KeyError, TypeError, ValueError):
        report["harness_error"] = {"code": "malformed_fixture_or_registry"}
    except (OSError, RuntimeError, browser_error_type):
        # Avoid persisting Playwright tracebacks containing URLs or input values.
        report["harness_error"] = {"code": "browser_or_local_server_error"}
    report["blocked_external_hostnames"] = sorted(blocked)
    if out is not None:
        (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                "status": report["status"],
                "passed": report.get("passed", 0),
                "total": report.get("total", 0),
                "harness_error": report.get("harness_error"),
            }
        )
    )
    return (
        0
        if report["status"] == "passed"
        else 1
        if report["status"] == "contract_failed"
        else 2
    )


if __name__ == "__main__":
    sys.exit(main())
