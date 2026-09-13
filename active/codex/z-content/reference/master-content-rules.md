# Unified Content Rules — compact developer reference

This file keeps the non-kernel rules needed for audits and deep review. Load `SKILL.md` first; load one type workflow second. The kernel owns the normal operating path.

## 0. Priority and failure gates

Apply in order: user task and format; truth and source authority; source fidelity; GEO/AEO extraction; EAV specificity; linguistic clarity; silent QA. Never invent facts, features, prices, dates, rankings, citations, testimonials, or comparisons. Never drop decision-critical source entities, numbers, tables, lists, quotes, or recommendations during preservation work. Keep audit logic out of public output.

## 1. Topic boundary

Define, before drafting:

- source purpose and authority;
- one central entity and one search intent;
- core attributes, supporting attributes, and the monetization path.

Keep every section on one context path. Stop when the intent is answered. Do not pad thin input, mix unrelated topics, or turn an article into a sales page without a request.

## 2. GEO/AEO extraction

- Put the direct answer in the first one or two sentences of each section.
- Convert H2/H3 headings to real user questions when meaning remains intact.
- Put one source-grounded, definitive answer under each eligible H2; keep it under 40 words, hard limit 45, and bold the answer rather than the keyword.
- Answer FAQs and PAA queries with one complete sentence before detail.
- Put named source, date, and baseline beside every metric.
- Use short paragraphs, explicit lists, dimension-rich tables, and one intent per section.

## 3. EAV and linguistic rules

Write facts as `Entity | Attribute | Value`; target 15–20 explicit triples in long-form work. Replace vague quantities with exact values and qualify broad nouns with types, versions, limits, or examples. Start sentences with the entity and a precise verb; use SVO order, zero unsupported modality or opinion, no filler/analogy, and sentences below 15–20 words where practical. Expand newly introduced plurals with three concrete examples. Put conditions at the end of the sentence.

Use domain verbs such as deploys, routes, encrypts, measures, verifies, compares, publishes, schedules, filters, syncs, parses, and monitors. Introduce every list with a complete scope sentence. Keep list items grammatically parallel. Use `<ol>` for ordered steps and `<ul>` for features, examples, criteria, or risks.

## 4. Tables and links

Use descriptive headers such as `Entity | Attribute | Operational Value | Source`. Every cell contains a verified value or `—`; never use vague labels such as “fast” or “best”. In preservation mode, keep source rows, columns, order, and values. Use anchor text that names the destination entity; never use “click here”, “read more”, or “this article”.

## 5. Source-preserving transformation

Read the main body only. Return `PAGE NOT FOUND 404`, `PAGE IS A FORUM`, `PAGE IS A LISTING`, or `PAGE IS A HOMEPAGE` for those exact classifications. Remove only navigation, cookie/footer UI, author credits, affiliate disclosures, signup forms, bottom related links, and the original conclusion.

In strict preservation mode, copy first and format second: keep every body sentence in order; map headings to H1–H3, bullets to `<ul>`, numbered steps to `<ol>`, and tables to semantic table tags. Keep body word count within ±10%, section paragraph depth, every list item, every table row/column, every named entity, number, quote, case study, and informative caption. Never summarize or compress source content unless the user explicitly requests it. Add a new conclusion only after all preserved decision content.

## 6. Product and comparison safety

Mention products only from the source, user request/data, client catalog, or verified research. A product name does not prove features, price, rankings, outcomes, or integrations. On request, insert one product as the second H2 without rewriting surrounding source content. Preserve comparison columns, rows, order, and values; use `—` for unknowns; never add unsupported labels such as “best”, “cheapest”, or “top choice”. Compare measurable attributes, not opinions. Keep product mappings client-specific.

## 7. Raw HTML contract

When raw HTML is requested, output only HTML: first character `<`, last character `>`, no Markdown fences, prose, audit, or preamble. Use only the requested semantic tags (`article`, `h1`–`h3`, `p`, `strong`, lists, tables, and links) unless a frozen template governs the output.

## 8. Silent QA

Check intent/entity continuity, source fidelity, EAV density, direct answers, source citations, certainty, SVO, plural qualification, list/table uniformity, and HTML hygiene. Score the five core dimensions at 20 points each: truth/claims, linguistic clarity, GEO/AEO extraction, EAV/source proof, and structure. Fix any invented fact, dropped entity, unsupported modality, missing answer, or preservation word-count failure before output. Never print the score unless asked.

## 9. Platform extensions

### Ads

| Platform | Hard limit | Safe target |
|---|---:|---:|
| Google RSA headline / description | 30 / 90 | 25–28 / 75–85 |
| Meta primary / headline / description | 2,200 / 255 / 255 | hook 100–120 / 30–35 / 20–30 |
| LinkedIn intro / headline | 600 / 200 | 130–140 / 50–70 |
| TikTok caption | 100 | 60–80 |
| X post | 280 | 200–260 |

Use five different angles: category, numeric proof, pain point, feature/integration, and direct CTA. Count spaces. Tag assets with `[XX/Limit]`. Extract source phrases before writing ads; trace every consequential asset to source data. Use charity-specific empathy/trust/impact angles only when the source supports them.

### Organic social

Put a complete hook before the platform fold: LinkedIn 130–140, Instagram 100–115, TikTok 80–90, Facebook 400–450, YouTube 130–150, X 260–270 characters. Keep each post standalone, use one CTA, max 3–5 hashtags, max 1–2 purposeful emojis, and never publish invented statistics or filler.
