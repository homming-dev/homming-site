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
