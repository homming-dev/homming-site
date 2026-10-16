# homming — deploy bundle

`index.html` is the landing page and is fully self-contained (logo, favicon and
app icons are embedded as data URIs), so it works from any static host.

| File | Role |
|---|---|
| `index.html` | Landing page — served at the site root |
| `brand.html` | Brand style guide — available at `/brand` (cleanUrls) or `/brand.html` |
| `favicon-32.png`, `apple-touch-icon.png`, `icon-512.png` | Icons, already embedded in the HTML as data URIs |
| `assets/homming_mark.png` | Transparent knot mark, kept for reuse |
| `vercel.json` | Clean-URL config |

## Vercel (recommended, ~1 min)
1. Unzip this folder.
2. vercel.com -> Add New -> Project -> **drag the folder in** (or `npx vercel deploy --prod`).
3. Settings -> Domains -> add `homm.ing`, then set the DNS records Vercel shows you at your registrar.

## Netlify (no account needed for a quick test)
1. Unzip.
2. app.netlify.com/drop -> drag the folder in -> instant HTTPS URL.

## Cloudflare Pages
1. Unzip. 2. Cloudflare dash -> Workers & Pages -> Create -> Pages -> Upload assets -> drag the folder.

## Note on the contact address
The email on the landing page is entity-encoded on purpose so Cloudflare's
Email Address Obfuscation cannot rewrite it into `[email protected]`.
If you ever see that placeholder again, turn off
Scrape Shield -> Email Address Obfuscation for the zone.


## Pilot form checks

`index.html` accepts general email addresses and requires the unchecked consent
box before submission. The existing API still receives the field named `gmail`.
See `docs/pilot-form-fix.md` for scope and the separately reviewed legal drafts.

The three registered privacy checks exercise disabled JavaScript (button and
Enter) and a failed signup-handler initialization. They verify that the form
cannot accept input or submit email, role, or consent through a native URL query
before its submission handler is ready. They use synthetic inputs, block all
external requests, and do not simulate a successful signup.

Use an existing Python environment with Playwright and an installed Chromium
executable. The command does not install a browser. Choose a new output directory
outside Git repositories:

```sh
python tests/run_browser_contracts.py \
  --browser-executable /absolute/path/to/chromium \
  --out-dir /absolute/path/outside-repositories/new-result-directory
```

The command exits with `0` for three passing contracts, `1` for a contract
failure, or `2` for a runner/environment error. The result records source and
fixture hashes. These checks do not cover live signup acceptance, email delivery,
Google registration, or the complete form-validation matrix.
