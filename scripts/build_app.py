"""Build app.html: the preview of the family web space (homm.ing/app), not a working service.

    python3 scripts/build_app.py

A person types the six-digit code KakaoTalk gave them and sees their family: who is connected,
what they share and at which level, what went back and forth, the next family letter, and which
services are connected. Everything on the page is synthetic and nothing leaves the browser.
Favicons, fonts and the brand mark are copied from index.html so the page matches the landing
page. Run the humanizer on any Korean you change.
"""
from __future__ import annotations

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")


def between(start: str, end: str, *, keep_end: bool = False) -> str:
    a = INDEX.index(start)
    b = INDEX.index(end, a)
    return INDEX[a : b + (len(end) if keep_end else 0)]


HEAD_LINKS = between('<link rel="icon"', "<style>").rstrip()
BRAND_SVG = between('<svg viewBox="0 0 684 649"', "</svg>", keep_end=True)

PAGE = open(ROOT / "scripts" / "app_template.html", encoding="utf-8").read()
PAGE = PAGE.replace("{{HEAD_LINKS}}", HEAD_LINKS).replace("{{BRAND_SVG}}", BRAND_SVG)
(ROOT / "app.html").write_text(PAGE, encoding="utf-8")
print("wrote app.html", len(PAGE.encode()), "bytes")
