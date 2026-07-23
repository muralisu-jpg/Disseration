# Claude Code task: improve this non-iconicity pipeline (work on the code, do not rewrite)

## Your role
You are **working on an existing, working Python pipeline** (in this folder) whose rule engine already
**consolidates the strongest general rules across all four tracks** (`pipeline/rules.py`: P1..P10 past,
R1..R5 present, F1..F6 future, I1..I8 imaginary, with the EVIDENTIAL guard). Your job is to **run it,
verify it, and refine it further** for maximum accuracy -- make targeted edits, preserve the module
layout / function names / schema, and keep a short changelog. This is a code-improvement task, not a new
build, and **not** a reinvention from scratch.

Ground your analysis in ISO-TimeML, the international standard for annotating events and temporal relations in text (ISO 24617-1). Under that standard an EVENT is any situation that happens or holds — occurrences, states, reporting verbs, perceptions, aspectual verbs, and intensional actions or states. A temporal link (TLINK) asserts how two events stand relative to one another, drawing on Allen's interval algebra: BEFORE, AFTER, IBEFORE, IAFTER, SIMULTANEOUS, IDENTITY, INCLUDES, IS_INCLUDED, DURING, BEGINS, ENDS, BEGUN_BY, ENDED_BY. Separately, TimeML defines subordinating links, where one event is embedded under another and is therefore not asserted as having occurred: MODAL (possibility, wish, ability, obligation), CONDITIONAL (dependent on an unmet or unresolved condition), COUNTER_FACTIVE (presupposed not to have happened), FACTIVE (presupposed to have happened), and EVIDENTIAL (reported or perceived rather than directly narrated). Treat the subordinating relations as the primary signal for the IMAGINARY track

## The task the pipeline performs
Detect **non-iconicity** in a story -- places where the order events are *told* differs from the order
they *happen* -- on four tracks:
- **past**: an event told later than it happened (a flashback).
- **present**: two events told one after another that actually overlap in time.
- **future**: an event told before it happens (a plan, prediction, prophecy).
- **imaginary**: an event told as if on the timeline but only on a hypothetical branch (dream, wish,
  threat, conditional, counterfactual).

The pipeline reads **only the plain story text**. It must stay deterministic and blind.

## The codebase
```
run.py               orchestrator: texts/ -> predictions/ + run_report.md (per-track confidence gates here)
pipeline/common.py   NLTK bootstrap, sentence offsets, POS tagging, lexicons, participle detection
pipeline/events.py   sentence split + event (verb) extraction with tense + construction flags
pipeline/rules.py    THE DECIDING STEP -- per-track regex detectors (+ EVIDENTIAL guard, cue_type, modal_force)
pipeline/selfcheck.py verify triggers, de-duplicate, apply per-track confidence gates
pipeline/predictions.py output schema
pipeline/timeline.py  timeline string + irrealis sub-timeline + fate
texts/               the input stories
```
Run it first (`pip install -r requirements.txt && python run.py`) to see the baseline, then improve.

## Objective
Maximise accuracy (precision **and** recall) on **all four tracks at once**. Improvements should come
from sound linguistic reasoning about the constructions, not from tuning to any specific text.

## Where to improve (all edits inside the named modules)
**Past** (`rules.py`, `events.py`): widen participle detection so more "had/have + past participle"
cases are caught; add preposed participial / absolute clauses ("the work done, he left"); make the
retrospective-adverbial and subordinator rules require a nearby finite verb so they stop firing on
non-anterior uses; put the lower-confidence past rules behind the confidence gate.

**Present** (`rules.py`): extend the Allen coverage -- besides the co-temporal connectives, add
durative/stative-includes-punctual within one clause, and identity/coreference (the same event retold).
Require a shared participant so precision holds. This track is currently the thinnest -- it has the most
room to gain.

**Future** (`rules.py`): keep "will/shall + V" and the prediction/promise speech-act verbs; add an
imperative-with-fulfilment rule (a command counts as future only if the commanded act actually occurs
later in the text); suppress non-predictive uses of "would".

**Imaginary** (`rules.py`, `selfcheck.py`): keep the full SLINK coverage (modal / conditional /
counter-factive / factive) and the **EVIDENTIAL guard** (never flag plain reported speech). Add
habitual / iterative / generic events and events under negation of occurrence ("never did X", "without
V-ing"). Preserve precision via the guard and the confidence gate.

**Cross-cutting**: the per-track confidence thresholds live in `run.py` (`THRESHOLDS`) -- treat these as
your tunables and report a short ablation of their effect in the changelog. Keep `cue_type` honest:
`explicit_marker` only when a real surface cue is matched, otherwise `inferred`.

## Process
1. Read `pipeline/*` and `run.py`; run the baseline and save `predictions_baseline/`.
2. Improve one track at a time; after each, re-run and compare to the baseline by the reasoning above.
3. Keep `CHANGELOG.md`: file changed, what changed, why, expected per-track effect.
4. Emit final `predictions/` (same schema) and an updated `run_report.md`.

## Hard constraints
- **Improve, don't rewrite.** Keep the module boundaries, function names, and schema; deliver a diff +
  changelog, not a new codebase.
- **Deterministic and self-contained.** No network at inference time; the only dependency is NLTK.
- **Blind.** Do not read, fetch, or fit to any expert annotation / answer key. Optimise purely by the
  linguistic reasoning above.
- **No story-specific logic.** Every rule must be general. A rule that only works on one story is not
  allowed. Do not hard-code names, phrases, or expected outputs from any particular text.
- Keep the schema: `story, rule, track, tlink, slink, earlier, later, cue_type, confidence,
  modal_force, rationale`, plus the timeline string and irrealis sub-timeline + fate.
