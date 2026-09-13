# Article Compact Rules v1

Use this grouped framework for article-style content: blog posts, guides, comparisons, FAQs, rewrites, refreshes, scraped article cleanup, and article HTML formatting. The goal is dense, accurate, extractable content that preserves source facts, answers search intent directly, and avoids unsupported claims.

This file is a compact operating rulebook, not a short summary. Preserve the meaning of every rule group. Load the workflow files only when the task requires scraped cleanup, short-input expansion, outdated refresh, or final audit detail.

## Priority Stack

Apply this order when rules conflict:

1. Follow the user's explicit task and requested output format.
2. Preserve source meaning, facts, entities, numbers, tables, lists, recommendations, examples, and order unless the user asks for rewrite, compression, or refresh.
3. Never invent facts, product claims, features, prices, dates, citations, rankings, testimonials, metrics, case studies, comparisons, or outcomes.
4. Use exact numbers only from source text, user data, product data, or verified research.
5. For scraped format-only work, copy first and format second.
6. For AEO or SEO work, improve headings and snippets only when preservation stays intact.
7. For article drafting without a source, build from verifiable facts and clearly scoped assumptions; omit missing facts instead of filling them with generic copy.
8. Do not mention internal rules, audits, frameworks, rulebooks, validation files, or content processes in final article content unless the user asks.

Critical failures:

- Invented facts or unsupported product claims.
- Replaced source entities with unrelated entities.
- Dropped decision-critical facts, tables, lists, examples, quotes, recommendations, or case studies.
- Compressed preserved source content when preservation was required.
- Added unsupported rows, columns, prices, features, rankings, or claims to comparison tables.
- Wrapped requested raw HTML in Markdown fences, labels, preambles, postambles, or backticks.

## P1 Topical Map And Intent Boundaries

Covers: source context, central entity, central search intent, core sections, outer sections, section scope, context flow, appropriate length coverage.

Rules:

- Define the source context before writing: publication purpose, audience, business context, content type, and why the article should exist.
- Define the central entity in one clear noun phrase. Every heading, paragraph, list, and table must connect to that entity or to a directly supporting attribute.
- Define the central search intent as a verb-noun goal, such as "compare help desk tools", "choose email automation software", "understand social listening", or "format a scraped guide".
- Separate core sections from supporting sections. Core sections answer the main intent. Supporting sections add proof, examples, alternatives, objections, definitions, or implementation detail.
- Keep one unbroken context path from H1 to conclusion. Each new section must answer a real sub-question or supply a needed attribute.
- Match length to coverage. Long intent requires full attribute coverage; simple intent should stop when the answer is complete.
- In scraped or preservation mode, the source article's own structure is the boundary. Improve formatting without changing the article's scope.

Do not:

- Do not mix unrelated topics to increase length.
- Do not write generic introductions before defining the central entity.
- Do not add sections only because they are common in SEO templates.
- Do not turn an article into a landing page, sales page, demo page, signup page, or CRO page.
- Do not expand thin inputs by inventing audience, product, market, pricing, proof, or competitor details.

Bad:

"This article explains social listening, general marketing automation, email productivity, and why modern teams need smarter digital workflows."

Good:

"Social listening is the process of tracking online conversations, measuring audience sentiment, comparing competitor mentions, and turning those signals into marketing and product decisions."

Why the good version works:

- Central entity: social listening.
- Intent: understand and apply social listening.
- Core attributes: conversations, sentiment, competitor mentions, decisions.
- No unrelated topic drift.

## P2 Factual Integrity And Claim Safety

Covers: no invention, source fidelity, exact numbers, citations, stable versus unstable facts, product claims, competitor claims, current facts, unsupported recommendations.

Rules:

- Preserve source meaning unless the user asks for transformation. Rewrite wording only when it keeps the same facts, relationships, limits, and emphasis.
- Keep every named entity from the source when it is part of the article body: companies, tools, people, products, locations, features, dates, statistics, case studies, quotes, and examples.
- Keep exact numeric values as written: percentages, prices, ranges, dates, counts, durations, rankings, years, feature limits, and performance metrics.
- If a number is unavailable, use a concrete non-numeric attribute or omit the claim. Do not replace vague source wording with invented precision.
- Verify unstable facts when the user asks for current, latest, refreshed, updated, or new information. Unstable facts include prices, plans, features, integrations, laws, model names, rankings, company metrics, statistics, and competitor comparisons.
- Cite external evidence next to the claim it supports when the claim depends on research, market data, legal/medical/financial facts, benchmarks, pricing, rankings, or product capabilities.
- Keep factual claims narrower than the evidence. If the source proves one channel, one plan, or one case study, do not generalize it to all channels, all plans, or all customers.
- Use recommendation language only when the recommendation is supported by the source, user data, or verified research.

