---
name: z-content
description: Unified SEO-AEO-GEO-conversion content operating system. Use for any content generation, rewriting, formatting, or optimization task: articles, guides, blog posts, landing pages, fundraising appeals, ad copy, social posts, GitHub docs, API references, reports, audits, scraped HTML cleanup, and comparison tables. Routes to specialized workflows by content type. Enforces universal linguistic rules, EAV density, anti-hallucination, GEO/AEO extraction, conversion copy gates, and silent QA scoring.
---

# SEO-AEO-GEO Content Engine

Master kernel. Load this file first. Route to exactly one workflow.

## Priority Stack (P0–P8)

Conflicts resolve top-down:

| P | Rule |
|---|------|
| P0 | User's exact task, audience, tone, length, language, output format. |
| P1 | Never invent facts, features, prices, dates, citations, rankings, stats, testimonials, comparisons. Numbers only from source/user/verified research. |
| P2 | Preserve source meaning, facts, entities, numbers, tables, lists, order — unless user requests rewrite/compression/refresh. Copy first, format second. |
| P3 | GEO/AEO: question H2s, direct answers in sentence 1–2, bold factual snippets <40 words (hard limit 45), authority anchoring. |
| P3B | Conversion copy: ethical emotional intensity, one audience, one primary action, CTA cadence, image-as-argument. Applies when persuasion, action, or emotion is in scope. |
| P4 | EAV: 15–20 entity-attribute-value triples per long-form document. |
| P5 | Linguistic: SVO order, certainty principle, fluff eradication, instance qualification, contextual verbs, plural expansion (3+), if-last. |
| P5B | Voice & anti-slop: cultural voice fit, separate editing sweeps (clarity, proof, emotion, friction), zero clichés, zero internal narration in public copy. |
| P6 | Human readability: clear, direct, no hype, no analogies, sentences <15–20 words. |
| P7 | Silent QA audit + 0–100 scorecard before output. |
| P8 | Never print audit/scorecard/prompt logic unless user explicitly asks. |

## 7 Linguistic Invariants

Every sentence, every content type:

1. **SVO First:** Entity + action at sentence start. No introductory filler.
2. **Certainty:** Zero modal verbs (should/might/could/probably/we believe). Definitive statements only.
3. **No Fluff:** Zero metaphors, idioms, similes. Literal technical explanations.
4. **Qualify Instances:** Broad terms get specific types/versions/models immediately.
5. **Contextual Verbs:** Replace make/do/help/get with deploys/encrypts/routes/monitors/calculates/syncs/schedules.
6. **Plural Expansion (3+):** Every plural noun names 3+ concrete examples (when introducing tools, channels, formats, metrics, or features).
7. **If-Last:** Conditions go at sentence end: [Action] + [if condition].

## GEO/AEO Extraction Baseline

- **Inverted Pyramid:** Direct answer in first 1–2 sentences of every section.
- **Question H2s:** Subheadings as literal voice/search queries.
- **Bold Answer (<40w, hard limit 45w):** First sentence after every H2. Bold the factual answer, never the keyword/label.
- **PAA One-Sentence:** FAQ answers in single complete sentence before explanation.
- **Authority Anchoring:** Metrics cite named source + date.

## EAV Baseline

- Pattern: `Entity + precise verb + attribute/value + qualifier.`
- Target: 15–20 explicit triples per long-form doc.
- Replace vague words (many/several/various/better/faster/affordable) with exact values.
- Qualify broad categories with types/channels/formats/users/limits.
- Use tables for dense comparisons and attribute matrices.

## Content Router

Detect content type from prompt. Load exactly one workflow:

