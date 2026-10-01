# BA Spec Harness

A menu-driven, 4-step BA spec pipeline that runs the same way on Kiro,
Claude Code, and Gemini CLI. All logic lives in one place
(`harness/ORCHESTRATOR.md` + `harness/steps/*.md`); each platform just
needs its own loader file to point at it.

## Why this exists

Kiro skills, Claude Code slash-commands/skills, and Gemini CLI's
custom-commands/skills all use different, incompatible formats. The only
things all three platforms actually share are: (1) a file that gets loaded
into context automatically at session start, and (2) plain file read/write.
This harness is built entirely on those two, so there's one source of
truth instead of three parallel implementations to keep in sync.

## Layout

```
new/
├── CLAUDE.md                    # loader for Claude Code (auto-loaded)
├── GEMINI.md                    # loader for Gemini CLI (auto-loaded)
├── .kiro/steering/harness.md    # loader for Kiro (inclusion: always, includes ORCHESTRATOR.md directly)
├── state.json                   # pipeline state — which step ran, on what, when
├── inputs/                      # drop raw drafts here — read-only to the AI
├── outputs/                     # every step's result lands here
└── harness/
    ├── ORCHESTRATOR.md          # entry point — session start, step menu, base-file rules, approval gates
    ├── principles.md            # the citation test — the actual "don't assume" rule, plus common traps
    ├── reference_structure.md   # target spec section structure (1–10)
    ├── review-checklist.md      # domain gap checklist used in ba_review
    ├── persona-focus.md         # 5 lenses used in team_review
    ├── scripts/
    │   └── validate_structure.py  # structure checker — run after every file write, no exceptions
    └── steps/
        ├── 01-rewrite.md        # structure only, no questions
        ├── 02-ba-review.md      # draft → approve loop → finalize, with traceability
        ├── 03-team-review.md    # same pattern, 5-persona feasibility lens
        └── 04-estimation.md     # T-shirt sizing, lighter loop
```

## How to use

1. Drop a raw draft into `inputs/` (or just tell the AI what you want to
   analyze and paste it in).
2. Open this project in Kiro / Claude Code / Gemini CLI and say something
   like "analyze abc.md". The loader file for that platform points the AI
   at `harness/ORCHESTRATOR.md`, which takes over from there.
3. First run: it asks what language to write outputs in, then scans
   `inputs/` and shows you what's already been done.
4. Pick a step, in any order — steps can be skipped. The AI resolves which
   file to base it on (see table below), states the plan, and waits for
   your "approve" before running.
5. `rewrite` just writes a structured file — no questions, no approval
   loop, read it and move on. Optional: `ba_review`/`team_review` can run
   directly on the raw input if you skip it.
6. `ba_review` and `team_review` both work the same way: the AI writes a
   **draft** with `` `[OPEN: ...]` `` questions inline, you answer them
   directly in that file (either replace the tag in place, or answer
   under the matching entry in the Open Questions list — both work), then
   say "approve". The AI then folds every resolved answer into the
   **shared final document** for this input — creating it if this is the
   first step to finalize, or updating the existing one in place if
   `ba_review` and `team_review` have both run. Either way you end up with
   exactly one current spec file, with a traceability section at the
   bottom listing every question and answer, grouped by which step raised
   it.
7. `estimation` reads the shared final document (or the raw input, with a
   warning, if neither review step has run yet) and produces a
   T-shirt-size table per requirement — lighter weight, no draft/approve
   split, but it will stop and ask you directly if a requirement is too
   unclear to size rather than guessing.
8. After every file write, the AI runs a structure-check script and fixes
   any issue before telling you the step is done — see "Structure
   validation" below.
9. Whenever you ask something mid-step, the AI answers it, then always
   closes with a footer showing where you are and what you can do next —
   it won't leave you drifting without a next step.

## Base-file resolution

| Step | Reads from (first match wins) |
|---|---|
| `rewrite` | the raw input — always |
| `ba_review` | the shared final document → latest `rewrite` output → raw input (warn) |
| `team_review` | the shared final document → latest `rewrite` output → raw input (warn) |
| `estimation` | the shared final document → raw input (warn) |

Skipping a step just means the next one falls further down this chain —
there's no special-casing needed. `ba_review` and `team_review` write to
**one shared final document** per input (see `ORCHESTRATOR.md`, "The
final document") rather than two separate "final" files, so `estimation`
always reads the most current version of the spec regardless of which
review steps actually ran.

## Output files

| File pattern | Written by | Lifespan |
|---|---|---|
| `[rewrite]-<basename>-[ts].md` | `rewrite` | one per run |
| `[ba-review-draft]-<basename>-[ts].md` | `ba_review` Phase A | throwaway once finalized |
| `[team-review-draft]-<basename>-[ts].md` | `team_review` Phase A | throwaway once finalized |
| `[final]-<basename>-[ts].md` | `ba_review`/`team_review` Phase C | **the** current spec — exactly one on disk per input |
| `[estimation]-<basename>-[ts].md` | `estimation` | one per run |

There is only ever **one** `[final]-...` file on disk per input. Each new
finalize is built by reading the previous one in full and carrying every
section forward, so the new file is always a strict superset of the one
it replaces — nothing is lost. Once the new file is written and passes
`validate_structure.py` with 0 FAIL, the AI updates `state.json` →
`final_document.path` to the new one, then deletes the previous
`[final]-...` file for that input — in that order, so `state.json` never
points at a file that no longer exists.

## Structure validation

Every file write is followed by
`python3 harness/scripts/validate_structure.py <path>` (stdlib only, no
dependencies). It checks section headings, a real Table of Contents,
`FR-<NNN>` numbering, edge-case cross-references, that every
`` `[OPEN: ...]` `` tag is backtick-wrapped, and step-specific shape (all
5 persona headings in `team_review`, at least one traceability group in
`[final]-...` files, the sizing table + disclaimer in `estimation`). The
AI fixes any FAIL and re-runs until it passes before marking a step done
in `state.json` — see `ORCHESTRATOR.md` step 9. Requires a Python 3
interpreter and shell/execute tool access on whichever platform you're
running.

It also prints **WARN**-only hints for `reference_structure.md`'s
Sentence craft rules — hedge words outside an `` `[OPEN: ...]` `` tag,
filler phrases, numbers spelled out next to a unit. These never block a
step (prose quality isn't something a regex can judge reliably), but the
AI is expected to read them and fix what's genuinely wrong before
reporting the step done — see `review-checklist.md` item 15 for the
manual audit these hints support.

## Notes

- No hooks, no skills, no slash-commands — this harness intentionally
  avoids every platform-specific extension mechanism so it behaves
  identically everywhere.
- `state.json` only tracks AI-run steps. If you hand-edit an `outputs/`
  file outside of an active approval loop, that edit isn't logged — use
  your own VCS if you need a record of it.
- This harness was designed after (and intentionally departs from) an
  earlier Kiro-only version. The main differences: `rewrite` now owns
  structuring (previously `ba_review` did both structure and review in
  one pass); `ba_review` and `team_review` finalize into one **shared**
  final document instead of each keeping a separate final file, so
  skipping either step, or running them in any order, never leaves
  `estimation` unsure which file is current.
