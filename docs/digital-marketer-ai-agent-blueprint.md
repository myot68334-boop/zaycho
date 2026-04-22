# Digital Marketer AI Agent Blueprint

This blueprint is for building a practical AI agent stack that a professional digital marketer can use every day on a local machine with Ollama, Telegram, and automations.

## Goal

Build one assistant that can help with:

- campaign ideas
- ad copy and hook generation
- SEO keyword clustering
- content calendar planning
- customer reply drafting
- landing page review
- offer positioning
- basic analytics summaries
- Telegram-based daily assistant workflows

## Recommended Stack

### Core model layer

- `qwen2.5:7b`
  Best lightweight default for bilingual marketing drafting.
- `qwen2.5:14b`
  Better for strategy, tone control, and long-form analysis if hardware allows.
- `qwen2.5vl:7b`
  Use for screenshot review, ad creative critique, and landing page feedback.

### Workflow layer

- `Ollama`
  Local model runtime.
- `n8n`
  Agent workflows, scheduling, Telegram automation, and tool chaining.
- `Telegram Bot`
  Fast mobile control surface for prompts, alerts, reports, and test messages.
- `ZayCho frontend/admin`
  Optional internal dashboard for marketer actions and product context.

### Data layer

- product catalog
- campaign notes
- offer library
- keyword lists
- customer FAQ / support snippets
- weekly reports

## Agent Roles

Instead of one vague agent, use one system with 5 clear roles.

### 1. Campaign Strategist

Used for:

- campaign angles
- positioning
- audience pain points
- promotion concepts

Output examples:

- 3 campaign concepts
- target audience summary
- best hook by segment

### 2. Copywriter

Used for:

- headlines
- ad primary text
- CTA variants
- product descriptions
- Telegram broadcast copy

Output examples:

- 10 hooks
- 5 ad copies
- 3 landing page hero options

### 3. Content Planner

Used for:

- weekly posting ideas
- social calendar
- content buckets
- launch sequences

Output examples:

- 7-day plan
- 30-day content calendar
- post idea matrix by product/category

### 4. Support + Sales Assistant

Used for:

- customer replies
- product recommendations
- objection handling
- upsell / bundle suggestions

Output examples:

- Telegram reply drafts
- personalized product suggestions
- FAQ responses

### 5. Analyst

Used for:

- report summaries
- KPI interpretation
- creative test notes
- next-step recommendations

Output examples:

- weekly report summary
- what worked / what failed
- next 3 actions

## Daily Operating Flow

### Morning

1. Review yesterday's orders, traffic, and messages
2. Ask the Analyst agent for a summary
3. Ask the Strategist for today's focus
4. Ask the Content Planner for today's posts

### Midday

1. Generate ad variations
2. Review landing page or product page
3. Draft Telegram or social promotional message

### Evening

1. Summarize customer questions
2. Update FAQ / support prompts
3. Save campaign learnings into a notes file or database

## Core Telegram Commands

These are the most useful marketer-facing commands to add.

- `/help`
  Show commands and usage examples.
- `/menu`
  Category menu with quick buttons.
- `/shop`
  Open storefront.
- `/ideas`
  Generate campaign ideas for a product or audience.
- `/copy`
  Generate ad copy variants.
- `/plan`
  Generate a content plan.
- `/report`
  Summarize recent performance data.
- `/offer`
  Suggest a bundle, discount, or promotion angle.

## Message Parsing Rules

The assistant should parse user messages into structured intent.

### Target fields

- `budget`
- `category`
- `style`
- `skin_concern`
- `color`
- `audience`
- `goal`
- `platform`

### Example prompts

- `black office outfit under 8000 yen`
- `oily skin skincare under 5000 yen`
- `gift idea for teenage girl`
- `write 5 Facebook ad copies for lip tint`
- `give me a 7-day launch content plan`

### Parsing behavior