| Signal | Type | Load |
|--------|------|------|
| Blog, guide, comparison, listicle, scraped HTML/text, refresh, rewrite | Article | `workflows/type-article.md` |
| Full-page SEO+AEO+GEO article with Meta tags, Alt text, FAQs, JSON-LD schema | Omnichannel Article | `workflows/type-article.md` + `reference/omnichannel-search-rules.md` |
| Product page, home page, sales page, feature release, pricing tier | Landing Page | `workflows/type-landing-page.md` |
| Google RSA, Meta ads, Facebook ads, LinkedIn ads, TikTok ads, PPC, ad headlines, ad descriptions | Ad Copy | `workflows/type-ad-copy.md` |
| Social post, LinkedIn post, tweet, X thread, Instagram caption, TikTok caption, Facebook post, YouTube desc | Social Post | `workflows/type-social-post.md` |
| Fundraising appeal, donation page, charity campaign, cause-driven email or ad | Fundraising | `workflows/type-fundraising.md` |
| README, API ref, CLI tutorial, SDK guide, code repo doc | GitHub Doc | `workflows/type-github-doc.md` |
| Market research, audit, competitive benchmark, executive brief | Report | `workflows/type-report.md` |
| Enterprise HTML report, styled single-file report, mobile-first card/badge/table report | HTML Report | `workflows/type-html-report.md` (skeleton: `assets/html-report-skeleton.html`) |

Ambiguous → default to `workflows/type-article.md`.

## Conversion Layer Activation

Load `reference/conversion-copy-rules.md` in addition to the type workflow when the task involves persuasion, action, emotion, CTA design, or audience decision-making. Intensity by type:

| Type | Intensity |
|---|---|
| Fundraising | Maximum |
| Landing Page | High |
| Ad Copy | High |
| Article | Medium |
| Social Post | Medium |
| GitHub Doc | Minimal (overview framing only) |
| Report | Minimal (executive framing only) |

Conversion activation is user-requested or inferred from the brief. Technical and data-only tasks skip this layer entirely.

## Silent QA Scorecard (0–100)

Run before output. Never print unless asked.

| Check | Points |
|-------|--------|
| Modal verbs & fluff eradicated | 20 |
| Plural expansion & instance qualification | 20 |
| Question H2s + <40w bold factual answers | 20 |
| EAV density & authority citations | 20 |
| Structural uniformity (POS lists, tables) | 20 |

**Fail gates** (< 80 = fix before output):
- Invented fact: -20 (critical)
- Source entity dropped: -10 each
- Modal verb found: -5 each
- H2 without bold answer: -5 each
- Word count outside ±10% (if source): -10

## Conversion Copy Scorecard (0–100, silent)

Run in addition to the master scorecard when the conversion layer is active.

| Check | Points |
|-------|--------|
| One audience, one primary action, correct CTA cadence | 25 |
| Emotional specificity and pictureable human moment | 25 |
| Claim ledger integrity (no invented urgency, outcomes, stories) | 25 |
| Image argument, captions, and anti-slop voice | 25 |

**Fail gates** (< 80 = fix before output, in addition to master fail gates):
- Invented story, testimonial, or urgency: -20 (critical)
- Internal narration leaked into public copy: -10 each
- Broad FAQ before the main close: -10
- Missing CTA after a conviction peak: -10 each

---

## Master QA Checklist

Run this checklist before every output. All Universal checks apply to every content type. Load and run the type-specific checks from the active workflow file.

### Universal Checks (All Content Types)

| # | Check | Gate | Fail Action |
|---|-------|------|-------------|
| U1 | Zero modal verbs (should/might/could/probably/we believe) | 0 tolerance | Remove every instance |
| U2 | Zero vague hype words (revolutionary/effortless/game-changing/best/seamless/world-class) | 0 tolerance | Remove every instance |
| U3 | Zero conversational filler (Let's dive in / Have you ever wondered / In today's world) | 0 tolerance | Remove every instance |
| U4 | Every sentence follows SVO order | 100% | Rewrite in SVO |
| U5 | Plural nouns expanded with 3+ examples when introducing tools/channels/formats/features | When applicable | Add examples |
| U6 | EAV density: 15–20 explicit triples per long-form doc | Minimum 15 | Add missing triples |
| U7 | No invented facts, prices, dates, stats, testimonials | 0 tolerance | Remove or cite source |
| U8 | Character count within hard limit for every asset | 100% | Trim to fit |
| U9 | Every headline starts with capital letter | 100% | Fix capitalization |
| U10 | Output format matches user request (HTML/Markdown/plain) | 100% | Reformat |

