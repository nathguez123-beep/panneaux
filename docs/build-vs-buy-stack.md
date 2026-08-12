# Client site factory + AI generator — what to build vs. what to take

Decision doc, Aug 2026. Context: Astro site `panneaux` already built (7 FR pages, SEO layout, robots.txt open to AI crawlers, sitemap). Goal: turn it into a reusable "blank page" editable per client, plus an AI generator that handles clients who already have a site.

---

## 1. The reusable site — build it yourself (2–3h of refactor)

No repo does this better than restructuring `panneaux`. The pattern:

```
panneaux/                    ← mark as a GitHub TEMPLATE repository
  src/
    config/client.json       ← every client-specific value lives here
    content/                 ← Astro content collections (services, faq, testimonials)
    layouts/ components/     ← never touched per client
```

`client.json` holds: business name, city, phone, booking link, primary/accent colour, logo path, 3–6 services, tone. Components read from it — zero hardcoded strings in the layout.

New client = `gh repo create client-x --template panneaux` → edit one JSON + a few markdown files → deploy. Netlify MCP is already connected in this session, so site creation and deploys can be driven from chat.

**Optional nicer base:** [folex-lite-astro](https://github.com/getastrothemes/folex-lite-astro) (39★, Astro + Tailwind agency theme) — worth 20 min to strip for components, not worth adopting wholesale.

**Why not a "multi-tenant monorepo":** one repo serving 15 clients means one bad deploy breaks 15 sites, and clients can't be handed over or sold off. Template repo + per-client repo is the right unit at this stage. Revisit at 20+ clients.

---

## 2. The audit ("does the client already have a site?") — take it, don't build it

**[Auriti-Labs/geo-optimizer-skill](https://github.com/Auriti-Labs/geo-optimizer-skill)** — 599★, MIT, v4.15.0 (Jul 2026). This is almost exactly the product being planned:

- Scores any URL 0–100 across 8 categories (robots.txt, llms.txt, JSON-LD, meta, content structure, brand coherence, technical signals, AI discovery endpoints) — 47 research-backed checks
- **Citation checking**: queries real engines to see whether the brand actually gets cited by ChatGPT / Perplexity / Gemini / AI Overviews
- Ships as CLI (`uvx --from geo-optimizer-skill geo audit --url …`), Python library, **MCP server** (`claude mcp add geo-optimizer -- geo-mcp`), **Astro integration** (auto-generates llms.txt at build), and a **GitHub Action** with SARIF output
- Stack overlap is exact: Python + Astro

This becomes the front of the sales motion: run the audit on a prospect's site, send the score + top 5 fixes as the cold outreach. And the GitHub Action turns into an automated monthly client report — the retainer.

**Map of everything else in this space:** [discoveredlabs/awesome-aeo-seo-tools](https://github.com/discoveredlabs/awesome-aeo-seo-tools)

**Ongoing tracking (sell as retainer):**
- [danishashko/geo-aeo-tracker](https://github.com/danishashko/geo-aeo-tracker) — 152★, MIT, Next.js dashboard, tracks 6 engines (ChatGPT, Perplexity, Gemini, Copilot, AI Overview, Grok). Needs Bright Data + OpenRouter keys.
- `elmo`, `canonry`, `ansvisor` — self-hosted citation monitors, all in the awesome-list

---

## 3. The AI generator — this is the only part worth building

Everything above is commodity. The product is the **glue**:

```
input: business name OR existing URL
  ├─ has a site  → geo-optimizer audit → gap report → generate fixes (schema, llms.txt, rewritten pages)
  └─ has no site → generate client.json + content collections → template repo → Netlify deploy
output: live URL + booking link + audit score before/after
```

Build it as a **Claude skill** (`SKILL.md` + scripts) first, not an app. It runs inside Claude Code, uses geo-optimizer as an MCP tool, and writes files into the template repo. If it proves out, port to the Claude Agent SDK for a hosted version clients can self-serve.

---

## 4. Platform features to lean on

| Need | Use |
|---|---|
| Reusable per-client workflow | Claude **skill** + private **plugin marketplace** (bundle skill + geo MCP, install per session) |
| Many clients processed at once | **Subagents / workflows** — fan out one agent per client site |
| New client repo in one command | GitHub **template repositories** + `gh repo create --template` |
| Automated monthly audits | **GitHub Actions** (geo-optimizer Action, SARIF, fails on regression) |
| Deploys from chat | **Netlify MCP** (already connected) |

---

## 5. On the Agentic Academy link

[agentic-academy.fr](https://agentic-academy.fr) — French Claude Code course. €47/mo or €147 lifetime. Covers Claude Code fundamentals, building sites/apps end-to-end, security, SEO, pre-configured skills + MCP setups, project templates and prompts.

Assessment: legitimate, but it's packaging free material. The pre-built skills and prompt templates save time; they aren't a moat, and nothing in the syllabus is unavailable in Anthropic's own docs. The community and Q&A are the real product. Worth €147 only if the accountability of a cohort is the missing piece — not for the templates.
