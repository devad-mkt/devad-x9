# Workflow: Social Media Content

Handles: LinkedIn posts, X (Twitter) posts & threads, Instagram captions, TikTok captions, Facebook updates, YouTube descriptions, Pinterest pins, Threads posts.

Load `SKILL.md` first. This file provides platform-specific formatting, truncation fold strategy, and character enforcement rules.

---

## Platform Detection

Detect target platform from prompt keywords:

| Signal | Platform | Load Section |
|--------|----------|--------------|
| LinkedIn post, thought leadership, B2B content, professional update | LinkedIn | Section 2A |
| Tweet, X post, X thread, Twitter thread, microblog | X/Twitter | Section 2B |
| Instagram caption, IG caption, Reel caption, carousel caption, feed post | Instagram | Section 2C |
| TikTok caption, TikTok text, short-form caption | TikTok | Section 2D |
| Facebook post, FB update, Facebook status | Facebook | Section 2E |
| YouTube description, video description, YT desc | YouTube | Section 2F |
| Generic ("social post", "write a post", "social media content") | **Cross-Channel Trio** | Sections 2A + 2B + 2C |

---

## 1. The Truncation Fold Strategy

Every social post must place the complete core hook **before the platform's "See More" truncation fold**. The fold is a headline slot — treat it like one.

| Platform | Hard Limit | Truncation Fold | Hook Target |
|----------|-----------|-----------------|-------------|
| LinkedIn | 3,000 chars | ~210 desktop / ~140 mobile | **130–140 chars** |
| Instagram | 2,200 chars | ~125 chars | **100–115 chars** |
| TikTok | 4,000 chars | ~90 chars | **80–90 chars** |
| Facebook | 63,206 chars | ~477 chars | **400–450 chars** |
| YouTube | 5,000 chars | ~157 chars | **130–150 chars** |
| X (Twitter) | 280 chars | No fold (full display) | **260–270 chars** |
| Threads | 500 chars | No fold (full display) | **450–480 chars** |
| Pinterest | 500 chars | ~50 chars in feed | **40–50 chars** |

### Hook Completeness Rule

The hook must deliver **one complete thought** — a full value proposition, not a cliffhanger that forces expansion.

- **Wrong (Cliffhanger):** "Have you ever wondered why your support team is overwhelmed?"
- **Right (Complete Hook):** "Support teams handle 40% more tickets when chat, email, and WhatsApp route through one inbox."

---

## 2. Platform Formats & Archetypes

### A. LinkedIn Post (B2B Authority / Thought Leadership)

**Structure:**
1. **Line 1 (Hook):** Provocative, data-backed thesis or contrarian industry fact. Under 140 chars.
2. **Body:** 3–5 short punchy paragraphs or a bulleted EAV breakdown with uniform POS tags.
3. **Outro:** One conversational question to drive comments.
4. **Hashtags:** 3–5 relevant, niche-specific hashtags at the bottom.

**Rules:**
- Short paragraphs (1–2 sentences). Line breaks for readability.
- Use lists, bullet points, or numbered steps for scanability.
- No hashtags in the first line (wastes hook space).
- Front-load the value proposition before any context.

**Example Template:**
```
[Hook: 130 chars max — data-backed thesis or contrarian fact]

[Body paragraph 1: 1–2 sentences, expands the hook]

[Body paragraph 2: 1–2 sentences, provides evidence or EAV data]

[Outro: 1 conversational question]

#hashtag1 #hashtag2 #hashtag3
```

### B. X / Twitter (High-Density Microcontent)

**Single Post (under 280 chars):**
- One complete idea. Subject-Verb-Object clarity.
- No hashtags in promoted posts (wastes characters).
- URLs count as 23 chars (t.co shortening).

**Thread (3–5 tweets):**
- Tweet 1: Hook + quantified promise (under 280).
- Tweets 2–4: Distinct EAV data points or actionable steps (each under 280).
- Final Tweet: Summary takeaway + single CTA link placeholder.

**Thread Connectors:**
- Tweet 1 ends with: "Here's what I found:"
- Tweet 2 starts with "1/" or a numbered step.
- Final tweet: "TL;DR" or "In summary" + takeaway.

**Rules:**
- No hashtags in promoted tweets.
- No image tags or media mentions unless requested.
- Each tweet must stand alone as a complete thought.

### C. Instagram / TikTok Captions

**Structure:**
1. **Line 1 (Visual Hook):** Aligns with image/video. Under 125 chars.
2. **Body:** Scannable tips, steps, or product context. EAV triples throughout.
3. **Hashtag Matrix:** 3–5 targeted hashtags.

**Hashtag Matrix (3–5 tags):**
| Tag Type | Purpose | Example |
|----------|---------|---------|
| Broad Category | Reach discovery | #CustomerSupport |
| Niche Entity | Targeted audience | #UnifiedInbox |
| Specific Feature | Feature search | #WhatsAppIntegration |
| Branded/Campaign | Brand recall | #YourBrandName |
| Trending (optional) | Timely reach | Only if genuinely relevant |

**Rules:**
- Line 1 must deliver complete value before the 125-char truncation fold.
- Emojis: max 1–2 per section as visual bullet anchors, not decoration.
- No "link in bio" in organic posts unless explicitly requested.
- Instagram: max 5 hashtags (reduced from 30 in late 2025).

