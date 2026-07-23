# Prompt — Claude Code arm v4 — Non-Iconicity Extraction (ProppLearner Corpus)
## TimeML-faithful, accuracy-oriented revision

> Paste into a fresh Claude Code session started in a workspace containing only a `stories/` folder with the 15 `.txt` files — no `.sty`, no prior outputs, no earlier scripts.
> All examples below are generic invented sentences, not drawn from any story. Do not look up the corpus.

---

## How you must work

Implement the task as code you write yourself, one script per step, saved with the exact names `code/01_sentences.py` … `code/06_timeline.py`. Run each, save its output to the path named in the step, and keep the scripts (they are part of the deliverable). Standard libraries plus `nltk` are allowed (`pip install nltk`; one-time `nltk.download`). Process each story end to end; treat all stories identically.

---

## Method basis

Detection follows three established temporal-annotation frameworks. Use them as the organising logic, not as story-specific cues:

- **ISO-TimeML** — events are linked by **TLINK** (temporal: BEFORE, IBEFORE, AFTER, SIMULTANEOUS, INCLUDES, IS_INCLUDED, BEGINS, ENDS, …) and by **SLINK** (subordination: MODAL, CONDITIONAL, COUNTER_FACTIVE, FACTIVE, EVIDENTIAL, NEG_EVIDENTIAL). Non-iconicity is a TLINK or SLINK whose asserted structure does not match text order.
- **Allen's interval algebra** — the 13 relations between two intervals (before, meets, overlaps, starts, during, finishes, equals, and inverses). Use these to decide PRESENT-track co-temporality precisely (overlaps / during / starts / finishes / equals = co-temporal; before / meets = sequential).
- **Reichenbach's E-R-S model** — every finite clause has an event time E, a reference time R, and a speech time S. Anteriority (E before R) ⇒ PAST track; posteriority (E after R) ⇒ FUTURE track; perfect = E before R with R at S. Use E-R-S as the catch-all test when no surface keyword fires but the tense configuration implies a reordering.

---

## Role and task

For each of 15 folktales, identify every **non-iconicity** — every pair of events whose told order differs from their storyworld order. Four tracks:

- **PAST** — E earlier than its text position implies (anteriority, flashback, pluperfect).
- **PRESENT** — events told in sequence that are actually co-temporal (Allen overlaps/during/starts/finishes/equals).
- **FUTURE** — E later than the surrounding narrative (plan, prophecy, intention, prediction).
- **IMAGINARY (irrealis)** — events on a hypothetical sub-timeline (SLINK: MODAL, CONDITIONAL, COUNTER_FACTIVE, FACTIVE). This is the priority track for accuracy in this revision.

Blind: no `.sty`, no web lookup, no prior-run anchoring.

---

## Rule set

### PAST (anteriority — Reichenbach E before R)
- P1 `had + PP` (past perfect). *"She had locked the door before they arrived."*
- P2 `having + PP` — **fan out to every matrix verb in scope**, excluding the participle.
- P3 past adverbials: before, earlier, previously, already, just, long ago, once (retrospective), ago, by then.
- P4 counterfactual past perfect `would/could/might have + PP` (also IMAGINARY/COUNTER_FACTIVE).
- P5 reported/recollected pasts: remembered/recalled/told/learned/discovered + that-clause describing an earlier event.
- P6 `after/once/when/as soon as + (had) V` where the subordinate event precedes the matrix.
- P7 present perfect `have/has + PP` in dialogue (event prior to the utterance).
- P8 `from + V-ing` / prepositional retrospection (`tired from running`).
- P9 backward relative clause: `who/which/that + (had) V` when the clause content predates the matrix.
- P10 discovery + stative: discovery verb (saw/found/met/noticed/came upon/discovered/heard) + stative (lying/sitting/sleeping/waiting/standing…); state precedes discovery.
- P11 `no sooner … than`, `hardly/scarcely … when`, `by the time` — order-reordering constructions.
- P12 preposed participial/absolute clause: *"The letter written, he left."* / *"His work done, …"* — the clause event precedes the matrix.
- P13 nominalised prior event: `after/since the death/arrival/departure of …`, `on his return` — the named event precedes the matrix.
- P14 **Reichenbach catch-all**: any clause whose E is established as before the current R by sequence-of-tense, with no P1–P13 keyword. Mark `cue_type: inferred`, `confidence: low`.

### PRESENT (co-temporal — Allen overlaps/during/starts/finishes/equals)
- R1 `while X, Y`. R2 `as X` (durative). R3 reduplication (one extended event). R4 `until X` (co-extensive up to the bound). R5 stative co-occurrence under a shared adverbial. R6 `meanwhile / all the while / at the same time / in the meantime`. R7 `during / throughout / as long as`. R8 `as soon as / the moment / just as` (Allen *meets/starts*).

### FUTURE (posteriority — Reichenbach E after R)
- F1 modal future: `will/shall/'ll + V`, `going to`. F3 prophetic: `predicted/foretold/promised/swore/vowed`. F4 planned: `was about to/set out to/meant to/intended to/decided to`. F5 anticipated: `awaited/expected/longed to/wanted to/hoped/feared`. F6 conditional future: `if X … will/'ll`. F7 purpose-as-future: `in order to / so as to / so that` (the purpose event is posterior).
- **F2 (constrained):** imperative-as-future fires **only** when the commanded action is a distinct storyworld event that the narrative later reports as carried out; otherwise do not fire. A bare command with no later fulfilment is not prolepsis. When F2 does fire, mark `confidence: medium`. (This constraint is deliberate — do not flood the future track with every imperative.)

