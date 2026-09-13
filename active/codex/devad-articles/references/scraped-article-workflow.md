# Scraped Article Workflow

Use this workflow for copied or scraped article content when the user asks to clean, preserve, format, convert, or output article HTML.

## Classification

Process the input as an article when it has one clear topic and article-body prose. Only stop with a label when the whole body is clearly one of these cases:

- `PAGE NOT FOUND 404`
- `PAGE IS A FORUM`
- `PAGE IS A LISTING`
- `PAGE IS A HOMEPAGE`

When in doubt, process it as an article.

## Copy First, Format Second

- Preserve source meaning and body order.
- Do not summarize, compress, paraphrase, or rewrite unless the user asks.
- Preserve every article-body heading, paragraph, list item, table row, example, recommendation, comparison, evidence point, named entity, number, price, and date unless the user asks for compression.
- Process the article block by block: source heading to output heading, source paragraph to output paragraph, source list to output list, source table to output table.
- If a source section has 10 paragraphs, the output section must not shrink it to 2 paragraphs unless the user asks for compression.
- Remove navigation, cookie banners, author boxes, affiliate disclosures, generic CTAs, newsletter blocks, related-link blocks, and footer content.
- Remove only true outro filler when replacing a conclusion. Preserve final factual summaries, recommendations, or decision guides.
- If no H1 exists in the article body, create one that reflects the exact source topic without editorializing.
- Convert informal dash or bullet text into `<ul><li>` or `<ol><li>` markup while preserving every item.

## SEO Formatting In Preservation Mode

- Rewrite headings as questions only when the meaning stays intact.
- Add bold direct answers only from facts already present in the same section or adjacent source context.
- When adding a bold answer under a major heading, bold a full factual answer under 40 words, not a label or isolated keyword.
- AEO additions are additive only: insert a short source-derived answer after the heading, then preserve the original source block.
- AEO additions must not reduce paragraph count, list item count, table row count, named entities, numbers, examples, recommendations, quotes, or case-study details.
- For raw HTML article output, every H2 except `Conclusion`, `Key takeaways`, and source-preserved non-answer sections should be followed immediately by `<p><strong>...</strong></p>`.
- If no source-supported answer can be written, keep the source content unchanged and flag the missing snippet during the silent audit instead of inventing one.
- Do not introduce new claims in snippets.
- Do not update old facts unless the user asks for refresh or current information.
- Keep the output body close to source length unless the user asks for compression.
- Format-only output should stay within +/-10% of the source article body word count after removing page noise.
- The +/-10% target applies after adding snippets; if snippets would exceed it, prioritize H2 snippets over H3 snippets.
- A large word-count drop usually means source paragraphs, examples, tables, or decision-critical details were lost.
- Do not trade source preservation for shorter SEO copy in format-only mode.

## HTML Output

When raw HTML is requested:

- First character must be `<`.
- Last character must be `>`.
- Use no Markdown fences, backticks, preamble, or postamble.
- Add no preamble or postamble.
- If the draft starts with ```html, ```, text labels, or explanations, strip them before final output.
- If any ``` remains anywhere in the final raw HTML, revise before responding.
- Convert paragraphs, headings, lists, and tables into clean article HTML.
- Preserve list item count and table row count.
