"""Build the unlisted people pages of homm.ing from the landing page's shell.

    python3 scripts/build_team.py

Writes team.html (everyone) and team/<slug>.html (one person each, for the QR code on that
person's business card). The background, header, fonts and language switch are copied from
index.html so the pages always match the landing page. Texts live in PEOPLE and TEXT below;
facts follow the team section of the 모두의 창업 business plan (2026-09-28) and the YC
application for the names. Run the humanizer on any text you change.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")


def slice_between(start: str, end: str, *, keep_end: bool = False) -> str:
    a = INDEX.index(start)
    b = INDEX.index(end, a)
    return INDEX[a : b + (len(end) if keep_end else 0)]


HEAD_LINKS = slice_between('<link rel="icon"', "<style>").rstrip()
CSS = slice_between("<style>", "</style>", keep_end=True)
STAGE = slice_between('<div class="stage" id="stage">', "</div>\n\n<div class=\"content\">").rstrip()
HEADER = slice_between('    <header class="nav">', "</header>", keep_end=True)
BG_SCRIPT = slice_between("<script>\n(function(){\n  // Trigger intro animations", "</script>", keep_end=True)

PEOPLE = [
    {
        "slug": "eunyoung",
        "role": {"en": "Founder · CEO", "ko": "창업자 · CEO"},
        "name": {"en": "Eun Young Kwoun", "ko": "권은영"},
        "alt": {"en": "권은영", "ko": "Eun Young Kwoun"},
        "paras": {
            "en": [
                "Leads product strategy, customer discovery and business development. More than twenty years in technology and product: former CPO and Senior Director of Product at an AI company, where she led 0-to-1 AI products and a consumer launch across 23 countries.",
                "Graduate studies in Applied Technology and Aging (M.S. in progress). Bilingual product and community experience across the United States and Korea. She lives in the United States; her parents live in Korea.",
            ],
            "ko": [
                "제품 전략과 고객 검증, 사업 개발을 맡고 있습니다. 기술과 제품 분야에서 20년 넘게 일했고, AI 회사에서 CPO와 제품 시니어 디렉터로 새 AI 제품을 처음부터 만들어 23개국에 출시했습니다.",
                "지금은 응용기술과 노화(Applied Technology and Aging) 석사 과정을 밟고 있습니다. 미국과 한국 양쪽에서 제품을 만들고 커뮤니티를 꾸려 온 경험이 있고, 미국에 살며 부모님은 한국에 계십니다.",
            ],
        },
        "links": [],
        # Illustrated timeline shown below the intro on her own page only. The art is lettered,
        # so each image has a Korean original and an English version (same drawing, text
        # replaced); the language switch shows one set. The three images continue one red
        # thread, so they are stacked without gaps in this order.
        "story": {
            "label": {"en": "The story so far", "ko": "지금까지의 이야기"},
            "images": [
                {"w": 1000, "h": 1435,
                 "ko": ("/assets/team/eunyoung-story-1.webp",
                        "일상을 프로젝트로 만드는 사람: 감동을 주고 싶던 초등학생, 대학 시절 ADPOWER에서 밤새 나눈 아이디어, 광고·캐릭터·게임을 기획한 첫 커리어, 미국 이주, 가족교육 회사 Hummingtree와 기획서 한 장으로 시작한 생활 속 프로젝트."),
                 "en": ("/assets/team/eunyoung-story-1-en.webp",
                        "Someone who turns everyday life into projects: a sixth grader who wanted to move people, nights of sharing ideas at ADPOWER in college, a first career planning ads, characters and games, the move to the U.S., and everyday projects from the family education company Hummingtree to pitching with a single proposal.")},
                {"w": 1000, "h": 1374,
                 "ko": ("/assets/team/eunyoung-story-2.webp",
                        "가족의 대화에서 AI 제품까지: 라디오 코리아의 가족 영화 토론 프로그램, 이민 여성의 새 출발을 도운 Simple Steps, 청소년과 가족을 위한 배움의 장 Culture Dots, AI 서비스를 기획하고 출시한 Dotdotdot."),
                 "en": ("/assets/team/eunyoung-story-2-en.webp",
                        "From family conversations to AI products: a film discussion program for families on Radio Korea, Simple Steps helping immigrant women start fresh, Culture Dots creating learning spaces for teens and families, and Dotdotdot, where she led the planning and launch of AI services.")},
                {"w": 1000, "h": 1436,
                 "ko": ("/assets/team/eunyoung-story-3.webp",
                        "지금 만드는 일, 앞으로의 꿈: 가족이 서로를 이해하고 챙기도록 돕는 AI를 만드는 Homming, USC 대학원에서 에이징테크 공부, City of Bellevue에서 시민의 대화를 여는 일, 그리고 여든에 스탠드업 코미디언으로 데뷔하는 꿈."),
                 "en": ("/assets/team/eunyoung-story-3-en.webp",
                        "Now, and the dream ahead: Homming, an AI that helps families understand and care for each other; graduate study in AgeTech at USC; opening civic conversations with the City of Bellevue; and a dream of debuting as a stand-up comic at 80.")},
            ],
        },
    },
    {
        "slug": "jiwoong",
        "role": {"en": "CTO", "ko": "CTO"},
        "name": {"en": "Jiwoong Kim", "ko": "김지웅"},
        "alt": {"en": "김지웅", "ko": "Jiwoong Kim"},
        "paras": {
            "en": [
                "Leads AI development, system architecture and technical delivery. Ph.D. in particle physics, with large-scale experiment data analysis, distributed training and signal-classification models from the CMS experiment at CERN.",
                "Quantitative researcher: built and operates a machine-learning model for a public mutual fund, and led the research and development of an AI-agent system that automates investment research. Production AI, evaluation and benchmarking, multi-agent research systems.",
                "At Homming he owns the architecture: the personal agents, Hodu between them, the consent contract, and the evaluation-first way the team ships.",
            ],
            "ko": [
                "인공지능 개발과 시스템 설계, 기술 구현을 맡고 있습니다. 입자물리학 박사로, CERN의 CMS 실험에서 대규모 실험 데이터를 분석하고 분산 학습과 신호 분류 모델을 만들었습니다.",
                "그 뒤 퀀트 리서처로 공모펀드에 쓰이는 기계학습 모델을 만들어 운영했고, 투자 리서치를 인공지능 에이전트가 스스로 돌리는 시스템의 연구개발을 이끌었습니다. 실제 서비스에 올라간 AI와 정량 평가, 다중 에이전트 시스템이 전문입니다.",
                "호밍에서는 구조를 책임집니다. 사람마다 하나씩 두는 퍼스널 에이전트, 그 사이를 잇는 호두, 동의 계약, 그리고 평가 사례부터 만들고 고치는 개발 방식까지.",
            ],
        },
        "links": [
            ("linkedin.com/in/jkimquant", "https://www.linkedin.com/in/jkimquant"),
            ("ico1036.github.io/notes", "https://ico1036.github.io/notes"),
        ],
    },
    {
        "slug": "soyeon",
        "role": {"en": "UX Research & Product Planning", "ko": "제품 기획 · 사용자 연구"},
        "name": {"en": "Soyeon Park", "ko": "박소연"},
        "alt": {"en": "박소연", "ko": "Soyeon Park"},
        "paras": {
            "en": [
                "Runs user research and product planning: interviews with parents and adult children, usability tests of the prototype, checks on how well the agents answer, and the measures that tell us whether the pilot works.",
                "M.S. in Business Analytics. More than three years of product management for AI services, with over thirty qualitative studies, analytics-driven UX improvements, evaluation of AI output and app launches. Fluent in Korean and English, so she can talk with both sides of a family directly.",
            ],
            "ko": [
                "사용자 연구와 제품 기획을 맡고 있습니다. 부모님과 자녀를 직접 인터뷰하고, 시제품의 사용성과 에이전트 답의 품질을 확인하고, 시범 서비스가 제대로 되는지 재는 기준을 만듭니다.",
                "비즈니스 애널리틱스 석사. AI 서비스의 제품 관리를 3년 넘게 했고, 정성 사용자 조사 30회 이상, 이용 데이터로 사용 경험을 고친 경험, AI 출력 평가와 앱 출시 경험이 있습니다. 한국어와 영어 모두 능숙해서 가족 양쪽과 바로 이야기합니다.",
            ],
        },
        "links": [],
    },
    {
        "slug": "jaejun",
        "role": {"en": "AI Engineering Advisor", "ko": "AI 엔지니어"},
        "name": {"en": "Jaejun Lee", "ko": "이재준"},
        "alt": {"en": "이재준", "ko": "Jaejun Lee"},
        "paras": {
            "en": [
                "Reviews how Homming is built: the architecture of the AI system, the code that matters most, and how it is deployed and run in the cloud.",
                "B.S. in Aerospace Engineering and Computer Science. More than seven years building platform and backend software, including platforms that run machine-learning and large language models, and leading development teams. Experienced in orchestrating AI workflows and building cloud-based systems.",
            ],
            "ko": [
                "호밍이 어떻게 만들어지는지를 봐 줍니다. 인공지능 시스템의 구조, 핵심 코드, 그리고 클라우드에 올려 운영하는 방식을 검토합니다.",
                "항공우주공학과 컴퓨터과학 학사. 플랫폼과 백엔드 소프트웨어를 7년 넘게 만들었고, 기계학습과 대규모 언어모델을 운영하는 플랫폼을 개발하며 개발팀을 이끌었습니다. AI 작업 흐름을 엮고 클라우드 기반 시스템을 세운 경험이 있습니다.",
            ],
        },
        "links": [],
    },
]

TEXT = {
    "en": {
        "status": "Quietly in the making · 2026",
        "eyebrow": "The people · 2026",
        "title": "Who is building <em>Homming</em>",
        "lede": "Four people, one shared worry: parents in Korea, children living far away, and no good way to stay close.",
        "all": "Everyone at Homming &rarr;",
        "back": "&larr; homm.ing",
        "private": "© Homming · unlisted page",
    },
    "ko": {
        "status": "조용히 만드는 중 · 2026",
        "eyebrow": "만드는 사람들 · 2026",
        "title": "호밍을 만드는 <em>사람들</em>",
        "lede": "부모님은 한국에, 자녀는 멀리. 네 사람 다 같은 걱정을 안고 있었고, 가까이 지낼 마땅한 방법이 없어서 호밍을 시작했습니다.",
        "all": "호밍 사람들 모두 보기 &rarr;",
        "back": "&larr; homm.ing",
        "private": "© Homming · 비공개 페이지",
    },
}

EXTRA_CSS = """<style>
  .people{position:relative; z-index:5; max-width:1100px; margin:0 auto; width:100%; padding:0 8px 48px;}
  .people h1.pp{font-family:var(--serif); font-weight:300; font-optical-sizing:auto; font-size:clamp(40px, 6.5vw, 96px); line-height:1.0; letter-spacing:-0.03em; margin:0 0 20px; color:var(--ink-900);}
  .people h1.pp em{font-style:italic; font-weight:400;}
  .people .lede{margin:0 0 40px; max-width:620px;}
  .grid{display:grid; grid-template-columns:repeat(2, minmax(0,1fr)); gap:28px;}
  .grid.one{grid-template-columns:minmax(0,640px);}
  @media (max-width: 860px){ .grid{grid-template-columns:1fr;} }
  .person{display:flex; flex-direction:column; gap:14px;}
  .person .role{font-family:var(--mono); font-size:11px; letter-spacing:0.22em; text-transform:uppercase; color:var(--ink-700);}
  .person .name{font-family:var(--serif); font-weight:400; font-size:clamp(28px, 3.4vw, 40px); line-height:1.1; letter-spacing:-0.02em; margin:0; color:var(--ink-900);}
  .person .name small{display:block; font-family:var(--sans); font-weight:500; font-size:15px; letter-spacing:0; color:var(--ink-500); margin-top:6px;}
  .person p{margin:0; font-size:17px; line-height:1.6; color:var(--ink-700);}
  .person .links{display:flex; flex-wrap:wrap; gap:14px; margin-top:6px;}
  .person .links a, .people .more a{font-family:var(--mono); font-size:12px; letter-spacing:0.08em; color:var(--ink-700); text-decoration:none; border-bottom:1px solid var(--ink-300); padding-bottom:2px;}
  .person .links a:hover, .people .more a:hover{color:var(--ink-900); border-color:var(--ink-900);}
  .people .more{margin-top:28px;}
  .foot .home{color:var(--ink-700); text-decoration:none; border-bottom:1px solid var(--ink-300);}
