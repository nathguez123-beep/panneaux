#!/usr/bin/env python3
"""Prove the three files are actually served correctly on the live site.

Usage: python3 verify.py https://site.com
"""
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

UA = "Mozilla/5.0 (compatible; ai-visibility-pack/1.0)"
AI_BOTS = ["GPTBot", "ClaudeBot", "PerplexityBot", "Google-Extended"]


def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, "", ""
    except Exception as e:
        return None, str(e), ""


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: verify.py https://site.com")
    base = sys.argv[1].rstrip("/")
    results = []

    # llms.txt
    status, ctype, body = fetch(f"{base}/llms.txt")
    if status == 200:
        n = len([l for l in body.splitlines() if l.startswith("#")])
        has_price = any(c in body for c in ("€", "$", "£")) or "price" in body.lower() or "tarif" in body.lower()
        results.append(("llms.txt", "PASS", f"{len(body)} bytes, {n} sections"))
        results.append(("  prices present", "PASS" if has_price else "FAIL",
                        "found" if has_price else "no prices - this is the #1 reason models skip a business"))
    else:
        results.append(("llms.txt", "FAIL", f"HTTP {status}"))

    # robots.txt
    status, ctype, body = fetch(f"{base}/robots.txt")
    if status == 200:
        results.append(("robots.txt", "PASS", f"{len(body)} bytes"))
        for bot in AI_BOTS:
            ok = bot.lower() in body.lower()
            results.append((f"  allows {bot}", "PASS" if ok else "WARN",
                            "named" if ok else "not named explicitly"))
        results.append(("  sitemap ref", "PASS" if "sitemap:" in body.lower() else "FAIL", ""))
    else:
        results.append(("robots.txt", "FAIL", f"HTTP {status}"))

    # sitemap.xml
    status, ctype, body = fetch(f"{base}/sitemap.xml")
    if status == 200:
        try:
            root = ET.fromstring(body)
            urls = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url")
            prios = {u.findtext("{http://www.sitemaps.org/schemas/sitemap/0.9}priority") for u in urls}
            results.append(("sitemap.xml", "PASS", f"valid XML, {len(urls)} urls"))
            results.append(("  priority spread", "PASS" if len(prios) > 1 else "WARN",
                            f"{len(prios)} distinct values" +
                            ("" if len(prios) > 1 else " - flat sitemap tells Google nothing")))
        except ET.ParseError as e:
            results.append(("sitemap.xml", "FAIL", f"invalid XML: {e}"))
    else:
        results.append(("sitemap.xml", "FAIL", f"HTTP {status}"))

    # markdown mirror content-type - the failure everyone hits
    status, ctype, body = fetch(f"{base}/index.md")
    if status == 200:
        ok = "text/plain" in ctype or "text/markdown" in ctype
        results.append(("/index.md", "PASS", f"served, Content-Type: {ctype}"))
        results.append(("  content-type", "PASS" if ok else "FAIL",
                        ctype if ok else f"'{ctype}' - browsers will download it. See references/hosting.md"))
    else:
        results.append(("/index.md", "WARN", f"HTTP {status} - mirrors not deployed yet?"))

    width = max(len(r[0]) for r in results) + 2
    print(f"\n{base}\n")
    for name, verdict, detail in results:
        print(f"{name.ljust(width)}{verdict.ljust(7)}{detail}")
    fails = sum(1 for r in results if r[1] == "FAIL")
    print(f"\n{len(results) - fails}/{len(results)} checks passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
