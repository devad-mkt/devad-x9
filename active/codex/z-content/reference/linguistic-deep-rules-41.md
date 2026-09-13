# Linguistic Deep Rules — compact 41-rule catalog

Load only for deep rule debugging or developer review. The normal path is `SKILL.md` plus one workflow. The 41 identities remain separate so this file is a compressed reference, not a merged replacement for other capabilities.

| # | Rule | Compact application |
|---:|---|---|
| 1 | Semantic triples | State facts as `Subject → Predicate → Object`. |
| 2 | EAV density | Target 15–20 explicit `Entity | Attribute | Value` facts in long-form content. |
| 3 | Numeric precision | Replace vague quantities with exact numbers, ranges, dates, prices, or capacities. |
| 4 | Qualify instances | Add type, version, audience, channel, or constraint after broad terms. |
| 5 | Proper word sequence | Start sentences with the main entity and a precise action. |
| 6 | Principle of certainty | Remove unsupported modality, hedging, and personal opinion. |
| 7 | Fluff and analogy eradication | Explain functions literally; remove filler, idioms, and metaphors. |
| 8 | Linguistic instance qualification | Name concrete examples after broad categories. |
| 9 | Contextual verbs | Replace `make/do/help/get` with domain verbs such as routes, verifies, or schedules. |
| 10 | Plural noun expansion | Follow newly introduced plurals with at least three concrete examples when applicable. |
| 11 | If statements last | Put the action first and the condition at the end. |
| 12 | POS list consistency | Keep every item in one list grammatically parallel. |
| 13 | Heading vectors | Use literal, question-shaped H2/H3 headings when the meaning remains intact. |
| 14 | Immediate direct answers | Answer the heading in the first sentence after it. |
| 15 | 40-word snippet | Bold the complete factual answer; keep it under 40 words, hard limit 45. |
| 16 | Semantic anchor text | Name the destination entity in links; never use “click here”. |
| 17 | Table optimization | Use dimension-rich headers and clean, extractable cells. |
| 18 | EAV output list | Silently extract the actual triples before finalizing long-form content. |
| 19 | Compliance scorecard | Score truth, clarity, extraction, EAV proof, and structure at 20 points each. |
| 20 | Advanced anchor matching | Build internal context bridges with explicit target entities. |
| 21 | Sentence shortening | Split compound propositions into short, declarative sentences. |
| 22 | Contextless word deletion | Delete words that add no entity, attribute, value, condition, or relationship. |
| 23 | Information density | Prefer specific mechanism, feature, constraint, and metric over generic benefits. |
| 24 | Context vector maintenance | Keep one semantic path from H1 through the conclusion. |
| 25 | Academic/data proof | Put named source, date, and baseline beside measurable claims. |
| 26 | Bold the answer | Bold the factual value, not the repeated search term. |
| 27 | Zero personal opinions | Replace “we believe” and superlatives with verifiable attributes. |
| 28 | Formal language | Use professional, audience-appropriate wording without consumer hype. |
| 29 | Tonal analogy eradication | Describe software, products, and outcomes literally. |
| 30 | Unnecessary word removal | Remove intensifiers and words that repeat existing meaning. |
| 31 | Clarity through brevity | Stop when the intent is answered; do not pad for length. |
| 32 | Tonal direct answers | Do not delay the answer with generic context after a heading. |
| 33 | Reliable source citations | Prefer primary, dated, authoritative evidence for claims. |
| 34 | Appropriate coverage | Cover the intent completely, then stop. |
| 35 | Featured snippet | Keep the direct answer factual, bolded, and below the hard word limit. |
| 36 | PAA response | Give one complete answer sentence before any explanation. |
| 37 | Relevant anchors | Match link wording to the target page’s central entity. |
| 38 | Strong listing intros | Introduce the scope before a feature or instruction list. |
| 39 | Definitive answers | State verified conditions directly instead of “it depends”. |
| 40 | Clear instruction lists | Use `<ol>` for chronological setup and procedural steps. |
| 41 | Relational matrices | Compare tiers/entities with neutral, measurable columns and source values. |

## Minimal audit

Check the 41 rules silently. Preserve source entities, lists, tables, quotes, numbers, and order during strict transformation. Treat unsupported facts, dropped source material, broken links, missing direct answers, and invented certainty as failures.
