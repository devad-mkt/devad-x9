# Devad LP/CRO Compact Rules v2.1

Use this grouped framework for landing-page content, product pages, sales pages, signup pages, demo-booking pages, lead-capture pages, paid-campaign pages, and conversion-rate optimization audits. The goal is factual, entity-led, conversion-focused page content that gives one visitor segment one clear reason to act.

This file is the active LP/CRO rulebook. It is compact, but it is not a short summary. Preserve the meaning of each rule group. v2.1 adds a source analysis, page-size router, and section-selection gate so landing-page copy does not become article-length by default. Use `lp-templates.md` only when a reusable source analysis, size router, brief, wireframe, section-copy, feature-card, HTML, or audit format is useful.

## Priority Stack

Apply this order when rules conflict:

1. Follow the user's explicit product facts, offer, audience, traffic source, constraints, and requested format.
2. Keep the page landing-page specific. Route blog articles, scraped article cleanup, article refreshes, and long informational guides to `devad-articles`.
3. Use one big idea, one acquisition offer, and one primary CTA path unless the user explicitly asks for a comparison or multi-offer page.
4. Never invent product features, prices, discounts, guarantees, metrics, testimonials, customer counts, awards, compliance claims, integrations, competitor claims, health claims, legal claims, or financial outcomes.
5. Use exact values only from source text, user data, product data, or verified research.
6. Put commercial intent near the top: product definition, concrete outcome, primary CTA, and functional component or product visual.
7. Match CTA friction to the source-defined offer, price, purchase model, and visitor commitment.
8. Select Short / Compact, Medium / Standard, or Full / Expanded before drafting. Default to Medium / Standard when the user does not specify size.
9. Use only the landing-page parts supported by the source, offer, audience, and conversion goal.
10. Use structured cards, proof blocks, FAQs, CTAs, and visual intent cues to support the same conversion message.
11. Remove distractions that compete with the primary CTA.
12. Do not mention internal rules, audits, frameworks, rulebooks, validation files, or content processes in final landing-page copy unless the user asks.

Critical failures:

- Page has multiple unrelated big ideas or CTA destinations.
- Hero does not define product, audience, outcome, mechanism, or offer.
- Page reads like an article instead of a conversion path.
- Functional component is missing when visitor intent requires action.
- CTA friction is wrong for the offer, such as forcing a cheap self-serve addon into a sales demo form.
- Proof, testimonials, metrics, pricing, comparisons, or guarantees are invented.
- Product capabilities are inferred from a name instead of provided facts.
- Secondary navigation, blog links, social links, or unrelated offers distract from conversion.
- Default production copy becomes an article, guide, market overview, or full educational essay.
- The output includes every template section instead of selected landing-page parts.
- Raw HTML is wrapped in Markdown fences, labels, preambles, postambles, or backticks.

## P1 Landing-Page Intent Map

Covers: source context, commercial purpose, central entity, visitor intent, traffic source, one big idea, acquisition offer, CTA destination, proof, objections, page-vs-segment decision.

Rules:

- Define the commercial purpose before writing: what this page sells, captures, schedules, qualifies, downloads, or starts.
- Define the central entity as the product, service, feature, audience-specific offer, campaign asset, or conversion flow.
- Define the target visitor and traffic source. Paid ad visitors, organic search visitors, email-click visitors, referral visitors, and returning users need different proof and friction handling.
- Define the visitor's primary verb-noun goal: book demo, start trial, request quote, order product, estimate cost, compare plans, validate fit, download asset, or create account.
- Define one big idea that connects audience, outcome, and mechanism in a memorable phrase.
- Define one acquisition offer: what the visitor gets after clicking the CTA.
- Define one CTA destination: same form, same scheduler, same checkout, same signup, same download, or same on-page module.
- Define proof assets before writing: screenshots, metrics, testimonials, customer logos, compliance facts, review counts, case snippets, benchmarks, or product constraints.
- Decide page versus segment. Create a standalone page only when the product, offer, audience, feature, or campaign has independent search demand or acquisition value.

Do not:

- Do not create a landing page for a minor feature that belongs as an H2/H3 segment on a parent page.
- Do not mix unrelated products, personas, offers, or CTAs to make the page feel larger.
- Do not use a generic company homepage structure for a single-offer landing page.
- Do not start with market history, broad education, or a long problem essay.
- Do not invent missing audience, proof, pricing, guarantee, or competitor details.

