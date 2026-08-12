# ai-visibility-pack — the 3-file skill

Built Aug 2026. Delivered as `ai-visibility-pack.skill`. Reusable across every client site.

Turns the three-file AEO play (llms.txt, Markdown mirrors, weighted sitemap + open robots.txt) into a repeatable skill instead of a one-off manual job.

## Contents

```
ai-visibility-pack/
  SKILL.md                          6-step workflow: recon → interview → 3 files → verify
  scripts/recon.py                  detects framework, build dir, routes, host, existing files
  scripts/make_mirrors.py           HTML → clean .md next to every page, updates llms.txt
  scripts/make_sitemap.py           priority-weighted sitemap + robots.txt (19 named crawlers)
  scripts/verify.py                 live check: 200s, Content-Type, bot allows, XML validity
  references/llms-txt-template.md   structure + full worked FR example (solar installer)
  references/hosting.md             text/plain config per host, Astro wiring, Search Console
```

## Usage

```bash
python3 scripts/recon.py .                                              # look before asking
python3 scripts/make_mirrors.py dist --base-url https://X --update-llms public/llms.txt
python3 scripts/make_sitemap.py dist --base-url https://X --dry-run     # confirm the split
python3 scripts/make_sitemap.py dist --base-url https://X --out public
python3 scripts/verify.py https://X                                     # after deploy
```

Astro wiring — mirrors and sitemap regenerate on every deploy, no manual step:

```json
"build": "astro build && python3 scripts/make_mirrors.py dist --base-url $SITE_URL --update-llms dist/llms.txt && python3 scripts/make_sitemap.py dist --base-url $SITE_URL"
```

Deps: `pip install beautifulsoup4 markdownify` (recon/sitemap/verify are stdlib only).

## What it changes vs. the raw prompts it came from

- **Recon before interview.** Reads the site first, so the client is only asked what can't be detected.
- **Priority split is confirmed, not assumed.** `--dry-run` prints the proposed weighting for sign-off before writing. A flat sitemap tells Google nothing — the spread is the entire value.
- **Verification step.** The original had none. `verify.py` catches the failure everyone hits: `.md` served as `application/octet-stream` instead of `text/plain`, so browsers download the mirror instead of reading it.
- **Pricing enforced.** The pricing rule is in SKILL.md as a hard rule and re-checked by `verify.py`. Models list businesses that publish numbers and skip "contact us for a quote" — this is the highest-leverage rule in the whole play.
- **Bot list is wider.** 19 named crawlers including `OAI-SearchBot`, `Claude-User`, `Claude-SearchBot`, `Applebot-Extended`, `meta-externalagent`.
- **Multi-client by design.** Client facts belong in `src/config/client.json`; llms.txt generates from it at build time so it can't drift from the site.

## Tested

Ran end-to-end against a 6-page fake Astro build: recon detected the framework and routes; mirrors stripped nav/footer/scripts/cookie banner and kept the pricing tables; sitemap produced 5 distinct priority tiers and valid XML; verify returned 11/12 over a local server — the one FAIL correctly flagged a stub llms.txt with no prices.

## Related

Full 47-check audit and real citation tracking: `geo-optimizer` (see build-vs-buy-stack.md).
