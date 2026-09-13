# Workflow: Ad Copy & Paid Campaigns

Handles: Google RSA, Meta (Facebook/Instagram) Ads, LinkedIn Sponsored Ads, TikTok Ads, X Promoted Ads, PPC campaign copy.

Load `SKILL.md` first. This file provides ad-platform-specific structure, character enforcement, and angle diversification rules.

---

## Platform Detection

Detect target platform from prompt keywords:

| Signal | Platform | Load Section |
|--------|----------|--------------|
| Google Ads, RSA, search ads, PPC, text ads | Google | Section 2A |
| Meta Ads, Facebook Ads, Instagram Ads, feed ads | Meta | Section 2B |
| LinkedIn Ads, sponsored content, lead gen, B2B ads | LinkedIn | Section 2C |
| TikTok Ads, in-feed ad, Spark Ads | TikTok | Section 2D |
| X Ads, Twitter Ads, promoted tweet | X/Twitter | Section 2E |
| Generic ("ad copy", "campaign copy", "write ads") | **Core Triad** | Sections 2A + 2B + 2C |

---

## 0. Source Extraction (When Landing Page Provided)

When a landing page URL or text is provided, execute this before generating any ad copy:

**Step 1 — Pull exact phrases from the source.** Extract 10–15 specific word-for-word phrases that describe the offer, product, or campaign. These become your raw material for headlines and descriptions. Never paraphrase when the source has a usable phrase.

**Step 2 — Map phrases to headlines.** Assign each extracted phrase to an angle:

| Headline Slot | Source | Rule |
|---------------|--------|------|
| H1 (Keyword Match) | Exact product/service name or primary keyword from source | Word-for-word from source |
| H2 (EAV/Metric) | Specific number, price, speed, or quantified claim from source | Word-for-word from source |
| H3 (Emotional/Story) | Emotional phrase from source body copy | Word-for-word or minimal trim to fit char limit |
| H4 (Pain-Point) | Problem statement from source | Paraphrase allowed if source doesn't have exact headline phrase |
| H5 (CTA) | Action phrase or directive from source | Word-for-word preferred |

**Step 3 — Map phrases to descriptions.** Descriptions must use the source's own words, reordered to fit character limits. No invented claims. No generic filler.

**Step 4 — Mark the trace.** After every headline and description, append `[Source: exact phrase or line reference]` in the internal draft (strip before final output).

---

## 1. Angle Diversification Engine

When generating ad variations, cover these 5 strategic angles. Never output 5 variations of the same sentence.

### Product / SaaS Angles (default)

| # | Angle | Description |
|---|-------|-------------|
| 1 | **Keyword/Category Match** | Direct reflection of high-intent search query or product category. |
| 2 | **EAV & Numeric Proof** | Concrete capability, price point, speed metric, or quantified outcome. |
| 3 | **Pain-Point Hook** | Immediate resolution of a specific operational friction. |
| 4 | **Feature/Integration Spec** | Exact tools, formats, platforms, or technical specs supported. |
| 5 | **Direct CTA** | Imperative command with zero ambiguity. |

### Cause-Driven / Charity Angles (use for nonprofits, campaigns, donation pages)

| # | Angle | Description |
|---|-------|-------------|
| 1 | **Call to Generosity** | Direct appeal to give — "Give the best charity", "Be a lifeline". |
| 2 | **Ongoing Reward (Sadaqah Jariyah)** | Emphasize lasting spiritual impact — "Start an ongoing Sadaqah", "Build your reward". |
| 3 | **Personal Connection** | Honor a loved one — "Gift a share in memory of your mother", "Give in honor of someone you love". |
| 4 | **Trust Signal + Impact** | Verify credibility — "Zakat verified", "$50 provides 1 family safe water for months". |
| 5 | **Empathy + Urgency** | Emotional appeal to suffering — "Quench thirsty souls", "End thirst". |

**Selection rule:** Detect context from the source. If the page mentions charity, donation, nonprofit, sadaqah, zakat, campaign → use cause-driven angles. Otherwise → use product angles.

### Wrong vs. Right

- **Wrong (Generic/Transactional):** "Clean Water Donation Online [27/30]"
- **Right (Emotional Storytelling):** "Give Water, Save a Life Today [28/30]"
- **Right (Cause-Driven):** "Be a Lifeline: Gift Water Today [29/30]"
- **Right (Product):** "Automate Ad Copy in 5 Mins [27/30]"

