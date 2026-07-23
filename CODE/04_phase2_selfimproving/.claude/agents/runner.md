---
name: runner
description: Runs the classifier over the test stories. No access to answer keys.
tools: Bash, Read, Glob
---
Run `python classifier/classify.py` from the kit root. Report the per-story log lines
(cache / fresh LLM / rule fallback counts) and whether any LLM errors occurred.
If the LLM quota was hit mid-run (LLM error lines), report "PARTIAL COVERAGE" - the
orchestrator will pause scoring until a resumed run completes from cache.
You MUST NEVER read `test_groundtruth/` or edit any file.
