# BA Review Checklist

Used during `ba_review`'s draft phase, after applying the citation test in
`principles.md`. Run each category against the structured spec. Skip a
category only if clearly inapplicable.

---

## 1. Terminology consistency
- Exactly one term per actor/role throughout? Watch for drift across sections.
- Every domain term defined on first use?

## 2. State & status models
- All possible values enumerated for every status field? Valid transitions defined?
- Trap: "hidden", "out of stock", "inactive" may be *separate* states, not synonyms.

## 3. Time-bound rules
- Timezone specified for any expiry/schedule/deadline?
- Exact moment defined (end of day vs. specific timestamp)?
- Observable behavior at the boundary — immediate, next action, or reload?

## 4. Numeric & currency precision
- Type, unit, min, max — defined by the source, not general convention?
- Currency precision stated by source, not assumed from common practice?
- Floor/ceiling defined for any pricing or percentage math?

## 5. Entity cardinality
- Every relationship confirmed 1-to-1, 1-to-many, or many-to-many — not assumed?

## 6. Deletion & lifecycle side-effects
- What happens to dependents when an entity is deleted? Cascade, soft-delete, orphan?
- Is the delete action itself even confirmed in scope?

## 7. Concurrent & real-time behavior
- Conflict behavior defined for two users editing the same entity?
- Real-time vs. polling vs. reload-only for auto-triggered state changes?

## 8. Search & filter scope
- Exact fields searched? Exact actor (which roles can search)?
- Partial/exact match? Case- and diacritic-insensitive where relevant?

## 9. Permission scope & data boundaries
- Data access scoped explicitly per role ("own workspace only")?
- Can one role inadvertently reach another tenant's/branch's data?

## 10. Integration & async failure paths
- Timeout, retry policy, failure state defined for every external call?

## 11. Cross-feature dependencies
- Does any requirement depend on an entity/spec that doesn't exist yet in this doc?

## 12. Actions referenced but never defined
- Scan every edge case for a verb (delete, cancel, revoke...) — is there a
  requirement defining *that action's* behavior, or does the edge case just
  assume it exists? If undefined, add a stub requirement, don't just patch
  the edge case.

## 13. Internal consistency (full re-read)
- See `principles.md` §4 — run this as a whole-document pass, not point by point.

## 14. Citation audit (final pass, whole document)
- Go section by section, including every table cell and entity field. For
  each claim, can you name the source sentence or resolved answer behind
  it? If not, it fails the citation test — flag it, even if it doesn't
  match any category above.

## 15. Sentence craft audit (final pass, whole document)
Re-read `reference_structure.md`'s Sentence craft section, then check the
highest-risk spots — the Trigger/Behavior/Returns/On error lines for every
FR, plus Sections 2 and 3 (Overview, Defined Scope):
- Passive voice hiding a missing actor? ("is validated" — by whom, what?)
- Two behaviors or triggers joined by "and" in one sentence that should be
  two?
- A hedge word ("generally", "typically", "in most cases") standing in for
  a rule that should either be stated plainly or flagged `` `[OPEN: ...]` ``?
- Filler that adds no information ("basically", "in order to", "is able
  to")?
- A number spelled out instead of a numeral near a unit (five megabytes,
  a couple of seconds)?
- A buried double negative that would read more plainly rewritten?
Rewrite anything that fails a check — this is a prose fix, not a finding
to add to the BA Review Findings table.
