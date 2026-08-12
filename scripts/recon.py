#!/usr/bin/env python3
"""Inspect a site directory so the agent can stop guessing and start asking good questions.

Usage: python3 recon.py <site-dir>
"""
import json
import os
import sys
from pathlib import Path

FRAMEWORK_MARKERS = [
    ("Astro", ["astro.config.mjs", "astro.config.ts", "astro.config.js"], "dist"),
    ("Next.js", ["next.config.js", "next.config.mjs", "next.config.ts"], "out"),
    ("Nuxt", ["nuxt.config.ts", "nuxt.config.js"], ".output/public"),
    ("SvelteKit", ["svelte.config.js"], "build"),
    ("Hugo", ["hugo.toml", "config.toml", "hugo.yaml"], "public"),
    ("Eleventy", [".eleventy.js", "eleventy.config.js"], "_site"),
    ("Jekyll", ["_config.yml"], "_site"),
]

HOST_MARKERS = {
    "netlify.toml": "Netlify",
    "_headers": "Netlify or Cloudflare Pages",
    "_redirects": "Netlify or Cloudflare Pages",
    "vercel.json": "Vercel",
    "wrangler.toml": "Cloudflare",
    "firebase.json": "Firebase Hosting",
    ".nojekyll": "GitHub Pages",
    "CNAME": "GitHub Pages",
    "nginx.conf": "Nginx",
    ".htaccess": "Apache",
}

SKIP_DIRS = {"node_modules", ".git", ".astro", ".next", ".cache", ".vercel", "vendor"}


def detect_framework(root: Path):
    for name, markers, out in FRAMEWORK_MARKERS:
        for m in markers:
            if (root / m).exists():
                return name, out
    return "Plain HTML / unknown", None


def find_build_dir(root: Path, hinted):
    candidates = []
    if hinted:
        candidates.append(hinted)
    candidates += ["dist", "out", "build", "_site", "public", "."]
    for c in candidates:
        d = root / c
        if d.is_dir() and any(d.rglob("*.html")):
            return d
    return None


def list_pages(build_dir: Path, limit=200):
    pages = []
    for p in sorted(build_dir.rglob("*.html")):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        rel = p.relative_to(build_dir)
        route = "/" + str(rel.parent).replace("\\", "/").strip(".").strip("/")
        if rel.name != "index.html":
            route = route.rstrip("/") + "/" + rel.stem
        route = "/" + route.strip("/")
        pages.append(route if route != "/" else "/")
        if len(pages) >= limit:
            break
    return pages


def main():
    if len(sys.argv) < 2:
        print("usage: recon.py <site-dir>", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).expanduser().resolve()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2

    framework, hinted_out = detect_framework(root)
    build_dir = find_build_dir(root, hinted_out)
    pages = list_pages(build_dir) if build_dir else []

    hosts = sorted({label for f, label in HOST_MARKERS.items() if (root / f).exists()})

    static_root = None
    for cand in ("public", "static"):
        if (root / cand).is_dir():
            static_root = cand
            break

    existing = {}
    for fname in ("llms.txt", "sitemap.xml", "robots.txt"):
        found = []
        for base in filter(None, [root, build_dir, root / (static_root or "")]):
            f = Path(base) / fname
            if f.exists():
                found.append(str(f.relative_to(root)))
        existing[fname] = sorted(set(found))

    mirrors = len(list(build_dir.rglob("*.md"))) if build_dir else 0

    report = {
        "site_dir": str(root),
        "framework": framework,
        "build_dir": str(build_dir.relative_to(root)) if build_dir else None,
        "static_root": static_root,
        "page_count": len(pages),
        "routes": pages[:60],
        "existing_files": existing,
        "existing_md_mirrors": mirrors,
        "hosting_detected": hosts or ["unknown - ask the user"],
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))

    print("\n--- next ---", file=sys.stderr)
    if not build_dir:
        print("No rendered HTML found. Build the site first (e.g. `npm run build`).", file=sys.stderr)
    if not hosts:
        print("Hosting unknown - ask the user before configuring Content-Type headers.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
