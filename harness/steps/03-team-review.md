# Step 3 — Team Review (draft → approve loop → finalize)

## Required reading (do this now, in full, before anything else)
- `../principles.md` — §1–4. The citation test applies here too, for the
  same reason as in `ba_review`: do not assert a finding as settled fact
  without a traceable source.
- `../persona-focus.md` — the full file, all 5 personas. Re-read it now
  even if you ran `ba_review` earlier in this session — do not rely on
  memory of a similar-sounding file.
- `../reference_structure.md` — needed in Phase C, same as `ba_review`.

## Role
You are simulating a cross-functional review meeting: Backend, Frontend,
QA, Design/UX, and Product/Data each reading the finalized spec through
their own lens, raising concerns as the same kind of open questions
`ba_review` raises — but from an implementation/delivery angle, not a
requirements-completeness angle.

Same three-phase structure as `ba_review` (`02-ba-review.md`). This file
only notes what's different.

---

## Phase A — Draft

**Base file:** resolved by the orchestrator per `ORCHESTRATOR.md`
§"Base-file resolution" — the shared `final_document` if one exists for
this input, else the latest `rewrite` output, else the raw input directly
(with the usual warning). This is the same rule `ba_review` uses; if
`ba_review` was skipped entirely, `team_review` still resolves correctly
on its own. Never a step's own draft, and never the input to a step that
hasn't been approved yet.

1. Read the base file completely.
2. Go through the 5 personas **one at a time, in order** — Backend
   Engineering, Frontend Engineering, QA/Testing, Design/UX, Product/Data.
   For each, actually re-apply that persona's lens from `persona-focus.md`
   to the spec before moving to the next one — do not produce one merged
   pass of findings and sort them into buckets afterward.
3. Anchor every finding to a specific `FR-<NNN>` or section. No floating
   concerns.
4. Tag each finding's severity: **[Blocking]** (would stop implementation
   or require rework), **[Needs discussion]** (should be resolved before
   dev starts, doesn't block sign-off), or **[Note]** (worth logging).
5. When a finding needs a stakeholder decision (not just an engineering
   choice), phrase it as an inline `[OPEN (<Persona>): <question>]` in the
   relevant spec section — same mechanic as `ba_review`'s `[OPEN: ...]`,
   plus the persona tag so the question's origin is traceable — and list
   it in the end-of-document Open Questions list with the same tag.
6. Add an **Overall Verdict** at the end of the draft:
   `🔴 Not ready` / `🟡 Ready with conditions` / `🟢 Ready to estimate`,
   with the blocking items listed by persona + FR.
7. Write to
   `outputs/[team-review-draft]-<basename>-[<timestamp>].md`.
8. Tell the user the draft is ready, name the file, summarize the verdict
   and blocking count, ask for review/approval. Flow footer follows.

### Output format — one section per persona, always

The draft must contain all 5 persona headings, in this exact order, every
time — never omit one:

```
## Backend Engineering
## Frontend Engineering
## QA / Testing
## Design / UX
## Product / Data
```

Under each heading, list that persona's findings (`**[Severity]** FR-NNN —
summary`, one line each). If a persona genuinely has nothing to add for
this spec, write "No findings from this lens for this spec." under its
heading — never delete the heading or skip it silently. A missing section
is indistinguishable from "forgot to check it"; an explicit "no findings"
line is not.

## Phase B — Waiting for approval
Same mechanics as `ba_review` Phase B. Status checks re-scan for genuinely
unresolved `[OPEN (<Persona>): ...]` tags per `principles.md` §2 (the
persona tag doesn't change how resolution is detected — Method A/B both
still apply).

## Phase C — Finalize (on approval)

Same two-case mechanics as `ba_review` Phase C (`02-ba-review.md`) — this
step writes to the **same shared `final_document`**, never a
`team_review`-specific final file. Check `final_document.path` in
`state.json` first:

**Case 1 — no `final_document` exists yet** (`team_review` is running
before any `ba_review` finalize, e.g. `ba_review` was skipped entirely):
build the full structured spec (sections 1–10, `FR-<NNN>` IDs) from the
Phase A base file, folding in every resolved answer, exactly as
`ba_review`'s Case 1 does.

**Case 2 — a `final_document` already exists:** read it fresh, fold this
draft's newly resolved answers into the correct section/`FR-<NNN>` in
place, per `reference_structure.md`'s **Clarity rules** and **Sentence
craft** sections (same as `ba_review`).

**Both cases**, in addition to what `ba_review` does:
- Run the internal consistency check (`principles.md` §4) once over the
  whole document.
- **Carry the 5 persona-findings sections and the Overall Verdict into the
  finalized document itself.** These are part of the finalized spec's
  permanent record, not just this draft's scratch findings — they must
  never be silently dropped when writing to `outputs/[final]-...`.
  Position them directly after Section 10 and before any traceability
  groups.
  - **Case 1 (first team_review finalize for this input):** copy this
    draft's `## Backend Engineering` / `## Frontend Engineering` /
    `## QA / Testing` / `## Design / UX` / `## Product / Data` sections
    and the `## Overall Verdict` section into the final document, as-is.
  - **Case 2 (the final document already has persona sections from an
    earlier team_review finalize):** update the *existing* sections in
    place — do not append a second copy of the 5 headings. For every
    finding this run resolved, prefix it `**[Resolved]**` and keep the
    original finding text (don't delete it — resolution history matters).
    Add any new findings from this run's draft under the matching
    persona. Then recompute the `## Overall Verdict`: 🔴 if any
    `[Blocking]` finding across all personas remains unresolved, 🟡 if no
    `[Blocking]` remains but a `[Needs discussion]` item still needs a
    decision, 🟢 if every `[Blocking]` and `[Needs discussion]` item is
    resolved. State plainly what changed from the prior verdict.
- Append (never overwrite) this step's traceability group, with the
  persona recorded per question:
  ```
  ## Resolved Questions — team_review (<this finalize's timestamp>)
  1. **Persona:** <e.g. Backend Engineering>
     **Q:** <the original open question, verbatim>
     **A:** <the user's original answer, verbatim>
     **Applied at:** <section/FR where it was incorporated>
  ```
- Write to a new `outputs/[final]-<basename>-[<timestamp>].md` (fresh
  timestamp, never overwrite a prior `[final]-...` file).
- Once the new file passes `validate_structure.py` with 0 FAIL, update
  state: `final_document.path` to the new file, `final_document.
  produced_by` to `"team_review"`, `final_document.updated_at` to now;
  mark `team_review`'s own entry `done` with its `draft_path`
  (`ORCHESTRATOR.md` steps 9–10).
- **If this was Case 2** (an old `final_document` existed): now that
  `state.json` points at the new file, delete the old `[final]-...`
  file — see `ORCHESTRATOR.md` §"The final document" and step 11. The
  new file already carries forward everything the old one had (including
  the persona sections/verdict, updated per the rule above), so nothing
  is lost. If this was Case 1, there is no old file to delete.
- Flow footer with the next step (`estimation`).

## Note on scope
This step evaluates feasibility/delivery risk on top of an
already-finalized spec. If a finding implies the spec itself is wrong
(not just hard to build), still raise it as `[OPEN: ...]` here — the user
may choose to go back and re-run `ba_review` on the amended spec, or
resolve it directly in this document if it's narrow enough. Don't silently
assume which path they want.
