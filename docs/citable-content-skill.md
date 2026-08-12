# citable-content — the content engine

Built Aug 2026. Delivered as `citable-content.skill`. Pairs with `ai-visibility-pack`.

## The thesis it encodes

Generic content doesn't get cited. Assistants cite specific, dated, verifiable numbers — and they cite whoever has them right.

Regulated markets change by decree. When they do, every existing page goes stale overnight, and the site publishing the correct new figures first becomes the default answer for weeks or months. That's not luck and it's not solar-specific: France produces these constantly — heat pumps, insulation, EV charging, MaPrimeRénov' revisions, insurance rules.

The skill runs that play end to end and structurally refuses to publish anything unverified.

## Six phases

1. **Find the change** — search the vertical for what recently changed. Sweet spot is 1–6 months old: younger and sources contradict, older and competitors have caught up.
2. **Verify** — source hierarchy, two independent sources or one primary, every figure dated.
3. **Validate the window** — `staleness_scan.py` checks whether competitors are actually still wrong. If they've updated, the window is closed and the skill says so.
4. **Structure** — one `facts.json`, single source of truth.
5. **Write** — for extraction, not for reading.
6. **Publish + schedule the re-check** — every fact carries a `review_by`.

## The architectural idea: facts.json

Every published figure lives in exactly one file. Pages import it, `llms.txt` generates from it. A number can't drift between pages, and updating a rate is a one-line change.

Each fact carries `value`, `as_of`, `supersedes`, `sources`, `confidence`, `review_by`.

`confidence` is a publication gate enforced **in code**, not by discipline:

- `high` — 2+ independent sources (or one primary), dated. Renders as a specific figure.
- `medium` — renders only as a range, with an "indicative" qualifier appended automatically.
- `do-not-publish` — kept in the file for the record, never rendered anywhere.

That last tier is the important one. The record of what you checked and rejected is worth keeping, and it's structurally impossible for it to leak into a page.

## The highest-leverage sentence pattern

`supersedes` powers this, and it's the single most useful thing in the method:

> "1,1 c€/kWh depuis le 5 juin 2026, contre 4,73 c€/kWh auparavant"

The model has seen both figures across its sources and can't tell which is current. A page that resolves the contradiction becomes the citation.

## Usage

```bash
python3 scripts/init_facts.py --vertical "..." --market FR --today YYYY-MM-DD
python3 scripts/staleness_scan.py --urls competitors.txt --obsolete "80 €/kWc" --current "1,1 c€"
python3 scripts/build_llms.py --facts src/data/facts.json --out public/llms.txt
python3 scripts/build_llms.py --facts src/data/facts.json --check-expiry --today YYYY-MM-DD
```

Then run `ai-visibility-pack` for mirrors, weighted sitemap and robots.txt.

## Tested

Rebuilt the real solar dataset — 9 facts, 3 high / 5 medium / 1 do-not-publish — and confirmed end to end:

- The `do-not-publish` fact (conflicting 10% TVA claim) never reached the output
- `medium` facts rendered as ranges with an automatic qualifier
- French dates rendered as prose ("5 juin 2026"), not ISO
- Validation caught all four seeded defects — `high` with one source, malformed date, invalid confidence level, duplicate id — and refused to write the file
- Expiry check correctly flagged the one fact already past `review_by`
- Staleness scanner returned correct verdicts across stale / updated / mixed / off-topic / 404 fixtures, normalising NBSP and HTML entities, and excluded errors and off-topic pages from the ratio

## Retainer angle

Regulated figures expire. `--check-expiry` is the maintenance loop, and it's also the recurring product: a client pays for the numbers staying right, which is the thing that keeps them cited.

## The honest limitation

This produces content that gets **cited**. Citation is not conversion. A cited page with no booking link, quote form, or phone number generates reputation, not revenue.
