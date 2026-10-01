# Core Principles

These rules apply across every step in this harness. Read this file in full
before running `ba_review` or `team_review`. `rewrite` and `estimation` use
only the relevant subsection noted below.

---

## 1. The citation test (applies to `ba_review` and `team_review`)

This is the actual rule. Everything else in this file is a reference aid,
not a substitute for this test.

Before writing *any* factual claim into the spec — a field's
required/optional status, a default value, an entity relationship, a
permission scope, a word like "confirmed", or a value written directly into
a table cell — ask:

> **Can I point to the exact sentence in the source, or the exact answer
> the user gave me, that says this?**

- **Yes** → write it as settled content.
- **No** → it is an assumption, full stop, regardless of how obvious,
  standard, or low-risk it seems. Flag it `[OPEN: <question>]` **at the
  exact point it appears** — inline in a sentence, inside a table cell, in
  an entity field definition, anywhere. Never let a table cell, a
  parenthetical, or a schema field state something as fact just because
  surrounding prose hedges it elsewhere.

This test has no exception list. It applies even when you're confident of
the real-world answer ("VND has no decimal places", "percentages cap at
100%"). Domain convention and common practice are not a substitute for the
source or the user confirming it for *this* spec.

**Formatting, every time, no exceptions:** wrap the tag in backticks when
you write it into the document, so it renders as inline code and stands
out from surrounding prose — `` `[OPEN: ...]` ``, or
`` `[OPEN (<Persona>): ...]` `` in `team_review`. Never write a bare,
un-backticked `[OPEN: ...]`. `harness/scripts/validate_structure.py`
checks this on every output file; a bare tag is a FAIL, not a style nit.

Do not treat the trap list in section 3 as a checklist to "clear" and then
stop looking — it names patterns that come up often so you recognize them
faster. Anything that fails the citation test gets `[OPEN: ...]`, matching
trap or not.

---

## 2. Resolving `[OPEN: ...]` items

Applies identically to `team_review`'s `[OPEN (<Persona>): ...]` tags — the
persona label is just an added source attribution, not a different
mechanic.

A human can resolve an open item two equally valid ways. Recognize both —
never assume only one is acceptable, and never re-flag an item that was
resolved by either method.

- **Method A — inline replacement:** the `[OPEN: ...]` tag in the body is
  replaced directly with the resolved answer, and the matching entry is
  removed from the end-of-document list.
- **Method B — answer in the list:** the inline tag stays untouched, and
  the answer is written directly under the matching entry in the
  Open Questions list (e.g. `**Answer:** ...`).

An item is resolved if either method was used. If answered by both and
they disagree, the list entry's answer is authoritative — note the
discrepancy for the human, don't block on it.

**Matching a list entry to its inline tag:** entries are generated in the
same order the tags appear in the body, so entry *N* corresponds to the
*N*th tag. If order is ambiguous, match by comparing question text.

---

## 3. Common assumption traps (reference, not exhaustive)

| Trap | What it looks like | What to flag |
|---|---|---|
| **Terminology drift** | Source uses multiple terms for what looks like the same actor (e.g. "owner", "admin", "chủ quán") | `[OPEN: Are "X" and "Y" the same role, or distinct?]` |
| **State model collapse** | Overlapping terms for one status ("hidden", "out of stock", "inactive") get flattened into one boolean | `[OPEN: Are "X" and "Y" the same state or distinct? Define allowed transitions.]` — do not flatten |
| **Grouped-attribute bleed** | Source lists several attributes in one sentence ("each item has a name, price, image, description") — this proves the fields *exist*, not that they're all *required* | `[OPEN: Is <field> required or optional? Source lists it as an attribute but doesn't state its requirement status.]` — check each field individually |
| **Entity existence implies scope** | Creating an entity with an auto-generated ID silently assumes the system supports *multiple* instances (multi-tenant), even if the source only ever describes one implicitly | `[OPEN: Does this serve a single X, or many? This affects whether isolation between them is a requirement at all.]` |
| **Hedge reified as fact** | Source says "probably" / "likely" / "chắc" for a feature, and a narrower related question gets answered — that does not resolve the original hedge | `[OPEN: Source called this "probably" needed, not confirmed — is it firmly in scope, a fast-follow, or still undecided?]` |
| **Answer over-extension** | A resolved answer names one specific actor, and it gets applied to a broader group without a matching answer for the rest | `[OPEN: The answer covers <role X> — does it extend to <role Y>, or is that still open?]` |
| **Referenced-but-undefined action** | An edge case mentions an action (delete, cancel...) that has no requirement of its own defining it | `[OPEN: Is <action> in scope at all? Source never describes it.]` — add a stub requirement rather than only patching the edge case |
| **Actor scope assumption** | A feature's actor is stated generically ("search is needed") and defaults to "everyone" or "customer only" without the source saying so | `[OPEN: Does <feature> apply to customers, admins, or both?]` |
| **Schema silently picks an answer** | An `[OPEN: ...]` question lists several possible answers, but the field's actual type next to it already rules one out (e.g. a single nullable FK can't represent "many") | Flag this explicitly — either widen the field or narrow the question to match what it can represent |
| **Observed-state-as-fact** | You looked at (or the source references) an external artifact — a Figma link, a screenshot, a live page — and you write down what it currently shows or how it currently behaves (e.g. "shows an unauthenticated embed prompt") as if that were a specified requirement | `[OPEN: The linked <artifact> currently shows <observation> — is that the intended state, incidental to how it's being viewed right now, or not something this spec should describe at all?]` — an incidental rendering/access state of a link is never source content on its own; it fails the citation test the same as any other unconfirmed claim |

---

## 4. Internal consistency (run once, at the end of `ba_review`/`team_review` finalize)

Re-read the whole finished document once, specifically for contradictions
*between* sections:

- Does any table cell or parenthetical assert a scope/value as settled
  while an `[OPEN: ...]` elsewhere says the same thing is unresolved?
- Does any entity field's shape already rule out an option that a nearby
  open question still lists as available?
- Does any default value or required/optional label lack a traceable
  source sentence or resolved answer?

If yes to any: fix it before presenting the finalized document.

---

## 5. Fidelity rule for `rewrite` (structure only, no questions)

`rewrite` does **not** use the citation test above and never writes
`[OPEN: ...]`. Its only job:

- Map the source content into the section structure in
  `reference_structure.md`.
- Preserve the source's meaning exactly — do not add, remove, reinterpret,
  or resolve any ambiguity.
- Where a section has no corresponding content in the source, write
  "Not yet defined" and move on. Do not guess. Do not ask.
- Finding and flagging gaps is `ba_review`'s job, not `rewrite`'s.

**Sentence craft is allowed here — meaning is not.** You may apply
`reference_structure.md`'s Sentence craft rules (split a run-on sentence,
turn passive into active, cut filler) as long as the rewritten sentence
still asserts exactly the same actor, action, and condition as the
source — nothing added, nothing dropped, nothing made more or less certain.
- ❌ **Meaning changed** (don't do this): source says "Cancellations are
  processed within 3–5 days" (no actor stated) → rewritten as "The system
  cancels within 3 days" (actor invented, range narrowed to one number).
- ✅ **Sentence craft only** (this is fine): source says "Cancellations
  are processed within 3–5 days" → rewritten as "Cancellations are
  processed within 3–5 days" left as-is if the actor is genuinely absent
  from the source (do not invent one) — but "The user can view their
  order status, and if they cancel it, a refund is issued within 3–5
  days" → split into "The user can view their order status. If they
  cancel it, a refund is issued within 3–5 days." (same two facts, one
  idea per sentence, nothing changed about who does what or the range).
If you're unsure whether a rewrite changed the meaning, don't make it —
leave the sentence closer to the source's original phrasing instead.

**Do not add observations about a linked artifact's current state.** If
the source contains a link (a Figma URL, an external doc, an image), copy
the link as-is. Never add a parenthetical describing what that link
currently shows or how it currently behaves when opened (e.g. "shows an
unauthenticated embed with a 'Connect your account' prompt") — that is a
new claim about the state of an external resource at the moment you or
someone looked at it, not source content, and it can go stale or be
wrong immediately. `rewrite` cannot flag this `[OPEN: ...]` (it never
writes that tag), so the only correct move is to leave it out entirely;
if it's genuinely worth asking about, that's `ba_review`'s job, not
`rewrite`'s.
