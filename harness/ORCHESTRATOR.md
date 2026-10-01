# BA Spec Harness — Orchestrator

You are running a menu-driven, 4-step BA spec pipeline: `rewrite` →
`ba_review` → `team_review` → `estimation`. There is no fixed order beyond
each step's own base-file dependency — the user picks what runs next. This
file is the entry point; read the relevant `steps/0N-*.md` file only when
that step is actually chosen, not upfront.

You never edit anything under `inputs/`. You never guess a base file
silently. You never treat silence as approval. You never assert a claim in
a spec you're producing without being able to point to the exact source
sentence or resolved answer behind it (see `principles.md`).

All file paths in this document are relative to this harness's root (the
directory containing this `harness/` folder, `inputs/`, `outputs/`, and
`state.json`).

---

## If an input is a PDF

Every step in this harness reads Markdown/text. If the file selected from
`inputs/` is a `.pdf`, use agent skill `pdf` to read file. Do not copy or duplicate the `pdf` skill's files into this
harness — its `LICENSE.txt` prohibits copying its materials outside where
they already live; only reference it by path.

---

## Session start

Do this whenever the user's message is the first one referencing this
harness in the session, or they explicitly ask for status. Do not redo
this on every message — mid-flow messages (picking a step, answering a
question, saying "approve") go straight to "Choosing and running a step"
below.

1. **Read `state.json`.**
   - Doesn't exist → create it:
     ```json
     {"output_language": null, "inputs": {}}
     ```
   - Exists but `output_language` is `null` → ask: *"What language should
     all outputs be written in?"* Wait for the answer, write it into
     `state.json`, then continue.
   - Already set → mention it once (e.g. "Output language: Vietnamese").
2. **List everything in `inputs/`.** Diff against `state.json`'s known
   inputs (keyed by basename). Report:
   - Known inputs and which steps have run for each (step → status →
     output path).
   - Any file in `inputs/` not yet tracked ("new input detected").
3. **Ask the user:** continue a known input, start a new one from
   `inputs/`, or start from a prompt they type directly (no file). For a
   prompt-based input, generate a short slug as its basename, store it in
   `state.json` with `"source": "prompt"`, and treat it identically to a
   file-based input from then on.

---

## Choosing and running a step

1. Once an input is selected, show its current status per step:

   | Step | What it does | Depends on |
   |---|---|---|
   | `rewrite` | Structures the raw draft into sections 1–10. No questions asked. One output, no approval loop. | the raw input |
   | `ba_review` | **Two separate approvals, two outputs:** (1) approve to run → writes a **draft** with `[OPEN: ...]` questions; (2) you answer them and approve again → *that* finalizes into the shared `final_document`. Choosing this step does **not** by itself produce the final document — see step 3 below for which of the two this invocation actually is. | `final_document` → `rewrite` output → raw input |
   | `team_review` | Same two-approval, two-output pattern as `ba_review` (draft with persona findings → finalize into the same `final_document`). | `final_document` → `rewrite` output → raw input |
   | `estimation` | T-shirt sizing per requirement. One output, no approval loop. | `final_document` → raw input |

2. Ask which step to run. Any step, any order, including one already run
   (a re-run).

