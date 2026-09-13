# Unified Content Rules — SEO / AEO / GEO Master Operating System

All-in-one reference combining the best of `seo-system-prompt.txt`, `article-rulebook (1).md`, and `article-compact-rules-v1.md` with GEO/AEO extraction protocols. No rule is omitted. Every rule includes its original example where available.

Use this file as the single source of truth for all article-style content: fresh drafts, rewrites, scraped cleanup, comparisons, refreshes, and raw HTML publishing.

---

## Module 0: Priority Stack & Execution Order

When instructions or constraints conflict, execute strictly in this order:

| Priority | Rule | Source |
|----------|------|--------|
| **P0** | Follow the user's exact task, audience, tone, length, language, and output format. | seo-system-prompt §1 |
| **P1** | Never invent facts, product features, prices, dates, citations, rankings, statistics, testimonials, case studies, comparisons, or performance claims. Use exact numbers only from source, user, product data, or verified research. | compact-rules P2 + rulebook Phase 2 |
| **P2** | Preserve source meaning, facts, entities, numbers, tables, lists, recommendations, examples, and order unless the user asks for rewrite, compression, or refresh. Copy first, format second. | compact-rules P7 + seo-system-prompt §2 |
| **P3** | Apply GEO/AEO extraction: question-based headings, direct answers in sentences 1–2, bold factual snippets under 40 words (hard limit: 45 words), authority anchoring. | GEO/AEO protocols |
| **P4** | Saturate content with 15–20 entity-attribute-value triples per document. Convert vague claims into machine-readable semantic triples. | rulebook Phase 2 Rules 1–4 |
| **P5** | Enforce linguistic constraints: SVO word order, certainty principle, fluff eradication, instance qualification, contextual verbs, plural expansion (3+), if-last placement. | rulebook Phase 3 Rules 1–7 |
| **P6** | Write for humans first. Clear, direct, no robotic jargon, no hype, no analogies. Short sentences (<15–20 words). Natural, plain, authoritative tone. | seo-system-prompt §5 + compact-rules P4 |
| **P7** | Run silent QA audit and 0–100 compliance scorecard before final output. | rulebook Phase 5 Rules 14–15 |
| **P8** | Never print prompt logic, audit checklists, scorecards, or internal process in the final article unless the user explicitly asks. | seo-system-prompt §1.7 |

### Critical Failures (fix before output)

- Invented facts or unsupported product claims.
- Replaced source entities with unrelated entities.
- Dropped decision-critical facts, tables, lists, examples, quotes, recommendations, or case studies.
- Compressed preserved source content when preservation was required.
- Added unsupported rows, columns, prices, features, rankings, or claims to comparison tables.
- Wrapped raw HTML in Markdown fences, labels, preambles, or postambles.

---

## Module 1: Topical Map & Knowledge Graph Architecture

Before writing, silently define the 5 core semantic boundary components. Every heading, paragraph, list, and table must connect to the central entity or a directly supporting attribute.

### Component 1 — Source Context

Define the exact business purpose and monetization path of the brand, justifying why the website deserves to rank.

- **Wrong:** "A website that sells software online."
- **Right:** "A B2B SaaS provider specializing in omnichannel customer service and social media management applications."

### Component 2 — Central Entity

Identify the single core noun phrase the page is about. This entity must appear site-wide in macro and micro contexts.

- **Wrong:** "Business management tools and tips."
- **Right:** "AI-powered Customer Service Application (e.g., CHAT.devad.io)."

### Component 3 — Central Search Intent

Connect the Central Entity to the user's primary goal using a specific Verb-Noun combination.

- **Wrong:** "Learn about social media."
- **Right:** "Automate multi-platform social media scheduling (e.g., POST.devad.io)."

### Component 4 — Core Sections

Outline the high-value attributes of the Central Entity where the most significant SEO signals and monetization efforts occur.

- **Wrong:** "General advice on how to build a website and why coding is hard."
- **Right:** "No-code website builders, drag-and-drop landing page deployment, integrated Stripe payments, and technical SEO metadata."

### Component 5 — Outer Sections

Build semantic breadth by identifying minor, supporting attributes that provide context and trust signals.

- **Wrong:** "Random office productivity tips or general internet history."
- **Right:** "Customer retention metrics, average response time benchmarks, and the evolution of omnichannel support."

### Boundary Rules