**Example Template:**
```
[Hook: 125 chars max — aligns with visual, delivers complete value]

[Body: scannable tips, steps, or EAV data]

[CTA: single action prompt]

#hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5
```

### D. Facebook Post

**Structure:**
1. **Line 1 (Hook):** Complete value under 477 chars (truncation fold).
2. **Body:** Longer-form context if needed. Line breaks for readability.
3. **CTA:** Direct action prompt.

**Rules:**
- Facebook allows long posts (63K chars), but 85% of readers won't expand past 477 chars.
- Front-load the hook. Supporting context can extend.
- No hashtags in organic posts (reduces reach unless it's a branded campaign).
- Link previews pull from the URL — don't duplicate link text in the post.

### E. YouTube Description

**Structure:**
1. **Line 1 (SEO Hook):** Primary keyword + value proposition. Under 150 chars.
2. **Body:** Chapters, timestamps, key points, links.
3. **CTA:** Subscribe, watch next, visit link.

**Rules:**
- First 150 chars show in search results and above the fold. Front-load keywords.
- Use chapters with timestamps for videos over 10 minutes.
- Include 3–5 relevant keywords naturally in the first 200 chars.
- Link to related videos, social profiles, and landing pages in the body.

### F. Pinterest Pin

**Structure:**
- **Title:** Under 100 chars (only ~30–40 show in feed).
- **Description:** Under 500 chars (~50 show in feed).

**Rules:**
- Description must be keyword-rich for Pinterest search.
- Front-load the most important keyword in the first 50 chars.
- Include a CTA: "Save this pin", "Click to read more".

---

## 3. Social Copy Guardrails

| Rule | Enforcement |
|------|-------------|
| Zero modal verbs | No should, might, could, probably, we believe. |
| Zero vague hype | Forbidden: revolutionary, effortless, game-changing, best, seamless, world-class, cutting-edge. |
| Zero conversational filler | Forbidden: Let's dive in, Have you ever wondered, In today's world, It's no secret that, As we all know. |
| Mandatory SVO | Subject + Verb + Object at sentence start. No introductory filler. |
| Hook completeness | Line 1 must deliver a complete thought before the truncation fold. |
| No invented facts | Numbers, prices, percentages, and stats only from user-provided data or verified research. |
| Emoji restraint | Max 1–2 per section. Use as visual bullet anchors, not decoration. |
| Hashtag restraint | Max 3–5 per post. Never more than 5 on Instagram (2025+ limit). |

---

## 4. Output Templates

### LinkedIn Post Template
```
[Hook — 130 chars]: Support teams handle 40% more tickets when chat, email, and WhatsApp route through one inbox. Our platform cuts average response time from 4 hours to 12 minutes.

[Body]: Here's how it works:

• Unified inbox aggregates all channels into a single dashboard
• AI routing assigns tickets by skill level and availability
• SLA tracking prevents response SLA breaches before they happen

[Outro]: What's the biggest bottleneck in your support workflow right now?

#CustomerSupport #UnifiedInbox #HelpDeskSoftware
```

### X / Twitter Thread Template
```
Tweet 1 (Hook — 265 chars): Support teams handle 40% more tickets when chat, email, and WhatsApp route through one inbox. Here's what I found after testing 5 platforms:

Tweet 2 (275 chars): 1/ Unified inbox reduces context switching by 60%. Every message — regardless of channel — appears in a single feed. No more tab-switching.

Tweet 3 (270 chars): 2/ AI routing cuts first response time from 4 hours to 12 minutes. Tickets auto-assign by skill level, availability, and topic.

Tweet 4 (260 chars): 3/ SLA tracking prevents breaches. Real-time dashboards show response times before they become problems.

Tweet 5 (250 chars): TL;DR: One inbox + AI routing + SLA tracking = 40% more tickets handled. Try it free for 14 days. [Link placeholder]
```

### Instagram Caption Template
```
[Hook — 120 chars]: Support teams handle 40% more tickets with a unified inbox. Here's the breakdown:

[Body]: The math is simple:

• 3 channels (chat, email, WhatsApp) → 1 dashboard
• Avg response time: 4 hours → 12 minutes
• Tickets resolved per agent: +40%

No more tab-switching. No more lost context.

[CTA]: Save this for your next ops review.

#CustomerSupport #UnifiedInbox #HelpDesk #SaaSTools #SupportTeam
```

### TikTok Caption Template
```
[Hook — 85 chars]: The support inbox hack that cuts response time from 4 hours to 12 minutes:

[Body]: One dashboard. Chat + email + WhatsApp. AI routing. SLA tracking. 40% more tickets resolved.

[CTA]: Link in bio to try free.

#SupportHack #CustomerService #SaaS #HelpDesk
```

---

## 5. Social Copy QA Checklist

Run before output. Never print unless asked.

| Check | Gate |
|-------|------|
| Hook delivers complete thought before truncation fold | FAIL if cliffhanger or incomplete |
| Character count within hard limit | FAIL if any post exceeds |
| Zero forbidden hype words | FAIL if any found |
| Zero modal verbs | FAIL if any found |
| Zero conversational filler phrases | FAIL if any found |
| Hashtag count within platform limit (max 5 for IG) | FAIL if exceeded |
| Emoji count ≤ 2 per section | FAIL if exceeded |
| Every sentence follows SVO order | FAIL if intro filler detected |
| No invented facts or statistics | FAIL if unverified claim found |
