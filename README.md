# homming-site — 프로젝트 구분

이 저장소에는 **Homming 웹사이트**와 **Everymilestone Studio 제작 도구**가 함께 있습니다. 수정할 영역부터 선택하세요.

| 작업 대상 | 위치 | 시작 문서 |
| --- | --- | --- |
| Homming 랜딩·브랜드·앱·팀 페이지 | 루트 `index.html`, `brand.html`, `app.html`, `team.html`, `team/`와 관련 자산 | 아래 메인 사이트 안내와 해당 파일 |
| Everymilestone 사이트 형식·콘텐츠 뷰·제작 스킬 | `everymilestone-studio/` | [Studio README](everymilestone-studio/README.md) · [Studio 작업 규칙](everymilestone-studio/AGENTS.md) · [모듈 구조](everymilestone-studio/ARCHITECTURE.md) |

에이전트는 먼저 [루트 AGENTS.md](AGENTS.md)로 작업 범위를 확인합니다. **Studio 작업은 `cd everymilestone-studio` 후 실행**하며, 루트의 `scripts/`, `tests/`, `assets/`, `index.html`은 Studio 안의 같은 이름 경로와 다른 파일입니다.

Studio의 고객 사이트 출력은 `everymilestone-studio/.local/builds/<프로젝트>/<빌드 ID>/`입니다. 아래 배포 안내는 Homming 메인 사이트에 관한 것으로, Studio 소스 폴더나 저장소 전체를 고객 사이트 결과물로 전달하는 절차가 아닙니다. 이 디렉토리 구분은 배포 제외 설정을 대신하지 않으며 실제 게시 파일 범위는 배포할 때 확인합니다.

---

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