- Do not mix unrelated topics to increase length.
- Do not write generic introductions before defining the central entity.
- Do not add sections only because they are common in SEO templates.
- Do not turn an article into a landing page, sales page, demo page, signup page, or CRO page.
- Do not expand thin inputs by inventing audience, product, market, pricing, proof, or competitor details.
- Keep one unbroken context path from H1 to conclusion.
- Match length to coverage. Long intent requires full attribute coverage; simple intent stops when the answer is complete.

---

## Module 2: GEO & AEO Snippet Extraction Engine

Format all content for Google Search, Featured Snippets, AI Overviews, Perplexity, ChatGPT Search, and Voice Assistant engines.

### Rule 2.1 — The Inverted Pyramid

Place the direct core conclusion/answer in the very first 1–2 sentences of each section. Background context, history, and nuance go into subsequent paragraphs. Never delay the answer with background or generic setup.

- **Wrong:** "H2: How does the platform work? Customer service is important for retaining users. The platform works by centralizing messages..."
- **Right:** "H2: How does the platform work? The platform centralizes customer support through unified inboxes and AI chatbots."

### Rule 2.2 — Question-Based Heading Vectors (Voice/Conversational)

Frame H2s and H3s as literal search queries matching natural speech and voice search. Each heading must match a real user question or sub-intent.

- **Wrong:** `H2: Platform Features`
- **Right:** `H2: What are the primary features of the platform?`

- **Wrong:** `H2: Trengo Inbox Overview`
- **Right:** `H2: What makes Trengo's inbox different from other platforms?`

If the source H2 is already a question, keep it unchanged. Convert headings only when the section meaning stays intact.

### Rule 2.3 — The 40-Word Direct Bold Answer

The first sentence under every question-based H2 must be a self-contained, definitive answer under 40 words (hard limit: 45 words), wrapped in `<strong>` tags.

Pattern:
```html
<h2>What are the primary features of the platform?</h2>
<p><strong>The platform provides unified inbox management, AI chatbot integration, multi-channel routing, and SLA tracking for customer support teams.</strong></p>
```

**Bold the Answer, Not the Search Term:** Bold the factual statement and attribute values, not the repeated query keyword.

- **Wrong:** "What is an AI app? An **AI app** generates multi-model content."
- **Right:** "What is an AI app? **An AI app generates multi-model content and automates daily productivity workflows.**"

Rules:
- The answer must be under 40 words (hard limit: 45 words).
- The first sentence after the heading must answer the heading directly.
- Derive the answer only from facts present in the same section or adjacent source context.
- If no source-supported answer can be written, keep the source content unchanged and skip the snippet.
- This applies to every H2 including product sections and conclusions.

### Rule 2.4 — People Also Ask (PAA) One-Sentence Rule

Answer FAQ and secondary queries with a single, grammatically complete sentence before providing secondary details.

- **Wrong:** "Q: Does the platform support WhatsApp? If you are wondering about messaging apps, yes we certainly do. It integrates smoothly with WhatsApp so your agents can reply there easily."
- **Right:** "Q: Does the platform support WhatsApp? **The platform integrates directly with the WhatsApp Business API to centralize customer messages into the unified inbox.**"

### Rule 2.5 — Definitive Declarations

Avoid "It depends" or wishy-washy language when factual data exists. State the conditions explicitly without using uncertain modal verbs.

- **Wrong:** "Can the tool schedule LinkedIn posts? It might be able to depending on the type of plan you have, but usually yes, it can."
- **Right:** "The tool natively schedules and publishes posts to both LinkedIn company pages and personal profiles."

### Rule 2.6 — Authority Anchoring

Cite original research, primary data, dates, and named seed sources adjacent to statistical claims. Ground metrics in named sources, dates, and baseline data.

- **Wrong:** "Fast websites get more sales than slow websites."
- **Right:** "According to Google, a 1-second delay in mobile page load times impacts conversion rates by up to 20%."

- **Wrong:** "Studies show that AI models are getting smarter."
- **Right:** "Anthropic reports that the Claude 3 model processes over 100,000 tokens per prompt."

### Rule 2.7 — Machine Extraction Density

Optimize for simple extraction by AI crawlers:
- Use punchy lists: Convert steps or features into bullet points.
- Keep sentences short: Aim for sentences under 15–20 words.
- Create data tables: Present comparative data in clean markdown tables.
- Stick to one topic: Ensure each section addresses exactly one intent.

