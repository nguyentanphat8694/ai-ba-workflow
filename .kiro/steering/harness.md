---
inclusion: always
---

# BA Spec Harness

This project runs a menu-driven BA spec pipeline. Follow the orchestrator
below exactly — it defines session start behavior, the step menu,
base-file resolution, approval gates, and state tracking.

#[[file:../../harness/ORCHESTRATOR.md]]

Do not read the individual `harness/steps/*.md` files until the
orchestrator tells you which step is being run — they are loaded on
demand, not all at once.