Bad:

"A complete platform for teams that want better workflows, more productivity, stronger marketing, easier operations, and smarter growth."

Good:

"A social analytics landing page for agencies that need one dashboard to compare Facebook, Instagram, TikTok, YouTube, and LinkedIn performance before sending client reports."

Why the good version works:

- Entity: social analytics dashboard.
- Audience: agencies.
- Outcome: compare platform performance and send client reports.
- Mechanism: one dashboard.
- CTA path can be demo, trial, or report preview.

## P2 Source Analysis, Size Router, And Section Selection

Covers: source-to-landing-page conversion, Short / Compact pages, Medium / Standard pages, Full / Expanded pages, default size, recommended LP parts, awareness level, section budget, source preservation without article drift.

Rules:

- When source content is provided, analyze it before writing. Identify the product or service entity, audience, traffic source, conversion goal, source-backed facts, proof assets, objections, missing facts, CTA path, strongest commercial attributes, and awareness level.
- Unless the user asks for raw HTML, CMS blocks, or final copy only, show a short public setup before the draft:
  - `Source Analysis`: entity, audience, goal, proof available, missing facts, and awareness level.
  - `Recommended LP Parts`: selected size, included sections, excluded sections, functional component, CTA path, and reason for the selection.
- If the user asks for final copy only, run the analysis silently and output only the requested copy.
- If the user asks for raw HTML, output raw HTML only. Do not prepend source analysis, recommendations, labels, or Markdown.
- Choose one of three sizes before drafting:
  - Short / Compact: use for simple signup pages, lead magnets, one-feature campaign pages, direct ecommerce offers, or low-friction traffic. Typical output: 400-700 words, 5-7 sections.
  - Medium / Standard: default when the user does not specify size. Use for most SaaS, service, product, demo-booking, lead-capture, or campaign landing pages. Typical output: 800-1,300 words, 7-9 sections.
  - Full / Expanded: use only when requested or when the offer is complex enough to require deeper proof, security, implementation, comparison, regulated-claim caution, or enterprise objection handling. Typical output: 1,500-2,500 words, 9-12 sections.
- Treat size ranges as guardrails, not filler targets. A complete Medium page can be shorter if the source has limited proof.
- Do not escalate to Full / Expanded because the source is long, because SEO is mentioned, or because many templates exist.
- Select parts using the source and commercial goal. Possible parts include hero, product definition, functional component, feature cards, proof, comparison, use cases, risk reducers, FAQ, contextual bridge, and final CTA.
- Use awareness level to choose flow:
  - Most aware: lead with offer, price, proof, CTA, and risk reducer.
  - Product aware: lead with differentiator, mechanism, proof, comparison, and CTA.
  - Solution aware: lead with outcome, use case, feature cards, proof, and CTA.
  - Problem aware: use a short problem-to-solution bridge, then product, mechanism, proof, and CTA.
  - Cold traffic: add limited context, but do not create a broad article.
- Use PAS or AIDA as an invisible flow choice, not as visible labels. PAS fits problem-aware traffic. AIDA fits colder traffic. Most-aware visitors usually need direct offer architecture.
- Convert long article sources into landing-page inputs: extract the offer, proof, objections, use cases, and EAV facts; do not preserve the article's essay structure unless the user asks for article content.

Do not:

- Do not create article-length landing pages by default.
- Do not convert the whole source article into a landing-page article.
- Do not include every available template section to appear comprehensive.
- Do not mix unrelated topics, products, personas, or benefits to increase length.
- Do not add long market history, broad education, generic "why this matters" essays, or SEO filler.
- Do not use CRO test hypotheses inside production copy unless the user asks for CRO recommendations.
- Do not invent proof to justify a larger page.
- Do not hide missing proof; use precise placeholders.

Bad:

"The source article is 4,000 words, so the landing page should include the complete market problem, every platform section, a full guide to analytics, pricing comparisons, FAQs, case studies, and CRO tests."

Good:

Source Analysis:

- Entity: social analytics dashboard.
- Audience: agencies and marketers managing multiple social channels.
- Goal: get the analytics addon, download the module, or preview the reporting workflow.
- Proof available: supported channels, white-label PDF reports, post history metrics, yearly cost note, and profile/support comparison table.
- Missing facts: verified customer quote and demo destination.
- Awareness level: solution aware.