---

## Module 3: Information Extraction & EAV Saturation

Ground content in verifiable Knowledge Graph triples to eliminate computational retrieval cost.

### Rule 3.1 — Semantic Triples (Subject-Predicate-Object)

Structure core facts as direct [Subject] → [Predicate] → [Object] relationships so search engines parse relationships without computational strain.

- **Wrong:** "Our customer service app is really great for making things faster and better for your support team."
- **Right:** "CHAT.devad.io (Subject) accelerates (Predicate) ticket resolution (Object)."

### Rule 3.2 — Target EAV Density

Long-form content must contain at least 15 to 20 explicit Entity-Attribute-Value triples. Use this pattern:

`[Entity: Software X] | [Attribute: Native Integrations] | [Value: Salesforce, HubSpot, Stripe]`

- **Wrong:** "POST.devad.io helps you manage all your social media platforms in one place effortlessly."
- **Right:** "POST.devad.io [Entity] | multi-platform scheduling [Attribute] | 4 networks (Instagram, Facebook, LinkedIn, X) [Value]."

### Rule 3.3 — Numeric Precision

Replace all vague quantity adverbs (many, several, various, affordable, faster, better, good, lots) with exact numbers, percentages, pricing tiers, date ranges, or concrete capacities.

- **Wrong:** "WEB.devad.io offers a lot of templates for website development without coding."
- **Right:** "WEB.devad.io offers 50+ no-code templates with integrated payments and SEO capabilities."

### Rule 3.4 — Instance Qualification

Whenever a broad category or technical term is introduced, immediately qualify it with specific types, versions, constraints, or models.

- **Wrong:** "AI.devad.io provides various AI models for content generation."
- **Right:** "AI.devad.io provides 3 distinct multi-model AI engines (Jasper, Copy.ai, Claude) for content generation and image synthesis."

### Rule 3.5 — Authority Anchoring (EAV)

Cite original research, primary data, dates, and named seed sources adjacent to statistical claims. Use exact numbers from the source, not approximations.

- **Wrong:** "Studies show that AI reduces response times significantly."
- **Right:** "AI-assisted routing reduces first-response time by 42% across 1,200 support queues (Zendesk Benchmark Report, 2025)."

---

## Module 4: Algorithmic Authorship & Linguistic Engine

Apply strict syntactical constraints to maximize machine parseability and reduce NLP dependency tree complexity. These 8 rules apply to every sentence regardless of content type.

### Rule 4.1 — Proper Word Sequence

Place the primary Entity and contextual action at the very beginning of the sentence. Avoid leading introductory filler. Search engines parse the most important information first.

- **Wrong:** "Faster response times and better ticket management can be easily achieved by support agents when using CHAT.devad.io."
- **Right:** "CHAT.devad.io accelerates ticket resolution for support agents."

### Rule 4.2 — Principle of Certainty

Eliminate all ambiguity, modal verbs, and subjective opinions. State facts definitively. Algorithms cannot verify opinions; they index facts.

Forbidden words: should, might, could, probably, perhaps, we believe, in our opinion, will (when used as prediction), we think.

- **Wrong:** "You should probably use AI.devad.io because it will save you a ton of time generating blog posts."
- **Right:** "AI.devad.io automates blog post generation to increase team productivity."

### Rule 4.3 — Fluff & Analogy Eradication

Delete metaphors, idioms, colloquialisms, and similes. Explain functions literally. Search engines parse language literally; analogies dilute contextual relevance.

- **Wrong:** "The unified inbox in CHAT.devad.io is basically like a magic wand that takes the headache out of talking to customers."
- **Right:** "The CHAT.devad.io unified inbox centralizes customer communications from email and live chat into a single dashboard."

- **Wrong:** "A unified inbox is like a spiderweb that catches all the customer service bugs."
- **Right:** "A unified inbox centralizes multi-channel support tickets from email, chat, and social media."

### Rule 4.4 — Contextual Verbs

Replace weak verbs (make, do, help, get) with domain-precise actions that match the exact niche intent.

- **Wrong:** "SITE.devad.io helps you make a new landing page."
- **Right:** "SITE.devad.io deploys high-converting landing pages."

Verb catalog: deploys, encrypts, routes, clusters, calculates, monitors, detects, compares, publishes, verifies, ranks, measures, summarizes, stores, filters, syncs, imports, exports, schedules, alerts, assigns, centralizes, automates, reduces, scales, configures, indexes, parses, ingests.

