# BA Spec Harness

This project runs a menu-driven BA spec pipeline. Before doing anything
else in this project, read `harness/ORCHESTRATOR.md` in full and follow it
exactly. It defines session start behavior, the step menu, base-file
resolution, approval gates, and state tracking.

Do not read the individual `harness/steps/*.md` files until the
orchestrator tells you which step is being run — they are loaded on
demand, not all at once.
