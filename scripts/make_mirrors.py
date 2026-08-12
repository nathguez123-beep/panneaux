#!/usr/bin/env python3
"""Generate clean Markdown mirrors next to every HTML page.

An AI crawler reading your HTML fights nav, scripts, cookie banners and popups.
This writes the same page as plain text at /page/index.md.

Usage:
  python3 make_mirrors.py <build-dir> --base-url https://site.com
  python3 make_mirrors.py dist --base-url https://site.com --update-llms public/llms.txt
"""
import argparse
import datetime
import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup
    from markdownify import markdownify as md
except ImportError:
    sys.exit(
        "Missing dependencies. Install with:\n"
        "  pip install beautifulsoup4 markdownify\n"
        "  (or: uv pip install beautifulsoup4 markdownify)"
    )

STRIP_TAGS = ["script", "style", "noscript", "nav", "header", "footer", "aside",
              "iframe", "svg", "form", "template"]

STRIP_SELECTORS = [
    "[class*=cookie]", "[id*=cookie]", "[class*=consent]", "[id*=consent]",
    "[class*=banner]", "[class*=popup]", "[id*=popup]", "[class*=modal]",
    "[class*=newsletter]", "[class*=breadcrumb]", "[role=navigation]",
    "[role=banner]", "[role=contentinfo]", "[aria-hidden=true]",
    "[class*=skip-link]", "[class*=social-share]",
]

SKIP_DIRS = {"node_modules", ".git", ".astro", ".next", "_astro", "assets"}


def route_for(html_path: Path, build_dir: Path) -> str:
    rel = html_path.relative_to(build_dir)
    if rel.name == "index.html":
        route = "/" + str(rel.parent).replace("\\", "/").strip(".").strip("/")
    else:
        route = "/" + str(rel.with_suffix("")).replace("\\", "/").strip("/")
    route = "/" + route.strip("/")
    return route if route != "/" else "/"


def extract(html: str):
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.get_text(strip=True) if soup.title else ""
    desc = ""
    tag = soup.find("meta", attrs={"name": "description"})
    if tag and tag.get("content"):
        desc = tag["content"].strip()

    for t in soup(STRIP_TAGS):
        t.decompose()
    for sel in STRIP_SELECTORS:
        try:
            for t in soup.select(sel):
                t.decompose()
        except Exception:
            pass

    main = soup.find("main") or soup.find("article") or soup.body or soup
    body = md(str(main), heading_style="ATX", strip=["a"] if False else None)

    lines = [ln.rstrip() for ln in body.splitlines()]
    out, blanks = [], 0
    for ln in lines:
        if not ln.strip():
            blanks += 1
            if blanks > 1:
                continue
        else:
            blanks = 0
        out.append(ln)
    return title, desc, "\n".join(out).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("build_dir")
    ap.add_argument("--base-url", required=True, help="e.g. https://site.com")
    ap.add_argument("--update-llms", metavar="PATH",
                    help="append a Markdown Mirrors section to this llms.txt")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    build_dir = Path(args.build_dir).expanduser().resolve()
    if not build_dir.is_dir():
        sys.exit(f"not a directory: {build_dir}")
    base = args.base_url.rstrip("/")
    today = datetime.date.today().isoformat()

    html_files = [p for p in sorted(build_dir.rglob("*.html"))
                  if not any(part in SKIP_DIRS for part in p.parts)]
    if not html_files:
        sys.exit(f"no .html found under {build_dir} - build the site first")

    written, urls, skipped = 0, [], []
    for html_path in html_files:
        try:
            title, desc, body = extract(html_path.read_text(encoding="utf-8", errors="replace"))
        except Exception as e:
            skipped.append((html_path.name, str(e)))
            continue

        if len(body) < 80:
            skipped.append((str(html_path.relative_to(build_dir)), "too little content"))
            continue

        route = route_for(html_path, build_dir)
        url = base + route
        md_url = (base + route.rstrip("/") + "/index.md") if route != "/" else base + "/index.md"

        header = [f"# {title}" if title else "", ""]
        if desc:
            header += [f"> {desc}", ""]
        header += [f"url: {url}", f"last_updated: {today}", "", "---", ""]
        content = "\n".join(x for x in header if x is not None) + "\n" + body + "\n"

        out_path = html_path.with_name("index.md") if html_path.name == "index.html" \
            else html_path.with_suffix(".md")

        if not args.dry_run:
            out_path.write_text(content, encoding="utf-8")
        written += 1
        urls.append(md_url)

    print(f"{'would write' if args.dry_run else 'wrote'} {written} markdown mirrors under {build_dir}")
    if skipped:
        print(f"skipped {len(skipped)}:")
        for name, why in skipped[:10]:
            print(f"  - {name}: {why}")

    if args.update_llms and not args.dry_run:
        llms = Path(args.update_llms).expanduser().resolve()
        section = "## Markdown Mirrors\n\nClean text version of every page, for AI crawlers:\n\n" \
                  + "\n".join(f"- {u}" for u in sorted(urls)) + "\n"
        if llms.exists():
            text = llms.read_text(encoding="utf-8")
            if "## Markdown Mirrors" in text:
                text = text.split("## Markdown Mirrors")[0].rstrip() + "\n\n" + section
            else:
                text = text.rstrip() + "\n\n" + section
        else:
            text = section
        llms.write_text(text, encoding="utf-8")
        print(f"updated {llms} with {len(urls)} mirror URLs")

    print("\nREMINDER: serve .md as Content-Type: text/plain, or browsers download it.")
    print("See references/hosting.md for your host's config.")


if __name__ == "__main__":
    main()
