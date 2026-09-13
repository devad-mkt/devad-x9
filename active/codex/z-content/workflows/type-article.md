# Workflow: Article / Guide

Handles: long-form guides, comparisons, blog posts, listicles, scraped HTML cleanup, article rewrites, content refreshes.

Load `SKILL.md` first. This file provides article-specific structure and preservation rules.

---

## Structural Model

```
H1 (Exact article topic — entity phrase)
  └─ H2 (Question-based, matches real user sub-intent)
       ├─ <strong>Bold direct answer (<40 words, hard limit 45)</strong>
       ├─ Supporting EAV proof paragraph
       ├─ Examples, data, or case study
       └─ Comparison table (if applicable)
  └─ H2 (Next question)
       └─ ...
  └─ Conclusion (4 short paragraphs)
```

### H1 Rule
One H1 that states the exact article topic. Create an H1 only when the source lacks one. Never editorialize the H1.

- **Wrong:** `H1: The Ultimate Guide to Customer Support Tools You Need in 2026`
- **Right:** `H1: Customer Support Software Features and Comparisons`

### H2 Question Vectors
Convert section headings into direct questions when the section meaning stays intact. Keep exact source headings only when conversion would distort meaning.

- **Wrong:** `H2: Trengo Inbox Overview`
- **Right:** `H2: What makes Trengo's inbox different from other platforms?`

If the source H2 is already a question, keep it unchanged.

### Bold Snippet After Every H2
Every H2 except `Conclusion` and `Key takeaways` must be followed immediately by a bold factual answer.

Pattern:
```html
<h2>What are the primary features of the platform?</h2>
<p><strong>The platform provides unified inbox management, AI chatbot integration, multi-channel routing, and SLA tracking for customer support teams.</strong></p>
```

Rules:
- The answer must be under 40 words (hard limit: 45 words for AI answer engines).
- Bold the complete factual answer, not just the keyword or label.
- The first sentence after the heading must answer the heading directly.
- Derive the answer only from facts present in the same section or adjacent source context.
- If no source-supported answer can be written, keep the source content unchanged and skip the snippet.

---

## Scraped Preservation Engine

### Step 0 — Classify the Input

Read only the main body content. Ignore navigation, sidebars, footers.

| Entire body content is... | Output and stop |
|---------------------------|-----------------|
| HTTP 404 or blank page | `PAGE NOT FOUND 404` |
| Thread of user replies | `PAGE IS A FORUM` |
| Only article titles, zero prose | `PAGE IS A LISTING` |
| Homepage, multiple unrelated sections | `PAGE IS A HOMEPAGE` |

When in doubt, process as a valid article.

### Step 1 — Strip UI Noise

Remove silently and completely:
- Navigation menus, cookie banners, footers
- Author names, author bios, "written by" credits
- Affiliate disclosures
- "Try for free", "Get a demo", "Book a demo" CTAs
- Newsletter signup forms
- Related article link sections at the bottom
- The original conclusion (will be replaced)

Remove nothing else. Every sentence of article body content stays.

### Step 2 — Format Paragraph by Paragraph

**Core rule: copy first, format second. Never summarize. Never compress.**

Take each paragraph from the source in order. Copy every sentence. Wrap in `<p>`. Move to the next paragraph.

- Section headings → `<h1>` / `<h2>` / `<h3>`
- Bullet points → `<ul><li>`
- Numbered lists → `<ol><li>`
- Tables → `<table><thead><tr><th>` / `<tbody><tr><td>`
- If no `<h1>` exists in source → write one matching the exact article topic

### Step 3 — Verify Fidelity

Run these checks before proceeding:

**Named entity check:** Every company name, product name, customer story, statistic, percentage, price, founding year, recommendation bullet, case study, and quote from the source must appear in the output.

**Section depth check:** If source H2 has 4 paragraphs → output H2 must have 4 paragraphs. Never fewer.

**Word count check:** Output body (excluding any product section and conclusion) must be within ±10% of source word count.

**List fidelity check:** Every bulleted list item → `<ul><li>` with identical text. Every numbered list → `<ol><li>` with identical text. Never merge two items. Never drop an item.

**Closing section check:** The source often ends with a recommendation list or decision guide. This is article content, not a conclusion. It must appear verbatim before any new conclusion.

**Expert quotes & captions:** Preserve expert quotes, bylined statements, and informative image captions verbatim. Do not drop, compress, or paraphrase them.

### Step 4 — HTML Output Rules

