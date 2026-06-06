# The step plan — worked examples

The step plan is the heart of the specify stage. Decompose the task into steps — **one logical
action each** — and tag each with the cheapest tier that can do it reliably. This file shows how
real tasks decompose, and (just as important) how to resist reaching for a model when a rule fits.

## The tiers, cheapest first

| Tier          | Mechanism                                   | Use for                                           |
|---------------|---------------------------------------------|---------------------------------------------------|
| Deterministic | Plain code (regex, parser, HTTP call)       | Anything expressible as a precise rule            |
| Local model   | A local LLM on the user's machine           | Fuzzy classification, small summaries, extraction |
| Hosted model  | A hosted LLM called with the user's API key  | Steps that genuinely need frontier judgment       |

Try the cheapest tier that can do the job, and escalate a step only when the tier below genuinely
can't handle it. Each tier up also costs availability: a hosted step needs the network and a
provider that hasn't changed its terms; a local step needs a model present; a deterministic step
needs neither. **A model call where a regex would do is a bug.**

Two things to keep straight:

- **Tier is per step, not per app.** One app commonly mixes tiers — deterministic for most steps, a
  local model for the one fuzzy step, a hosted model for a step that needs frontier judgment.
- **Tiers are pinned at authoring time.** The tier you tag a step with is written into `APP.md`,
  and that's the tier it runs at. The run-time app does **not** quietly bump a struggling step up a
  tier. If a local model turns out not reliable enough, that's caught in *validate* and fixed by a
  plan change and rebuild — not a silent run-time fallback.

### The one declared exception