Do not:

- Do not invent product features from a product name.
- Do not insert a product into an article unless the user asks, the source includes it, or verified product data is provided.
- Do not replace source companies, tools, case studies, or examples with another brand.
- Do not add unsupported table rows, pricing cells, "best for" labels, awards, rankings, integrations, limits, or outcomes.
- Do not convert quoted or attributed statements into anonymous claims if the attribution matters.
- Do not cite unsupported internal claims as verified facts.
- Do not say "industry-leading", "best", "fastest", "cheapest", "most trusted", or similar superlatives without reliable evidence.

Bad:

"The platform monitors every social network, integrates with all CRMs, and delivers the lowest price in the market."

Good:

"The monitoring tool can be described by its supported channels, alert options, sentiment analysis, reporting features, and pricing only when those details appear in the source or verified product data."

Example conversion:

Source fact: "Plan A costs $49 per month and includes email alerts."

Good article sentence: "Plan A costs $49 per month and includes email alerts."

Bad article sentence: "Plan A is the cheapest option and includes alerts, analytics, integrations, and unlimited monitoring."

## P3 Entity-Attribute-Value Density

Covers: semantic triples, entity-attribute-value facts, numeric precision, qualifying broad categories, plural noun expansion, information responsiveness, no padding.

Rules:

- Convert vague claims into entity-attribute-value facts: entity, attribute, value.
- Use subject-verb-object sentences so relationships are easy to extract.
- Start sentences with the main entity, attribute, problem, or action when possible.
- Replace vague quantity words with exact values when reliable values exist. Vague words include many, several, various, multiple, numerous, often, usually, better, faster, and affordable.
- Qualify broad categories with specific examples, types, channels, formats, users, constraints, scale, use cases, or values.
- Expand plural nouns with examples when the examples improve clarity. A plural such as "channels", "features", "risks", "teams", or "metrics" should usually name the included items.
- Use tables for dense attribute comparisons, feature matrices, pricing, alternatives, decision criteria, and entity-attribute-value groupings.
- In long-form articles, include repeated concrete facts across sections. In short content, scale density to length.
- Stop when the search intent and entity attributes are covered. Dense does not mean long.

Do not:

- Do not use EAV as permission to invent missing values.
- Do not pad with generic background, broad benefits, or abstract strategy language.
- Do not list examples that are unrelated to the central entity.
- Do not use exact-looking numbers without a reliable source.
- Do not hide important values in vague copy when a table would be clearer.

Bad:

"Customer support software gives teams many useful features and helps companies improve service."

Good:

"Customer support software centralizes email, chat, social messages, help-center tickets, SLA rules, routing queues, customer history, and reporting dashboards for service teams."

Good EAV table:

| Entity | Attribute | Value |
| --- | --- | --- |
| Customer support software | Supported channels | Email, live chat, social messages, and help-center tickets |
| Routing queue | Function | Assigns conversations to the right team or agent |
| SLA rule | Function | Tracks response deadlines by priority level |

Why the good version works:

- It names the entity.
- It lists concrete attributes.
- It avoids invented performance outcomes.
- It uses a table when relationships are dense.

## P4 Sentence Quality, Syntax, And Tone

Covers: entity-first phrasing, direct subject-verb-object propositions, certainty, precise verbs, no filler, no analogies, no personal opinion, formal tone, brevity, if-statements last.

Rules:

