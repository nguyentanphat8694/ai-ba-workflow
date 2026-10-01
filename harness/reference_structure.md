# Spec Structure Reference

The target section structure every spec in this harness must use, starting
from the `rewrite` step onward. If a section has no source content, write
"Not yet defined" — never delete the heading.

## Sections 1–10

| # | Section | What goes here |
|---|---|---|
| 1 | Metadata | Owner, Reviewer, Approver, Approval date, Ticket ID, Dev/Designer in charge, Change history, Table of Contents (a real linked list — one Markdown link per section, `[2. Overview](#2-overview)` — never a placeholder sentence), Source input (relative link) |
| 2 | Overview | 1–2 plain paragraphs: what the feature does, who it's for. No marketing language. |
| 3 | Defined Scope | What we ARE building, and just as important, what we are NOT building. |
| 4 | Features and Behaviors (FR) | Per feature: **Requirement ID** (`FR-<NNN>`, sequential, never reused/renumbered), trigger, inputs, what it does, what it returns, what happens on error. Behaviors, not wishes. |
| 5 | Edge Cases and Error States | Missing input, invalid input, missing dependency, failed call — per feature, referencing its FR ID as `FR-<NNN>-E<n>`. |
| 6 | Auth and Permissions | Who can do what — a table with explicit qualifiers ("own only", "within workspace"). |
| 7 | Data Model & Data Dictionary | Per entity: field name, type, required/optional, validation rules, relationships. |
| 8 | Integrations & Data Flows (if any) | What flows in/out of each integration, expected response, retry/failure behavior. |
| 9 | UI/UX Notes (optional) | Brief layout/interaction notes — not full visual design. |
| 10 | Success Metrics / NFRs (optional) | How we'll know it worked; performance/scale/security targets if any. |

## Clarity rules (apply from `ba_review` onward)

- Be specific: exact ranges, formats, units ("integer 1–120", not "the
  user's age").
- Write permissions in the affirmative ("Users can only access data within
  their own workspace") — not as a prohibition only.
- Avoid passive voice for anything with an actor, trigger, or failure path.
  State who does what, when, and what happens on error.
- Distinguish required vs optional explicitly, for every field.
- Use one consistent term per actor/concept; define domain terms on first
  use.
- For any non-trivial business rule (pricing, permissions, scoring), give
  at least two examples: one where it applies, one where it doesn't.
- Don't spec visual design — link to a design reference or leave it open.
- For third-party integrations, define only what flows in/out (payload,
  response, timeout/retry) — not the vendor's internals.

## Sentence craft (making it read sharp, not just complete)

The clarity rules above govern *content*. These govern the *prose itself*
— the difference between a technically-complete sentence and one that
reads like an experienced BA wrote it.

- **Lead with actor + action; push the condition to the end.**
  ❌ "In the case where the discount value exceeds the item price, the
  system rejects it." ✅ "The system rejects the discount if its value
  exceeds the item price."
- **One sentence, one idea.** Split anything joined by "and" that
  describes two different behaviors, triggers, or outcomes.
- **Strong verbs, not noun-heavy phrasing.** ❌ "The system is responsible
  for validation of the input." ✅ "The system validates the input."
- **Cut filler that adds no information**: "basically", "simply", "in
  order to" → "to", "is able to" → "can", "there is a need for" → drop it
  entirely.
- **Present tense throughout** for system behavior — not "will do", not
  "should do", unless the sentence is genuinely describing a future
  business rule (e.g. a planned rollout phase).
- **No hedging outside an explicit `[OPEN: ...]` tag.** If a sentence
  needs "generally", "typically", or "in most cases" to be true, that's a
  sign it's actually two rules hiding in one sentence — split them, or
  flag the ambiguous one open instead of softening the language around it.
- **Parallel structure** across list items and across requirements of the
  same kind — the Trigger line for FR-001 and FR-002 should read the same
  grammatical shape, not one "when the user..." and the other "if a
  request is made...".
- **Numerals for anything countable or technical** (5MB, not "five
  megabytes"; 2 seconds, not "a couple of seconds").
- **No buried double negatives.** ❌ "Cannot be hidden unless not
  out of stock." ✅ Rewrite plainly, even if longer.

## Cross-file links

Any reference to another file in this project uses a relative Markdown
link, never an absolute path.