Recommended LP Parts:

- Size: Medium / Standard.
- Include: hero, product definition, dashboard preview, channel/reporting cards, comparison table, proof placeholder, 5-question FAQ, and final low-friction CTA.
- Exclude: long platform-by-platform education, market history, CRO hypotheses, and unrelated blog-style guide sections.

## P3 One Big Idea, Offer, And CTA Path

Covers: message discipline, one offer, CTA consistency, conversion path, distraction removal, page memory.

Rules:

- Choose one big idea and repeat it across H1, subheadline, visual annotation, feature cards, proof, FAQ, and CTA.
- If the traffic source is provided, keep message match across ad promise, email promise, search intent, hero headline, subheadline, and CTA. The visitor should feel they landed on the exact promised offer.
- Choose one acquisition offer. Examples: book a demo, start a trial, request a quote, order now, get an audit, create an account, download the promised asset.
- Use one CTA destination. CTAs can appear multiple times, but they should point to the same action or the same on-page module.
- CTA copy must name the action and expected result. Examples: `Get the addon`, `Download the module`, `Start the free trial`, `Get the audit`, `Estimate my cost`, `Order now`, `Book a demo`.
- Match CTA friction to buying context:
  - Low-cost, self-serve, addon, template, plugin, download, or simple ecommerce offers should use direct action CTAs such as `Get the addon`, `Download the module`, `Install the plugin`, `Start using it`, or `Order now`.
  - Trial-led SaaS should use `Start the free trial`, `Create account`, or `Try the workflow`.
  - Quote-led services should use `Request a quote`, `Estimate my cost`, or `Send project details`.
  - Sales-led, enterprise, regulated, custom, or high-price offers can use `Book a demo`, `Talk to sales`, or `Schedule a consultation`.
- If a secondary control is necessary, make it support the same path, such as scrolling to the form, opening the same scheduler, or previewing the same calculator.
- Use CTA-adjacent microcopy to reduce risk: time commitment, no credit card, response time, what happens next, cancellation, security, or delivery expectation.
- Place the strongest source-backed micro-proof directly near the first CTA when it reduces hesitation. If the proof is strong but not verified, use a precise placeholder instead of hiding it lower on the page.

Do not:

- Do not place newsletter signup beside demo booking unless the user explicitly asks for a newsletter landing page.
- Do not use "Learn more" as a primary CTA on a high-intent landing page.
- Do not use low-value primary CTA copy such as "Submit", "Continue", "Click here", or "More info" when a value-led action is possible.
- Do not default to `Book a demo` for low-cost, self-serve, downloadable, addon, or simple purchase offers.
- Do not gate a preview behind email capture when the offer should feel low-risk and self-serve.
- Do not add pricing-plan choice grids as the main decision when the page goal is demo booking or lead capture.
- Do not add broad navigation, social icons, unrelated product links, generic blog links, or footer menus in the main conversion flow.
- Do not introduce a new CTA in the final section.
- Do not use fake scarcity, fake countdowns, fake limited seats, or unsupported urgency.

Bad:

Hero CTA: "Start trial." Mid-page CTA: "Read our blog." Final CTA: "Join newsletter." Footer CTA: "Follow us on social."

Good:

Hero CTA: "Book a 20-minute demo." Mid-page CTA: "See the demo workflow." Final CTA: "Book a 20-minute demo."

Good low-friction CTA:

Hero CTA: "Get the Analytics Addon - $59/yr." Micro-proof: "Agencies report saving an average of 5 hours per client per month [source proof needed]." Mid-page CTA: "Preview the report workflow." Final CTA: "Get the Analytics Addon - $59/yr."

## P4 Hero, Initial Contact, And Headline Path

Covers: above-the-fold clarity, headline specificity, product definition, scanner readability, first proof cue, visual or component placement.

Rules:

