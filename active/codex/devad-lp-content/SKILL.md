---
name: devad-lp-content
description: Use when Codex is asked to create, rewrite, optimize, audit, or structure landing-page content, sales-page copy, SaaS/product pages, demo-booking pages, signup pages, lead-capture pages, campaign pages, or CRO-focused page copy.
---

# Devad LP Content v2.1

## Overview

Use this skill to produce factual, entity-led landing-page content and conversion-rate optimization recommendations. Before substantial landing-page or CRO work, read `references/landing-page-rulebook.md`; read `references/lp-templates.md` when a source analysis, size router, brief, wireframe, section copy, HTML outline, direct-response product page, or audit template would help.

Use `devad-articles` for blog articles, scraped article cleanup, old article refreshes, guides, comparison posts, and article HTML formatting.

## Core Rule

Build the page around one memorable commercial message, one acquisition offer, and one CTA path. Select the landing-page size and useful sections before drafting. Every headline, visual annotation, proof block, FAQ, testimonial, and CTA must reinforce the same idea.

## Workflow

1. Run the source analysis and size router before drafting:
   - Source analysis: identify the product/service entity, audience, traffic source, commercial goal, source-backed facts, proof assets, objections, missing facts, and strongest commercial attributes.
   - Awareness level: classify the visitor as most aware, product aware, solution aware, problem aware, or cold traffic when evidence is available.
   - CTA friction: identify whether the offer is self-serve, low-cost, downloadable, trial-led, demo-led, quote-led, or enterprise sales-led. Do not default to demo booking when the source indicates a low-friction purchase or download.
   - Page size: choose Short / Compact, Medium / Standard, or Full / Expanded. Default to Medium / Standard when the user does not specify size.
   - Recommended LP parts: include only the sections the source and conversion goal support. Do not output every template section by default.
   - For normal Markdown production copy, show a brief `Source Analysis` and `Recommended LP Parts` block before the copy unless the user asks for final copy only.
   - For raw HTML, CMS blocks, or final-copy-only requests, run the router silently and output only the requested format.

2. Define the landing-page intent map:
   - Product or service entity.
   - Target audience and traffic source.
   - Primary acquisition goal: demo, signup, trial, quote, purchase, or lead capture.
   - One big idea that explains why the offer matters.
   - One acquisition offer and one CTA destination.
   - One CTA friction level that fits the source, price, buying model, and visitor commitment.
   - Functional component needed to satisfy intent: form, booking module, calculator, demo preview, comparison selector, estimator, or product interaction.
   - Proof assets, objections, and constraints supplied by the user.

3. Decide page vs segment:
   - Create a standalone landing page only when the product, offer, feature, or audience has independent search demand or acquisition value.
   - Keep minor features, integrations, or settings as H2/H3 segments inside a stronger parent page.
   - Do not create thin pages for small attributes that can be handled by structured feature cards.

4. Write the headline path first:
   - H1 states the one big idea with a concrete outcome, audience, mechanism, or value.
   - H2s and H3s should let a scanner understand the product by reading headings only.
   - Avoid vague headings such as "Powered by AI", "Why Choose Us", "Features", or "All-in-One Platform".
   - Use specific headings such as "Resolve WhatsApp, Email, and Instagram Tickets From One Inbox".

5. Structure the page according to the selected size:
   - Initial contact section: H1, short product definition, one primary CTA, and the most important visual or functional component.
   - Hero proof: place the strongest source-backed micro-proof or proof placeholder near the first CTA when it reduces purchase friction.
   - Centerpiece annotation: one clear product summary near the top.
   - Functional component: form, calculator, booking module, trial input, ROI estimator, product preview, ungated sandbox, selector, or equivalent task-completion block.
   - Structured attribute cards: one card or section per major feature, each with entity, attribute, and value.
   - Visual intent cues: include concise notes for screenshots, product GIFs, dashboards, charts, forms, buttons, report previews, or product states when they help designers pair copy with UI.
   - Proof section: testimonials, metrics, screenshots, case snippets, compliance facts, or benchmark data that support the big idea.
   - Objection handling: concise FAQ or comparison content focused on purchase friction.
   - Contextual bridge: specific internal proof links, not generic blog links.
   - Final CTA: repeat the same offer and destination as the first CTA.
   - Do not create article-length landing pages by default. Expand only when the user requests Full / Expanded or the source proves the offer needs deeper proof and objection handling.

