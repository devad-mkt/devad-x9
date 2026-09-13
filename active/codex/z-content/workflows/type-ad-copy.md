# Workflow: Ad Copy & Paid Campaigns — compact

Handles Google RSA, Meta/Facebook/Instagram ads, LinkedIn sponsored content, TikTok ads, X promoted posts, and PPC. Load `SKILL.md` first; load the conversion reference for emotional or cause-driven campaigns.

## Platform detection and source gate

Route the prompt to the matching platform:

| Signal | Platform |
|---|---|
| Google Ads, RSA, search, PPC | Google |
| Meta, Facebook, Instagram feed | Meta |
| LinkedIn, sponsored, lead gen, B2B | LinkedIn |
| TikTok, in-feed, Spark | TikTok |
| X, Twitter, promoted tweet | X |
| Generic ad request | Google + Meta + LinkedIn core trio |

When a landing page or source is supplied, extract 10–15 exact phrases first. Map product/keyword, metric, emotional, pain-point, and CTA phrases to assets. Trace each headline and description to a source line internally; strip traces from final output. Never invent a claim or paraphrase a usable source phrase.

## Five angles

Use distinct variations, not five rewrites of one line:

1. Keyword/category match.
2. EAV or numeric proof.
3. Specific pain-point resolution.
4. Feature, integration, or technical specification.
5. Direct imperative CTA.

For charity or campaigns, use source-supported generosity, continuing benefit, personal connection, trust/impact, and empathy/urgency angles. Do not promise individual outcomes or spiritual rewards without authority.

## Limits and output

Count spaces and tag every asset `[XX/Limit]`.

| Platform | Hard limits | Safe target / fold |
|---|---|---|
| Google RSA | headline 30; description 90; paths 15 each | 25–28; 75–85; paths 10–12 |
| Meta | primary 2,200; headline 255; description 255 | hook 100–120; headline 30–35; description 20–30 |
| LinkedIn | intro 600; headline 200; description 300 | hook 130–140; headline 50–70; description 70–100 |
| TikTok | caption 100; CTA 30 | 60–80; CTA 20–25 |
| X | post 280; card title 70; card description 200 | post 200–260; title 50–60; description 120–150 |

Required packages:

- **Google:** 5–15 headlines, 3–4 descriptions, two display paths.
- **Meta:** primary hook, headline, optional description, and supported CTA button.
- **LinkedIn:** complete professional intro, headline, and optional description.
- **TikTok:** outcome-led caption plus CTA.
- **X:** one standalone post or 3–5 standalone thread posts; URL counts as 23 characters.

## Guardrails

- Use source facts, exact numbers, verified trust signals, and one clear CTA.
- Use SVO and active imperative CTA verbs: Deploy, Integrate, Compare, Start, Get, Give, Donate, or Support.
- Remove unsupported modal verbs, vague hype, filler, fabricated urgency, testimonials, guarantees, and outcomes.
- Put the primary keyword in Google headline 1. End descriptions with an action prompt.
- Match CTA grammar and context to the offer. Do not use noun-only or mismatched relief CTAs.
- Keep charity headlines as cause → action → supported outcome, not generic transactions.

## QA

Check character limits/tags, five distinct angles, three source-traced headlines when a source exists, source-language descriptions, zero hype/modality/filler, capitalized headlines, EAV coverage in at least half of headlines, and a valid CTA on every package.