- Use direct subject-verb-object sentences.
- Put the main entity and action early. Conditions, caveats, and "if" clauses usually belong after the main action.
- Use precise contextual verbs. Examples: monitors, detects, clusters, compares, routes, publishes, verifies, ranks, measures, summarizes, calculates, stores, filters, syncs, imports, exports, schedules, alerts, assigns.
- Remove filler, hedging, hype, adverbs, conversational phrases, empty transitions, and emotional pressure.
- Remove personal opinion. Replace "we think", "I believe", "in our experience", and "you should probably" with factual claims or sourced recommendations.
- Use formal, objective language. The article can persuade through facts, not through excitement.
- Avoid analogies and metaphors when they connect the topic to irrelevant entities.
- Split overloaded sentences into shorter factual statements.
- Use modal verbs only when the meaning requires possibility, obligation, or future timing. Avoid "might", "could", "should", "probably", and "will" when they create uncertainty or unsupported prediction.
- Delete words that do not add an entity, attribute, value, condition, example, or relationship.

Do not:

- Do not start sections with "In today's fast-paced world", "It is important to note", "When it comes to", or similar filler.
- Do not use hype as proof.
- Do not compare software to magic, engines, weapons, animals, secret sauces, or other irrelevant objects.
- Do not bury the answer behind background paragraphs.
- Do not use "easy", "powerful", "robust", "seamless", or "game-changing" unless the sentence explains the specific attribute behind the claim.

Bad:

"In today's fast-paced world, many teams should probably consider a powerful tool that can act like a central hub and help them do a better job."

Good:

"The platform centralizes customer messages from email, chat, and social channels. It reduces manual inbox switching when those channels are connected."

Why the good version works:

- The entity comes first.
- The verbs are specific.
- The condition stays attached to the claim.
- The sentence avoids hype and analogy.

## P5 Headings, Snippets, And Answer Extraction

Covers: question-based H2/H3 headings, immediate direct answers, 40-word snippets, bolding the fact, PAA answers, definitive answers, heading vectors, preservation-aware SEO.

Rules:

- Use one H1 that states the exact article topic.
- Use question-based H2s and H3s when natural. A heading should match a real user question or a clear sub-intent.
- In fresh articles, rewrites, SEO upgrades, and raw HTML article output, every H2 except `Conclusion`, `Key takeaways`, and source-preserved non-answer sections must be followed immediately by a bold direct answer.
- In raw HTML, the answer pattern is `<p><strong>Complete factual answer under 40 words.</strong></p>`.
- The first sentence after each major H2 must answer the heading directly.
- When optimizing for snippets or AI answers, make the first answer sentence factual, bold, and under 40 words.
- Bold the factual answer, not only the keyword, a label, a verb, or a search term.
- For FAQ and PAA-style sections, answer in one direct sentence before adding explanation.
- Use definitive answers when the source supports certainty. If certainty is not supported, state the condition or limitation directly.
- In scraped preservation mode, convert headings into questions only when the section meaning stays intact.
- In scraped preservation mode, add the bold answer as an extra paragraph after the heading; do not replace, compress, or rewrite the preserved source paragraph.
- In scraped preservation mode, derive the bold answer only from facts already present in the same section or immediately adjacent preserved source context.
- If no source-supported answer can be written, keep the source content unchanged and flag the missing snippet during the silent audit instead of inventing one.
- Prefer question-form H2s when the source heading can be converted without changing meaning. Keep exact source headings only when conversion would distort the source.
- AEO structure must not remove paragraphs, shorten case studies, alter tables, or change source facts.

Do not:

- Do not delay the answer with background or generic setup.
- Do not bold labels such as "Benefits:", "Optimize", "Key point", or "Overview" when a factual answer is expected.
- Do not invent a snippet answer that is not in the source.
- Do not rewrite every heading if doing so changes the source meaning or order.
- Do not turn a comparison, example, or future-trends section into a sales claim.
- Do not count bold list labels, table labels, category names, or isolated keywords as direct answers.

Bad:

```html
<h2>Benefits of Social Listening</h2>
<p>Marketing teams have many channels to manage today, and the online environment changes quickly.</p>
```

Good:

```html
<h2>What are the benefits of social listening?</h2>
<p><strong>Social listening helps teams monitor brand reputation, measure sentiment, compare competitors, detect trends, and respond to audience feedback.</strong></p>
```

Why the good version works:

- The heading is a question.
- The first sentence answers the question.
- The bolded text is a complete factual answer.
- The answer stays under 40 words.

## P6 Lists, Tables, Links, And HTML Structure

Covers: list grammar, ordered steps, unordered variations, strong list introductions, table dimensions, semantic anchor text, raw HTML, article tags, output format.

Rules:

- Use ordered lists for procedures, sequences, workflows, setup steps, ranking logic, or instructions.
- Use unordered lists for examples, attributes, benefits, risks, tools, variations, use cases, criteria, and non-sequential details.
- Introduce every list with a complete sentence that defines the list context.
- Keep list items grammatically consistent. Start items with the same part of speech when possible.
- Preserve list item count in copied or scraped content.
- Use tables when comparing features, prices, tiers, alternatives, categories, use cases, pros and cons, or entity-attribute-value relationships.
- Use dimension-rich table headers. Headers should explain the relationship, not just say "Thing" and "Info".
- Preserve source table rows, columns, order, and values in preservation mode unless the user asks for a changed table.
- Use descriptive anchor text that names the destination topic, entity, product, or article. Generic anchors weaken semantic relevance.
- Match the user's requested output format exactly: Markdown, raw HTML, CMS HTML, plain text, table, outline, or JSON-like structure.
- For raw HTML, the first character must be `<` and the last character must be `>`.
- For raw HTML, output only HTML. Never use Markdown fences, backticks, labels, explanations, preambles, postambles, or whitespace outside the article HTML.
- If a raw HTML draft contains ``` or text before the first HTML tag, remove the wrapper before final output.
- Use valid article tags: `<article>`, `<h1>`, `<h2>`, `<h3>`, `<p>`, `<strong>`, `<ul>`, `<ol>`, `<li>`, `<table>`, `<thead>`, `<tbody>`, `<tr>`, `<th>`, and `<td>`.

Do not:

- Do not merge two source list items into one.
- Do not drop a list item because it sounds redundant.
- Do not add or remove comparison-table columns in preservation mode.
- Do not use "click here", "read more", "learn more", or "this page" as anchor text.
- Do not put Markdown bold syntax inside HTML tags.
- Do not wrap raw HTML in ```html.

Bad list:

"Things to track: sentiment, you should check competitors, trends are important, reports."

Good list:

"Social listening workflows commonly track these signal types:

- Monitor brand mentions.
- Measure sentiment changes.
- Compare competitor share of voice.
- Detect emerging topics.
- Report campaign feedback."

Good table:

| Social listening attribute | What the attribute measures | Example output |
| --- | --- | --- |
| Sentiment analysis | Positive, neutral, or negative tone | Weekly sentiment trend |
| Share of voice | Mention volume by competitor | Competitor comparison chart |
| Topic clustering | Repeated conversation themes | Content topic ideas |

## P7 Scraped, Copied, Short, And Old Article Workflows

Covers: input classification, UI-noise removal, paragraph-by-paragraph preservation, list/table fidelity, word-count coverage, old-content refresh, thin-source expansion, citations.

Rules:

- Treat copied or scraped prose as an article when it has one clear topic and article-body paragraphs.
- Return a non-article label only when the whole input is clearly a 404 page, forum, listing, homepage, or blank page.
- When in doubt, process the input as an article instead of rejecting it.
- Remove UI noise: navigation, cookie banners, author boxes, affiliate disclosures, newsletter forms, unrelated CTAs, related-link blocks, footers, and repeated page furniture.
- Preserve article-body headings, paragraphs, lists, tables, examples, recommendations, comparisons, evidence, named entities, numbers, prices, and dates.
- Process block by block: heading to heading, paragraph to paragraph, list to list, table to table.
- Create an H1 only when the source lacks one; the H1 must reflect the exact article topic without editorializing.
- Convert informal dash or bullet text into proper list markup while preserving every item.
- If a source section has four paragraphs, the output section should not shrink to one paragraph unless compression was requested.
- Format-only scraped output should stay within +/-10% of the article body word count after page noise is removed.
- Preserve final factual summaries, recommendation lists, and decision guides. Remove only true outro filler when replacing a conclusion.
- For short or thin inputs, build from known facts, ask only when a missing fact blocks the task, and omit unsupported details.
- For old content, refresh facts only when the user asks for current, latest, refreshed, updated, or new information.
- When refreshing old content, verify unstable facts before replacing them.

Do not:

- Do not summarize, compress, paraphrase, or rewrite copied article text unless requested.
- Do not trade source preservation for shorter SEO copy.
- Do not drop image captions, quotes, or bylined expert statements when they contain article-body information.
- Do not update old prices, features, dates, rankings, or claims without verification.
- Do not pretend missing facts exist in a short brief.
- Do not treat a normal article with CTAs as a listing page.

