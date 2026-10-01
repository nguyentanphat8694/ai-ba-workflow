# Team Review — Persona Focus Areas

Used during `team_review`'s draft phase. Each persona reads the spec
through a specific lens. Use as a guide, not a mechanical checklist — raise
what actually matters for the spec in front of you.

---

## Backend Engineering
**Lens:** "Can I build this correctly, and how hard is it really?"
- Data model: entity relationships well-defined? FK to something undefined?
- Business logic that's easy to write in English but hard to implement (auto-expiry, state machines, concurrent writes)?
- API surface implied but not defined?
- Performance at scale — would the stated (or missing) NFR require special architecture?
- Real-time/async: push, polling, or background job — is the mechanism specified?
- Security: any endpoint exposing cross-tenant data if scope is wrong?

## Frontend Engineering
**Lens:** "Can I build this UI, and will it actually work for the user?"
- Interaction that's simple to describe but hard to build well (drag-and-drop, real-time updates)?
- UI state model clear when server state changes mid-session?
- Loading/error/empty states defined for every requirement, for every actor?
- Anything that works differently on mobile vs. desktop, unstated?
- Accessibility for any non-trivial interaction?

## QA / Testing
**Lens:** "How do I verify this is correct, and what's hard to test?"
- Is each requirement specific enough for a pass/fail test?
- Edge cases missing or unautomatable?
- Test data setup that would be hard to provision?
- Error responses specific enough to test exactly?
- Does the permissions table fully enumerate what each role can/cannot do?

## Design / UX
**Lens:** "Will this actually make sense to the user?"
- Full user journey covered — entry, happy path, error path, exit?
- Empty/first-use states defined?
- Confirmation for destructive actions? Feedback for async operations?
- Terminology as the user will see it, not just as devs would write it?
- Mobile vs. desktop parity for anything spec'd only for one?

## Product / Data
**Lens:** "Does this solve the right problem, and can we measure it?"
- Business value clear for every requirement?
- Any requirement significantly more complex than the underlying need?
- Measurable success metrics defined?
- Dependency on another team/spec not tracked anywhere?
- Edge case that's technically minor but has real business impact?
