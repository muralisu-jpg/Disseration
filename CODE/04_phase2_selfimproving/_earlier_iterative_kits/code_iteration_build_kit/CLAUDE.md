# Project: Self-improving non-iconicity detector

## The task
Detect **non-iconicity** in a story — places where the order events are *told*
differs from the order they *happen* — on four tracks:
- past: an event told later than it happened (flashback)
- present: two events told in sequence that actually overlap
- future: an event told before it happens (plan, prophecy, threat)
- imaginary: an event only on a hypothetical branch (dream, wish, conditional, counterfactual)

The system reads only plain story text. It stays deterministic and blind.

## Hard rules (apply to every agent)
- Only the `scorer` agent may read `groundtruth/`. No other agent reads it.
- The `scorer` writes ONLY aggregate per-track numbers to `feedback.json`.
  Never per-example misses, never quotes, never story/line names.
- The `improver` may edit ANY stage inside `pipeline/` (preprocessing, tokenization,
  sentence splitting, contraction/POS handling, event extraction, or rules) — but ONE
  focused, incremental, general change per iteration. It builds on the existing code,
  never rewrites a stage from scratch, and never hard-codes story-specific strings.
- Optimise on the **dev** split only (see split.json). The **test** split is touched
  once, by the human, at the very end — never by any agent.
- Keep every change focused: one improvement per iteration so its effect is readable.

## Folders
- stories/      the 15 story .txt files
- pipeline/     the detection code (improver edits, runner runs)
- groundtruth/  the answer key (scorer ONLY)
- predictions/  runner writes here, scorer reads here
- iterations/   per-iteration checkpoints: iter_01/, iter_02/, ...
- split.json    which stories are dev vs test
- state.json    loop state (current iteration, best score, plateau count)
- feedback.json scorer's aggregate-only output to the improver