---

## 2. Platform Specifications & Layouts

### A. Google Search (Responsive Search Ads — RSA)

| Field | Hard Limit | Safe Target | Quantity |
|-------|-----------|-------------|----------|
| Headline | 30 chars | 25–28 chars | 5–15 |
| Description | 90 chars | 75–85 chars | 3–4 |
| Display Path | 15 chars each | 10–12 chars | 2 |

**Rules:**
- Append character count to every asset: `Headline Text [XX/30]`
- Front-load primary keyword in Headline 1.
- Every headline must start with a capital letter. No sentence fragments starting with "and", "or", "but".
- Descriptions must include at least one EAV triple and end with a CTA.

### B. Meta Ads (Facebook & Instagram Feed)

| Field | Hard Limit | Safe Target | Notes |
|-------|-----------|-------------|-------|
| Primary Text | 2,200 chars | 100–120 chars (hook fold) | Hook must complete before char 125 |
| Headline | 255 chars | 30–35 chars | Truncates at ~40 on mobile |
| Description | 255 chars | 20–30 chars | Only visible in Marketplace, Audience Network |
| CTA Button | — | Choose from: Learn More, Get Quote, Start Free Trial, Sign Up, Shop Now, Donate Now, Give Now | — |

**Rules:**
- Primary text hook must land in first 120 chars. Supporting copy can extend to 250 chars.
- Headline goes under image/creative. No ambiguity about what the user gets.
- Description is conditional — never put critical info here. Use primary text.
- Output with `[XX/125]` tag on primary text hook line.

### C. LinkedIn Sponsored Content

| Field | Hard Limit | Safe Target | Notes |
|-------|-----------|-------------|-------|
| Intro Text | 600 chars | 130–140 chars (mobile fold) | Truncates at ~140 mobile, ~210 desktop |
| Headline | 200 chars | 50–70 chars | Hard truncate — no rescue |
| Description | 300 chars | 70–100 chars | Only shows on Audience Network, right rail |

**Rules:**
- Tone: professional, analytical, B2B decision-focused. Zero consumer hype.
- Hook in first 140 chars must deliver complete value proposition.
- Use line breaks for readability. Short paragraphs (1–2 sentences each).

### D. TikTok In-Feed Ads

| Field | Hard Limit | Safe Target | Notes |
|-------|-----------|-------------|-------|
| Ad Caption | 100 chars | 60–80 chars | UI buttons overlay right edge |
| CTA Text | 30 chars | 20–25 chars | "Learn More", "Shop Now", etc. |

**Rules:**
- Caption supplements the video — never narrate what the video shows.
- Lead with the outcome or benefit, not the product name.

### E. X / Twitter Promoted Ads

| Field | Hard Limit | Safe Target | Notes |
|-------|-----------|-------------|-------|
| Tweet Text | 280 chars | 200–260 chars | Full display, no fold |
| Card Title | 70 chars | 50–60 chars | Truncates at ~50 on mobile |
| Card Description | 200 chars | 120–150 chars | Supporting context |

**Rules:**
- Single post or thread (3–5 tweets). Thread tweet 1 = hook + quantified promise.
- No hashtags in promoted tweets (wastes characters, reduces trust).
- URL counts as 23 chars (t.co shortening).

---

## 3. Ad Copy Guardrails

| Rule | Enforcement |
|------|-------------|
| Source fidelity (mandatory) | When a landing page or source document is provided, extract headlines and descriptions word-for-word from the source text. Never use generic paraphrases when the source has usable phrases. Every ad asset must trace back to a specific line in the source. |
| Zero modal verbs | No should, might, could, probably, we believe, arguably. |
| Zero vague hype | Forbidden: revolutionary, effortless, game-changing, best, seamless, world-class, cutting-edge, best-in-class. |
| Mandatory SVO & imperatives | CTA lines start with active verbs: Deploy, Integrate, Calculate, Compare, Automate, Start, Get, Try, Give, Donate, Support. |
| EAV in headlines | Every headline = [Entity/Offer] + [Attribute/Value] + [Constraint/Proof]. |
| Character compliance | Count spaces as 1 char. Never exceed hard limits. Use inline `[XX/Limit]` tags. |
| No invented facts | Numbers, prices, percentages, and stats only from user-provided data or verified research. |
| CTA grammar | CTAs must be grammatically complete. No "Help Us Providing" → "Help Us Provide". No "Send a Clean Water" → "Send Clean Water". No noun-only CTAs ("Your Sadaqah Jariyah" → "Give Your Sadaqah Jariyah"). |
| CTA-context match | CTAs must match the content type. "Send Emergency Relief" is wrong for water donation projects. Use "Donate Now", "Give Water Now", "Support the Water Project". |
| Emotional storytelling | For charity/campaign copy: headlines must tell a micro-story (cause → action → outcome). Never output generic transactional headlines for emotional causes. |
| Trust signals | Include verification badges (Zakat Verified, Tax-Deductible, Registered Nonprofit) when source provides them. |