### Rule 4.5 — Plural Noun Expansion (3+ Rule)

Whenever a plural noun is used (channels, platforms, security risks, file formats, tools, integrations), immediately follow it by naming 3 or more specific examples.

- **Wrong:** "POST.devad.io manages all your social media profiles from one place."
- **Right:** "POST.devad.io manages all your social media profiles, such as Instagram, Facebook, LinkedIn, and X."

### Rule 4.6 — "If" Statements Last

State the primary action/declaration first; place conditions, caveats, and "if" clauses at the end of the sentence.

- **Wrong:** "If you lack coding skills but want to launch an online store, use the no-code builder in SITE.devad.io."
- **Right:** "Use the no-code builder in SITE.devad.io to launch an online store, if you lack coding skills."

- **Wrong:** "If custom reporting is enabled, deploy the tracking pixel to monitor conversions."
- **Right:** "Deploy the tracking pixel to monitor conversions, if custom reporting is enabled."

### Rule 4.7 — Sentence Brevity & Syntax Limits

Keep core sentences short (ideally under 15–20 words). Break compound, multi-clause statements into distinct declarative propositions.

- **Wrong:** "AI.devad.io provides multi-model AI generation for content and images which saves your marketing team a lot of time during their daily workflows while managing campaigns."
- **Right:** "AI.devad.io provides multi-model AI generation for content and images. This software reduces content creation time for marketing teams."

- **Wrong:** "Because coding can be difficult for beginners, using applications like SITE.devad.io makes it incredibly easy to build landing pages very quickly."
- **Right:** "SITE.devad.io deploys no-code landing pages quickly."

### Rule 4.8 — Anti-Filler Directives

Never start paragraphs with these forbidden openings:
- "In today's fast-paced world"
- "It is important to remember"
- "It is important to note"
- "When it comes to"
- "In this section, we will"
- "Here, you can"
- "As you can see"
- "First, let's"
- "Now we need to"
- "Simply..."
- "Just..."

Delete words that do not add an entity, attribute, value, condition, example, or relationship.

- **Wrong:** "It is very important to note that the unified inbox inside CHAT.devad.io easily centralizes your messages."
- **Right:** "The CHAT.devad.io unified inbox centralizes multi-channel customer messages."

---

## Module 5: Structured Data Formatting & Tables

### Rule 5.1 — Grammatically Uniform Lists (POS Tagging)

Start every list item (`<li>`) within a single list with the exact same Part of Speech (e.g., all active verbs, all direct nouns, or all adjectives).

- **Wrong:**
  - Automate post scheduling.
  - Analytics for Instagram.
  - You can manage Facebook.
- **Right:**
  - Automate post scheduling via the platform.
  - Track analytics across Instagram and LinkedIn.
  - Manage Facebook engagement centrally.

### Rule 5.2 — List Sentence Introductions

Introduce every list with a complete sentence ending in a colon that defines the scope and context of the list items.

- **Wrong:** "Things to track: sentiment, you should check competitors, trends are important, reports."
- **Right:** "Social listening workflows commonly track these signal types:"

### Rule 5.3 — Ordered vs. Unordered Classification

- Use `<ol>` strictly for chronological steps, workflows, rankings, and setup instructions.
- Use `<ul>` for feature sets, examples, criteria, risks, and attribute variations.

### Rule 5.4 — Dimension-Rich Tables

Compare tools, tiers, or entities using Markdown or HTML tables with descriptive dimensional headers.

- **Wrong:** "Thing" / "Info" / "Price"
- **Right:** "Tool" / "Supported Channels" / "AI Capability" / "Pricing Basis" / "Best-Supported Use Case"

Example:
| Customer Service App | Primary Function | AI Capability |
| :--- | :--- | :--- |
| CHAT.devad.io | Unified Inbox | AI Chatbot Integration |
| Zendesk | Multi-channel Support | Automated Ticketing |

Rules:
- Every row must contain a verifiable value or `—`.
- No cell may contain a vague claim ("high", "fast", "good").
- Include source column when data comes from external research.
- Preserve source table rows, columns, order, and values in preservation mode.

### Rule 5.5 — Semantic Anchor Text

Hyperlink anchor text must explicitly reflect the target entity or page topic. Never use "click here", "read more", "learn more", or "this article".