- Write the headline path before body copy. A scanner should understand product, audience, outcome, mechanism, and offer by reading only H1, H2, H3, button text, and card labels.
- H1 should combine a concrete outcome, audience, and mechanism when the facts are available.
- Prefer clear value proposition architecture over cleverness. A strong H1 names the outcome or offer in a short, memorable phrase; supporting copy can carry the extra detail.
- Put the product/category definition near the top: `[Product] is a [category] for [audience] that [achieves outcome] through [mechanism].`
- The initial contact section should include H1, short definition, primary CTA, functional component or annotated product visual, and one proof cue if available.
- Hero micro-proof should sit close to the first CTA when it supports the conversion decision. Use a short proof line, review count, price cue, delivery promise, or precise placeholder.
- The strongest commercial attribute should appear early. This may be price, speed, integration coverage, time savings, compliance, channel coverage, report quality, setup time, free trial, demo booking, or a verified result metric.
- Use specific headings. Each H2 should advance the conversion story: problem, mechanism, component, feature group, proof, objections, bridge, final CTA.
- Use page copy that helps selection, not just education. Commercial visitors need enough clarity to act.

Do not:

- Do not use vague H1s such as "Grow faster", "All-in-one solution", "Powered by AI", "Work smarter", or "The future of productivity" without a concrete entity and mechanism.
- Do not hide the product definition below proof, company history, or generic problem copy.
- Do not lead with a stock-style hero image unless it directly shows the product, result, component, or user task.
- Do not make the first screen a blog introduction.

Bad:

"Grow your business with smarter insights."

Good:

"Compare every client social channel from one analytics dashboard."

Good product definition:

"The analytics module is a social reporting dashboard for agencies that centralizes Facebook, Instagram, TikTok, YouTube, and LinkedIn metrics in one workspace."

## P5 Functional Goal Component

Covers: calculator, scheduler, signup, form, checkout, product preview, comparison selector, diagnostic, quote form, demo module, action completion.

Rules:

- Match the page's functional component to visitor intent.
- If the visitor wants cost clarity, include calculator, estimator, quote form, or pricing selector copy.
- If the visitor wants sales validation, include demo scheduler, demo request form, workflow preview, or qualification form copy.
- If the visitor wants to try the product, include signup form, sandbox input, product preview, or first-action prompt.
- If the visitor wants to preview a low-cost or self-serve product, prefer an ungated preview, toggle, slider, mock workflow, sample report, open calculator, or screenshot carousel before asking for contact details.
- If the visitor wants to compare, include comparison table, selector, checklist, or plan recommender.
- If the visitor wants fit validation, include diagnostic quiz, use-case selector, checklist, or requirements form.
- Explain what the component does and what happens after the visitor uses it.
- Keep form labels concrete and accessible. Ask only for fields needed for the conversion.
- For preview, estimator, calculator, and sandbox components, include a compact input/output table when the source supports it.

Do not:

- Do not write only explanatory copy when the visitor needs to calculate, book, try, compare, request, order, or validate.
- Do not add a component that creates a different offer from the primary CTA.
- Do not ask for excessive form fields without a qualification reason.
- Do not require work email, phone number, or sales qualification for a preview when the source points to a low-cost self-serve offer.
- Do not imply instant results if the component actually triggers manual follow-up.

Good component copy:

"Choose your monthly reporting volume to estimate how many client reports your team can prepare from one dashboard."

Good ungated preview component:

| Visitor Input | Immediate Output |
|---|---|
| Agency workflow | Sample white-label PDF report preview |
| Managed channels | Dashboard tabs for Facebook, Instagram, TikTok, YouTube, and LinkedIn |
| Reporting frequency | Suggested monthly reporting view |

Good form microcopy:

"After you submit the form, the team sends a demo time and a sample reporting workflow for your selected channels."

## P6 Structured Attribute Cards And EAV Density

Covers: feature cards, modules, entity-attribute-value facts, unique attributes, broad category qualification, proof-card structure, card labels.

Rules:

- Convert major product facts into isolated cards or sections.
- Each card needs an entity, attribute, and value. The value can be a channel, metric, integration, workflow, limit, use case, proof point, constraint, or verified outcome.
- Translate features into buyer-visible benefits with this chain: source feature -> mechanism -> practical outcome. Keep the source feature visible so the benefit does not become an unsupported claim.
- Use specific card labels. Labels should identify the capability, not a generic benefit.
- Use a scannable entity matrix when the source contains many comparable entities, platforms, integrations, metrics, products, or use cases. Keep the persuasive sentence short, then show the extraction-friendly list or table.
- Prioritize unique commercial attributes over root attributes when the source supports them. Root attributes include price, speed, and ease. Unique attributes include exact integrations, reporting exports, workflow limits, compliance details, or niche use cases.
- Qualify broad categories immediately. If you mention channels, integrations, reports, automations, roles, or metrics, name them.
- Use feature cards for modules, integrations, use cases, steps, outcomes, constraints, and differentiators.
- Use tables when comparison is central to selection.