### IMAGINARY (irrealis — SLINK types) — PRIORITY TRACK
Tag each prediction with its `slink_type`. Cover the space systematically rather than by single keywords:

- **I-MODAL → slink_type MODAL:** irrealis modal auxiliaries (`would, could, might, may, should, must`-epistemic, `shall` in non-future use); volition/desire/intention predicates (`want/wish/hope/desire/long/intend/plan/mean/decide/resolve to`); ability (`be able to`); optatives (`may he live long`).
- **I-COND → slink_type CONDITIONAL:** `if / unless / provided (that) / as long as / in case / supposing / were … to / should … `, both protasis and apodosis.
- **I-CF → slink_type COUNTER_FACTIVE:** counterfactual conditionals (`if … had …, … would have …`), `would that`, `if only`, `wish … had`, `as if / as though`, `pretended that`, `falsely believed`.
- **I-FACT → slink_type FACTIVE:** factive predicates embedding a proposition (`know / realise / forget / regret / notice that`).
- **I-EMBED → slink_type MODAL:** dreams, visions, and stories told within the story (the embedded events are irrealis relative to the main timeline).

**Precision guard (important):** plain reported speech and perception (`said that`, `saw that`, `heard that`) are **EVIDENTIAL**, a different SLINK type that is **not** on the imaginary track. Do **not** tag ordinary reporting as imaginary — that was a precision sink in earlier runs. Only the four types above count here.

A construction may belong to two tracks (e.g. a counterfactual past perfect is PAST and IMAGINARY); record both.

---

## Precision discipline

Broadening recall must not collapse precision. For every prediction:
- Set `cue_type`/`confidence` mechanically: explicit unambiguous marker → `explicit_marker`/`high`; marker present but context ambiguous → `explicit_marker`/`medium`; no marker, recovered by E-R-S reasoning → `inferred`/`low`.
- De-duplicate identical `(track, slink_or_tlink, earlier_offset, later_offset)` rows.
- Re-anchor every trigger to a real offset and confirm it is a verbatim substring (`verbatim_ok`).
- Apply the EVIDENTIAL guard above.

---

## Six-step pipeline (one script each)
1. `code/01_sentences.py` → `intermediates/<id>/step1_sentences.json` — skip the `/** … */` header; sentences (S-string) `{sent_id, text, char_offset, approx_line}`.
2. `code/02_events.py` → `intermediates/<id>/step2_events.json` — POS-tag; one event per finite verb (never collapse coordinates) `{event_id, sent_id, clause_id, trigger, char_offset, type, tense, reichenbach}` where `reichenbach` ∈ {E<R, E=R, E>R, n/a}.
3. `code/03_rules.py` → `intermediates/<id>/step3_candidates.json` — apply P/R/F/I; P2 fans out; record `rule`, `track`, `slink_type`/`tlink_type`, events, rationale.
4. `code/04_selfcheck.py` → `intermediates/<id>/step4_checked.json` — re-anchor + verbatim check; confirm P2 fan-out; apply EVIDENTIAL guard; de-duplicate.
5. `code/05_predictions.py` → `predictions/<id>_predictions.json` — canonical schema (below).
6. `code/06_timeline.py` → `intermediates/<id>/step6_timeline.json` + `run_report.md` — main-timeline string, irrealis sub-timelines, iterative compressions.

---

## Canonical prediction schema (Step 5) — placeholder values
```json
{"story_id":"<id>",
 "predictions":[
  {"track":"<past|present|future|imaginary>","rule":"<rule id>",
   "tlink_type":"<BEFORE|SIMULTANEOUS|INCLUDES|AFTER|null>",
   "slink_type":"<MODAL|CONDITIONAL|COUNTER_FACTIVE|FACTIVE|null>",
   "earlier_event":{"trigger_text":"<verbatim>","char_offset":0,"approx_line":0,"construction":"<surface form>","reichenbach":"<E<R|E=R|E>R>"},
   "later_event":{"trigger_text":"<verbatim>","char_offset":0,"approx_line":0,"construction":"main clause","reichenbach":"<...>"},
   "relation":"<BEFORE|SIMULTANEOUS|AFTER|MODAL|COUNTERFACTUAL>",
   "cue_type":"<explicit_marker|inferred>","confidence":"<high|medium|low>",
   "timeline_string":"[<earlier>][<later>]",
   "irrealis":null,
   "rationale":"<rule + why>"}]}
```
For future/imaginary, `irrealis` = `{sub_timeline_id, modal_force (dream|threat|prophecy|conditional|counterfactual|plan|wish), anchor_trigger, anchor_line, fate (realized|averted|open|never_actual), projects_back_to|null}`.

## Timeline schema (Step 6) — placeholder values
```json
{"story_id":"<id>","n_sentences":0,"main_timeline_string":"[e1][e2]...",
 "sub_timelines":[{"sub_timeline_id":"st1","modal_force":"<force>","slink_type":"<type>","anchor_line":0,"string":"[<sub event>]","fate":"<fate>","projects_back_to":null}],
 "iterative_compressions":[{"quote":"<verbatim>","approx_line":0,"note":"one telling compresses repeated events"}]}
```

---

## Constraints
No `.sty`; no web search for the corpus; no prior-run anchoring; all six steps and the six scripts are deliverables; every `trigger_text` verbatim; broaden recall but obey the precision discipline and the EVIDENTIAL guard; when genuinely unsure, flag `inferred`/`low` rather than skip.

## When you finish
Write `run_report.md`: per-story per-track counts; `explicit_marker` vs `inferred` split; imaginary predictions broken down by `slink_type`; sub-timelines by `modal_force`/`fate`; and any non-iconicity no rule covers. Do not score yourself. Confirm `code/` holds the six scripts you ran.
