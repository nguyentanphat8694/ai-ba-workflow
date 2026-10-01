# Step 4 — Estimation (T-shirt sizing)

## Required reading
None of `principles.md`, `review-checklist.md`, or `persona-focus.md`
apply to this step — do not read them for this step. This is intentional,
not an oversight: this step never asserts a fact as settled (it proposes
sizes explicitly labeled as assumptions) and never writes `[OPEN: ...]`
tags, so the citation test has nothing to enforce here. When a requirement
is genuinely too unclear to size, the rule below (step 4) has you ask the
user directly instead.

`reference_structure.md`'s **Sentence craft** section does apply, but only
to the prose you write — the "Key assumption" and "Key risk/unknown"
columns, and any note outside the table itself. It does not apply to the
table's structural cells (FR ID, size letter) — those are labels, not
sentences. Read that section now if you haven't already this session.

## Role
You are giving a rough, pre-technical-design estimate — not a commitment.
This step is lighter than `ba_review`/`team_review`: no inline `[OPEN: ...]`
tags, no draft/approve-loop/finalize split. It's a direct conversation that
ends in a sizing table.

## Base file
Resolved by the orchestrator per `ORCHESTRATOR.md` §"Base-file
resolution": the shared `final_document` for this input, if one exists —
else the raw input directly. There is no `rewrite`-only fallback for this
step; if `final_document` doesn't exist, you're sizing off unreviewed raw
material.

## What to do
1. Read the base file completely.
2. **If the base file is the raw input (no `final_document` exists):**
   say so explicitly before sizing anything — this spec was never
   structured or reviewed, so requirement boundaries may not be clean and
   sizes carry more risk than usual. Do the best-effort breakdown into
   FR-like items anyway (numbering them provisionally, e.g. `FR-001` per
   distinct behavior you can identify), but expect to ask more questions
   than you would off a finalized spec.
3. Break the spec down by `FR-<NNN>` (or provisional item, per step 2).
4. For each: propose a T-shirt size (**S** / **M** / **L** / **XL**),
   stating the key assumption behind that size and the key risk/unknown
   that could shift it.
5. If a requirement's scope is genuinely too unclear to size — because the
   spec still carries an unresolved `[OPEN: ...]` that materially affects
   effort, because two plausible readings of the same requirement would
   size completely differently, or because a dependency it needs isn't
   defined anywhere in the base file — **stop and ask the user directly**
   before sizing that item. Don't silently pick the middle size, and don't
   silently pick one reading over another to move on.
6. Give an overall range across all requirements, not a false-precision
   total.
7. Call out anything that needs a technical spike before a firmer estimate
   is possible.

## Output
A table:

| FR | Size | Key assumption | Key risk/unknown |
|---|---|---|---|

Followed by the overall range, spike flags (if any), and a short list of
any question you had to ask the user to size a requirement (for
traceability — lighter than the full Resolved Questions section in the
other steps, since this isn't a gap-finding pass).

Explicitly label the output: *"Rough estimate, pre-technical-design — not
a commitment."*

Write to `outputs/[estimation]-<basename>-[<timestamp>].md`.

## After writing
This is the last step in the pipeline. After writing, update state, mark
`estimation` done, and tell the user the pipeline for this input is
complete — offer to start a new input or revisit any earlier step.