</style>"""

STORY_CSS = """<style>
  /* Illustrated story on the same .card surface as the intro. The WebP files carry the
     paper as transparency (white un-multiplied into alpha), so the card's own translucent
     background shows through exactly as it does behind the intro text. */
  .story{padding:28px 0 8px; overflow:hidden;}
  .story .role{padding:0 24px; margin-bottom:4px; font-family:var(--mono); font-size:11px; letter-spacing:0.22em; text-transform:uppercase; color:var(--ink-700);}
  .story a{display:block;}
  .story img{display:block; width:100%; height:auto;}
  /* Each image comes in a Korean and an English version; the language script sets
     <html lang> and only the matching set is shown. The images are lazy, so the hidden
     set is never downloaded. */
  html[lang="ko"] .story a.en, html:not([lang="ko"]) .story a.ko{display:none;}
</style>"""


def js_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def card(p: dict, lang: str = "en") -> str:
    paras = "\n".join(
        f'          <p data-i18n="{p["slug"]}.p{i}">{t}</p>' for i, t in enumerate(p["paras"][lang], 1)
    )
    links = ""
    if p["links"]:
        items = "\n".join(
            f'            <a href="{href}" target="_blank" rel="noopener">{label}</a>' for label, href in p["links"]
        )
        links = f'\n          <div class="links">\n{items}\n          </div>'
    return f'''        <article class="card person" id="{p["slug"]}">
          <div class="role" data-i18n="{p["slug"]}.role">{p["role"][lang]}</div>
          <h2 class="name"><span data-i18n="{p["slug"]}.name">{p["name"][lang]}</span><small data-i18n="{p["slug"]}.alt">{p["alt"][lang]}</small></h2>
{paras}{links}
        </article>'''


def story(p: dict) -> str:
    s = p.get("story")
    if not s:
        return ""
    imgs = "\n".join(
        f'          <a class="{lang}" lang="{lang}" href="{img[lang][0]}" target="_blank" rel="noopener">'
        f'<img src="{img[lang][0]}" width="{img["w"]}" height="{img["h"]}" alt="{img[lang][1]}" loading="lazy" decoding="async"></a>'
        for img in s["images"] for lang in ("ko", "en")
    )
    return f'''

        <section class="card story" aria-labelledby="{p["slug"]}-story">
          <div class="role" id="{p["slug"]}-story" data-i18n="{p["slug"]}.story">{s["label"]["en"]}</div>
{imgs}
        </section>'''


def dictionary(people: list[dict], lang: str, *, titles: bool) -> str:
    rows = []
    base = TEXT[lang]
    keys = ["status", "eyebrow", "title", "lede", "all", "back", "private"] if titles else ["status", "eyebrow", "all", "back", "private"]
    for k in keys:
        rows.append(f"      {js_str(k)}: {js_str(base[k])},")
    for p in people:
        s = p["slug"]
        rows.append(f"      {js_str(s + '.role')}: {js_str(p['role'][lang])}, {js_str(s + '.name')}: {js_str(p['name'][lang])}, {js_str(s + '.alt')}: {js_str(p['alt'][lang])},")
        for i, t in enumerate(p["paras"][lang], 1):
            rows.append(f"      {js_str(f'{s}.p{i}')}: {js_str(t)},")
        if not titles and p.get("story"):
            rows.append(f"      {js_str(s + '.story')}: {js_str(p['story']['label'][lang])},")
    return "\n".join(rows).rstrip(",")


def page(people: list[dict], *, single: bool, title_en: str, title_ko: str) -> str:
    cards = "\n\n".join(card(p) for p in people)
    grid_class = "grid one" if single else "grid"
    has_story = single and bool(people[0].get("story"))
    cards += story(people[0]) if has_story else ""
    extra_css = EXTRA_CSS + ("\n" + STORY_CSS if has_story else "")
    if single:
        p = people[0]
        head = f'''      <div class="eyebrow"><span class="rule"></span> <span data-i18n="eyebrow">{TEXT["en"]["eyebrow"]}</span></div>'''
        intro = ""
        more = f'''      <div class="more"><a href="/team" data-i18n="all">{TEXT["en"]["all"]}</a></div>'''
        page_title = f"{title_en}"
        og_desc = p["paras"]["en"][0]
    else:
        head = f'''      <div class="eyebrow"><span class="rule"></span> <span data-i18n="eyebrow">{TEXT["en"]["eyebrow"]}</span></div>
      <h1 class="pp" data-i18n="title">{TEXT["en"]["title"]}</h1>'''
        intro = f'''      <p class="lede" data-i18n="lede">{TEXT["en"]["lede"]}</p>\n'''
        more = ""
        page_title = title_en
        og_desc = TEXT["en"]["lede"]
    en = dictionary(people, "en", titles=not single)
    ko = dictionary(people, "ko", titles=not single)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{page_title}</title>
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="{og_desc.replace('"', '&quot;')}">
{HEAD_LINKS}
{CSS}
{extra_css}
</head>
<body>

{STAGE}

<div class="content">

{HEADER}

    <main class="people" id="hero">
{head}
{intro}      <div class="{grid_class}">
{cards}
      </div>
{more}
    </main>

    <footer class="foot">
      <div class="foot-left"><a class="home" href="/" data-i18n="back">&larr; homm.ing</a></div>
      <div class="foot-center"></div>
      <div class="foot-right"><span data-i18n="private">© Homming · unlisted page</span></div>
    </footer>

</div>

{BG_SCRIPT}

<script>
/* Language: EN / 한국어. Same switch as the landing page, remembered per device. */
(function () {{
  var I18N = {{
    en: {{
{en}
    }},
    ko: {{
{ko}
    }}
  }};
  var KEY = "homming_lang";
  function stored() {{ try {{ return localStorage.getItem(KEY); }} catch (e) {{ return null; }} }}
  function remember(lang) {{ try {{ localStorage.setItem(KEY, lang); }} catch (e) {{}} }}
  function pick() {{
    var saved = stored();
    if (saved === "en" || saved === "ko") return saved;
    var nav = (navigator.language || "").toLowerCase();
    return nav.indexOf("ko") === 0 ? "ko" : "en";
  }}
  function apply(lang) {{
    var d = I18N[lang] || I18N.en;
    document.documentElement.lang = lang;
    var nodes = document.querySelectorAll("[data-i18n]");
    for (var i = 0; i < nodes.length; i++) {{
      var k = nodes[i].getAttribute("data-i18n");
      if (d[k] !== undefined) nodes[i].innerHTML = d[k];
    }}
    var buttons = document.querySelectorAll(".lang button");
    for (var b = 0; b < buttons.length; b++) {{
      buttons[b].setAttribute("aria-pressed", buttons[b].getAttribute("data-lang") === lang ? "true" : "false");
    }}
    document.title = lang === "ko" ? {js_str(title_ko)} : {js_str(title_en)};
  }}
  apply(pick());
  var toggles = document.querySelectorAll(".lang button");
  for (var t = 0; t < toggles.length; t++) {{
    toggles[t].addEventListener("click", function () {{ var lang = this.getAttribute("data-lang"); remember(lang); apply(lang); }});
  }}
}})();
</script>
</body>
</html>
'''


def main() -> None:
    (ROOT / "team").mkdir(exist_ok=True)
    (ROOT / "team.html").write_text(page(PEOPLE, single=False, title_en="homming · people", title_ko="호밍 · 만드는 사람들"), encoding="utf-8")
    for p in PEOPLE:
        html = page([p], single=True, title_en=f"{p['name']['en']} · homming", title_ko=f"{p['name']['ko']} · 호밍")
        (ROOT / "team" / f"{p['slug']}.html").write_text(html, encoding="utf-8")
    print("wrote team.html and", ", ".join(f"team/{p['slug']}.html" for p in PEOPLE))


if __name__ == "__main__":
    main()
