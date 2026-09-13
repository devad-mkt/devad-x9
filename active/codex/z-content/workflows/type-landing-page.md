# Workflow: Landing Page

Handles: product pages, home pages, sales pages, feature releases, pricing tiers, CRO pages.

Load `SKILL.md` first. Load `reference/conversion-copy-rules.md` when the task involves persuasion, emotion, or audience decision-making. This file provides landing-page-specific structure and conversion rules.

---

## Structural Model

```
1. Hero Section
   ├─ Primary Entity (product name)
   ├─ Core Value Proposition (1 sentence, EAV-dense)
   ├─ Primary CTA
   └─ Proof Metric (exact number, named source)

2. Problem/Solution Bridge
   ├─ Quantified pain point (metric + source)
   └─ Exact mechanism of resolution (how the product fixes it)

3. Feature-to-Attribute Matrix (EAV)
   └─ Table: Feature | Attribute | Operational Value

4. Social Proof & Benchmark Authority
   └─ Exact metrics: "Reduces latency by 42% across 1,200 endpoints"

5. Comparison Grid
   └─ Table: Our Tool vs. Status Quo vs. Competitors (dimension headers)

6. Final Conversion Action
   └─ Low-friction next step (no long forms, no heavy commitment)
```

---

## Hero Section Rules

### Value Proposition Formula
`[Product] [precise verb] [attribute] for [audience] to [measurable outcome].`

- **Wrong:** "The most powerful customer service platform for modern teams."
- **Right:** "CHAT.devad.io centralizes multi-channel support tickets to reduce average response time by 35%."

### Proof Metric Requirements
Every hero must include one verifiable proof metric:
- Exact number (percentage, count, time reduction)
- Named source or baseline ("internal benchmark", "Google study", "1,200 endpoints tested")
- No round numbers without source ("thousands of users" is forbidden)

### CTA Hierarchy
| Level | Purpose | Example |
|-------|---------|---------|
| Primary | Main conversion action | "Start free trial" |
| Secondary | Lower-commitment alternative | "View live demo" |
| Supporting | Information gathering | "Read the full comparison" |

One primary CTA per hero. Secondary and supporting are optional.

---

## Feature-to-Attribute Matrix

Convert every feature into an entity-attribute-value triple presented as a table.

| Feature (Entity) | Attribute | Operational Value |
|------------------|-----------|-------------------|
| Unified inbox | Channels supported | Email, live chat, WhatsApp, social DMs, help-center tickets |
| AI chatbot | Automation scope | Resolves tier-1 queries without agent intervention |
| SLA rules | Tracking method | Alerts at 80% deadline, escalates at 100% |
| Routing queue | Assignment logic | Skill-based, priority-based, round-robin |

Rules:
- Every row must name the entity, its attribute, and a concrete value.
- Do not use vague values ("many channels", "fast response", "easy setup").
- Use `—` for values that are unavailable or not verified.
- Do not invent integrations, limits, or performance claims.

---

## Comparison Grid Rules

### Column Headers
Use dimension-rich headers that explain the relationship:

- **Wrong:** "Thing" / "Info" / "Price"
- **Right:** "Tool" / "Supported Channels" / "AI Capability" / "Pricing Basis" / "Best-Supported Use Case"

### Comparison Propositions
Compare using specific, measurable attributes:

- **Wrong:** "CHAT.devad.io is much better and way easier to use than Zendesk."
- **Right:** "CHAT.devad.io offers unlimited agent seats on its base tier, whereas Zendesk restricts base tiers to a single user."

### Row Rules
- Preserve all existing rows if modifying an existing table.
- Add the product row only if data matches existing columns.
- Use `—` for unavailable values.
- Do not add or remove columns.
- Do not reorder rows to favor one product.

---

## Conversion & Voice Additions (When Conversion Layer Active)

Beyond the EAV/precision defaults of this workflow, apply these additions:

- **Audience-first hero:** replace entity-first value proposition with audience-stakes headline when awareness is low or emotional stakes are high. Keep the EAV value prop as subheadline.
- **Problem/solution bridge:** open the problem section with a pictureable consequence ("For a support team that loses tickets every hour..."), not a metric.
- **Feature-to-consequence translation:** for each matrix row, add one consequence line ("This prevents your agents from manually reassigning 40 tickets per day.").
- **Proof placement:** place exact metrics beside the claim they support, not only in hero.
- **Objection resolution:** identify 1–3 genuine blockers and resolve each beside the relevant CTA or section.
- **CTA cadence:** primary CTA in hero, after the comparison grid, and at the close. No intermediate hesitation headings.
- **Image markers:** each image has role (stakes, mechanism, proof, outcome), alt text, and caption direction.

## Linguistic Guardrails for Landing Pages

### Zero Hype Words
These words are forbidden without a specific attribute explanation:
- revolutionary, game-changing, effortless, seamless, powerful, robust, best-in-class, cutting-edge, world-class, next-generation, industry-leading, trusted by thousands

### Persuasion Through Specs
Persuade only through:
- Exact performance metrics (latency, throughput, uptime, reduction percentages)
- Feature counts and supported types
- Integration lists with specific platform names
- Pricing with clear basis (per seat, per month, per transaction)
- Case study numbers with named sources

### Neutral Sentiment
Remove all sensationalism, excitement, and emotional manipulation. Write like technical documentation that happens to sell something.

- **Wrong:** "You will be absolutely blown away by how incredibly fast our builder is!"
- **Right:** "The builder deploys landing pages in under 5 minutes."

---

## Landing Page QA Additions

In addition to the master scorecard:

- [ ] **Hero proof metric:** One exact number with named source in hero section.
- [ ] **Feature matrix:** At least 5 feature-attribute-value rows in the EAV table.
- [ ] **Zero hype:** No forbidden hype words without attribute backing.
- [ ] **CTA clarity:** One primary CTA, clearly stated.
- [ ] **Comparison fairness:** All rows/columns preserved, no favoritism in ordering.
