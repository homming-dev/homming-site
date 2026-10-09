"""Build the unlisted acceptance checklist page of homm.ing (/acceptance) from the team's checklist.

    python3 scripts/build_acceptance.py --source ../alpha/docs/prototypes/feature-checklist-2026-10-10.html

The source is the internal checklist page in the product repository: its SECTIONS (what to try,
what to send, what should happen) and CLAUDE (the current verdict and a note per item). This page
shows the same items read-only for anyone with the link. It leaves out what only the team needs:
ticket, pull request and commit numbers, internal file and engine names, the per-viewer result
buttons. The shell (background, header, fonts) is copied from index.html, as build_team.py does.
Run it again whenever the checklist changes, then open a pull request.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
KST = dt.timezone(dt.timedelta(hours=9))


def slice_between(start: str, end: str, *, keep_end: bool = False) -> str:
    a = INDEX.index(start)
    b = INDEX.index(end, a)
    return INDEX[a : b + (len(end) if keep_end else 0)]


HEAD_LINKS = slice_between('<link rel="icon"', "<style>").rstrip()
CSS = slice_between("<style>", "</style>", keep_end=True)
STAGE = slice_between('<div class="stage" id="stage">', '</div>\n\n<div class="content">').rstrip()
BG_SCRIPT = slice_between("<script>\n(function(){\n  // Trigger intro animations", "</script>", keep_end=True)

# Verdicts as the team writes them, mapped to what a reader outside the team needs.
STATUS = [
    # (prefix of the team's verdict, class, public label)
    ("됨", "ok", "됨"),
    ("고쳐서", "fix", "고쳤고 다시 확인 중"),
    ("안 됨(예상대로)", "plan", "아직 없음"),
    ("안 됨", "no", "안 됨, 고치는 중"),
    ("애매함", "meh", "일부만 됨"),
    ("서버 꺼짐", "off", "준비됨, 아직 꺼 둠"),
    ("JW 시험", "wait", "시험 전"),
    ("확인 못 함", "wait", "시험 전"),
]
ORDER = ["ok", "fix", "no", "meh", "wait", "off", "plan"]

SECTION_TITLES = {
    "호두": "가족 사이",
}

# Words only the team uses, in the order they are replaced.
WORDS = [
    ("persona.md에", "호밍의 메모에"),
    ("persona.md", "호밍의 메모"),
    ("볼트", "보안 로그인 화면"),
    ("호두", "가족 사이를 잇는 쪽"),
    ("JW 폰 시험", "팀 시험"),
    ("JW 시험", "팀 시험"),
    ("JW가", "팀이"),
    ("JW", "팀"),
    ("Claude", "사전 시험"),
    ("운영판:", "지금 서비스에서:"),
    ("(옛 코드 이전 결정 뒤)", ""),
    ("카카오 제휴 회신을 기다립니다.", "아직 없습니다."),
    ("초대장이 서버에서 켜진 뒤", "초대 기능을 켠 뒤"),
    ("A가족 ", "시험용 "),
    ("배포 뒤 재시험", "반영 뒤 다시 시험"),
    ("재시험 대기", "다시 시험 예정"),
    ("머지", "반영"),
    ("배포", "반영"),
    ("코드가 막음", "자동으로 막음"),
]

# Notes whose public form must differ from a mechanical cleanup (too technical, or a design
# decision that needs one plain sentence). Keyed by item id; update when the team note changes.
PUBLIC_NOTE = {
    "web-share": "공유 상태를 보여 주기만 하고, 바꾸는 버튼은 없습니다. 바꾸려는 요청은 막힙니다.",
    "refuse": "'말하지 마'라고 하면 가족 쪽에 아무것도 가지 않고, '응'이라고 하면 허락으로 저장합니다.",
    "after": "가족 쪽에 넘길 때 '가족 쪽에 알릴 만한 일인지 살펴볼게요'라고만 말하고, 전해 드린다고 약속하지 않습니다.",
    "relay": "말을 그대로 옮기는 기능은 없습니다. 가족이 직접 부탁하면 함께 일정을 맞추는 기능을 만들고 있습니다.",
    "push": "카카오톡 일반 채널에서는 호밍이 먼저 말을 걸 수 없습니다. 비즈니스 채널로 바꾼 뒤에 됩니다.",
    "group": "가족 단톡방에서 호밍을 쓰는 기능은 아직 없습니다.",
    "daily": "딸이 먼저 자기 이야기를 해야 제안이 생깁니다. 일부러 이렇게 정했습니다.",
    "invite": "초대장 만들기는 준비됐지만 아직 꺼 두었습니다. 꺼져 있을 때 '가족 초대'라고 하면 지금은 안 된다고 안내합니다.",
    "naver": "네이버 장바구니를 열지 못합니다. 호밍이 없는 주소를 열려고 하거나, '로그인해서 봐 줘'라는 말에 열어 보지도 않고 거절합니다. 고치는 중입니다.",
}

REFS = [
    re.compile(r"\s*\([^()]*(?:HOMM-\d+|PR ?#\d+|#\d{2,4}\b|\b[0-9a-f]{7,40}\b)[^()]*\)"),
    re.compile(r"\s*(?:PR ?)?#\d{2,4}(?!\d)(?:에서|로)?"),
    re.compile(r"\s*서버 기록: [^.]*\."),
    re.compile(r"\s*\([A-F]가족[^)]*\)"),
    re.compile(r"\s*[^.]*배포 뒤에 시험하세요\."),
    re.compile(r"\s*HOMM-\d+"),
    re.compile(r"\s*\b[0-9a-f]{7,40}\b"),
]


def clean(text: str) -> str:
    for pattern in REFS:
        text = pattern.sub("", text)
    for old, new in WORDS:
        text = text.replace(old, new)
    text = re.sub(r"\(\s*\)", "", text)
    text = re.sub(r"\s+([.,])", r"\1", text)
    return re.sub(r"\s{2,}", " ", text).strip()


def status(verdict: str) -> tuple[str, str]:
    for prefix, cls, label in STATUS:
        if verdict.startswith(prefix):
            return cls, label
    return "wait", "시험 전"


def load(source: pathlib.Path) -> tuple[list[dict], dict]:
    text = source.read_text(encoding="utf-8")
    start = text.index("const SECTIONS")
    end = text.index("const TICKETS")
    script = text[start:end] + "\nprocess.stdout.write(JSON.stringify({SECTIONS, CLAUDE}));"
    out = subprocess.run(["node", "-e", script], check=True, capture_output=True, text=True).stdout
    data = json.loads(out)
    return data["SECTIONS"], data["CLAUDE"]


def item_html(n: int, it: dict, verdict: list[str]) -> str:
    cls, label = status(verdict[0])
    note = PUBLIC_NOTE.get(it["id"]) or clean(verdict[1])
    rows = []
    if it.get("prep"):
        rows.append(("준비", clean(it["prep"])))
    if it.get("say"):
        rows.append(("보낼 말", clean(it["say"])))
    rows.append(("되면 이렇게", clean(it["ok"])))
    body = "\n".join(
        f'          <div class="ck-k">{k}</div><div class="ck-v{" ck-say" if k == "보낼 말" else ""}">{html.escape(v)}</div>'
        for k, v in rows
        if v
    )
    return f'''        <article class="ck" data-status="{cls}">
          <div class="ck-top"><span class="ck-num">{n}</span><h3>{html.escape(clean(it["t"]))}</h3><span class="ck-pill {cls}">{label}</span></div>
          <div class="ck-rows">
{body}
          </div>
          <p class="ck-now"><span>지금</span> {html.escape(note)}</p>
        </article>'''


def page(sections: list[dict], verdicts: dict, updated: str) -> str:
    counts = {cls: 0 for cls in ORDER}
    parts = []
    n = 0
    for sec in sections:
        items = []
        for it in sec["items"]:
            n += 1
            verdict = verdicts.get(it["id"], ["시험 전", ""])
            counts[status(verdict[0])[0]] += 1
            items.append(item_html(n, it, verdict))
        title = SECTION_TITLES.get(sec["title"], clean(sec["title"]))
        sub = clean(sec.get("sub", ""))
        parts.append(
            f'''      <section class="ck-group">
        <h2>{html.escape(title)}</h2>
        <p class="ck-sub">{html.escape(sub)}</p>
{chr(10).join(items)}
      </section>'''
        )
    labels = {cls: label for _, cls, label in STATUS}
    summary = "".join(
        f'<button class="ck-pill {cls}" data-filter="{cls}" aria-pressed="false">{labels[cls]} {counts[cls]}</button>'
        for cls in ORDER
        if counts[cls]
    )
    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>호밍 기능 점검표</title>
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="호밍이 지금 카카오톡에서 무엇을 하고 무엇을 아직 못 하는지, 항목마다 시험하는 법과 현재 상태.">
{HEAD_LINKS}
{CSS}
{EXTRA_CSS}
</head>
<body>

{STAGE}

<div class="content">

    <main class="sheet" id="hero">
      <div class="eyebrow"><span class="rule"></span> <span>homming · 점검표</span></div>
      <h1 class="pp">호밍 기능 점검표</h1>
      <p class="lede">호밍이 카카오톡에서 지금 무엇을 하고, 무엇을 아직 못 하는지 정리한 목록입니다. 항목마다 시험하는 법과 지금 상태를 적었습니다. 시험에는 실제 가족 정보 대신 시험용 일정과 메일을 씁니다.</p>
      <p class="ck-updated">마지막 갱신 {updated} · 전체 {n}개</p>
      <div class="ck-summary">{summary}<button class="ck-pill all" data-filter="" aria-pressed="true">전체 보기</button></div>
{chr(10).join(parts)}
    </main>

    <footer class="foot">
      <div class="foot-left"><a class="home" href="/">&larr; homm.ing</a></div>
      <div class="foot-center"></div>
      <div class="foot-right"><span>© Homming · unlisted page</span></div>
    </footer>

</div>

{BG_SCRIPT}

<script>
/* Filter by status. Nothing is stored. */
(function () {{
  var buttons = document.querySelectorAll(".ck-summary [data-filter]");
  function show(cls) {{
    document.querySelectorAll(".ck").forEach(function (el) {{
      el.hidden = !!cls && el.getAttribute("data-status") !== cls;
    }});
    document.querySelectorAll(".ck-group").forEach(function (g) {{
      g.hidden = !g.querySelector(".ck:not([hidden])");
    }});
    buttons.forEach(function (b) {{ b.setAttribute("aria-pressed", b.getAttribute("data-filter") === cls ? "true" : "false"); }});
  }}
  buttons.forEach(function (b) {{ b.addEventListener("click", function () {{ show(this.getAttribute("data-filter")); }}); }});
}})();
</script>
</body>
</html>
'''


EXTRA_CSS = """<style>
  .sheet{position:relative; z-index:5; max-width:880px; margin:0 auto; width:100%; min-width:0; padding:0 0 48px; box-sizing:border-box;}
  .sheet h1.pp{font-family:var(--serif); font-weight:300; font-size:clamp(36px, 6vw, 72px); line-height:1.05; letter-spacing:-0.03em; margin:0 0 18px; color:var(--ink-900);}
  .sheet .lede{margin:0 0 10px; max-width:640px;}
  .ck-updated{font-family:var(--mono); font-size:12px; letter-spacing:0.04em; color:var(--ink-700); margin:0 0 18px;}
  .ck-summary{display:flex; flex-wrap:wrap; gap:8px; margin:0 0 28px;}
  .ck-summary .ck-pill{cursor:pointer; font:inherit; font-size:13px;}
  .ck-summary .ck-pill[aria-pressed="true"]{outline:2px solid var(--ink-900); outline-offset:1px;}
  .ck-group{margin:0 0 30px;}
  .ck-group h2{font-family:var(--serif); font-weight:400; font-size:clamp(24px, 3vw, 32px); margin:0 0 4px; color:var(--ink-900);}
  .ck-sub{margin:0 0 14px; font-size:15px; color:var(--ink-700);}
  .ck{display:block; background:rgba(255,255,255,0.8); border:1px solid rgba(0,0,0,0.08); border-radius:16px; padding:16px 18px; margin:0 0 12px; -webkit-backdrop-filter:blur(6px); backdrop-filter:blur(6px);}
  .ck-top{display:flex; align-items:flex-start; gap:10px;}
  .ck-top h3{flex:1; min-width:0; margin:0; font-size:17px; font-weight:600; line-height:1.4; color:var(--ink-900);}
  .ck-num{font-family:var(--mono); font-size:12px; color:var(--ink-500); min-width:22px; padding-top:4px;}
  .ck-rows{display:grid; grid-template-columns:84px minmax(0,1fr); gap:6px 12px; margin:12px 0 0 32px; font-size:15px; line-height:1.55; color:var(--ink-700);}
  .ck-k{font-family:var(--mono); font-size:12px; letter-spacing:0.02em; padding-top:3px; color:var(--ink-500);}
  .ck-say{color:var(--ink-900); font-weight:500;}
  .ck-now{margin:12px 0 0 32px; font-size:15px; line-height:1.55; color:var(--ink-900);}
  .ck-now span{font-family:var(--mono); font-size:12px; color:var(--ink-500); margin-right:6px;}
  .ck-pill{display:inline-block; flex:none; border-radius:999px; padding:3px 10px; font-size:12px; font-weight:600; white-space:nowrap; border:1px solid transparent; background:#eee; color:#333;}
  .ck-pill.ok{background:#e3f4e6; color:#1d6b33;}
  .ck-pill.fix{background:#e6eefc; color:#244f9e;}
  .ck-pill.no{background:#fde5e3; color:#a23224;}
  .ck-pill.meh{background:#fdf1d8; color:#8a5a00;}
  .ck-pill.wait{background:#efefef; color:#555;}
  .ck-pill.plan{background:#f1ecf9; color:#5b3f8f;}
  .ck-pill.off{background:#eef3f3; color:#2f5d62;}
  .ck-pill.all{background:#fff; border-color:rgba(0,0,0,0.15);}
  .foot .home{color:var(--ink-700); text-decoration:none; border-bottom:1px solid var(--ink-300);}
  @media (max-width: 600px){
    .content{padding:24px 16px;}
    .ck{padding:14px 14px;}
    .ck-rows{grid-template-columns:minmax(0,1fr); gap:2px; margin-left:0;}
    .ck-k{padding-top:8px;}
    .ck-now{margin-left:0;}
  }
</style>"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=pathlib.Path, required=True)
    parser.add_argument("--updated", help="갱신 시각(기본: 지금, KST)")
    args = parser.parse_args()
    sections, verdicts = load(args.source)
    updated = args.updated or dt.datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
    (ROOT / "acceptance.html").write_text(page(sections, verdicts, updated), encoding="utf-8")


if __name__ == "__main__":
    main()