Do not:

- Do not put five unrelated features into one paragraph.
- Do not make cards with vague labels such as "Powerful", "Simple", "Smart", or "Flexible".
- Do not use EAV structure to invent missing values.
- Do not exaggerate a feature into an absolute benefit. For example, do not turn "256-bit encryption" into "your data is unhackable"; use a source-safe benefit such as "data is encrypted in transit and at rest" only when that exact fact is provided or verified.
- Do not claim a differentiator unless the source or verified research supports it.
- Do not bury product constraints; constraints can increase trust when stated clearly.

Bad:

"The tool has strong analytics and helpful reporting for every platform."

Good:

| Card | Entity | Attribute | Value |
| --- | --- | --- | --- |
| Channel Dashboard | Analytics module | Channel coverage | Facebook, Instagram, TikTok, YouTube, and LinkedIn |
| PDF Reporting | Reporting module | Export format | White-label PDF report |
| Post History | Content table | Row-level metrics | Views, reach, reactions, comments, shares, and engagement rate |

Good scannable entity matrix:

| Platform | Key Metrics From Source | Visitor Decision |
|---|---|---|
| YouTube | Views, watch duration, subscribers, traffic source | Identify videos that retain viewers |
| Instagram | Reach, views, interactions, saves | Identify content worth repeating |
| LinkedIn | Page views, clicks, followers, engagement | Measure professional audience response |

## P7 Visual And Annotational Semantics

Covers: screenshot captions, component annotations, visual-text alignment, product preview, charts, forms, calculators, buttons, semantic HTML structure.

Rules:

- Text near a visual must explain exactly what the visual, button, chart, form, calculator, or screenshot lets the visitor see or do.
- Add a `Visual Intent:` cue under major sections when the output is meant to guide design, developer handoff, page building, or content placement. Keep it concise and tied to a real product state.
- Caption product visuals with entity, action, and value.
- Place visual annotations next to the component they describe, not far below the page.
- For dashboards, name the data shown and the visitor decision it supports.
- For forms, state what the visitor receives after submission.
- For calculators, name the input and output.
- For comparison tables, state the decision criteria.
- For screenshots, identify the workflow or product state visible in the screenshot.

Do not:

- Do not use decorative visuals as proof.
- Do not caption a dashboard with vague copy such as "Work smarter."
- Do not describe one feature next to an unrelated image or component.
- Do not rely on icons alone to explain a feature.
- Do not show a product visual without nearby explanatory text.
- Do not leave designers guessing which screenshot, chart, GIF, report preview, button, or UI state should support the copy.

Bad:

"Screenshot caption: Everything you need in one place."

Good:

"Screenshot caption: The dashboard compares Facebook reach, Instagram interactions, TikTok views, YouTube watch time, and LinkedIn clicks in one reporting workspace."

Good visual intent cue:

Visual Intent: Insert a 3-second looping product GIF showing the user selecting a client, clicking `Export`, and seeing a white-label PDF report preview.

## P8 Proof, Trust, And Claim Safety

Covers: testimonials, metrics, screenshots, review counts, customer logos, case snippets, security, compliance, benchmarks, risk reducers, proof placement.

Rules:

- Place proof near the claim it supports.
- Place micro-proof near the first high-friction moment: hero CTA, price, signup button, checkout, quote form, demo scheduler, or download action.
- Use proof that repeats the big idea instead of adding a new angle.
- Use exact proof only when provided or verified: metrics, review counts, customer names, customer logos, certifications, awards, compliance, pricing, guarantees, uptime, security, or before/after results.
- If proof is missing, use placeholders such as `[proof metric needed]`, `[customer quote needed]`, `[screenshot needed]`, or `[security claim needs verification]`.
- Use risk reducers that match the offer: no credit card, response time, cancellation, onboarding support, setup requirement, refund policy, data handling, or delivery expectation.
- Use formal, factual, restrained persuasion. Benefits should be tied to attributes, proof, or clear use cases.
- For regulated categories, use only verified claims and add source placeholders where needed.

