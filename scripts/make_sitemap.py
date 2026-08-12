#!/usr/bin/env python3
"""Generate a priority-weighted sitemap.xml plus an AI-crawler-open robots.txt.

A sitemap where every page is 0.5 tells Google nothing. The weighting is the point.

Usage:
  python3 make_sitemap.py <build-dir> --base-url https://site.com --dry-run
  python3 make_sitemap.py dist --base-url https://site.com --out public
"""
import argparse
import datetime
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

SKIP_DIRS = {"node_modules", ".git", ".astro", ".next", "_astro", "assets"}

# (label, priority, changefreq, regex matched against the route)
RULES = [
    ("homepage",   1.0, "weekly",  r"^/$"),
    ("legal",      0.3, "yearly",  r"(mentions-legales|privacy|politique|cgv|cgu|terms|legal|cookies)"),
    # Regulatory-change pages are the citation play: freshest content, fastest decay.
    ("reform",     0.9, "weekly",  r"(reforme|arrete|decret)"),
    # Supporting explainers: real traffic, but they answer "how does it work",
    # not "what do I get" - so they sit below the money pages.
    ("guide",      0.8, "monthly", r"(rentabilite|tva|calcul|simulateur|comprendre|comment)"),
    ("service",    0.9, "monthly", r"(service|prestation|offre|solution|produit|tarif|pricing|devis"
                                   r"|aide|prime|autoconsommation)"),
    ("location",   0.9, "monthly", r"(zone|region|ville|city|secteur|agence|near-me|autour)"),
    ("about",      0.8, "monthly", r"(about|a-propos|apropos|contact|equipe|team|qui-sommes)"),
    ("blog post",  0.7, "monthly", r"(blog|article|actualite|news|guide|post)/.+"),
    ("blog index", 0.8, "weekly",  r"(blog|actualite|news)/?$"),
    ("faq",        0.8, "monthly", r"(faq|questions)"),
]
DEFAULT = ("other", 0.6, "monthly")

AI_BOTS = [
    "GPTBot", "OAI-SearchBot", "ChatGPT-User",
    "ClaudeBot", "Claude-User", "Claude-SearchBot", "anthropic-ai",
    "PerplexityBot", "Perplexity-User",
    "Google-Extended", "Googlebot", "Bingbot",
    "CCBot", "Applebot", "Applebot-Extended",
    "meta-externalagent", "Amazonbot", "Bytespider", "cohere-ai",
]


def route_for(html_path: Path, build_dir: Path) -> str:
    rel = html_path.relative_to(build_dir)
    if rel.name == "index.html":
        route = "/" + str(rel.parent).replace("\\", "/").strip(".").strip("/")
    else:
        route = "/" + str(rel.with_suffix("")).replace("\\", "/").strip("/")
    route = "/" + route.strip("/")
    return route if route != "/" else "/"


def classify(route: str):
    for label, prio, freq, pattern in RULES:
        if re.search(pattern, route, re.I):
            return label, prio, freq
    return DEFAULT


def build_robots(base: str) -> str:
    lines = ["# Allow every crawler, including AI assistants.", "", "User-agent: *", "Allow: /", ""]
    lines.append("# Named explicitly so there is no ambiguity.")
    for bot in AI_BOTS:
        lines += ["", f"User-agent: {bot}", "Allow: /"]
    lines += ["", f"Sitemap: {base}/sitemap.xml", ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("build_dir")
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--out", help="where to write (default: the build dir)")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the proposed priority split, write nothing")
    args = ap.parse_args()

    build_dir = Path(args.build_dir).expanduser().resolve()
    if not build_dir.is_dir():
        sys.exit(f"not a directory: {build_dir}")
    out_dir = Path(args.out).expanduser().resolve() if args.out else build_dir
    base = args.base_url.rstrip("/")
    today = datetime.date.today().isoformat()

    html_files = [p for p in sorted(build_dir.rglob("*.html"))
                  if not any(part in SKIP_DIRS for part in p.parts)]
    if not html_files:
        sys.exit(f"no .html found under {build_dir} - build the site first")

    entries = []
    for p in html_files:
        route = route_for(p, build_dir)
        label, prio, freq = classify(route)
        entries.append((route, label, prio, freq))
    entries.sort(key=lambda e: (-e[2], e[0]))

    width = max(len(e[0]) for e in entries) + 2
    print(f"{len(entries)} pages\n")
    print(f"{'ROUTE'.ljust(width)}{'PRIORITY'.ljust(10)}{'FREQ'.ljust(10)}TYPE")
    for route, label, prio, freq in entries:
        print(f"{route.ljust(width)}{str(prio).ljust(10)}{freq.ljust(10)}{label}")

    if args.dry_run:
        print("\nDRY RUN - nothing written.")
        print("Show this split to the user and get confirmation, then re-run without --dry-run.")
        return

    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for route, _label, prio, freq in entries:
        loc = base + (route if route != "/" else "/")
        xml += ["  <url>",
                f"    <loc>{escape(loc)}</loc>",
                f"    <lastmod>{today}</lastmod>",
                f"    <changefreq>{freq}</changefreq>",
                f"    <priority>{prio}</priority>",
                "  </url>"]
    xml.append("</urlset>")

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "sitemap.xml").write_text("\n".join(xml) + "\n", encoding="utf-8")
    (out_dir / "robots.txt").write_text(build_robots(base), encoding="utf-8")

    print(f"\nwrote {out_dir/'sitemap.xml'} ({len(entries)} urls)")
    print(f"wrote {out_dir/'robots.txt'} (allows {len(AI_BOTS)} named crawlers)")
    print("\nNext: submit the sitemap in Google Search Console.")


if __name__ == "__main__":
    main()
