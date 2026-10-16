# Pilot form correction (HOMM-442)

The form accepts ordinary email addresses and makes the required consent explicit.
Consent names the submitted email and participant role, pilot invitations, and
Google connection preparation. The checkbox starts unchecked. The existing
collection purpose and retention statement remain in place.

The server accepts general email addresses through `signups.parse` and
`emails.normalize` in the product repository. Requests retain the API's legacy
JSON fields: `gmail`, `role`, and `consent`. A non-Google email can submit a pilot
request; this does not establish eligibility for Google services.

An initially disabled fieldset prevents entry and native form submission while
JavaScript is unavailable or the submission handler has not initialized. The
handler is installed before the fieldset is enabled. Validation errors focus the
relevant control, and failed requests retain the form for retry.

This correction does not publish the separate privacy and terms drafts. The
operating entity, retention commitments, Google preparation workflow, and
deletion procedure still need confirmation for that publication. The current
retention statement is preserved, not newly verified by these browser checks.

## Evaluation

Base: `bf5d477881bfe5e86ef3d207c845ca7a8f9854c0` (current Homming branding).
Synthetic browser cases were registered before resolving the production edit.

Evaluation case groups: `email-*`, `malformed`, `missing-role`,
`missing-consent`, `retry-*`, `copy-*`, `signup-nojs-button`,
`signup-nojs-enter`, and `signup-handler-init-failure`.

The local evidence directory is
`/Users/ryan/homming/.sharkly-migration/landing-safe-20261016`.
`form-cases-current-final.json` registers the 14 form checks.
The repository retains `experiments/tasks/golden-v1.json`, its fixture, and
`tests/run_browser_contracts.py` from the previously reviewed privacy correction.
The current-base comparison uses a copy whose fault target matches both revisions.
The copies use the same expectations before and after the change. The upstream
form passes 5 of 14 form checks and 0 of 3 privacy checks. The corrected form
passes all 14 form checks and all 3 privacy checks.

Final form evidence: `current-before-form-review/report.json` and
`current-candidate-form-review/report.json`. The historical baseline privacy
result is `current-before-privacy-retry/report.json`. The final replay using the
repository runner is `current-committed-privacy/report.json`.

All external browser requests are intercepted. Tests use synthetic inputs and
error responses; they do not submit a real signup or simulate successful
registration. They do not verify email delivery, Google registration, live API
acceptance, or legal sufficiency. Source hashes, failure details, and screenshots
are recorded with the results.
