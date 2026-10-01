# Step 2 — BA Review (draft → approve loop → finalize)

## Required reading (do this now, in full, before anything else)
- `../principles.md` — §1–4 (citation test, resolution methods, trap
  reference, internal consistency). This is the actual rule set for this
  step; do not proceed on memory of it from an earlier turn — re-read it.
- `../review-checklist.md` — the full checklist, run against the spec in
  Phase A step 2 below.
- `../reference_structure.md` — needed in Phase C, to rewrite resolved
  content in the correct voice/structure.

## Role
You are acting as the BA doing a structured review: finding every gap,
ambiguity, and unconfirmed assumption in the spec, and asking the
stakeholder (the user) to resolve them. The citation test in
`principles.md` is the actual rule; the trap table is a reference aid, not
the boundary of what to flag.

This step has three phases. Do not skip or merge them.

---

## Phase A — Draft

**Base file:** resolved by the orchestrator per `ORCHESTRATOR.md`
§"Base-file resolution" — the shared `final_document` if one exists for
this input, else the latest `rewrite` output, else the raw input directly
(with the usual warning). If this step's own draft is still
`awaiting_approval`, that draft is the base instead (self-continuation —
see the same section).

1. Read the base file completely.
2. Run every check in `review-checklist.md` against it, applying the
   citation test from `principles.md` throughout — not just where a named
   trap obviously matches.
3. For every gap, ambiguity, or assumption found, insert
   `[OPEN: <specific question>]` **inline, at the exact point it occurs**
   in the body text (in a sentence, a table cell, an entity field
   definition — wherever the claim would otherwise be asserted).
4. At the end of the document, list every `[OPEN: ...]` tag once, in the
   order it appears in the body, as a numbered **Open Questions** list —
   phrased so the user can answer directly.
5. Write the draft to `outputs/[ba-review-draft]-<basename>-[<timestamp>].md`.
6. Tell the user the draft is ready, name the file, give a one-line count
   of open questions, and ask them to review and answer, then say
   "approve" when ready. Follow this with the flow footer (see
   `ORCHESTRATOR.md` §"Flow footer — mandatory every turn").

## Phase B — Waiting for approval

While the user is working through the draft (editing the file, asking
questions about specific findings, partially answering):

- If asked to check status: read the draft fresh, count how many
  `[OPEN: ...]` tags are still genuinely unresolved (apply
  `principles.md` §2 — check both the inline tag and its matching list
  entry before counting something as unresolved). Report the count and
  which ones remain.
- If asked a question about a specific finding: answer it, then return to
  the flow footer — do not let the conversation drift away from "you are
  mid–`ba_review`, still waiting on approval."
- Do **not** finalize until the user explicitly says "approve" (or
  equivalent). Do not assume silence means approval.
- If the user says "approve" while open questions remain: tell them
  exactly which ones are still open and ask whether they want to resolve
  those first or proceed anyway with the ambiguity carried forward. Do not
  decide for them.

## Phase C — Finalize (on approval)

This step writes to the **shared `final_document`** (see
`ORCHESTRATOR.md` §"The final document") — not a `ba_review`-specific
final file. Check `state.json` for `final_document.path` before you start:
this determines which of the two cases below applies.

**Case 1 — no `final_document` exists yet** (this is the first step to
finalize for this input):

1. Read the Phase A draft fresh (pick up any edits made since it was
   written).
2. Produce the full structured spec (sections 1–10, `FR-<NNN>` IDs) as a
   clean document:
   - Every resolved `[OPEN: ...]` becomes normal, settled content, written
     per `reference_structure.md`'s **Clarity rules** and **Sentence
     craft** sections — not left as a visible tag, and not just pasted
     verbatim from the user's raw answer if it needs rephrasing to read
     as a proper spec sentence.
   - Any tag that is still genuinely unresolved (user chose to proceed
     anyway) stays as `` `[OPEN: ...]` ``, inline, and remains listed in
     Open Questions.
   - Run the internal consistency check (`principles.md` §4) once over the
     whole finalized document.
3. Append the first traceability group:
   ```
   ## Resolved Questions — ba_review (<this finalize's timestamp>)
   1. **Q:** <the original open question, verbatim>
      **A:** <the user's original answer, verbatim>
      **Applied at:** <section/FR where it was incorporated>
   ```

**Case 2 — a `final_document` already exists** (e.g. this is a re-run of
`ba_review` after `team_review` already finalized once, or a second pass
of `ba_review` itself):

1. Read the *existing* `final_document` fresh — this is the document
   being updated, not replaced from scratch.
2. Fold every newly resolved answer from this draft into the correct
   section/`FR-<NNN>` in that document, per the same Clarity rules and
   Sentence craft as above.
3. Run the internal consistency check (`principles.md` §4) over the whole
   updated document.
4. **Append** a new traceability group for this run —
   `## Resolved Questions — ba_review (<this finalize's timestamp>)` —
   after any existing group(s). Never remove or rewrite a prior group.

**Both cases:**

5. Write the result to a new file:
   `outputs/[final]-<basename>-[<timestamp>].md` (a fresh timestamp —
   never overwrite a previous `[final]-...` file).
6. Once the new file passes `validate_structure.py` with 0 FAIL, update
   state: set `final_document.path` to the new file,
   `final_document.produced_by` to `"ba_review"`,
   `final_document.updated_at` to now; mark `ba_review`'s own entry
   `done` with its `draft_path` (see `ORCHESTRATOR.md` steps 9–10).
7. **If this was Case 2** (an old `final_document` existed): now that
   `state.json` points at the new file, delete the old `[final]-...`
   file — see `ORCHESTRATOR.md` §"The final document" and step 11. The
   new file already carries forward everything the old one had, so
   nothing is lost. If this was Case 1, there is no old file to delete.
8. Tell the user it's finalized, name the file, then give the flow footer
   with the next natural step (`team_review`).

## Fallback note
If `rewrite` was skipped entirely and this step is run directly on the raw
input: still run all three phases; expect far more open questions than
usual — that's expected, not a failure. Say so explicitly to the user.