Do not:

- Do not invent testimonials, customer logos, review counts, clinical claims, revenue results, security certifications, or compliance badges.
- Do not say "trusted by thousands", "proven to double conversions", or "guaranteed results" without proof.
- Do not place proof far away from the claim it supports.
- Do not move the strongest purchase-reducing proof to the bottom when it directly supports the first CTA.
- Do not make unsupported competitor comparisons.
- Do not use emotional pressure as proof.

Bad:

"Trusted by thousands of agencies to save 10 hours every week."

Good:

"[Agency customer quote needed] should support the claim that unified reporting reduces manual report preparation."

## P9 Objection Handling, FAQ, And Conversion Friction

Covers: purchase friction, objections, risk, implementation, compatibility, pricing, time, support, migration, alternatives, FAQ direct answers.

Rules:

- Use FAQ to resolve conversion friction, not to add generic informational filler.
- Write objection questions from the buyer's perspective.
- Answer directly in the first sentence, then add conditions or detail.
- Prioritize objections that block action: cost, setup time, required access, integrations, migration, data accuracy, security, support, cancellation, results, qualification, and what happens after CTA.
- Use comparison content only when compared attributes are specific and supportable.
- Keep answers factual and concise.
- Include missing proof placeholders where a claim needs support.

Do not:

- Do not use FAQ to repeat marketing claims.
- Do not answer compatibility questions with unsupported "yes" claims.
- Do not hide pricing limitations, setup requirements, or data access constraints.
- Do not attack competitors.
- Do not introduce a second CTA path inside FAQ answers.

Good FAQ:

"Does the dashboard replace native platform analytics?"

"The dashboard centralizes selected metrics for cross-platform reporting, while native tools may still be needed for platform-specific configuration and campaign setup."

## P10 Contextual Bridge, Page Length, And SEO/CRO Balance

Covers: commercial-to-informational proof bridge, anchor text, page length, scan path, content density, page versus segment, search intent without article drift.

Rules:

- Add bottom proof links only when they strengthen the commercial page.
- Use anchor text that names the proof topic or destination entity.
- Link to guides, benchmarks, case studies, documentation, comparisons, or calculators that support the page's commercial claims.
- Keep page length proportional to commercial complexity. Simple signup pages can be short. Enterprise pages need proof, objections, security, use cases, and implementation detail.
- Use educational definitions only when they support selection or reduce uncertainty.
- Keep minor product attributes as page segments unless they have independent conversion value.
- Use SEO structure to clarify the offer, not to turn the page into an article.

Do not:

- Do not use generic anchors such as "read more", "learn more", "our blog", or "click here".
- Do not add broad informational sections that do not support the CTA.
- Do not create thin landing pages for every integration, feature, setting, or keyword variation.
- Do not make the page longer because "SEO needs more words."

Bad bridge:

"Read our blog for more tips."

Good bridge:

"Read the social reporting workflow guide to compare which metrics agencies should include in monthly client reports."

## P11 Output Modes And Format Gates

Covers: landing-page brief, headline wireframe, section copy, semantic HTML outline, CRO audit, raw HTML, placeholders, missing facts.

Rules:

- Default to clean Markdown unless the user requests raw HTML, CMS blocks, or a specific structure.
- For strategy requests, output a landing-page brief: product, audience, traffic source, big idea, offer, CTA, functional component, proof assets, objections, page-vs-segment decision, and missing facts.
- For architecture requests, output a headline wireframe with H1, H2/H3 scan path, CTA placements, proof placements, and component placement.
- For production copy, output ready-to-place sections: hero, product summary, component, feature cards, proof, FAQ, bridge, and final CTA.
- For developer handoff, output semantic HTML with `<main>`, `<section>`, headings, one primary CTA class, feature-card labels, captions, and accessible form labels.
- For audits, output findings, priority, conversion impact, rule violated, and replacement copy or test idea.
- Use concise placeholders when facts are missing and do not block the work. Ask one targeted question when a missing fact blocks the task.
- For raw HTML, first character must be `<` and last character must be `>`.
- For raw HTML, output only HTML. No Markdown fences, backticks, labels, preambles, postambles, or whitespace outside the HTML.
- If a raw HTML draft contains ``` or text before the first HTML tag, remove the wrapper before final output.

Do not:

- Do not print the audit unless requested.
- Do not include internal reasoning in final copy.
- Do not leave vague placeholders when a precise placeholder is possible.
- Do not wrap raw HTML in ```html.