---

## 4. Output Templates

### Google RSA Package

```
Path 1: /software
Path 2: /features

HEADLINES:
H1 (Keyword): No-Code Landing Page Builder [29/30]
H2 (EAV): Deploys in Under 5 Minutes [27/30]
H3 (Pain-Point): Stop Coding Web Pages [22/30]
H4 (Spec): Includes Stripe Payments [24/30]
H5 (CTA): Start Your Free Trial Now [26/30]

DESCRIPTIONS:
D1: Build mobile-responsive ecommerce sites with 50+ templates. No coding needed. [79/90]
D2: Integrate Stripe, automate technical SEO metadata, and launch today. Try free. [81/90]
D3: Join 2,400+ stores built with our platform. 14-day free trial, no card required. [83/90]
```

### Meta Feed Ad Package

```
PRIMARY TEXT (Hook + Body):
Reduce average ticket resolution time by 35% with a unified customer service inbox. Centralize chat, email, and WhatsApp into one dashboard. [132/125]

HEADLINE: Unified Inbox for Support Teams [31/35]
DESCRIPTION: Rated 4.8/5 on G2 across 1,200 reviews [38/40]
CTA BUTTON: Start Free Trial
```

### LinkedIn Sponsored Ad Package

```
INTRO TEXT:
Support teams handle 40% more tickets when chat, email, and WhatsApp route through a single inbox. Our platform centralizes multi-channel messages and cuts average response time from 4 hours to 12 minutes. [196/140]

HEADLINE: Multi-Channel Support Platform — 12-Min Avg Response [56/70]
DESCRIPTION: 98% uptime SLA. SOC 2 Type II certified. [46/100]
```

### Charity/Campaign Google RSA Package (Cause-Driven Example)

```
Path 1: /water-donation
Path 2: /give-life

HEADLINES:
H1 (Generosity): Give the Best Charity Today [25/30]
H2 (Ongoing Reward): Start Water Sadaqah Jariyah [26/30]
H3 (Personal): Gift Water in a Loved One's Name [28/30]
H4 (Trust): Zakat Verified Water Project [28/30]
H5 (CTA): Donate Clean Water Now [24/30]

DESCRIPTIONS:
D1: Give clean water to families in need. $50 provides one family safe drinking water for months. [87/90]
D2: Your water donation is ongoing charity. Every drop delivers reward. Donate through Elvefa today. [89/90]
D3: Sadaqah Jariyah in water. Help vulnerable families access clean, safe drinking water. Give now. [88/90]
```

### Charity/Campaign Meta Feed Package (Cause-Driven Example)

```
PRIMARY TEXT (Hook + Body):
Every $50 donation provides clean water to one family for months. Your Sadaqah Jariyah in water continues delivering reward — even after you're gone. Donate through Elvefa Association.

HEADLINE: Clean Water Donation — Give Life [33/40]
DESCRIPTION: Sadaqah & Zakat Eligible | Elvefa Org [39/40]
CTA BUTTON: Donate Now
```

---

## 5. Ad Copy QA Checklist

Run before output. Never print unless asked.

| Check | Gate |
|-------|------|
| Character count within hard limit for every asset | FAIL if any asset exceeds |
| Inline `[XX/Limit]` tags present on every headline and description | FAIL if missing |
| 5 distinct angles covered (not 5 variations of same line) | FAIL if duplicates found |
| At least 3 headlines trace directly to source phrases (word-for-word) | FAIL if fewer than 3 |
| Descriptions use source language, not invented claims | FAIL if generic paraphrase found |
| Zero forbidden hype words | FAIL if any found |
| Zero modal verbs | FAIL if any found |
| Every headline starts with capital letter | FAIL if lowercase start |
| Every description includes CTA or action prompt | FAIL if passive ending |
| EAV triple present in at least 50% of headlines | FAIL if below threshold |