Bad preservation:

Source has six bullets, two examples, a pricing table, and a final decision guide. Output has three bullets, no examples, a rewritten two-row table, and a generic conclusion.

Good preservation:

Source has six bullets, two examples, a pricing table, and a final decision guide. Output keeps six `<li>` items, both examples, every table row and column, and the decision guide before any new conclusion.

## P8 Product, Tool, Comparison, And CTA Rules

Covers: product insertion, tool examples, comparison propositions, table row safety, unavailable values, conclusion, CTAs, article-safe persuasion.

Rules:

- Mention a product or tool only when the source includes it, the user asks for it, the user provides product data, or reliable research verifies the details.
- Use product names as examples only. A name does not prove features, pricing, integrations, rankings, awards, or outcomes.
- When the user requests product insertion, insert one relevant product/tool section by default. Place it near the top, usually as the second H2, unless the user specifies a different placement.
- Select products only from the source, the user's catalog, the user's mapping, or verified research. Do not create a product mapping from assumptions.
- Keep product sections relevant to the central article topic and separate from preserved source sections.
- Add a product row to a comparison table only when the user requests it and product data matches the existing columns.
- Use the existing table structure. Preserve all source rows and columns.
- Use a neutral unavailable marker or omit the cell when product data is unavailable.
- Use comparison propositions only when the compared attributes are specific and supportable.
- Explain benefits through attributes, evidence, or use cases.
- Use calls to action only when the article purpose supports a next step. Keep CTAs short and factual.
- When a complete article needs a new conclusion, use an H2 conclusion with short paragraphs that summarize topic value, restate decision criteria or evaluation risk, optionally position the publication or tool category factually, and include a restrained CTA only when appropriate.
- Conclusions must not replace preserved final decision guides or recommendation lists; keep those source sections before any new conclusion.

Do not:

- Do not insert a product as the answer to every section.
- Do not replace source examples with the user's product.
- Do not infer features from a product category or domain name.
- Do not add unsupported "best for", "recommended", "top choice", "lowest price", or "most complete" labels.
- Do not change a comparison table to make one product look stronger.
- Do not add campaign-style CRO copy to an article.
- Do not add more than one product section unless the user asks for multiple products or a comparison.

Bad:

"Because ExampleDesk is the best platform, it should replace every help desk tool in the comparison table."

Good:

"ExampleDesk can be added to the table only if its supported channels, pricing, AI features, reporting options, and integration data are provided or verified. Missing values should stay unavailable instead of being invented."

## P9 Silent Audit And Final Gate

Covers: EAV audit, rule compliance score, final checks, hidden QA, no printed audit, critical failures.

Run this audit silently before final output:

- Intent: The article answers the user's exact task and stays article-style.
- Boundaries: The central entity, search intent, core sections, and supporting sections stay consistent.
- Source fidelity: Source facts, order, entities, numbers, examples, lists, tables, quotes, recommendations, and case studies are preserved when preservation is required.
- No invention: No unsupported claims, product features, statistics, prices, citations, rankings, testimonials, outcomes, or competitor claims were added.
- EAV: Vague claims were converted into concrete entity-attribute-value facts where reliable values exist.
- Syntax: Sentences use direct structure, precise verbs, formal tone, no filler, no unsupported superlatives, no personal opinion, and no irrelevant analogies.
- AEO: Major headings are questions when natural; first sentences answer directly; bold snippets are factual answers under 40 words when snippet optimization is requested.
- H2 gate: Every eligible H2 in SEO or raw HTML article output is followed by a complete bold factual answer under 40 words, or the missing snippet is intentionally preserved because no source-supported answer exists.
- Lists and tables: List item counts, table rows, columns, and values match the source in preservation mode.
- Links: Anchor text names the destination topic or entity.
- Product mentions: Product data is sourced, verified, or marked unavailable.
- Old content: Unstable facts were verified before refresh.
- Raw HTML: The first character is `<`, the last character is `>`, and no Markdown fences, backticks, labels, preambles, or postambles remain.
- Internal process: No audit, scorecard, rule list, validation note, or process explanation appears in the final article unless requested.

Do not print the audit unless the user explicitly asks for it.

If a critical failure is found, fix it before final output. If it cannot be fixed because data is missing, state the limitation outside the article output or ask the user for the missing fact.