A step whose *input* genuinely varies in shape — a clean PDF vs. a photo of one — may be wired with
an **explicit, opt-in fallback that names both paths in `APP.md`** (e.g. "deterministic PDF text
extraction; if the page has no text layer, fall back to local-model OCR"). A reader of `APP.md` can
see exactly what happens. Anything beyond that single declared fallback means the tier was wrong in
the plan.

## Hearing the deterministic shape under AI vocabulary

People describe the *behavior* they want in AI words because that's the vocabulary they have. Your
job is to hear the underlying shape and propose the deterministic version first.

- *"Categorize my downloads"* → look at the file extension and bucket by type. **Deterministic.**
  Not an LLM.
- *"Find the date in the filename"* → a regex for `\d{4}-\d{2}-\d{2}` and friends. **Deterministic.**
- *"Pull the headlines from these sites"* → fetch + parse the RSS feed or the known DOM selector.
  **Deterministic.**
- *"Tell me when the price changes"* → fetch, extract the price node, compare to last-seen.
  **Deterministic.**
- *"Group similar receipts"* → if "similar" means same vendor string, that's grouping by a parsed
  field. **Deterministic.** Only if "similar" means semantic similarity does it climb a tier.

Escalate to a local model only when you've genuinely failed to find a rule that fits — and to the
hosted tier only when the local model can't do it reliably.

## Worked example 1 — Morning news digest (mixed, mostly deterministic)

Task: *"Every morning, pull the top stories from these five sites and give me a one-page digest."*

| # | Step                                              | Tier          | Why                                             |
|---|---------------------------------------------------|---------------|-------------------------------------------------|
| 1 | Fetch each of the five feeds                       | Deterministic | HTTP GET — a precise rule                        |
| 2 | Parse out headline, link, timestamp               | Deterministic | RSS/DOM parse — structured extraction           |
| 3 | Drop items older than 24h / already seen           | Deterministic | Date compare against last-seen state            |
| 4 | Write a one-page digest file                       | Deterministic | Templated render                                 |

No model needed at all. This app runs every morning offline, forever. **Edge cases to pin:**
partial failure (one feed down → log and continue), empty results (nothing new → "nothing today"
note), idempotency (re-run → don't duplicate), output collision (today's file exists → suffix).

If the user instead asks *"...and summarize each story in two sentences"*, step 4 splits: rendering
stays deterministic, but "summarize" is a small fuzzy job → **local model** (a small text model via
Ollama). Still offline. Only if they want *"a sharp editorial summary of the whole landscape"* does
a step climb to the **hosted balanced** tier.

## Worked example 2 — Receipt filer (deterministic with one declared fallback)

Task: *"Rename and file the receipt PDFs in my Downloads by vendor and date."*

| # | Step                                                   | Tier                | Why                                          |
|---|--------------------------------------------------------|---------------------|----------------------------------------------|
| 1 | Find new PDFs in Downloads                             | Deterministic       | Directory scan + extension filter            |
| 2 | Extract text layer                                     | Deterministic       | PDF text extraction                          |
| 2b| *Fallback:* if no text layer, OCR the page            | Local model (vision)| Declared input-shape fallback (scan vs. PDF) |
| 3 | Pull vendor + date from the text                      | Deterministic       | Regex/known-format extraction first…         |
| 4 | Rename `<vendor>-<date>.pdf`, move to filed folder    | Deterministic       | String build + file move                      |

Step 2b is the **one allowed exception**: the input genuinely varies in shape (a born-digital PDF
vs. a phone photo saved as PDF), and both paths are named in `APP.md`. If vendor/date extraction in
step 3 turns out too messy for regex across real receipts, that step escalates to a **local model**
extraction — recorded as a plan change in `APP.md`, caught during *validate*, never a silent
run-time guess.

## Worked example 3 — Contract reviewer (genuinely needs the hosted top tier)

Task: *"Read a contract PDF and flag unusual or risky clauses."*

| # | Step                                          | Tier                  | Why                                            |
|---|-----------------------------------------------|-----------------------|------------------------------------------------|
| 1 | Load and extract the contract text            | Deterministic         | PDF text extraction                            |
| 2 | Split into clauses                            | Deterministic         | Structural/heading split                       |
| 3 | Judge each clause for risk and unusualness     | Hosted — **top** rung | Long-context legal reasoning needs frontier    |
| 4 | Render a flagged-clauses report               | Deterministic         | Templated render                               |

Step 3 is the rare case that earns the top hosted rung (Opus / flagship / Pro): fifty pages of
context, real legal judgment, consequences to a wrong call. Everything around it stays
deterministic.

## Cheapest-first keeps going inside the hosted tier

A hosted step is a **provider and a model**, and the instinct to pick the cheapest thing that works
doesn't stop at the tier boundary. Frontier providers ship roughly three rungs:

- **Top** (Anthropic Opus, OpenAI flagship, Gemini Pro) — frontier judgment: long-context
  reasoning, multi-step plans, a fifty-page contract.
- **Balanced** (Anthropic Sonnet, OpenAI mid, Gemini Flash) — **the default for most hosted
  steps.** Drafting an email, an extraction a local model fumbled, a moderate summary. Fast, a
  fraction of top-tier cost.
- **Fast/cheap** (Anthropic Haiku, the smallest hosted model) — high-volume or latency-sensitive
  steps where the judgment bar is low but a local model still wasn't reliable enough.

Default a hosted step to **balanced** and step up only when the step's description tells you it
needs frontier judgment. Calling the biggest, slowest, priciest model to rewrite a subject line is
the hosted-tier version of using an LLM where a regex would do — except the waste lands on the
user's bill every single run.

And because model identifiers churn — providers ship new versions and retire old ones on their own
schedule — **don't pin an app to a model string from memory.** Decide the tier, confirm the current
identifier with the user or the provider's model list, and write the verified `<provider>/<model>`
string into `APP.md`.

## Recording the plan in APP.md

Each step in `APP.md` records: the action, its tier, and (for local/hosted) the named model. For a
declared fallback, both paths appear. The plan readback to the user mirrors this list — numbered
steps, each tagged deterministic / local / hosted with the model named — so the tier conversation
happens before any code exists.
