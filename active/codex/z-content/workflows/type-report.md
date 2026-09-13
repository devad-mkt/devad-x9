# Workflow: Report / Audit

Handles: market research, competitive audits, executive briefs, whitepapers, competitive benchmarks, analysis reports.

Load `SKILL.md` first. This file provides report-specific structure and analytical tone rules.

---

## Structural Model

```
1. Executive Summary
   ├─ Core findings in sentences 1–2 (inverted pyramid)
   └─ High-level metrics with named sources

2. Methodology & Scope
   ├─ Datasets evaluated
   ├─ Date ranges
   ├─ Parameters and criteria
   └─ Limitations and exclusions

3. Key Findings (Data-Dense Sections)
   ├─ Thematic section 1
   │    ├─ Finding statement (direct answer)
   │    ├─ Supporting data table
   │    └─ Evidence citation
   ├─ Thematic section 2
   │    └─ ...

4. Risk & Impact Analysis
   ├─ Quantified implications
   └─ Severity × likelihood matrix

5. Actionable Recommendations
   └─ | Priority | Finding | Action Item | Expected Impact | Resource Effort |

6. Appendices (if applicable)
   ├─ Raw data tables
   ├─ Survey instruments
   └─ Full citation list
```

---

## Executive Summary Rules

### Inverted Pyramid
The first 2 paragraphs must contain:
1. The single most important finding (1 sentence).
2. The 2–3 supporting metrics that prove it (with named sources).

- **Wrong:** "In today's rapidly evolving market, companies face many challenges. This report examines various aspects of the competitive landscape..."
- **Right:** "Zendesk holds 34% market share in SMB customer support software across North America (G2, Q2 2026). Intercom follows at 21%, with Freshdesk at 18%."

### Metric Requirements
Every executive summary metric must include:
- Exact number (percentage, count, revenue, time period)
- Named source (company name, research firm, dataset name)
- Date or time frame (Q2 2026, January–June 2026, FY2025)

---

## Methodology & Scope

### Required Elements

| Element | What to State |
|---------|---------------|
| Dataset | Exact source names, record counts, sampling method |
| Date range | Start and end dates of data collection |
| Parameters | Criteria used for inclusion/exclusion |
| Tools | Software, APIs, or methods used for analysis |
| Limitations | What was not measured, excluded, or outside scope |

### Tone
Write methodology in past tense, passive voice is acceptable here:

- **Right:** "Data was collected from G2, Capterra, and TrustRadius between January and June 2026. Products with fewer than 50 reviews were excluded."

---

## Key Findings Structure

### Finding Statement Format
Each finding section opens with a direct answer:

```
[Finding H2]: [Entity] [measured attribute] [exact value] [source, date].
```

- **Right:** "Zendesk leads SMB market share: 34% across North America (G2, Q2 2026)."

### Data Tables
Use dimension-rich headers:

| Metric | Zendesk | Intercom | Freshdesk | Source |
|--------|---------|----------|-----------|--------|
| Market share (SMB, NA) | 34% | 21% | 18% | G2, Q2 2026 |
| Avg. response time | 2.1 hrs | 1.8 hrs | 3.4 hrs | Internal benchmark |
| CSAT score | 4.3/5 | 4.5/5 | 4.1/5 | TrustRadius, 2026 |

Rules:
- Every cell must contain a verifiable value or `—`.
- No cell may contain a vague claim ("high", "fast", "good").
- Include the source column for every table.

### Evidence Citation
Place the citation directly beside or below the claim:

- **Wrong:** "Studies show that AI reduces response times significantly."
- **Right:** "AI-assisted routing reduces first-response time by 42% across 1,200 support queues (Zendesk Benchmark Report, 2025)."

---

## Risk & Impact Analysis

### Severity × Likelihood Matrix

| Risk | Severity | Likelihood | Impact | Mitigation |
|------|----------|------------|--------|------------|
| Vendor lock-in (single provider) | High | Medium | 40% cost increase if contract renegotiation fails | Maintain 2-vendor architecture |
| Data migration failure | Critical | Low | 2–4 week project delay | Run parallel environments for 30 days |

Rules:
- Severity: Low / Medium / High / Critical (use exactly these labels)
- Likelihood: Low / Medium / High
- Impact: Quantified as percentage, time, or cost
- Mitigation: One specific action, not a strategy document

---

## Actionable Recommendations Table

| Priority | Finding | Action Item | Expected Impact | Resource Effort |
|----------|---------|-------------|-----------------|-----------------|
| P1 | Zendesk price increase 18% YoY | Negotiate 2-year lock-in before Q4 renewal | Avoid $12K/yr cost increase | 4 hours legal review |
| P2 | Intercom lacks WhatsApp integration | Evaluate Trengo as supplementary channel | Add WhatsApp without platform switch | 2-week pilot |
| P3 | Freshdesk CSAT declining (4.1 → 3.8) | Implement AI chatbot for tier-1 queries | Improve CSAT by 0.3–0.5 points | 1-week setup |

Rules:
- Priority: P1 (urgent), P2 (important), P3 (monitor)
- Every action item must be specific and time-bound.
- Expected impact must be quantified.
- Resource effort must state hours, days, or weeks.

---

## Linguistic Guardrails for Reports

### Formal Academic Tone
- Use third person ("The analysis found..." not "We found...").
- Past tense for methodology, present tense for findings.
- No contractions (use "do not" not "don't").

### Citation Rigor
Every claim requires one of:
- Named source + date
- Internal dataset reference + date range
- Third-party benchmark + year
- No unsourced statistics

### Neutral Analytical Language
- **Wrong:** "Intercom is clearly the best choice for most teams."
- **Right:** "Intercom leads in CSAT score (4.5/5) and response time (1.8 hrs), while Zendesk leads in market share (34%) and integration count (500+)."

### Data Synthesis
Combine multiple data points into single analytical statements:

- **Wrong:** "Zendesk has 34% market share. Zendesk has 500+ integrations. Zendesk is popular."
- **Right:** "Zendesk combines the largest SMB market share (34%) with the broadest integration ecosystem (500+ apps), creating the highest switching cost in the segment."

---

## Report QA Additions

In addition to the master scorecard:

- [ ] **Citation coverage:** Every metric has a named source and date.
- [ ] **Methodology completeness:** Dataset, date range, parameters, limitations stated.
- [ ] **Executive summary density:** First 2 paragraphs contain the core finding + 2–3 metrics.
- [ ] **Table format:** Every table has dimension-rich headers and source column.
- [ ] **Recommendation specificity:** Every action item is time-bound and quantified.
- [ ] **No unsourced claims:** Zero statistics without citation.