6. Write the copy:
   - Start sentences with the entity and action when possible.
   - Use factual subject-predicate-object propositions.
   - Convert EAV facts into structured feature cards and proof blocks.
   - Replace vague claims with exact values when reliable values are provided.
   - Qualify broad categories with examples, types, integrations, limits, or technical details.
   - Use persuasive clarity, not hype. Avoid personal opinion, analogies, unsupported superlatives, and modal uncertainty.
   - Do not invent features, prices, metrics, integrations, guarantees, testimonials, compliance claims, awards, customer counts, health/legal/financial claims, or competitor facts.

7. Remove conversion distractions:
   - Do not add secondary CTA paths, newsletter prompts, unrelated downloads, pricing-plan choice grids, generic navigation, "learn more" exits, or competing offers unless the user explicitly requires them.
   - If a secondary on-page control is necessary, make it support the same CTA path, such as scrolling to the demo form or opening the same booking module.
   - Keep CTAs consistent in action and destination.

8. Select output mode:
   - Landing-page brief: use for strategic planning before copy.
   - Headline wireframe: use for page architecture and scan path.
   - Section copy: use for ready-to-place page content.
   - Semantic HTML outline: use when the user needs developer-ready structure.
   - CRO audit: use when reviewing an existing page or draft.

9. Run the silent audit before final output:
   - Confirm the selected size matches the user request or defaults to Medium / Standard.
   - Confirm only useful landing-page parts are included and article-style filler is removed.
   - Confirm CTA friction matches the source. Low-cost, self-serve, downloadable, or addon offers should not be forced into demo forms.
   - Confirm gated forms are used only when the source or offer needs sales qualification. Prefer ungated preview, download, purchase, trial, or open calculator when commitment should stay low.
   - Confirm exactly one big idea, one acquisition offer, and one CTA destination.
   - Confirm the page is understandable from headlines alone.
   - Confirm the product/category definition appears near the top.
   - Confirm the functional component matches the visitor's commercial intent.
   - Confirm every major feature is isolated into a structured card or clear section.
   - Confirm proof and FAQs reinforce the big idea instead of adding new angles.
   - Confirm no unsupported metrics, testimonials, prices, or claims were invented.
   - Confirm no generic anchors, vague headings, modal uncertainty, hype, or unrelated exits remain.
   - Do not print the audit unless the user asks for it.
   - Do not mention internal rules, audits, frameworks, rulebooks, validation files, or content processes in final landing-page copy unless the user asks.

## Output Rules

Default to clean Markdown unless the user asks for HTML, a CMS block, or another format.

When the user asks for raw HTML, output raw HTML only:

- The first character must be `<`.
- The last character must be `>`.
- Do not use Markdown fences.
- Use semantic sections, one primary CTA class, labeled feature cards, descriptive image captions, and accessible form labels.
- Delete any leading Markdown fence, language label, blank line, or explanation before the first `<`.
- Delete any trailing fence, backticks, blank line, or explanation after the final `>`.
- If the first character is not `<`, the last character is not `>`, or any ``` remains, revise before responding.

When facts are missing, use concise placeholders such as `[proof metric needed]` or ask one targeted question if the missing fact blocks the work.

## References

- `references/landing-page-rulebook.md`: LP/CRO compact v2.1 rules for factual, entity-led, conversion-focused page content with source analysis, size routing, and section selection.
- `references/lp-templates.md`: reusable templates for source analysis, size routing, briefs, headline wireframes, section copy, feature cards, functional components, and audits.
