---
name: devad-articles
description: Use when Codex needs to draft, rewrite, refresh, expand, convert, audit, or format article-style content, including SEO blog articles, scraped article HTML, old article updates, short briefs, comparison articles, guides, FAQs, AEO content, featured-snippet content, and product insertion inside articles while enforcing the compact Devad article framework.
---

# Devad Articles

## Overview

Use this skill for article-style content: fresh blog articles, article rewrites, scraped article cleanup, old article refresh, short-to-full article expansion, comparison articles, guides, FAQs, article audits, and article HTML formatting.

Use `devad-lp-content` for pure landing pages, sales pages, product pages, signup pages, demo-booking pages, lead-capture pages, campaign pages, and CRO copy.

Always start with `references/article-compact-rules-v1.md`. Load the workflow references only when the task needs them.

## Rule Priority

Apply this priority order:

1. Follow the user's explicit request.
2. Never invent facts, numbers, citations, examples, outcomes, product claims, prices, testimonials, rankings, or metrics.
3. Preserve source meaning unless the user asks for rewrite, compression, transformation, or refresh.
4. Use exact numbers only from the source, user-provided data, or verified research.
5. For scraped format-only work, copy first and format second.
6. For outdated content, update facts only when the user asks for current or refreshed content.
7. Scale depth and EAV density to the requested content length without padding.

## Workflow

1. Classify the task:
   - Fresh article, rewrite, comparison, guide, FAQ, or audit: use `references/article-compact-rules-v1.md`.
   - Scraped or copied article cleanup/HTML: also use `references/scraped-article-workflow.md`.
   - Short brief, thin source, old article cleanup, outdated article formatting, or old article refresh: also use `references/short-old-article-workflow.md`.
2. Define the topical map: source context, central topic/entity, search intent, core sections, and supporting sections.
3. Write or transform using the compact rulebook.
4. Run `references/audit-checklist.md` silently before final output.
5. Do not print the audit unless the user explicitly asks for it.
6. Do not mention internal rules, audits, frameworks, rulebooks, validation files, or content processes in the final article unless the user explicitly asks.

## Output Defaults

Default to clean Markdown unless the user asks for raw HTML, CMS HTML, or another format.

When the user asks for raw HTML:

- Start the response with `<`.
- End the response with `>`.
- Do not use Markdown fences.
- Do not add preamble or postamble.
- Use valid article tags: `<h1>`, `<h2>`, `<h3>`, `<p>`, `<strong>`, `<ul>`, `<ol>`, `<li>`, `<table>`, `<thead>`, `<tbody>`, `<tr>`, `<th>`, and `<td>`.
- Before final, delete any accidental ``` fences, backticks, labels, explanations, or whitespace that appear before the first HTML tag or after the last HTML tag.
- Run a final wrapper strip before responding:
  1. Delete any leading Markdown fence, language label, blank line, or explanation before the first `<`.
  2. Delete any trailing fence, backticks, blank line, or explanation after the final `>`.
  3. If the first character is not `<`, the last character is not `>`, or any ``` remains, revise before responding.

## References

- `references/article-compact-rules-v1.md`: compact article framework and priority rules.
- `references/scraped-article-workflow.md`: source-preserving workflow for copied or scraped article content.
- `references/short-old-article-workflow.md`: short brief expansion, old article refresh, missing facts, and citations.
- `references/audit-checklist.md`: final silent QA checklist.
