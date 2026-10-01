# Step 1 — Rewrite (structure only, no questions)

## Required reading (do this now, in full, before anything else)
- `../principles.md` — §5 only (the fidelity rule for this step).
- `../reference_structure.md` — the full section structure (1–10) you must
  map the source into.

## Role
You are structuring the raw draft into the team's spec format. You are
**not** reviewing it, **not** finding gaps, and **not** asking questions.
That happens in `ba_review`.

## Base file
The original input file, read fresh from `inputs/`.

## What to do
1. Read the source file completely.
2. Map its content into the section structure defined in
   `reference_structure.md` (sections 1–10).
3. For any section with no corresponding content in the source, write
   "Not yet defined" and move on — do not guess, do not infer, do not ask.
4. Preserve the source's meaning and scope exactly. Do not add, remove, or
   reinterpret anything. Do not resolve any ambiguity you notice — leave
   it as-is in whichever section it naturally falls under; `ba_review`
   will find and flag it next.
5. Do not write any `[OPEN: ...]` tag in this step. If you catch yourself
   about to write one, stop — that question belongs in `ba_review`, not
   here.
6. Assign `FR-<NNN>` IDs to every distinct behavior you can identify in
   Section 4, sequential starting at `FR-001`.

## Output
One Markdown file, sections 1–10, following `reference_structure.md`
exactly. No Executive Summary, no findings, no open questions section —
just the structured spec itself.

Write to `outputs/[rewrite]-<basename>-[<timestamp>].md`.

## After writing
No approval loop for this step — write the file, then return to the
orchestrator flow (see `ORCHESTRATOR.md` §"After a step finishes") to tell
the user what's next.
