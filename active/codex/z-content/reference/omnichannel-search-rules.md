# Omnichannel Search Rules — compact SEO/AEO/GEO extension

Load beside `workflows/type-article.md` only for full SEO+AEO+GEO output, AI Overviews, Featured Snippets, voice search, metadata, or schema. Do not load for simple rewrites, scraped cleanup, developer docs, landing pages, or reports.

## SEO foundation

- **Meta title:** 50–60 characters; put the primary high-intent keyword in the first 30 characters and the brand at the end.
- **Meta description:** 140–160 characters; include secondary keywords, one verified attribute/metric, and a direct action.
- Put the primary keyword and central entity in the first 100 words without forced repetition.
- Keep paragraphs below 60 words and 3–4 sentences. Keep heading order H1 → H2 → H3 → H4.
- For visuals, emit a specific placeholder and 80–120 character descriptive alt text that explains the entity relationship.

## AEO extraction

- Mirror natural-language queries in H2/H3 headings.
- Put a definitive, source-grounded answer first after each eligible heading; keep standard snippets under 40 words, hard limit 45.
- Use explicit named entities instead of ambiguous opening pronouns such as “it”, “this”, or “they”.
- Answer FAQ/PAA questions in one complete sentence before explanation.
- Append valid, unescaped JSON-LD matching the content type: `FAQPage`, `HowTo`, `Article`, `SoftwareApplication`, or `Product`.

## GEO authority

Define the entity’s audience/scale, operational problem, capability, and industry category in the introduction. Answer compound prompts with layered sections. Support major claims with exact, verifiable numbers, named source, date, and baseline. Use neutral comparison tables with dimensions such as cost basis, integrations, SLA limits, and scalability; use `—` when data is unavailable.

## Output frame

```text
Meta Title / Meta Description
H1: exact topic and intent
Intro: entity + audience + problem + category
H2 question → bold direct answer → EAV proof
H2 decision framework → neutral table
H3 question → one-sentence answer
FAQ → one-sentence answers
JSON-LD schema
```