## P12 CRO Test Hypotheses

Covers: conversion-rate enhancement, test ideas, measurable variants, prioritization, ethical testing, no guaranteed lifts.

Rules:

- Treat CRO recommendations as hypotheses, not guaranteed improvements.
- Connect each test to a conversion problem: unclear value, weak message match, missing proof, CTA friction, form friction, visual ambiguity, objection gap, or trust gap.
- Provide specific variants. Example: outcome-led H1 versus product-category H1.
- Prioritize tests by expected impact and implementation effort.
- Define the conversion event: demo booked, trial started, quote requested, order submitted, form completed, asset downloaded, or checkout started.
- Suggest measurement notes when useful: traffic segment, primary metric, secondary metric, minimum runtime, or sample-size caution.
- Keep tests aligned with the one big idea and one CTA path.

Do not:

- Do not guarantee conversion lifts.
- Do not suggest manipulative urgency, dark patterns, hidden fees, prechecked consent, or misleading claims.
- Do not test multiple unrelated changes as one variant unless the user asks for a full-page concept test.

Good CRO test:

"Test an H1 that names the reporting outcome against an H1 that names the product category. Primary metric: demo form starts. Secondary metric: form completion rate."

## P13 Silent Audit And Final Gate

Run this audit silently before final output:

- Intent: The output is a landing page, sales page, product page, lead-capture page, campaign page, or CRO audit, not an article.
- Source analysis: Source-backed facts, proof, objections, missing facts, and awareness level were considered before drafting when source content was provided.
- Size: Short / Compact, Medium / Standard, or Full / Expanded was selected before drafting; undeclared size defaults to Medium / Standard.
- Parts: The output includes only useful landing-page parts and does not include every template section by default.
- Length: The output matches the selected size and does not become article-length unless Full / Expanded was requested or justified by source complexity.
- One big idea: The same message appears in hero, feature cards, proof, FAQ, and CTA.
- One offer: The page asks for one conversion decision.
- One CTA path: Every CTA points to the same destination or same on-page module.
- CTA friction: The CTA matches the source's price, purchase model, and commitment level; self-serve offers use self-serve CTAs unless the user asks otherwise.
- Hero: H1, product definition, primary CTA, proof cue, and functional component or annotated visual appear near the top when relevant.
- Hero proof: Source-backed micro-proof or a precise proof placeholder appears near the first CTA when it reduces friction.
- Functional component: The component matches visitor intent and explains what happens after use.
- Gating: Preview, calculator, sample report, sandbox, or selector components are ungated unless the source or sales model requires qualification.
- Structured cards: Major product facts are isolated into entity-attribute-value cards or sections.
- Scannability: Dense platform, metric, integration, or feature groups use bullets, tables, or entity matrices instead of long paragraphs.
- Visual annotations: Screenshots, forms, calculators, tables, and buttons have nearby explanatory copy.
- Visual intent: Design-facing outputs include concise visual intent cues for key product states, screenshots, GIFs, dashboards, reports, charts, buttons, or forms.
- Proof: Metrics, testimonials, prices, guarantees, compliance, awards, and comparisons are sourced, provided, verified, or marked with placeholders.
- Objections: FAQ resolves purchase friction and does not introduce a second CTA.
- Contextual bridge: Bottom links use specific proof-topic anchor text.
- Factuality: No invented product facts, proof, pricing, testimonials, guarantees, competitor claims, or regulated claims.
- Distraction control: No unrelated exits, secondary offers, broad navigation, or generic resource links weaken the conversion path.
- Format: Requested Markdown, HTML, CMS, or audit format is followed exactly.
- Raw HTML: First character is `<`, last character is `>`, and no Markdown fences or wrapper text remain.
- Internal process: No audit, scorecard, rule list, validation note, or process explanation appears in final copy unless requested.

If a critical failure is found, fix it before final output. If missing data blocks the work, ask one targeted question or mark the missing fact with a precise placeholder.
