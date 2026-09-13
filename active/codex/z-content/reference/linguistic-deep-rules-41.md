# Linguistic Deep Rules — Full 41-Rule Catalog

Reference file. Do not load during normal operation. Load only when deep rule debugging or developer review is needed.

Source: `article-rulebook.md`. Preserves all 41 original algorithmic authorship rules sequentially across the 8 functional phases.

---

## Phase 1: Information Extraction & EAV Saturation (Rules 1–4)

### Rule 1 — Semantic Triples (Subject-Predicate-Object)
**Purpose:** Structure facts as subject-predicate-object so search engines parse relationships without computational strain.
- **Wrong:** "Our customer service app is really great for making things faster and better for your support team."
- **Right:** "CHAT.devad.io (Subject) accelerates (Predicate) ticket resolution (Object)."

### Rule 2 — EAV (Entity-Attribute-Value) Density
**Purpose:** Saturate content with 15–20 specific EAV points to reduce retrieval cost and trigger zero-backlink rankings.
- **Wrong:** "POST.devad.io helps you manage all your social media platforms in one place effortlessly."
- **Right:** "POST.devad.io [Entity] | multi-platform scheduling [Attribute] | 4 networks (Instagram, Facebook, LinkedIn, X) [Value]."

### Rule 3 — Numeric Precision
**Purpose:** Replace vague quantity words with exact numbers to establish authority and factuality.
- **Wrong:** "WEB.devad.io offers a lot of templates for website development without coding."
- **Right:** "WEB.devad.io offers 50+ no-code templates with integrated payments and SEO capabilities."

### Rule 4 — Qualify the Instances
**Purpose:** Add descriptive details that specify and distinguish the subject, eliminating ambiguity for users and NLP parsers.
- **Wrong:** "AI.devad.io provides various AI models for content generation."
- **Right:** "AI.devad.io provides 3 distinct multi-model AI engines (Jasper, Copy.ai, Claude) for content generation and image synthesis."

---

## Phase 2: Algorithmic Authorship — Linguistic Rules (Rules 5–11)

### Rule 5 — Proper Word Sequence
**Purpose:** Place the main entity and action at the beginning of the sentence so search engines identify core context immediately.
- **Wrong:** "Faster response times and better ticket management can be easily achieved by support agents when using CHAT.devad.io."
- **Right:** "CHAT.devad.io accelerates ticket resolution for support agents."

### Rule 6 — The Principle of Certainty
**Purpose:** Remove all ambiguity, modal verbs, and subjective opinions to build algorithmic trust.
- **Wrong:** "You should probably use AI.devad.io because it will save you a ton of time generating blog posts."
- **Right:** "AI.devad.io automates blog post generation to increase team productivity."

### Rule 7 — Fluff & Analogy Eradication
**Purpose:** Eliminate contextless words and metaphors that dilute semantic density.
- **Wrong:** "The unified inbox in CHAT.devad.io is basically like a magic wand that takes the headache out of talking to customers."
- **Right:** "The CHAT.devad.io unified inbox centralizes customer communications from email and live chat into a single dashboard."

### Rule 8 — Qualify the Instances (Linguistic)
**Purpose:** Prove deep topical expertise by providing specific, descriptive details for broad categories.
- **Wrong:** "WEB.devad.io offers various templates for online businesses."
- **Right:** "WEB.devad.io offers 50+ mobile-responsive ecommerce templates with integrated Stripe payments."

### Rule 9 — Contextual Verbs
**Purpose:** Match verbs to the exact niche intent, strengthening the semantic relationship between entity and action.
- **Wrong:** "SITE.devad.io helps you make a new landing page."
- **Right:** "SITE.devad.io deploys high-converting landing pages."

### Rule 10 — Plural Noun Expansion
**Purpose:** Inject highly relevant entities by providing 3+ concrete examples after every plural noun.
- **Wrong:** "POST.devad.io manages all your social media profiles from one place."
- **Right:** "POST.devad.io manages all your social media profiles, such as Instagram, Facebook, LinkedIn, and X."

### Rule 11 — "If" Statements Last
**Purpose:** Ensure the search engine reads the primary action without processing conditional logic first.
- **Wrong:** "If you lack coding skills but want to launch an online store, use the no-code builder in SITE.devad.io."
- **Right:** "Use the no-code builder in SITE.devad.io to launch an online store, if you lack coding skills."

---

## Phase 3: Structural Engineering & NLP Formatting (Rules 12–17)