3. **Resolve the base file** — never invent this silently. There is **one
   document that carries forward across the whole pipeline**: the
   `final_document` (see "The final document" section below). Every step
   after `rewrite` resolves its base the same way — first match wins:

   - **`rewrite`** → the input file itself (or the stored prompt text).
     Always the raw input; never chains off anything else.
   - **`ba_review`, `team_review`** → in this order:
     1. `final_document.path` in state, if set (an earlier `ba_review` or
        `team_review` run already produced one for this input).
     2. else, the latest `rewrite` output for this input.
     3. else, the raw input directly — warn the user this means far more
        open questions than usual, since nothing was structured yet.
   - **`estimation`** → in this order:
     1. `final_document.path` in state, if set.
     2. else, the raw input directly — warn the user the spec was never
        reviewed, so sizes will carry more risk; proceed only if they
        confirm.
     Never the `rewrite` output alone, and never a step's own draft.

   This means: skipping `rewrite`, or skipping `ba_review` and jumping
   straight to `team_review`, both resolve correctly on their own — there
   is no separate "what if a step was skipped" case to special-case,
   because every step after `rewrite` reads the *same* field.

   **Self-continuation exception:** if the chosen step has its own output
   still in `awaiting_approval` for this input (mid-approval, not yet
   finalized), that step's own draft is the base for continuing the
   approval loop — not the chain above. This only matters for Phase
   B/C of `ba_review`/`team_review`; it does not change what Phase A reads
   to *produce* the draft in the first place.

   **Which phase does "choosing `ba_review`/`team_review`" actually mean
   right now?** Decide this *before* step 5, since it changes what you
   state in the plan:
   - If this step's status for this input is `not_started` or `done`
     (a fresh run / a re-run) → you are about to run **Phase A**. The
     base file above is what Phase A reads to produce a **draft**. The
     plan in step 5 must say the output is a *draft*, not the final
     document — finalizing is a separate, later approval (Phase C),
     triggered only once the user has answered the draft's
     `[OPEN: ...]` questions and says "approve" again.
   - If this step's status is `awaiting_approval` (the
     self-continuation exception above) → the user is continuing an
     existing draft. If they're asking a question or editing the draft,
     stay in Phase B — no new approval needed yet. Only move to
     **Phase C** (finalize) once they explicitly approve *that draft*.
     The plan in step 5 for *this* approval must say the output is the
     `final_document`, since this is the finalize call, not a fresh
     Phase A run.

4. **Scan the resolved base file** for genuinely unresolved open tags —
   `[OPEN: ...]` (from `rewrite`/`ba_review`) and `[OPEN (<Persona>): ...]`
   (from `team_review`) are both the same mechanic, just with an extra
   persona label on the latter. Read `principles.md` §2 now if you haven't
   already this session — an item resolved by either method described
   there doesn't count as unresolved. If any remain:
   - Warn the user, list them (or a count if there are many).
   - Offer: pause so they can resolve first, or proceed anyway,
     acknowledging the step's output will inherit that ambiguity.
   - Do not pick for them.

5. **State the plan plainly** before doing anything, matching whichever
   phase step 3 identified:

   - **`rewrite` or `estimation`** (always one-shot, no draft/finalize
     split): *"Will run `<step>` on `<base file path>`, output →
     `<output path per the naming convention below>`, language:
     <output_language>."*
   - **`ba_review`/`team_review`, Phase A** (fresh run or re-run —
     the common case when the user just says "run ba_review" or
     "tiếp tục ba_review" with no draft already pending): *"Will run
     `<step>` (draft phase) on `<base file path>`, output →
     `outputs/[ba-review-draft or team-review-draft]-<basename>-
     [<timestamp>].md`, language: <output_language>. This step does
     **not** write the final document yet — the draft will contain
     `[OPEN: ...]` questions; you answer them in the file, then approve
     again to finalize."* Do **not** mention `final_document` creation
     or update as this run's output — that only happens at the later,
     separate Phase C approval.
   - **`ba_review`/`team_review`, Phase C** (the user is approving an
     existing `awaiting_approval` draft to finalize it): *"Draft
     approved. Will finalize into the shared final document, output →
     `outputs/[final]-<basename>-[<timestamp>].md`."* Say explicitly
     whether this **creates** the first `final_document` for this input
     or **updates** the existing one at `<path>` (and, if updating,
     that the old `[final]-...` file will be deleted once the new one
     validates — see "The final document" below).

   Repeat any warning from step 4 if the user chose to proceed anyway.

6. **Wait for explicit approval** ("approve", "yes", "go ahead"...) before
   invoking the step's instructions from `steps/0N-*.md`.

7. **Read the matching `steps/0N-*.md` file now** and follow it exactly.

8. **After the step produces output**, write it to `outputs/` with the
   naming convention shown in the plan.

9. **Validate the file you just wrote — mandatory, every time, no
   exceptions.** Run:
   ```
   python3 harness/scripts/validate_structure.py "<path to the file you just wrote>"
   ```
   - **Exit code 0** → proceed to step 10.
   - **Exit code non-zero (FAIL present)** → read the printed FAIL lines,
     fix the file directly to address each one, then re-run the script on
     the same path. Repeat until it exits 0. Do not tell the user the step
     is done, and do not update `state.json`, and do not delete anything
     (see step 11), while any FAIL remains.
   - **WARN lines** don't block, but read them — fix what's easy to fix;
     mention any you left as-is when you report the step's completion.
   - If the platform's shell/execute tool is unavailable for any reason,
     say so explicitly to the user instead of skipping this step silently.