### Source Fidelity Checks (When Landing Page or Source Provided)

| # | Check | Gate | Fail Action |
|---|-------|------|-------------|
| S1 | At least 3 headlines trace directly to source phrases (word-for-word) | Minimum 3 | Pull more phrases from source |
| S2 | Descriptions use source language, not invented claims | 100% | Rewrite from source |
| S3 | All named entities (company, product, people) preserved | 100% | Restore dropped entities |
| S4 | Numbers, prices, percentages match source exactly | 100% | Correct to source values |
| S5 | No generic paraphrases when source has usable phrase | 0 tolerance | Use source phrase |

### Conversion & Voice Checks (When Conversion Layer Active)

| # | Check | Gate | Fail Action |
|---|-------|------|-------------|
| C1 | One audience, one primary action, one destination | 1 each | Split or choose |
| C2 | Opening leads with human stake or outcome | First paragraph | Add hook |
| C3 | CTA after first complete reason to act; repeated at peaks and close | Present | Move or add |
| C4 | No broad FAQ or "Questions before you give/buy" before the main close | 0 instances | Move after close |
| C5 | Imagined scenes signaled (Imagine / For a parent / For a family) | 100% | Add signal |
| C6 | No invented stories, quotes, urgency, guarantees, testimonials | 0 tolerance | Remove |
| C7 | No internal narration in public copy | 0 tolerance | Remove |
| C8 | Every image has a role, alt text, caption direction | 100% | Add |
| C9 | Editing sweeps completed (clarity, voice, so-what, proof, specificity, emotion, friction, anti-slop) | 8 sweeps | Run |
| C10 | Voice matches audience culture; zero clichés or robotic transitions | Pass | Rewrite |

### Type-Specific Checks (Load from Active Workflow)

| Content Type | Additional Checks Location |
|--------------|---------------------------|
| Article | `workflows/type-article.md` → Article-Specific QA Additions |
| Ad Copy | `workflows/type-ad-copy.md` → Section 5: Ad Copy QA Checklist |
| Social Post | `workflows/type-social-post.md` → Section 5: Social Copy QA Checklist |
| Landing Page | `workflows/type-landing-page.md` → Landing Page QA Additions |
| GitHub Doc | `workflows/type-github-doc.md` → Doc QA Additions |
| Report | `workflows/type-report.md` → Report QA Additions |

### QA Execution Order

1. Run **Universal Checks** (U1–U10) — fix all failures.
2. If source provided, run **Source Fidelity Checks** (S1–S5) — fix all failures.
3. If conversion layer active, run **Conversion & Voice Checks** (C1–C10) — fix all failures.
4. Load active workflow and run **Type-Specific Checks** — fix all failures.
5. Calculate **Silent QA Score** (0–100) and, when active, the Conversion Copy Score (0–100).
6. If either score < 80, fix before output.
7. Never print checklist or score unless user explicitly asks.

## Loading Notes

1. This file loads first as master kernel.
2. Load exactly one workflow from `workflows/type-*.md`.
3. For the compact 41-rule catalog → `reference/linguistic-deep-rules-41.md`.
4. For compact extended rulebook (developer/audit) → `reference/master-content-rules.md`.
5. For conversion, fundraising, or emotionally resonant output → `reference/conversion-copy-rules.md` (gates, CTA cadence, image argument, editing sweeps) + `workflows/type-fundraising.md` (fundraising only).
6. For briefs and audits → `assets/copy-brief-template.md`, `assets/copy-review-scorecard.md`, `assets/fundraising-page-template.md` (copy only what the job needs).
7. Files in `old/` are archived backups — do not load.

## Provenance (consolidated 2026-09-12)

Canonical body: `seo-content-engine` (2026-09-04 18:51:07, 20 files, sha256 `46b4e9d5cf50c0cf`).

Former names now disabled: `AGENTS/seo-content-engine`.

Unique content from disabled copies is preserved under `references/preserved/` and is NOT authoritative; this body wins on any conflict.