### Rule 12 — Consistent Part of Speech (POS) Tags in Lists
**Purpose:** Maintain grammatical uniformity in lists so NLP parsers extract and classify items without strain.
- **Wrong:**
  - Automate post scheduling.
  - Analytics for Instagram.
  - You can manage Facebook.
- **Right:**
  - Automate (verb) post scheduling via POST.devad.io.
  - Track (verb) analytics across Instagram and LinkedIn.
  - Manage (verb) Facebook engagement centrally.

### Rule 13 — Heading Vectors (Question-Based H2s)
**Purpose:** Align subheadings with user queries to trigger Answer Engine extraction.
- **Wrong:** `H2: AI.devad.io Features`
- **Right:** `H2: What are the primary features of AI.devad.io?`

### Rule 14 — Immediate Direct Answers
**Purpose:** Satisfy the query instantly. The first sentence after a heading must answer it directly.
- **Wrong:** "H2: How does SITE.devad.io work? Building a website is an important step for any business today. Many people struggle with coding, so tools like SITE.devad.io are helpful..."
- **Right:** "H2: How does SITE.devad.io work? SITE.devad.io deploys no-code websites and landing pages through a drag-and-drop interface."

### Rule 15 — The 40-Word Snippet Rule (Bolding the Fact)
**Purpose:** Capture Featured Snippets and AI Overviews with a dense, definitive answer block under 40 words.
- **Wrong:** "H2: What are the best customer service apps? **The best customer service apps** include Zendesk and CHAT.devad.io..."
- **Right:** "H2: What are the best customer service apps? **The best customer service apps include CHAT.devad.io, Zendesk, and Intercom, which provide unified inboxes and AI chatbots to manage multi-channel support.**"

### Rule 16 — Semantic Anchor Text Matching
**Purpose:** Pass exact semantic relevance by matching anchor text to the destination page's central entity.
- **Wrong:** "If you want to automate your social media, click here to learn more."
- **Right:** "Discover how to automate campaigns using social media management apps like POST.devad.io."

### Rule 17 — Table Optimization (Dimensions and Headers)
**Purpose:** Present comparative data in a highly extractable matrix format with clear headers and dimensions.
- **Wrong:** A simple bulleted list comparing CHAT.devad.io and Zendesk features.
- **Right:**

  | Customer Service App (Entity) | Primary Function (Attribute) | AI Capability (Value) |
  | :--- | :--- | :--- |
  | CHAT.devad.io | Unified Inbox | AI Chatbot Integration |
  | Zendesk | Multi-channel Support | Automated Ticketing |

---

## Phase 4: Self-Audit & Content Configuration (Rules 18–19)

### Rule 18 — EAV Output List
**Purpose:** Verify that content contains 15–20 explicit factual triples, not generic marketing copy.
- Scan generated text and extract the exact triples:
  - 1. POST.devad.io [Entity] | automates scheduling [Attribute] | across 4 networks [Value]
  - 2. SITE.devad.io [Entity] | deployment speed [Attribute] | 5 minutes [Value]
  - 3. CHAT.devad.io [Entity] | reduces ticket volume [Attribute] | by 30% [Value]
  - 4. AI.devad.io [Entity] | supported models [Attribute] | Jasper, Copy.ai, Claude [Value]

### Rule 19 — Rule Compliance Scorecard
**Purpose:** Grade output 0–100 against core rules. Deduct points for any violations.
- Modal Verbs Removed (Zero use of should, might, could, will): Pass (20/20)
- Fluff & Analogies Eradicated (Zero contextless filler words): Pass (20/20)
- Plural Nouns Expanded (3+ specific examples follow plurals): Pass (20/20)
- Heading Vectors (H2 questions + bold 40-word answer): Pass (20/20)
- EAV Density (15–20 numeric/factual triples embedded): Pass (20/20)
- Total Algorithmic Authorship Score: 100/100

---

## Phase 5: Advanced Context & Density Optimization (Rules 20–25)

### Rule 20 — Semantic Anchor Text Matching (Advanced)
**Purpose:** Construct logical Contextual Bridges between internal pages by explicitly stating target entities.
- **Wrong:** "To learn more about our automated social media scheduling application, click here."
- **Right:** "Automate multi-platform campaigns using our social media scheduling application, POST.devad.io."