- detect budget from numbers and currency terms
- detect category from catalog categories
- detect style from words like `casual`, `office`, `street`, `gift`
- detect skin concern from words like `oily`, `dry`, `sensitive`, `acne`
- detect color from product color vocabulary
- detect marketing task from words like `copy`, `ideas`, `plan`, `report`

## Telegram UX Blueprint

### `/menu`

Use inline buttons like:

- `Skincare`
- `Makeup`
- `Tops`
- `Bottoms`
- `Sets`
- `Accessories`
- `Shop Now`
- `Help`

### Rich reply style

Each reply should:

- greet lightly
- confirm what the user asked for
- present 2-3 useful recommendations
- explain why each item fits
- invite refinement

### Good Burmese tone

Prefer:

- polite but not stiff
- helpful sales tone
- short explanations
- confidence without sounding robotic

Good pattern:

`ဒီ budget နဲ့ ကိုက်မယ့် item လေးတွေ ရွေးပေးထားပါတယ်ရှင်`

Avoid:

- too literal machine phrasing
- long technical English-heavy output
- overly generic “try this” with no reason

## Suggested n8n Workflows

### 1. Telegram Marketing Assistant

Trigger:

- Telegram webhook

Flow:

- parse intent
- call Ollama
- enrich with catalog data
- return reply

### 2. Daily Marketing Brief

Trigger:

- every morning

Flow:

- collect recent orders
- collect new customer messages
- summarize trends
- send Telegram daily brief

### 3. Content Calendar Generator

Trigger:

- manual `/plan` command or scheduled weekly run

Flow:

- collect featured products
- select campaign theme
- ask Ollama for calendar
- send result to Telegram or save to file

### 4. Ad Copy Generator

Trigger:

- manual `/copy` command

Flow:

- user gives product + audience + platform
- Ollama creates hooks, headlines, primary text, CTA

### 5. Product Recommendation Engine

Trigger:

- Telegram text message

Flow:

- parse budget/category/style
- score products
- generate reply with explanation

## Prompt Design

### Strategy prompt

Use when asking for campaign direction:

`Act as a senior digital marketing strategist. Recommend 3 campaign angles for this product and audience. Focus on conversion, emotion, and offer clarity.`

### Copy prompt

`Act as a conversion copywriter. Write 5 short ad variants in natural Burmese with one clear hook, one product benefit, and one CTA.`

### Support prompt

`Act as a warm Burmese sales assistant. Recommend products based on the user's budget, category, and style. Be concise, helpful, and persuasive.`

## Data You Should Feed the Agent

The agent becomes much better if you give it:

- clean product catalog
- current promotions
- audience profiles
- customer FAQ
- top objections
- top-performing content
- failed content notes
- price bands by category

## Best Practices

- keep prompts short and specific
- always include budget if product recommendations are needed
- use category names that match your database
- keep a reusable offer library
- log common customer questions for future automation
- test Burmese phrasing on real conversations and refine often

## Phase-by-Phase Build Plan

### Phase 1

- Telegram shopping assistant
- `/help`, `/menu`, `/shop`
- budget/category/style parsing

### Phase 2

- campaign idea command
- copywriting command
- product-aware support recommendations

### Phase 3

- daily brief automation
- weekly content planner
- campaign performance summary

### Phase 4

- screenshot review with vision model
- landing page critique
- creative audit workflows

## Success Metrics

Track whether the agent improves:

- reply speed
- consistency of sales replies
- time saved in content planning
- ad drafting speed
- customer engagement from Telegram
- recommendation relevance

## Immediate Next Upgrades

If you continue from the current ZayCho setup, the next highest-value tasks are:

1. add Telegram commands for `/ideas`, `/copy`, `/plan`
2. save recent user interests for better follow-up
3. connect report uploads or spreadsheet summaries
4. add image/screenshot review with `qwen2.5vl`
5. build a daily Telegram marketing brief automation