10. **Update `state.json`** for this input/step (status, output path(s),
    `based_on`, `executed_at`; for `ba_review`/`team_review` finalizes,
    also `final_document.path/produced_by/updated_at` — now pointing at
    the file you just validated). Never mark a step done unless you
    actually ran it, wrote the file, and it passed validation. Do this
    **before** step 11 — `state.json` must always point at a file that
    exists, so if anything goes wrong before the old file is deleted, the
    old file is merely an extra leftover, never a broken pointer.

11. **If this write was a `ba_review`/`team_review` finalize that
    replaced an existing `final_document`** (Phase C, Case 2 in
    `02-ba-review.md`/`03-team-review.md`): now that `state.json` points
    at the new `[final]-...` file, delete the *previous*
    `[final]-<basename>-[<old-timestamp>].md` file — see "The final
    document" above for why this is safe (the new file is always a
    strict superset). If this finalize created the *first*
    `final_document` for this input (Case 1, nothing to replace), skip
    this — there is no old file to delete.

---

## Base-file resolution — quick table

| Step | Base file (first match wins) |
|---|---|
| `rewrite` | raw input — always, no predecessor |
| `ba_review` | `final_document.path` → latest `rewrite` output → raw input (warn) |
| `team_review` | `final_document.path` → latest `rewrite` output → raw input (warn) |
| `estimation` | `final_document.path` → raw input (warn, confirm before proceeding) |

## The final document — one file, updated in place across steps

Unlike `rewrite` (always a fresh file) and step drafts (throwaway once
approved), there is exactly **one** `final_document` per input, tracked at
`state.json` → `inputs.<basename>.final_document`. Both `ba_review` and
`team_review` write to it — never to two separate "final" files.

- **First time either step finalizes** (no `final_document` exists yet):
  the finalizing step is responsible for producing the **full structured
  spec** (sections 1–10, `FR-<NNN>` IDs — same shape `rewrite` would have
  produced) from its base file, with every resolved answer folded in, plus
  one **traceability group** for that step's resolved questions. Write to
  `outputs/[final]-<basename>-[<timestamp>].md` and set
  `final_document.path` to it.
- **Every subsequent finalize** (a `final_document` already exists): read
  it fresh, fold the newly resolved answers into the correct
  section/`FR-<NNN>` in place, and **append** a new traceability group
  for this step — never remove or overwrite a prior step's group. Write
  the updated content to a **new** `outputs/[final]-<basename>-
  [<timestamp>].md` (never edit a past final file in place) and update
  `final_document.path` to the new one.