- **Wrong:** "If you want to automate your social media, click here to learn more."
- **Right:** "Discover how to automate campaigns using social media management apps like POST.devad.io."

---

## Module 6: Source Preservation & Scraped Content Transformation

When rewriting, refreshing, or formatting existing/scraped content, apply these rules in addition to Modules 0–5.

### Step 0 — Input Classification

Read only the main body content. Ignore navigation, sidebars, footers.

| Entire body content is... | Output and stop |
|---------------------------|-----------------|
| HTTP 404 or blank page | `PAGE NOT FOUND 404` |
| Thread of user replies | `PAGE IS A FORUM` |
| Only article titles, zero prose | `PAGE IS A LISTING` |
| Homepage, multiple unrelated sections | `PAGE IS A HOMEPAGE` |

Default rule: If the input contains a title and 3+ paragraphs of prose on a unified topic, process it as a valid article. When in doubt, process as article.

### Step 1 — UI Noise Stripping

Remove silently and completely:
- Navigation menus, cookie banners, footers
- Author names, author bios, "written by" credits
- Affiliate disclosures
- "Try for free", "Get a demo", "Book a demo" CTAs
- Newsletter signup forms
- Related article link sections at the bottom
- The original conclusion (will be replaced)

Remove nothing else. Every sentence of article body content stays.

### Step 2 — Block-by-Block Preservation

**Core rule: copy first, format second. Never summarize. Never compress.**

Take each paragraph from the source in order. Copy every sentence. Wrap in `<p>`. Move to the next paragraph.

- Section headings → `<h1>` / `<h2>` / `<h3>`
- Bullet points → `<ul><li>`
- Numbered lists → `<ol><li>`
- Tables → `<table><thead><tr><th>` / `<tbody><tr><td>`
- If no `<h1>` exists in source → write one matching the exact article topic

### Step 3 — Preservation Gates

Run these checks before proceeding:

**Word Count Tolerance:**
- Output article body must stay within ±10% of the cleaned source body word count.
- Source is 3,500 words → output must be 3,150–3,850 words.
- Producing 950 words from a 3,500-word source is a total failure.

**Section Depth Check:**
- If source H2 has 4 paragraphs → output H2 must have 4 paragraphs.
- If source H2 has 2 paragraphs → output H2 must have 2 paragraphs.
- Never fewer than the source.

**List Fidelity Check:**
- Every bulleted list item → `<ul><li>` with identical text.
- Every numbered list → `<ol><li>` with identical text.
- Never merge two list items into one.
- Never drop an item because it seems redundant.
- Source has 6 bullets → output has 6 `<li>` items with identical text.

**Named Entity & Quote Check:**
Every company name, product name, customer story, statistic, percentage, price, founding year, recommendation bullet, case study, quote, and informative image caption from the source must appear in the output.

### Step 4 — Conclusion Replacement

The original conclusion was removed in Step 1. Add a new conclusion only after all preserved content:

1. One or two sentences on the value of the tools discussed.
2. A note that evaluating tools takes time and choosing wrong hurts ROI.
3. Position the publication that curates top tools for modern businesses.
4. CTA to explore more articles and subscribe.

Do not replace preserved final decision guides or recommendation lists. Keep those source sections before any new conclusion.

---

## Module 7: Product Insertion, Comparison & Neutrality Guardrails

### Rule 7.1 — Verified Product Insertion

Mention a product or tool only when the source includes it, the user asks for it, the user provides product data, or reliable research verifies the details.

- A product name does not prove features, pricing, integrations, rankings, awards, or outcomes.
- Do not invent features from a product category or domain name.
- Do not replace source examples with the user's product.

When the user requests product insertion:
- Insert one relevant product as its own `<h2>` section.
- Default placement is the **second H2** — between the first and second content sections.
- Do not move, shorten, or rewrite surrounding content to fit.
- Select products only from the user's catalog or provided data.

### Rule 7.2 — Comparison Table Safety

When adding products to comparison tables:
- Add a product row only when the user requests it and product data matches existing columns.
- Use the existing table structure. Preserve all source rows and columns.
- Use `—` (Unavailable) for unknown values.
- Do not add or remove columns.
- Do not reorder rows to favor one product.
- Do not change a comparison table to make one product look stronger.

### Rule 7.3 — Comparison Propositions

Compare using specific, measurable attributes, not subjective opinions:

