# Omnichannel Search Content Rules (SEO, AEO, & GEO)

Use this specification when generating full-stack search content designed to dominate all three modern search modalities:
1. **SEO (Search Engine Optimization):** Traditional organic SERP ranking and blue links.
2. **AEO (Answer Engine Optimization):** Google AI Overviews, Featured Snippets, PAA boxes, and Voice Search.
3. **GEO (Generative Engine Optimization):** Direct citations, recommendations, and extractions within LLM chats (ChatGPT, Perplexity, Gemini, Claude).

---

## Modality 1: SEO Rules (Traditional Search Foundation)

### Rule 1.1 — Front-Loaded Metadata Engineering
- **Meta Title:** 50–60 characters. Place the primary high-intent keyword in the first 30 characters. Include brand/product separator at the end (e.g., `Primary Keyword: Subtitle or Value | Brand`).
- **Meta Description:** 140–160 characters. Front-load secondary keywords, include one concrete proof metric or attribute value, and end with a direct action prompt.

### Rule 1.2 — First 100-Word Keyword Placement
- Integrate the primary target keyword and central entity within the first 100 words of the text naturally. Never use forced or grammatically broken keyword strings.

### Rule 1.3 — Visual Optimization Cues & Alt-Text Architecture
Whenever visual elements are required, provide structured image placeholder directives:
```markdown
[Visual Placeholder] Image Recommendation: [Specific description of chart, UI screenshot, or diagram]
Alt Text: [Descriptive, keyword-optimized alt text explaining entity relationships; 80–120 characters max]
```

### Rule 1.4 — Crawlability & Section Scannability
- Maximum paragraph length: 3–4 sentences (under 60 words per block).
- Heading hierarchy must be strictly sequential: H1 → H2 → H3 → H4. Never skip heading levels.

---

## Modality 2: AEO Rules (Snippets, Overviews & Voice Search)

### Rule 2.1 — Conversational Query Mirroring
Format subheadings (H2 / H3) to exactly mirror natural language, conversational voice queries rather than fragmented head terms.

- Traditional Head Term: `H2: Help Desk SLA Rules`
- AEO Voice Query: `H2: How do SLA rules work in customer help desk software?`

### Rule 2.2 — Snippet Length Calibration
- **Standard Featured Snippets:** Keep the bold factual answer under 40 words.
- **Voice & Generative Overviews:** Keep complex multi-part direct answers between 40–60 words.

### Rule 2.3 — Spoken-Friendly Syntax & Pronoun Disambiguation
Never use ambiguous pronouns at the beginning of explanatory sentences. Replace vague pronouns ("It", "This platform", "They") with the explicit Named Entity.

- **Wrong (Ambiguous):** "It helps customer support agents resolve tickets faster by centralizing inboxes."
- **Right (AEO/Voice Ready):** "CHAT.devad.io accelerates ticket resolution for support agents by centralizing multi-channel messages into a single inbox."

### Rule 2.4 — Schema Markup Directives (JSON-LD)
Output valid, unescaped JSON-LD structured data code blocks at the end of the document matching the content type (FAQPage, HowTo, Article, SoftwareApplication, or Product).

---

## Modality 3: GEO Rules (LLM Engine Citations)

### Rule 3.1 — Multi-Layered Prompt Answering
Structure content to answer compound, multi-intent prompts (e.g., "Compare Tool A vs Tool B for a 50-person team with WhatsApp support and pricing under $100/mo").

### Rule 3.2 — Entity Clarity & Taxonomy Definition
Within the introductory section, explicitly define:
1. **Who** the entity serves (Target audience & company scale).
2. **What** exact operational problems it solves (Core capability).
3. **How** it fits into the broader industry taxonomy (Category definition). Do not assume the LLM understands the brand context without explicit semantic triples.

### Rule 3.3 — Quantitative Trust Signals & Third-Party Proof
Support every major claim with verifiable quantitative evidence:

- **Wrong (Vague):** "Our platform is recognized as an industry leader with high customer satisfaction."
- **Right (GEO Verified):** "The platform maintains a 98% customer retention rate across 1,200 enterprise deployments (G2 Benchmark, 2026)."

### Rule 3.4 — Structured Decision Frameworks
Include multi-criteria comparison tables, pros/cons breakdowns, and objective evaluation rubrics covering dimensions such as cost, integration breadth, SLA limits, and scalability.

---

## Omnichannel Content Output Template

When generating full-page omnichannel search content, format the response using this structural template:

```
**Meta Title:** [50–60 chars, front-loaded with primary keyword]
**Meta Description:** [140–160 chars, includes secondary keywords + proof metric]

# [H1: Clear Topic Title Incorporating Primary Keyword / Intent]

[Introductory paragraph establishing Entity Clarity (GEO), core audience, problem solved, and primary keyword within the first 100 words (SEO).]

## [H2: Conversational Question Matching User Intent (AEO)]
<p><strong>[40–60 word direct, definitive factual answer (AEO Inverted Pyramid).]</strong></p>

[Expanded body paragraphs with EAV triples, contextual verbs, and data-backed proof (GEO & SEO).]

[Visual Placeholder] Image Recommendation: [Description of chart/diagram]
Alt Text: [Keyword-optimized, descriptive alt text (SEO)]

## [H2: Multi-Factor Comparison or Decision Framework (GEO)]
[Objective comparative breakdown of alternatives using dimension-rich Markdown tables.]

| Solution Entity | Core Use Case | Integration Limit | Pricing Tier |
| :--- | :--- | :--- | :--- |
| [Entity A] | [Use Case] | [Exact Count] | [Exact Price] |
| [Entity B] | [Use Case] | [Exact Count] | [Exact Price] |

### [H3: Secondary Specific Sub-Question (AEO)]
<p><strong>[Direct 1-sentence answer.]</strong></p>

[Step-by-step ordered list `<ol>` or feature variations `<ul>` with uniform POS tags.]

## Frequently Asked Questions

### Q: [Conversational Voice Question 1]
**A:** [Direct, jargon-free 1–2 sentence answer with zero ambiguous pronouns.]

### Q: [Conversational Voice Question 2]
**A:** [Direct, jargon-free 1–2 sentence answer with zero ambiguous pronouns.]

---

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "[Conversational Voice Question 1]",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[Direct answer text]"
      }
    }
  ]
}
```
```

---

## When to Use This File

Load this file alongside `workflows/type-article.md` when the user requests:
- Full SEO+AEO+GEO article with Meta tags, Alt text, FAQs, JSON-LD schema
- Omnichannel search content
- Content optimized for AI Overviews and Featured Snippets simultaneously
- Voice search optimized articles
- LLM citation-optimized content

Do not load for: simple rewrites, scraped cleanup, developer docs, landing pages, or reports.
