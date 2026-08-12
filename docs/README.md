# docs/

Research and decisions behind this site. Read before changing content or figures.

| File | What it is |
|---|---|
| `fr-solar-market-data-aug-2026.md` | Every figure on the site, with its date, source, and confidence. Includes a "do not publish" list of unresolved claims. **Start here before editing any number.** |
| `build-vs-buy-stack.md` | Why the stack is what it is — what to build, what to take off the shelf, and why the reusable unit is a template repo rather than a monorepo. |
| `ai-visibility-pack-skill.md` | The llms.txt / Markdown mirrors / weighted sitemap skill. What it does and how to run it. |
| `citable-content-skill.md` | The research-and-verify engine. The `facts.json` design, confidence gating, and the 6-phase workflow for launching a new vertical. |

## The rule that matters

No figure goes on a page unless it can be traced to a dated source. One wrong number costs more than ten missing ones — the entire strategy depends on being the site that is right while competitors are stale.

Unresolved claims stay in the "do not publish" list. They are not softened or hedged into the content; they are omitted until confirmed.

## Open questions

- **The domain.** `astro.config.mjs` still needs a real `site:`. Until then canonical tags point at a domain we don't own.
- **The conversion path.** The site has no booking link, form, or phone number. As it stands it earns citations and captures nobody.
