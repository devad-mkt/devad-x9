# Audit Checklist

Run silently before final output. Do not print unless the user asks.

## Intent Match

- The output answers the user's exact content goal.
- The central topic, entity, offer, or idea stays consistent.
- The format matches the requested content type.
- Landing-page or CRO work is routed to `devad-lp-content`.

## Factual Integrity

- Source meaning is preserved unless rewrite, compression, transformation, or refresh was requested.
- Named entities, numbers, dates, prices, comparisons, recommendations, and evidence are accurate.
- No facts, examples, results, citations, testimonials, rankings, prices, product claims, or metrics are invented.
- Missing facts are omitted, marked unavailable, or requested from the user.
- Internal rules, audits, frameworks, rulebooks, validation files, and content processes are not mentioned in the final article unless requested.

## SEO And AEO Structure

- The topical map is clear.
- Major headings answer real user questions when natural.
- The first sentence after each major heading answers the heading directly.
- Bold direct answers stay under 40 words when snippet optimization is requested.
- Bold snippets are factual answers, not labels or isolated keywords.
- In raw HTML article output, every eligible H2 is followed by `<p><strong>...</strong></p>`.
- H2 snippets are additive in scraped preservation mode and do not replace source paragraphs.
- Tables are used for comparisons, attributes, pricing, alternatives, or decision criteria.
- Lists use consistent grammar.

## Entity Density

- Vague claims are converted into entity-attribute-value facts.
- Broad categories include examples, types, channels, audiences, constraints, or use cases.
- Exact numbers are preserved when provided and omitted or generalized when unsupported.
- The article stays dense without padding.

## Copy Quality

- Sentences start with the main topic, entity, problem, offer, or action when possible.
- Verbs are precise.
- Filler, hedging, hype, analogies, personal opinion, and unsupported superlatives are removed.
- Long sentences are split when clarity improves.
- Benefits are tied to attributes or evidence.

## Scraped Or Copied Content

- Article-body order is preserved.
- Paragraphs, lists, tables, examples, recommendations, comparisons, and decision-critical details are not dropped.
- UI noise and unrelated page furniture are removed.
- Old facts are not updated unless refresh mode is active.
- Format-only output stays within +/-10% of the article-body word count after page noise is removed.
- Source list item counts and table row counts are preserved.

## Product Or Tool Mentions

- Product features, prices, integrations, rankings, awards, and outcomes come only from source text, user data, or verified research.
- Product names are examples only; no features are inferred from the name.
- Unavailable product data is omitted or marked neutrally.
- Product mentions stay relevant to the article topic.

## Raw HTML Gate

- The first character is `<` and the last character is `>` when raw HTML is requested.
- No Markdown fences, backticks, labels, preambles, postambles, or explanations wrap the HTML.
- No ``` sequence appears anywhere in final raw HTML.
- The output is revised before final if any wrapper text remains.
