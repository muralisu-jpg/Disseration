# Non-iconicity detection pipeline (v5)

A clean, deterministic pipeline that detects narrative **non-iconicity** -- places where the order
events are *told* differs from the order they *happen* -- on four tracks: **past** (flashback),
**present** (told in sequence but overlapping), **future** (told before it happens), **imaginary**
(dream / wish / threat / conditional). It reads only the plain story text; it never sees an answer key.

## Layout
```
PROMPT_v5.md         the task for Claude Code (a code-improvement brief)
run.py               orchestrator: texts/ -> predictions/ + run_report.md
requirements.txt     nltk
pipeline/
  common.py          NLTK bootstrap, offsets, POS, lexicons, participle detection
  events.py          sentence split + event (verb) extraction with tense/flags
  rules.py           the four-track rule engine (+ EVIDENTIAL guard, cue_type, modal_force)
  selfcheck.py       trigger verification, de-dup, per-track confidence gates
  predictions.py     (re-exported from selfcheck) output schema
  timeline.py        (re-exported from selfcheck) timeline string + irrealis sub-timeline + fate
texts/               the input stories (plain text)
```

## Run
```
pip install -r requirements.txt
python run.py
```
Outputs `predictions/<story>.json` (one record per detected non-iconicity, plus a timeline and
irrealis sub-timelines) and `run_report.md` (per-story / per-track counts).

## Output schema (per prediction)
`story, rule, track, tlink, slink, earlier, later, cue_type, confidence, modal_force, rationale`
where `cue_type` is `explicit_marker` (a surface cue matched) or `inferred` (from tense/structure),
and each imaginary case yields a sub-timeline with a `fate`: realized / averted / open / never_actual.

## Notes
- Deterministic and self-contained; the only external dependency is NLTK (POS tagging + sentence split).
- No story-specific logic: every rule is general. No answer-key (`.sty`) is read at any point.
- Tune accuracy via the per-track confidence gates in `run.py` (`THRESHOLDS`).
