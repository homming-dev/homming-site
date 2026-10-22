# homming-site

이 저장소는 https://homm.ing 에 올라가는 Homming 웹사이트다. 랜딩 페이지, 브랜드 가이드,
가족 웹공간 미리보기, 팀 소개 페이지가 들어 있다.

## 먼저 알아야 할 두 가지

**이 저장소는 public이다.** 누구나 GitHub 로그인 없이 모든 파일과 커밋 기록을 읽는다.
한 번 푸시한 파일은 나중에 지워도 커밋 기록에 남는다.

**`main`에 머지하면 그대로 공개 배포된다.** Vercel이 이 저장소의 GitHub에 연동되어 있고,
`main`이 바뀌면 저장소 루트 전체를 homm.ing으로 자동 배포한다. 사람이 배포를 실행하는 단계는
없다. `main`에 들어간 파일은 랜딩 페이지가 아니어도 homm.ing 주소로 열릴 수 있다.
2026-10-21에 이 사실을 모른 채 작업해서, 공개할 의도가 없던 디렉토리가 랜딩 페이지와 함께
배포됐다.

이전 README는 "폴더를 압축 풀어 Vercel에 끌어다 놓는" 수동 절차를 안내했다. 그 방식은
더 쓰지 않는다.

작업 규칙은 [AGENTS.md](AGENTS.md)에 있다. 파일을 고치기 전에 읽는다.

## 주소와 파일

`vercel.json`의 `cleanUrls`가 켜져 있어 공개 주소에는 `.html`이 없다. `brand.html`은
`/brand`로 열린다.

| 파일 | 공개 주소 | 설명 |
| --- | --- | --- |
| `index.html` | `/` | 랜딩 페이지. 손으로 고친다. 다른 페이지들이 머리말·배경·글꼴을 여기서 복사한다 |
| `brand.html` | `/brand` | 브랜드 가이드. 손으로 고친다 |
| `app.html` | `/app` | 가족 웹공간 미리보기. 동작하는 서비스가 아니고 내용은 전부 합성 데이터다. `scripts/build_app.py`가 만든다 |
| `team.html` | `/team` | 팀 소개 전체. `scripts/build_team.py`가 만든다 |
| `team/*.html` | `/team/jiwoong` 등 | 팀원 한 명씩. 명함 QR 코드가 가리킨다. `scripts/build_team.py`가 만든다 |

`vercel.json`은 `/pilot`을 `/#pilot`으로 보내는 임시 redirect도 갖고 있다.

설정 파일

- `vercel.json`: clean URL과 redirect
- `robots.txt`: 검색엔진 색인 범위. 전체를 막고 랜딩·브랜드·팀·법률 페이지만 허용한다.
  `/app`은 색인에서 빠지지만 주소를 아는 사람은 열 수 있다
- `.vercelignore`: 랜딩이 아닌 경로를 배포에서 제외한다. 저장소에 남은 파일이 homm.ing으로
  나가지 않게 막는 2차 장치다
- `.gitignore`

이미지와 아이콘: `assets/homming_mark.png`, `favicon-32.png`, `apple-touch-icon.png`,
`icon-512.png`

생성 스크립트: `scripts/build_app.py`, `scripts/build_team.py`, `scripts/app_template.html`

검사와 기록: `tests/run_browser_contracts.py`, `tests/fixtures/signup-privacy-v1.json`,
`experiments/tasks/golden-v1.json`, `docs/pilot-form-fix.md`

`privacy.html`, `terms.html`, `legal.css`, `legal.js`는 아직 커밋되지 않은 로컬 초안이다.
배포에도 없다. `robots.txt`와 푸시 전 검사 허용 목록에는 이름이 미리 들어 있다.

## 저장소 설정

- 공개 범위: public, 포크 0개
- `main` 브랜치 보호: Pull Request 필수, 승인 1건 필수, 새 커밋이 올라오면 기존 승인 자동
  해제, force push 금지, 브랜치 삭제 금지. admin 권한은 이 규칙을 우회할 수 있다
- Secret scanning과 push protection 켜짐. GitHub가 커밋 안의 토큰·키를 찾아내고 푸시를 막는다

## 가입 폼 개인정보 브라우저 계약 검사

`index.html`의 가입 폼은 일반 이메일 주소를 받고, 제출 전에 동의 상자(처음에는 체크 해제됨)를
요구한다. 기존 API는 아직 `gmail`이라는 이름의 필드를 받는다. 범위는
`docs/pilot-form-fix.md`에 있다.

등록된 검사 3개는 JavaScript가 꺼진 상태(버튼 클릭과 Enter)와 제출 처리기 초기화 실패를
재현한다. 제출 처리기가 준비되기 전에 폼이 입력을 받거나 이메일·역할·동의를 주소창 질의로
보내지 못하는지 확인한다. 합성 입력만 쓰고 외부 요청은 모두 차단하며, 가입 성공은 재현하지
않는다.

Playwright와 Chromium이 이미 설치된 Python 환경에서 실행한다. 이 명령은 브라우저를 설치하지
않는다. 결과 디렉토리는 Git 저장소 밖의 새 경로로 지정한다.

```sh
python tests/run_browser_contracts.py \
  --browser-executable /absolute/path/to/chromium \
  --out-dir /absolute/path/outside-repositories/new-result-directory
```

종료 코드는 셋이다. `0`은 세 계약 모두 통과, `1`은 계약 실패, `2`는 실행기나 환경 오류다.
결과에는 소스와 fixture의 해시가 남는다. 이 검사는 실제 가입 접수, 메일 발송, Google 등록,
폼 검증 전체를 확인하지 않는다.

## 랜딩 페이지의 연락처 주소

랜딩 페이지의 이메일 주소는 HTML 문자 참조로 적혀 있다. Cloudflare의 Email Address
Obfuscation이 주소를 `[email protected]`으로 바꿔 버리기 때문이다. 그 자리표시자가 다시
보이면 해당 zone의 Scrape Shield에서 Email Address Obfuscation을 끈다.