When raw HTML is requested:
- First character must be `<`. Last character must be `>`.
- Use only valid article tags: `<article>`, `<h1>`, `<h2>`, `<h3>`, `<p>`, `<strong>`, `<ul>`, `<ol>`, `<li>`, `<table>`, `<thead>`, `<tbody>`, `<tr>`, `<th>`, `<td>`.
- Never wrap HTML in Markdown fences, backticks, labels, explanations, preambles, or postambles.
- No preamble before `<h1>`. No postamble after last closing tag.
- No Markdown syntax anywhere in the output.
- No internal audit, checklist, or scorecard in the output.

---

## Product / Tool Insertion (When Requested)

When the user requests product insertion into an article:

- Insert one relevant product as its own `<h2>` section.
- Place it as the **second H2** — between the first and second content sections.
- Do not move, shorten, or rewrite surrounding content to fit.
- Match product to central intent using provided client data.
- Select products only from the user's catalog or provided data. Do not invent features.

### Table Insertion

If the article contains a comparison table, add the product as a new row:
- Match existing column structure exactly.
- Use only provided product data.
- Use `—` for unavailable values.
- Do not add or remove columns.
- Do not remove existing rows.

---

## Snippet & AEO Injection

For SEO rewrites, upgrades, and fresh articles (not strict preservation):

1. Convert eligible H2s into questions.
2. Inject bold direct answers as the first paragraph after each H2.
3. Answers must be factual, derived from the same section content.
4. Keep the answer under 40 words (hard limit: 45 for AI engines).
5. Bold the complete factual answer, never the keyword or label.
6. Do not alter original paragraph facts when injecting snippets.

---

## Conversion & Voice Layer (When Conversion Layer Active)

Load `reference/conversion-copy-rules.md` in addition to this workflow when the task involves persuasion, action, emotion, or audience decision-making.

Add to this article type:

- **Opening:** replace the clinical intro with a pictureable human moment (signal-imagined).
- **Human perspective:** one short scenario sentence per major section ("For a parent...", "For someone who...").
- **Rule summaries:** one compressed takeaway line after mechanism and timing sections.
- **Consequence framing:** explicit cost of wrong choice in the timing section.
- **Image markers:** role, alt text, caption for each image (mechanism, outcome roles).
- **CTA bridge:** connect the comparison table or key rule to the store/product CTA in the conclusion.

## Full Omnichannel Output Mode (When Full SEO/AEO/GEO is Requested)

If the user requests metadata, schema, or complete omnichannel optimization, load `reference/omnichannel-search-rules.md` and apply these additions:

1. Include **Meta Title** (50–60 chars) and **Meta Description** (140–160 chars) before H1.
2. Insert **Visual Placeholders** with descriptive, keyword-rich Alt Text instructions.
3. Replace all ambiguous pronouns at the start of answers with the explicit Named Entity.
4. Append an FAQ section with single-sentence answers.
5. Append valid **JSON-LD Schema Markup** (`FAQPage` or `Article`).

Do not apply omnichannel additions unless explicitly requested. Standard article workflow remains the default.

---

## Conclusion Template

When a new conclusion is needed (after all preserved content):

1. One or two sentences on the value of the tools discussed.
2. A note that evaluating tools takes time and choosing wrong hurts ROI.
3. Position the blog that curates top tools for modern businesses.
4. CTA to explore more articles and subscribe.

Do not replace preserved final decision guides or recommendation lists. Keep those source sections before any new conclusion.

---

## Article-Specific QA Additions

In addition to the master scorecard, verify:

- [ ] **Fidelity gate:** Word count ±10% of source (if source provided).
- [ ] **Entity preservation:** 100% of named entities, dates, numbers, case studies retained.
- [ ] **List count:** Every source list item present in output.
- [ ] **Table rows:** Every source table row and column preserved.
- [ ] **Snippet coverage:** Every eligible H2 has a bold answer under 40 words (hard limit 45).
- [ ] **HTML cleanliness:** No Markdown fences, no backticks, no preambles (if raw HTML requested).

### Article Conversion QA (When Conversion Layer Active)

- [ ] **Human perspective:** Signal-imagined scenario in each major section.
- [ ] **Rule summary:** One compressed takeaway after mechanism/timing sections.
- [ ] **CTA bridge:** Decision table or key rule connects to the store/product CTA.
- [ ] **Image markers:** Each image has role + alt text + caption direction.
- [ ] **Opening moment:** Pictureable human stake in the first paragraph.