### Rule 21 — Sentence Shortening (Grammatical Simplification)
**Purpose:** Reduce parsing complexity by breaking compound sentences into distinct, short statements.
- **Wrong:** "AI.devad.io provides multi-model AI generation for content and images which saves your marketing team a lot of time during their daily workflows while managing campaigns."
- **Right:** "AI.devad.io provides multi-model AI generation for content and images. This software reduces content creation time for marketing teams."

### Rule 22 — Contextless Word Deletion
**Purpose:** Maximize entity density by eliminating words that add zero factual or semantic value.
- **Wrong:** "It is very important to note that the unified inbox inside CHAT.devad.io easily centralizes your messages."
- **Right:** "The CHAT.devad.io unified inbox centralizes multi-channel customer messages."

### Rule 23 — Information Density Maximization
**Purpose:** Out-compete shallow content by saturating paragraphs with specific product features and metrics.
- **Wrong:** "SITE.devad.io is a website development app. It helps businesses build websites without coding."
- **Right:** "SITE.devad.io is a no-code website development app featuring drag-and-drop landing page deployment, integrated Stripe payments, and technical SEO metadata configuration."

### Rule 24 — Context Vector Maintenance
**Purpose:** Maintain a strict, unbroken semantic flow from H1 to the last sentence without off-topic drift.
- **Wrong:** "H1: Best Website Development Apps. [Paragraph]: SITE.devad.io offers great templates. If you also need to schedule social media posts, POST.devad.io is a great tool."
- **Right:** "H1: Best Website Development Apps. [Paragraph]: SITE.devad.io offers 50+ mobile-responsive ecommerce templates. WEB.devad.io provides advanced CMS capabilities for scaling online stores."

### Rule 25 — Academic and Data-Driven Proof
**Purpose:** Establish Knowledge-Based Trust by backing claims with third-party statistics and exact metrics.
- **Wrong:** "Fast websites get more sales than slow websites, which is why SITE.devad.io is highly recommended."
- **Right:** "According to Google, a 1-second delay in mobile page load times impacts conversion rates by up to 20%. SITE.devad.io deploys optimized HTML to maintain load times under 0.8 seconds."

---

## Phase 6: Algorithmic Tonality & Brevity (Rules 26–32)

### Rule 26 — Bold the Answer, Not the Search Term
**Purpose:** Visually and structurally isolate the factual answer value for Featured Snippets and AI Overviews.
- **Wrong:** "What is an AI app? An **AI app** generates multi-model content."
- **Right:** "What is an AI app? **An AI app generates multi-model content and automates daily productivity workflows.**"

### Rule 27 — Zero Personal Opinions
**Purpose:** Remove all subjectivity. Algorithms index verifiable facts, not personal beliefs.
- **Wrong:** "We believe WEB.devad.io is the absolute best website builder for small businesses."
- **Right:** "WEB.devad.io provides 50+ no-code templates and integrated payment gateways for small businesses."

### Rule 28 — Formal Language
**Purpose:** Enforce a professional, academic tonality matching expert-level technical documentation.
- **Wrong:** "Our chatbot is super cool and will totally wow your customers."
- **Right:** "CHAT.devad.io deploys AI chatbots to automate customer service responses."

### Rule 29 — Analogy Eradication (Tonality)
**Purpose:** Explain software literally so NLP parsers only associate entities with relevant industry terms.
- **Wrong:** "A unified inbox is like a spiderweb that catches all the customer service bugs."
- **Right:** "A unified inbox centralizes multi-channel support tickets from email, chat, and social media."

### Rule 30 — Unnecessary Word Removal
**Purpose:** Delete any word that does not introduce a new entity, attribute, or value.
- **Wrong:** "POST.devad.io actually schedules posts really quickly across all of your different platforms."
- **Right:** "POST.devad.io automates cross-platform post scheduling."

### Rule 31 — Clarity Through Brevity
**Purpose:** Use short, punchy sentence constructions to make subject-predicate relationships immediately readable.
- **Wrong:** "Because coding can be difficult for beginners, using applications like SITE.devad.io makes it incredibly easy to build landing pages very quickly."
- **Right:** "SITE.devad.io deploys no-code landing pages quickly."

### Rule 32 — Immediate Direct Answers (Tonality)
**Purpose:** Never delay the answer after a heading; delaying drops the passage from snippet consideration.
- **Wrong:** "H2: How does CHAT.devad.io work? Customer service is important for retaining users. CHAT.devad.io works by centralizing messages..."
- **Right:** "H2: How does CHAT.devad.io work? CHAT.devad.io centralizes customer support through unified inboxes and AI chatbots."