- **There is only ever one `[final]-...` file on disk per input.** Because
  each new finalize is built by reading the previous `final_document` in
  full and carrying every section forward (updated in place, nothing
  dropped) plus appending a new traceability group, the new file is
  always a strict superset of the one it replaces — nothing in the old
  file is lost. So, once the new file is written, has passed
  `validate_structure.py` with no FAIL, and `state.json` has been updated
  to point at it (steps 9–10 below), delete the previous `[final]-...`
  file for this input (step 11). Never delete the old file before
  `state.json` already points at the new one — if anything fails partway
  through writing or validating, `state.json` must still resolve to a
  file that exists. This applies to both `ba_review` and `team_review`
  finalizing (Phase C, Case 2 in each step's file).
- Each traceability group is headed by which step produced it:
  ```
  ## Resolved Questions — ba_review (2026-01-15T10:30:00Z)
  ...
  ## Resolved Questions — team_review (2026-01-16T09:00:00Z)
  ...
  ```
  A `final_document` that only ever went through `ba_review` has one
  group; one that also went through `team_review` has two; the file
  itself is always exactly one document with all groups stacked at the
  end, in the order they were produced.
- If `team_review` has finalized at least once for this input, the
  `final_document` must also carry the 5 persona-findings sections
  (`## Backend Engineering`, `## Frontend Engineering`, `## QA /
  Testing`, `## Design / UX`, `## Product / Data`) and the
  `## Overall Verdict` section, placed after Section 10 and before the
  traceability groups — see `steps/03-team-review.md` Phase C for how
  they're written/updated on each subsequent team_review finalize.
  `validate_structure.py` enforces this on any `final` file whose
  traceability shows a `team_review` group.

---

## After a step finishes — always say what's next

Every time a step produces output (including `rewrite`, which has no
approval loop), do not just stop. State:
1. What file was written.
2. Current status (done / awaiting approval / draft written).
3. The concrete next options (e.g. "run `ba_review` next", "answer the N
   open questions in the draft, then say approve").

Ask what the user wants to do — don't assume they want to continue
immediately.

---

## Flow footer — mandatory every turn during an active step

If the user asks a side question while a step is in progress (asks about a
specific finding, wants something explained, pushes back on a
recommendation) — **answer it fully**, then close the turn with:

```
---
📍 <input basename> · <step> · <phase/status>
Next: <the concrete action(s) available right now>
```

Do this even if the answer was long or the conversation drifted. Never let
a side discussion end without restating where the user is in the pipeline
and what their options are. This is not optional — it is the mechanism
that keeps a multi-turn approval loop from getting lost.

---

## State file schema

```json
{
  "output_language": "Vietnamese",
  "inputs": {
    "<basename>": {
      "source": "file | prompt",
      "original_path": "inputs/abc.md",
      "created_at": "<iso timestamp>",
      "final_document": {
        "path": "outputs/[final]-abc-[<timestamp2>].md",
        "produced_by": "team_review",
        "updated_at": "<iso timestamp2>"
      },
      "steps": {
        "rewrite": {
          "status": "done",
          "output_path": "outputs/[rewrite]-abc-[<timestamp0>].md",
          "based_on": "inputs/abc.md",
          "executed_at": "<iso timestamp0>"
        },
        "ba_review": {
          "status": "done",
          "draft_path": "outputs/[ba-review-draft]-abc-[<timestamp1>].md",
          "based_on": "outputs/[rewrite]-abc-[<timestamp0>].md",
          "executed_at": "<iso timestamp1>"
        },
        "team_review": {
          "status": "done",
          "draft_path": "outputs/[team-review-draft]-abc-[<timestamp2>].md",
          "based_on": "outputs/[final]-abc-[<timestamp1-final>].md",
          "executed_at": "<iso timestamp2>"
        },
        "estimation": { "status": "not_started" }
      }
    }
  }
}
```

`status` values: `not_started` / `draft` / `awaiting_approval` / `done`.
`rewrite` only ever uses `output_path`. `ba_review`/`team_review` use
`draft_path` while mid-approval; once finalized, the result lives in the
top-level `final_document` field (shared across both steps, see "The
final document" above) — they do **not** each keep their own final path.
`estimation` uses `output_path`.

`final_document` is absent/`null` until the first successful finalize.
`produced_by` records which step most recently updated it — informational
only, does not gate anything.

Update this file yourself, every time — the step instructions in
`steps/0N-*.md` never touch state directly; that's this file's job alone.

---

## Hard rules

- Never write, edit, or delete anything under `inputs/`. The one
  exception to "never delete under `outputs/`" is the old `[final]-...`
  file superseded by a new one — see step 11 and "The final document"
  above; that deletion is required, not just permitted, and only after
  `state.json` already points at the replacement.
- Never invent a base file silently — always resolve it via the table
  above and name it out loud.
- Never run a step on a base file with genuinely unresolved
  `[OPEN: ...]` items without having flagged them and gotten an explicit
  "proceed anyway".
- Never assume approval; require an explicit "approve" before finalizing
  `ba_review` or `team_review`, and before invoking any step at all.
- Never mark a step `done` in `state.json` until
  `harness/scripts/validate_structure.py` has been run against the file
  you just wrote and exits with no FAIL-level issues.
- Always update `state.json` right after a step produces output and
  passes validation — before moving on to anything else.
- If you're about to fill in a detail the source/user didn't actually
  specify, don't — flag it `[OPEN: ...]` per `principles.md`, in
  `ba_review`/`team_review`. In `rewrite`/`estimation`, ask the user
  instead of writing an open tag (see those steps' own files for why).
- Always end a turn during an active step with the flow footer.
