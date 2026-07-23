# Prompt — Claude Cowork arm — Non-Iconicity Extraction (ProppLearner Corpus)

> Paste into a fresh Claude Cowork session with only the 15 `.txt` files from `stories/` in the workspace — no `.sty` files, no prior outputs.

---

## How to work

Work however you find best — you do **not** need to write code. For each of the six steps below, produce the step's output and save it to the path named in that step, in the schema shown. Process each story end to end before the next; treat all stories the same way.

---

## Role and task

You are an agentic temporal-reasoning assistant analysing 15 Russian folktales from the ProppLearner corpus. For each story, identify every instance of **non-iconicity** — every pair of events where the order they are *told* differs from the order they *actually happen* in the story world.

A narrative is a sequence S of sentences describing a sequence E of events. Where S and E run in the same order it is **iconic**; where they diverge — flashback, simultaneity told as sequence, prophecy, dream — it is **non-iconic**.

Blind benchmark: do **not** open or look for `.sty` files, do **not** search the web for ProppLearner, do **not** rely on prior-run numbers. Work only from the 15 `.txt` files.

## The four tracks
- **PAST** — backward-pointing: real occurrence earlier than text position implies.
- **PRESENT** — co-temporal: events told as a sequence that actually overlap or include one another.
- **FUTURE** — forward-pointing: event not yet occurred relative to the surrounding narrative.
- **IMAGINARY** — irrealis: events only on a hypothetical sub-timeline (dream, wish, threat, conditional, counterfactual).

## The six-step pipeline
1. → `intermediates/<id>/step1_sentences.json` — skip the `/** … */` header, split body into sentences (S-string): `{sent_id, text, char_offset, approx_line}`.
2. → `intermediates/<id>/step2_events.json` — one event per finite verb (never collapse coordinated verbs): `{event_id, sent_id, clause_id, trigger, char_offset, type, tense}`.
3. → `intermediates/<id>/step3_candidates.json` — apply P/R/F/I; P2 fans out; each candidate records rule, track, events, rationale.
4. → `intermediates/<id>/step4_checked.json` — confirm every trigger is a verbatim substring (`verbatim_ok`); confirm P2 fanned out to every matrix verb in scope; de-duplicate.
5. → `predictions/<id>_predictions.json` — canonical enriched schema (below).
6. → `intermediates/<id>/step6_timeline.json` + `run_report.md` — main-timeline string, irrealis sub-timelines, iterative compressions.

## Canonical prediction schema (Step 5) — placeholder values, fill from the text
```json
{"story_id": "<id>",
 "predictions": [
  {"track":"<past|present|future|imaginary>","rule":"<rule id>",
   "earlier_event":{"trigger_text":"<verbatim span>","char_offset":0,"approx_line":0,"construction":"<surface form>"},
   "later_event":{"trigger_text":"<verbatim span>","char_offset":0,"approx_line":0,"construction":"main clause"},
   "relation":"<BEFORE|SIMULTANEOUS|AFTER|MODAL|COUNTERFACTUAL>",
   "cue_type":"<explicit_marker|inferred>","confidence":"<high|medium|low>",
   "timeline_string":"[<earlier>][<later>]","irrealis":null,
   "rationale":"<which rule fired and why>"}]}
```
- `cue_type`/`confidence`: `explicit_marker`+`high` = unambiguous marker; `explicit_marker`+`medium` = marker but ambiguous context; `inferred`+`low` = no marker, recovered by world reasoning.
- `timeline_string` = events as ordered snapshots, earliest first; co-temporal share a bracket `[a,b]`.
- `irrealis` = `null` for past/present; for future/imaginary: `{sub_timeline_id, modal_force (dream|threat|prophecy|conditional|counterfactual|plan|wish), anchor_trigger, anchor_line, fate (realized|averted|open|never_actual), projects_back_to|null}`.

## Timeline schema (Step 6) — placeholder values
```json
{"story_id":"<id>","n_sentences":0,
 "main_timeline_string":"[e1][e2]...",
 "sub_timelines":[{"sub_timeline_id":"st1","modal_force":"<force>","anchor_line":0,"string":"[<sub event>]","fate":"<fate>","projects_back_to":null}],
 "iterative_compressions":[{"quote":"<verbatim span>","approx_line":0,"note":"one telling compresses repeated events"}]}
```

## Constraints
No `.sty`; no web search for ProppLearner; no prior-run anchoring; all six steps required; the per-step files are the deliverable; every `trigger_text` verbatim; when in doubt flag (`inferred`/`low`) not skip.

## When you finish
Write `run_report.md` (per-story per-track counts; `explicit_marker` vs `inferred` split; sub-timelines by `modal_force`/`fate`; non-iconicity no rule covers). **Do not score yourself.**