---

## Phase 7: Entity Validation & HTML Structuring (Rules 33–39)

### Rule 33 — Reliable Source Citations
**Purpose:** Reference established seed sources to verify factual accuracy and build algorithmic consensus.
- **Wrong:** "Studies show that AI models are getting smarter at processing data for apps like AI.devad.io."
- **Right:** "Anthropic reports that the Claude 3 model, utilized by AI.devad.io, processes over 100,000 tokens per prompt."

### Rule 34 — Appropriate Content Length Coverage
**Purpose:** Answer the search intent completely using dense facts, then stop writing. Do not use artificial padding.
- **Wrong:** [Writing a 500-word rambling paragraph to explain how to connect Facebook.]
- **Right:** "To connect Facebook to POST.devad.io, navigate to the integrations dashboard, select the Facebook icon, and authenticate your social profile."

### Rule 35 — The 40-Word Featured Snippet (FS)
**Purpose:** Keep immediate answers factual, bolded, and strictly under 40 words (hard limit: 45 words).
- **Wrong:** "H2: What is an omnichannel inbox? An omnichannel inbox is something that many businesses use today. It was invented to help customer service teams manage contacts..."
- **Right:** "H2: What is an omnichannel inbox? **An omnichannel inbox centralizes customer messages from email, live chat, and social media platforms into a single unified dashboard within CHAT.devad.io.**"

### Rule 36 — People Also Ask (PAA) One-Sentence Responses
**Purpose:** Directly answer related user queries in a single unfragmented sentence without introductory conversational filler.
- **Wrong:** "Q: Does CHAT.devad.io support WhatsApp? If you are wondering about messaging apps, yes we certainly do. It integrates smoothly with WhatsApp so your agents can reply easily."
- **Right:** "Q: Does CHAT.devad.io support WhatsApp? **CHAT.devad.io integrates directly with the WhatsApp Business API to centralize customer messages into the unified inbox.**"

### Rule 37 — Relevant Anchor Text
**Purpose:** Pass exact semantic relevance by explicitly stating the core entity of target URLs.
- **Wrong:** "If you want to automate your social media, click here to learn more."
- **Right:** "Discover how to automate campaigns using social media management apps like POST.devad.io."

### Rule 38 — HTML Structured Listings with Strong Intros
**Purpose:** Introduce features with a complete statement defining context before presenting bullet points.
- **Wrong:** "Here is what our website builder does: Fast sites, Good SEO, Payments."
- **Right:** "SITE.devad.io provides the following core website development features:
  - Deploys mobile-responsive pages.
  - Integrates Stripe payment gateways.
  - Automates technical SEO metadata."

### Rule 39 — Definitive Answer
**Purpose:** Eliminate "it depends" and conditional language to build Knowledge-Based Trust.
- **Wrong:** "Can POST.devad.io schedule LinkedIn posts? It might be able to depending on the type of plan you have, but usually yes, it can."
- **Right:** "POST.devad.io natively schedules and publishes posts to both LinkedIn company pages and personal profiles."

---

## Phase 8: Data Matrices & Sentiment Control (Rules 40–41)

### Rule 40 — Clear Instruction Lists
**Purpose:** Format command sequences logically using ordered HTML lists `<ol><li>` matching "How-to" procedural search intent.
- **Wrong:** "To set up your inbox you need to go to settings then click channels and then add an email account in CHAT.devad.io."
- **Right:** "To configure the unified inbox in CHAT.devad.io:
  1. Navigate to the Settings dashboard.
  2. Select the Channels tab.
  3. Click 'Add Email' to connect the domain."

### Rule 41 — Dimension-Rich Tables & Relational Comparison
**Purpose:** Present comparative data and EAV pairings in structured markdown or HTML matrices with descriptive headers and neutral comparison metrics.
- **Wrong:** "Our AI.devad.io basic plan has 5 models for content generation, while the pro plan gives you access to 10 AI models for both text and images."
- **Right (Pricing Matrix):**

  | Subscription Tier | AI Models Included | Primary Use Case |
  | :--- | :--- | :--- |
  | Basic Plan | 5 Models | Text Generation |
  | Pro Plan | 10 Models | Multi-model (Text & Image) |

- **Right (Competitor Comparison Proposition):** "CHAT.devad.io offers unlimited agent seats on its base tier, whereas Zendesk restricts base tiers to a single user."