- **Wrong:** "Tool A is much better and way easier to use than Tool B for your customer service team."
- **Right:** "Tool A offers unlimited agent seats on its base tier, whereas Tool B restricts base tiers to a single user."

### Rule 7.4 — Unsupported Labels

Do not add these labels without reliable evidence:
- "best for", "recommended", "top choice", "lowest price", "most complete", "industry-leading", "most trusted", "fastest", "cheapest"

### Rule 7.5 — Dynamic Product Catalog (Client-Agnostic)

Use the client's provided product catalog when available. When no catalog is provided, match products to article intent dynamically:

| Article Intent Pattern | Product Category |
|------------------------|------------------|
| Customer support / messaging | Help desk / live chat / CRM tools |
| Social media management | Social scheduling / analytics tools |
| Mini websites / WhatsApp stores | No-code builders / micro-site platforms |
| Full websites / ecommerce | CMS / ecommerce platforms |
| AI content / automation | AI writing / automation tools |

**Sample mapping (DEVAD SaaS suite — use when writing for Devad clients):**
| Article Topic | Product |
|---------------|---------|
| Customer support / messaging | CHAT.devad.io |
| Social media management | POST.devad.io |
| Mini websites / WhatsApp stores | SITE.devad.io |
| Full websites / ecommerce | WEB.devad.io |
| AI content / automation | AI.devad.io |

Never hardcode products from one client into articles for another client.

---

## Module 8: HTML Production Rules (When Raw HTML is Requested)

When the user requests raw HTML output:

- First character must be `<`. Last character must be `>`.
- Output only HTML. No Markdown fences, no backticks, no labels, no explanations.
- No preamble before `<h1>`. No postamble after the last closing tag.
- No Markdown syntax anywhere in the output.
- No internal audit, checklist, or scorecard in the output.
- Use only valid tags: `<article>`, `<h1>`, `<h2>`, `<h3>`, `<p>`, `<strong>`, `<ul>`, `<ol>`, `<li>`, `<table>`, `<thead>`, `<tbody>`, `<tr>`, `<th>`, `<td>`, `<a>`.

---

## Module 9: Silent QA Engine & Algorithmic Compliance Scorecard

Execute this verification silently before generating final output. Do not print this audit in the response unless explicitly commanded.

### Silent Audit Gateway

| Check | Question | Status |
|-------|----------|--------|
| 1. Intent & Entity Match | Central entity unbroken from H1 to conclusion? | PASS/FAIL |
| 2. EAV Saturation | ≥15 concrete EAV data points embedded? | PASS/FAIL |
| 3. Heading Vector Check | H2s are conversational questions followed by bold factual answers under 40 words? | PASS/FAIL |
| 4. Inverted Pyramid | Every section delivers core takeaway before background context? | PASS/FAIL |
| 5. Principle of Certainty | Zero modal verbs (should/might/could)? | PASS/FAIL |
| 6. Linguistic Cleanliness | Zero analogies, zero subjective fluff? | PASS/FAIL |
| 7. SVO & Syntax | Plural nouns expanded (3+)? "If" statements last? Sentences <20 words? | PASS/FAIL |
| 8. Preservation Check | ±10% source word count maintained? Zero dropped entities, lists, or tables? | PASS/FAIL |
| 9. Output Hygiene | Raw HTML cleanly formatted without Markdown backticks or preambles? | PASS/FAIL |

### Algorithmic Authorship Scorecard (Target: 100/100)

| Category | Points |
|----------|--------|
| Modal Verbs & Fluff Eradicated | 20 |
| Plural Noun Expansion & Instance Qualification | 20 |
| Question H2s + <40-Word Bold Factual Answers | 20 |
| EAV Density & Authority Citations | 20 |
| Structural Uniformity (POS Lists, Markdown/HTML Tables) | 20 |
| **Total** | **100** |

### Fail Gates (< 80 = fix before output)

- Invented fact: -20 (critical failure)
- Source entity dropped: -10 per entity
- Modal verb found: -5 per instance
- H2 without bold answer: -5 per H2
- Word count outside ±10%: -10

---

## Module 10: Ad Copy Rules

Use when generating paid advertising copy across platforms.

### 10.1 — Character Limit Enforcement

