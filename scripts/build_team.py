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
# The slice stops before the stage's own closing tag, so close it here: left open, the fixed stage swallows
# .content and a page longer than the screen cannot scroll.
STAGE = slice_between('<div class="stage" id="stage">', "</div>\n\n<div class=\"content\">").rstrip() + "\n</div>"
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
        "story": {
            "tagline": {
                "en": "I build AI that helps families living far apart understand and look after one another.",
                "ko": "멀리 사는 가족이 서로를 이해하고 챙기도록 돕는 AI를 만듭니다.",
            },
            "sections": [
                {
                    "h": {"en": "Why I started Homming", "ko": "왜 호밍을 만들었나"},
                    "paras": {
                        "en": [
                            "I live in the United States. My parents live in Korea.",
                            "When time zones, generations and daily lives drift apart, families miss each other's days even when the love is there.",
                            "Could technology close that gap? Homming began with that question.",
                        ],
                        "ko": [
                            "저는 미국에 살고, 부모님은 한국에 계십니다.",
                            "시차가 다르고 세대가 다르고 사는 모습이 달라지면, 가족은 마음이 있어도 서로의 하루를 놓칩니다.",
                            "기술이 그 사이를 이어 줄 수 있을까. 호밍은 이 질문에서 시작했습니다.",
                        ],
                    },
                },
                {
                    "h": {"en": "What Homming is", "ko": "호밍은 어떤 회사인가"},
                    "paras": {
                        "en": [
                            "Homming is an early-stage startup building AI for families.",
                            "It helps each person with their own day, and with the things a family does together.",
                            "It is not a tool for getting work done faster. It is built around the relationships families most want to protect.",
                        ],
                        "ko": [
                            "호밍은 가족을 위한 AI를 만드는 초기 스타트업입니다.",
                            "한 사람 한 사람의 일상을 돕고, 가족이 함께할 일까지 챙깁니다.",
                            "일을 더 빨리 하게 하는 도구가 아니라, 가족이 가장 지키고 싶어 하는 관계를 중심에 두고 만듭니다.",
                        ],
                    },
                },
                {
                    "h": {"en": "Who I am", "ko": "어떤 사람인가"},
                    "paras": {
                        "en": ["For more than twenty years I have built products that bring people together."],
                        "ko": ["20년 넘게 사람과 사람을 잇는 제품을 만들었습니다."],
                    },
                    "items": {
                        "en": [
                            ("NCsoft", "Designed social online games."),
                            ("Dotdotdot (Dot3) · CPO", "Led OLOBO, an AI 3D avatar video app, from its first wireframe to launch in 23 countries, and built LoBo, an AI chatbot platform for organizations."),
                            ("Culturedots · Founder", "Created places where young people, families and immigrant communities learn each other's cultures. More than 200 young people took part."),
                            ("Now", "Studying the human life course and AgeTech in graduate school at USC, and connecting residents across cultures and generations at the City of Bellevue."),
                        ],
                        "ko": [
                            ("엔씨소프트", "소셜 온라인 게임을 기획했습니다."),
                            ("닷닷닷(Dot3) CPO", "AI 3D 아바타 영상 앱 OLOBO를 첫 화면 설계부터 23개국 출시까지 이끌었고, 기업용 AI 챗봇 플랫폼 LoBo를 만들었습니다."),
                            ("컬처닷츠 설립", "청소년과 가족, 이민자 커뮤니티가 서로의 문화를 배우는 자리를 만들었습니다. 청소년 200여 명이 참여했습니다."),
                            ("지금", "USC 대학원에서 사람의 생애 과정과 에이징테크를 공부하고, 벨뷰시에서 다양한 문화와 세대의 시민을 잇는 일을 합니다."),
                        ],
                    },
                },
                {
                    "h": {"en": "Turning everyday life into projects", "ko": "일상을 프로젝트로 만드는 사람"},
                    "image": {"en": "/assets/team/eunyoung-journey-en.webp", "ko": "/assets/team/eunyoung-journey-ko.webp"},
                    "size": (724, 2172),
                    "alt": {
                        "en": "An illustrated timeline of Eun Young's path, from a sixth-grader who wanted to touch hearts to Homming today.",
                        "ko": "초등학교 6학년 때의 꿈부터 지금의 호밍까지, 권은영이 걸어온 길을 그린 그림.",
                    },
                },
            ],
            "cta": {"href": "/", "label": {"en": "About Homming &rarr;", "ko": "호밍 알아보기 &rarr;"}},
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
  .person .tagline{font-family:var(--serif); font-size:clamp(22px, 2.6vw, 28px); line-height:1.35; letter-spacing:-0.01em; color:var(--ink-900);}
  .person .story{display:flex; flex-direction:column; gap:12px; margin-top:18px; padding-top:22px; border-top:1px solid rgba(26,22,20,0.14);}
  .person .story h3{font-family:var(--mono); font-weight:500; font-size:12px; letter-spacing:0.18em; text-transform:uppercase; color:var(--ink-700); margin:0 0 2px;}
  .person .story ul{list-style:none; margin:4px 0 0; padding:0; display:flex; flex-direction:column; gap:14px;}
  .person .story li{font-size:17px; line-height:1.6; color:var(--ink-700);}
  .person .story li strong{display:block; font-weight:600; color:var(--ink-900);}
  .person .story img{display:block; width:100%; height:auto; border-radius:14px; background:#fbf7f1;}
  .person .story .caption{font-size:15px; color:var(--ink-500);}
  .person .story.last{border-top:0; padding-top:0;}
  @media (max-width: 520px){ .person .story.wide{margin-left:-14px; margin-right:-14px;} .person .story.wide h3, .person .story.wide .caption{padding:0 14px;} }
  .foot .home{color:var(--ink-700); text-decoration:none; border-bottom:1px solid var(--ink-300);}
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


def story_entries(p: dict, lang: str) -> list[tuple[str, str]]:
    """The i18n keys and texts of a person's long story (their own page only)."""
    st, s = p["story"], p["slug"]
    out = [(f"{s}.tagline", st["tagline"][lang])]
    for n, sec in enumerate(st["sections"], 1):
        out.append((f"{s}.s{n}.h", sec["h"][lang]))
        for i, t in enumerate(sec.get("paras", {}).get(lang, []), 1):
            out.append((f"{s}.s{n}.p{i}", t))
        for i, (label, text) in enumerate(sec.get("items", {}).get(lang, []), 1):
            out.append((f"{s}.s{n}.i{i}", f"<strong>{label}</strong> {text}"))
        if "caption" in sec:
            out.append((f"{s}.s{n}.cap", sec["caption"][lang]))
    out.append((f"{s}.cta", st["cta"]["label"][lang]))
    return out


def story_card(p: dict, lang: str = "en") -> str:
    """One person's own page: name, one line, then the story in short blocks for a phone."""
    st, s = p["story"], p["slug"]
    text = dict(story_entries(p, lang))
    blocks = []
    for n, sec in enumerate(st["sections"], 1):
        rows = [f'            <h3 data-i18n="{s}.s{n}.h">{text[f"{s}.s{n}.h"]}</h3>']
        for i in range(1, len(sec.get("paras", {}).get(lang, [])) + 1):
            rows.append(f'            <p data-i18n="{s}.s{n}.p{i}">{text[f"{s}.s{n}.p{i}"]}</p>')
        count = len(sec.get("items", {}).get(lang, []))
        if count:
            lis = "\n".join(f'              <li data-i18n="{s}.s{n}.i{i}">{text[f"{s}.s{n}.i{i}"]}</li>' for i in range(1, count + 1))
            rows.append(f"            <ul>\n{lis}\n            </ul>")
        wide = ""
        if "image" in sec:
            # The picture differs by language, so the language script sets src; noscript keeps the English one.
            w, h = sec["size"]
            img = sec["image"]
            alt = {k: v.replace('"', "&quot;") for k, v in sec["alt"].items()}
            rows.append(
                f'            <img width="{w}" height="{h}" decoding="async" alt="{alt["en"]}" '
                f'data-src-en="{img["en"]}" data-src-ko="{img["ko"]}" data-alt-en="{alt["en"]}" data-alt-ko="{alt["ko"]}">\n'
                f'            <noscript><img width="{w}" height="{h}" src="{img["en"]}" alt="{alt["en"]}"></noscript>'
            )
            wide = " wide"
        if "caption" in sec:
            rows.append(f'            <p class="caption" data-i18n="{s}.s{n}.cap">{text[f"{s}.s{n}.cap"]}</p>')
        blocks.append(f'          <section class="story{wide}">\n' + "\n".join(rows) + "\n          </section>")
    body = "\n".join(blocks)
    links = [f'            <a href="{href}" target="_blank" rel="noopener">{label}</a>' for label, href in p["links"]]
    links.append(f'            <a href="{st["cta"]["href"]}" data-i18n="{s}.cta">{text[f"{s}.cta"]}</a>')
    link_rows = "\n".join(links)
    return f'''        <article class="card person" id="{s}">
          <div class="role" data-i18n="{s}.role">{p["role"][lang]}</div>
          <h1 class="name"><span data-i18n="{s}.name">{p["name"][lang]}</span><small data-i18n="{s}.alt">{p["alt"][lang]}</small></h1>
          <p class="tagline" data-i18n="{s}.tagline">{text[f"{s}.tagline"]}</p>
{body}
          <section class="story last">
          <div class="links">
{link_rows}
          </div>
          </section>
        </article>'''


def dictionary(people: list[dict], lang: str, *, titles: bool) -> str:
    rows = []
    base = TEXT[lang]
    keys = ["status", "eyebrow", "title", "lede", "all", "back", "private"] if titles else ["status", "eyebrow", "all", "back", "private"]
    for k in keys:
        rows.append(f"      {js_str(k)}: {js_str(base[k])},")
    for p in people:
        s = p["slug"]
        rows.append(f"      {js_str(s + '.role')}: {js_str(p['role'][lang])}, {js_str(s + '.name')}: {js_str(p['name'][lang])}, {js_str(s + '.alt')}: {js_str(p['alt'][lang])},")
        if not titles and "story" in p:
            for k, t in story_entries(p, lang):
                rows.append(f"      {js_str(k)}: {js_str(t)},")
            continue
        for i, t in enumerate(p["paras"][lang], 1):
            rows.append(f"      {js_str(f'{s}.p{i}')}: {js_str(t)},")
    return "\n".join(rows).rstrip(",")


def page(people: list[dict], *, single: bool, title_en: str, title_ko: str) -> str:
    cards = "\n\n".join(story_card(p) if single and "story" in p else card(p) for p in people)
    grid_class = "grid one" if single else "grid"
    if single:
        p = people[0]
        head = f'''      <div class="eyebrow"><span class="rule"></span> <span data-i18n="eyebrow">{TEXT["en"]["eyebrow"]}</span></div>'''
        intro = ""
        more = f'''      <div class="more"><a href="/team" data-i18n="all">{TEXT["en"]["all"]}</a></div>'''
        page_title = f"{title_en}"
        og_desc = p["story"]["tagline"]["en"] if "story" in p else p["paras"]["en"][0]
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
{EXTRA_CSS}
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
    var pics = document.querySelectorAll("img[data-src-en]");
    for (var m = 0; m < pics.length; m++) {{
      var src = pics[m].getAttribute("data-src-" + lang) || pics[m].getAttribute("data-src-en");
      if (pics[m].getAttribute("src") !== src) pics[m].setAttribute("src", src);
      pics[m].setAttribute("alt", pics[m].getAttribute("data-alt-" + lang) || pics[m].getAttribute("data-alt-en"));
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
