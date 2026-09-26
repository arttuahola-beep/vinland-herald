#!/usr/bin/env python3
"""Refresh the front page and the archive from issues/issues.json.

Run from anywhere:

    python3 scripts/build_site.py

The newest issue folder is the source for the site root. This script copies
that issue's index.html to /index.html and rewrites the navigation and favicon
links so they resolve from the root. It also writes /archive/index.html, newest
issue first.

An issue page is expected to carry this navigation (relative to its own folder)
and a matching favicon link. For an issue at issues/YYYY-MM-DD/ the prefix is
"../../":

    <link rel="icon" href="../../favicon.svg" type="image/svg+xml">
    <nav class="site-nav" aria-label="The Vinland Herald"><a class="nav-home" href="../../">Front page</a><a class="nav-archive" href="../../archive/">Archive</a></nav>
"""

from __future__ import annotations

import html
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "issues" / "issues.json"
REQUIRED = ("date", "volume", "number", "lead_headline", "path")


def fail(message: str) -> None:
    print(f"build_site.py: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_issues() -> list[dict]:
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"missing {MANIFEST.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        fail(f"issues/issues.json is not valid JSON: {exc}")
    if not isinstance(data, list) or not data:
        fail("issues/issues.json must be a non-empty list")
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            fail(f"entry {index} is not an object")
        missing = [key for key in REQUIRED if key not in item]
        if missing:
            fail(f"entry {index} is missing {', '.join(missing)}")
        try:
            datetime.strptime(item["date"], "%Y-%m-%d")
        except ValueError:
            fail(f"entry {index} has a date that is not YYYY-MM-DD: {item['date']}")
    return sorted(data, key=lambda item: item["date"], reverse=True)


def prefix_for(issue_path: str) -> str:
    parts = [part for part in issue_path.strip("/").split("/") if part]
    if not parts:
        fail(f"invalid issue path: {issue_path!r}")
    return "../" * len(parts)


def rewrite_for_root(page: str, issue_prefix: str, source: Path) -> str:
    icon = f'href="{issue_prefix}favicon.svg"'
    home = f'class="nav-home" href="{issue_prefix}"'
    archive = f'class="nav-archive" href="{issue_prefix}archive/"'
    rel = source.relative_to(ROOT)
    if icon not in page or home not in page or archive not in page:
        fail(
            f"{rel} is missing the site navigation or favicon link "
            f"for prefix {issue_prefix!r}"
        )
    page = page.replace(icon, 'href="favicon.svg"', 1)
    page = page.replace(archive, 'class="nav-archive" href="archive/"', 1)
    page = page.replace(home, 'class="nav-home" href="./"', 1)
    return page


def format_date(iso: str) -> str:
    when = datetime.strptime(iso, "%Y-%m-%d")
    return f"{when.strftime('%A')}, {when.day} {when.strftime('%B %Y')}"


def build_archive(issues: list[dict]) -> str:
    items = []
    for issue in issues:
        href = "../" + issue["path"].strip("/") + "/"
        date = html.escape(format_date(issue["date"]))
        volume = html.escape(f"Vol. {issue['volume']} · No. {issue['number']}")
        headline = html.escape(issue["lead_headline"])
        items.append(
            "    <li>\n"
            f'      <a href="{html.escape(href, quote=True)}">\n'
            f'        <span class="date">{date}</span>\n'
            f'        <span class="vol">{volume}</span>\n'
            f'        <span class="hed">{headline}</span>\n'
            "      </a>\n"
            "    </li>"
        )
    listing = "\n".join(items)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<title>Archive &middot; The Vinland Herald</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=Libre+Caslon+Text:ital,wght@0,400;0,700;1,400&family=Old+Standard+TT:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<style>
:root{{--ink:#1b1a17;--paper:#f6f1e4;--rule:#2a2824;--muted:#5a554b;--soft:#e9e1cc}}
*{{box-sizing:border-box}}
body{{margin:0;background:#d9d2c0;color:var(--ink);font-family:"Libre Caslon Text",Georgia,"Times New Roman",serif;font-size:16px;line-height:1.45}}
.site-nav{{background:var(--paper);border-bottom:1px solid var(--rule);font-family:"Old Standard TT",serif;font-size:12px;letter-spacing:.14em;text-transform:uppercase;text-align:center;padding:6px 12px}}
.site-nav a{{color:var(--ink);text-decoration:none;padding:0 14px}}
.site-nav a+a{{border-left:1px solid var(--rule)}}
.site-nav a:hover,.site-nav a:focus{{text-decoration:underline}}
.sheet{{max-width:820px;margin:24px auto;background:var(--paper);padding:22px 34px 36px;box-shadow:0 2px 18px rgba(0,0,0,.18)}}
header.mast{{text-align:center;border-bottom:4px double var(--rule);padding-bottom:8px;margin-bottom:8px}}
h1.title{{font-family:"UnifrakturMaguntia","Old English Text MT",serif;font-weight:400;font-size:clamp(40px,7vw,68px);margin:8px 0 0;line-height:1}}
.founded,.dateline{{font-family:"Old Standard TT",serif;font-size:14px}}
.founded{{font-style:italic;margin-top:4px}}
.dateline{{letter-spacing:.08em;text-transform:uppercase;font-weight:700;margin-top:6px}}
h2.section{{font-family:"Old Standard TT",serif;font-size:13px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;text-align:center;margin:12px 0 0;border-bottom:1px solid var(--rule);padding-bottom:6px}}
ol.issues{{list-style:none;margin:0;padding:0}}
ol.issues li{{border-bottom:1px solid var(--rule)}}
ol.issues a{{display:block;padding:14px 2px 16px;color:inherit;text-decoration:none}}
ol.issues .date{{display:block;font-family:"Old Standard TT",serif;font-size:13px;font-weight:700;letter-spacing:.06em;text-transform:uppercase}}
ol.issues .vol{{display:block;font-family:"Old Standard TT",serif;font-size:13px;color:var(--muted);margin-top:2px}}
ol.issues .hed{{display:block;font-family:"Playfair Display",Georgia,serif;font-weight:900;font-size:clamp(22px,3vw,30px);line-height:1.15;margin-top:6px}}
ol.issues a:hover .hed,ol.issues a:focus .hed{{text-decoration:underline}}
footer{{margin-top:22px;border-top:4px double var(--rule);padding-top:8px;font-size:12px;color:var(--muted);text-align:center;font-family:"Old Standard TT",serif}}
@media (max-width:720px){{
 .sheet{{margin:0;padding:16px 14px 28px}}
}}
</style>
</head>
<body>
<nav class="site-nav" aria-label="The Vinland Herald"><a class="nav-home" href="../">Front page</a><a class="nav-archive" href="./">Archive</a></nav>
<div class="sheet">
<header class="mast">
<h1 class="title">The Vinland Herald</h1>
<div class="founded">Founded 1867 &middot; Karontoborg</div>
<div class="dateline">The Commonwealth&rsquo;s Newspaper of Record</div>
</header>
<h2 class="section">Archive</h2>
<ol class="issues">
{listing}
</ol>
<footer>The Vinland Herald &middot; Founded 1867 &middot; Karontoborg</footer>
</div>
</body>
</html>
"""


def main() -> None:
    issues = load_issues()
    newest = issues[0]
    issue_html = ROOT / newest["path"].strip("/") / "index.html"
    if not issue_html.is_file():
        fail(f"missing {issue_html.relative_to(ROOT)}")
    page = issue_html.read_text(encoding="utf-8")
    root_page = rewrite_for_root(page, prefix_for(newest["path"]), issue_html)
    (ROOT / "index.html").write_text(root_page, encoding="utf-8")
    archive_dir = ROOT / "archive"
    archive_dir.mkdir(exist_ok=True)
    (archive_dir / "index.html").write_text(build_archive(issues), encoding="utf-8")
    print(f"Front page set from {newest['date']}: {newest['lead_headline']}")
    print(f"Archive lists {len(issues)} issue(s)")


if __name__ == "__main__":
    main()