| Platform | Field | Hard Limit | Safe Target |
|----------|-------|-----------|-------------|
| Google RSA | Headline | 30 chars | 25–28 chars |
| Google RSA | Description | 90 chars | 75–85 chars |
| Meta Feed | Primary Text | 2,200 chars | 100–120 chars (hook fold) |
| Meta Feed | Headline | 255 chars | 30–35 chars |
| LinkedIn | Intro Text | 600 chars | 130–140 chars (mobile fold) |
| LinkedIn | Headline | 200 chars | 50–70 chars |
| TikTok | Ad Caption | 100 chars | 60–80 chars |
| X/Twitter | Tweet Text | 280 chars | 200–260 chars |

Count spaces as 1 character. Append `[XX/Limit]` tag to every asset.

### 10.2 — Angle Diversification

Generate 5 distinct angles (not 5 variations of the same line):

1. **Keyword/Category Match:** Direct reflection of high-intent search query.
2. **EAV & Numeric Proof:** Concrete capability, price point, or quantified outcome.
3. **Pain-Point Hook:** Immediate resolution of a specific operational friction.
4. **Feature/Integration Spec:** Exact tools, formats, platforms, or technical specs.
5. **Direct CTA:** Imperative command with zero ambiguity.

### 10.3 — Ad Copy Guardrails

- Zero modal verbs (should/might/could/probably).
- Zero vague hype (revolutionary/effortless/game-changing/best/seamless/world-class).
- Mandatory SVO and imperatives. CTA lines start with active verbs.
- EAV in headlines: [Entity/Offer] + [Attribute/Value] + [Constraint/Proof].
- No invented facts. Numbers only from user-provided data or verified research.

### 10.4 — Platform-Specific Output

- **Google RSA:** 5–15 headlines + 3–4 descriptions + 2 display paths. Every asset tagged with character count.
- **Meta Feed:** Primary text hook under 120 chars + headline under 35 chars + description under 30 chars + CTA button label.
- **LinkedIn:** Intro text under 140 chars + headline under 70 chars. Professional tone, zero consumer hype.

---

## Module 11: Social Media Content Rules

Use when generating organic social media posts across platforms.

### 11.1 — Truncation Fold Strategy

Every post must deliver the complete core hook before the platform's "See More" fold:

| Platform | Hard Limit | Truncation Fold | Hook Target |
|----------|-----------|-----------------|-------------|
| LinkedIn | 3,000 chars | ~210 desktop / ~140 mobile | 130–140 chars |
| Instagram | 2,200 chars | ~125 chars | 100–115 chars |
| TikTok | 4,000 chars | ~90 chars | 80–90 chars |
| Facebook | 63,206 chars | ~477 chars | 400–450 chars |
| YouTube | 5,000 chars | ~157 chars | 130–150 chars |
| X/Twitter | 280 chars | No fold | 260–270 chars |

The hook must deliver one complete thought — not a cliffhanger.

### 11.2 — Platform Formats

- **LinkedIn:** Hook (140 chars) + 3–5 short paragraphs or bulleted EAV + conversational question outro + 3–5 hashtags.
- **X/Twitter:** Single post (280 chars) or thread (3–5 tweets). Each tweet standalone. No hashtags in promoted posts.
- **Instagram:** Hook (125 chars) + scannable body + 3–5 hashtags (max 5, 2025+ limit).
- **TikTok:** Hook (90 chars) + concise body + link-in-bio CTA. 3–5 hashtags.
- **Facebook:** Hook under 477 chars + longer body if needed. No hashtags in organic posts.
- **YouTube:** SEO hook (150 chars) + chapters/timestamps + links + CTA.

### 11.3 — Social Copy Guardrails

- Zero modal verbs and vague hype (same as ad copy).
- Zero conversational filler (Let's dive in / Have you ever wondered / In today's world).
- Hook completeness: Line 1 must deliver a complete thought before the truncation fold.
- Emoji restraint: Max 1–2 per section as visual bullet anchors.
- Hashtag restraint: Max 3–5 per post. Never more than 5 on Instagram.
- No invented facts. Numbers only from user-provided data or verified research.

### 11.4 — Hashtag Matrix

| Tag Type | Purpose | Example |
|----------|---------|---------|
| Broad Category | Reach discovery | #CustomerSupport |
| Niche Entity | Targeted audience | #UnifiedInbox |
| Specific Feature | Feature search | #WhatsAppIntegration |
| Branded/Campaign | Brand recall | #YourBrandName |
| Trending (optional) | Timely reach | Only if genuinely relevant |
