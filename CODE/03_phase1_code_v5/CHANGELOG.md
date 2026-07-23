# CHANGELOG -- non-iconicity pipeline (v5 refinement)

Improvements only -- module boundaries, public function names, and the output schema are
unchanged. Each rule remains a general construction (no story-specific phrases, no answer key).
Baseline (before these edits) is preserved in `predictions_baseline/` and `run_report_baseline.md`.

Totals: baseline **568** -> refined **536** (past 119->87, present 53->79, future 222->179,
imaginary 174->191). The net drop is almost entirely removed false positives; recall was added
where it is linguistically sound.

## Past (`pipeline/rules.py`)
- **POS-anchored participle test (`pp_ok`).** P1/P2/P7/P9 previously accepted any word whose
  suffix matched `(ed|en|wn|ne|...)`, so "had **seven** sons", "had **golden** hair", "have
  **often**" all fired as past perfect. They now require the candidate to be tagged **VBN** by
  NLTK *or* to be in the closed irregular-participle list. *Effect:* removes a large class of
  past false positives; the remaining "had/have + PP" hits are genuine anteriors.
- **P2 attaches to its own clause.** "having + PP" used to fan out to *every* matrix verb in the
  sentence (one prediction per verb). It now links to the nearest following matrix verb -- the
  clause it actually modifies. *Effect:* fewer duplicate-ish past rows, higher precision.
- **P3 / P6 / P8 require a finite verb.** The retrospective-adverbial (P3) and the `after`/`from`
  + V-ing subordinator rules (P6/P8) now fire only when there is a real matrix verb to be anterior
  to; otherwise they are skipped. *Effect:* stops them firing on non-anterior uses.
- **P11 preposed / absolute participial clause (new).** Detects the reduced absolute
  "the work done, **he** left" / "his sword drawn, **he** charged": a participle preceded only by a
  noun phrase (no subject pronoun / finite verb) and followed by a comma + an independent clause
  with its own pronoun subject. *Effect:* general recall for absolutes; in this folktale register
  the construction does not actually occur, and the strict shape keeps it from surfacing the
  VBD/VBN mis-tags that a looser version produced (verified: a permissive version emitted only
  mis-tags such as "the king came, feasted, ...").
- **Low-confidence past rules behind the gate.** P5 (recollection) and P10 (discovery + stative)
  dropped to 0.45 so the default 0.5 gate excludes them; they reappear only when `THRESHOLDS["past"]`
  is lowered. *Effect:* precision-favoring default, recall recoverable on demand.

## Present (`pipeline/rules.py`)  -- the thinnest track, most gain
- **Shared-clause requirement.** The co-temporal connectives `while` / temporal `as` / `until`
  (R1/R2/R4) now fire only when there is a matrix verb on *both* sides -- a practical proxy for the
  "shared participant / two overlapping events" requirement (true coreference is unavailable in a
  blind, NLTK-only pipeline). *Effect:* drops connective hits that had nothing to overlap.
- **R6 participial (-ing) adjunct overlap (new).** "she wrote ..., **asking** ...", "the dragon,
  **seeing** that ..., went out": a bare present-participle adjunct (not under be/aux, not governed
  by a re-timing subordinator) runs *simultaneously* with its matrix verb (Allen DURING/overlaps).
  *Effect:* the biggest present-track recall gain (+37 here), all genuine co-temporal pairs.
- **R7 durative-includes-punctual (new, inferred).** Within one clause, a stative/durative finite
  verb that co-occurs with a punctual event places the punctual *inside* the state. Confidence 0.45,
  so it sits behind the default gate with R5. *Effect:* extra Allen coverage available at
  `THRESHOLDS["present"] <= 0.45`.

## Future (`pipeline/rules.py`)
- **F2 imperative-with-fulfilment.** A sentence-initial bare verb used to count as future
  unconditionally (55 hits, many spurious -- including questions). It now counts only when the
  commanded act is actually carried out later in the text (the verb stem recurs as a finite event
  after the sentence), questions are excluded, and the prediction carries a `later` reference to the
  fulfilment. *Effect:* 55 -> 12, each justified by a real later occurrence; `cue_type` honestly
  `inferred` (the cue is structural + fulfilment, not a surface marker).
- **Non-predictive `would` suppressed.** Habitual "would often / would always / ..." no longer
  generates an I7 modal prediction; it is routed to the new habitual rule I9. (Kept `will`/`shall`/
  `going to` (F1) and the prediction/promise speech-act verbs (F3) as the future backbone.)

## Imaginary (`pipeline/rules.py`, `pipeline/timeline.py`)
- **EVIDENTIAL guard preserved** -- plain reported speech is still never flagged (the guard now also
  protects the new I9/I10).
- **I9 habitual / iterative / generic (new).** "used to", "would often", "each/every time",
  "whenever", "day after day", "again and again": a recurring event has no single timeline slot.
  `modal_force="habitual"`, fate `open`.
- **I10 negation-of-occurrence (new).** "never did X", "without V-ing", "failed to V", "no longer V":
  an event explicitly said not to happen lives on a counterfactual branch. `modal_force="averted"`,
  fate `never_actual`.
- **`_FATE` map extended** (`timeline.py`) with `averted -> never_actual`, `habitual/belief/embedded/
  imagined -> open`, so every modal force a rule can emit resolves to an explicit fate instead of the
  silent default.

## Cross-cutting
- **`cue_type` honesty.** Rules whose trigger is structural/inferred rather than a matched surface
  cue are now labelled `inferred`: F2 (fulfilment), R6/R7 (adjunct/durative structure), P11 (absolute
  structure), alongside the existing P5/P10/R5. Surface-marker rules (I9 "whenever", I10 "never",
  F4 "about to", F6 "if", connectives) stay `explicit_marker`.

## Threshold ablation (`run.py` `THRESHOLDS`, applied uniformly to all four tracks)
| thr | past | present | future | imaginary | total | note |
|----|----|----|----|----|----|----|
| 0.4 | 89 | 104 | 179 | 191 | 563 | surfaces inferred present (R5 statives, R7 durative) |
| **0.5** | **87** | **79** | **179** | **191** | **536** | **default -- balanced precision/recall** |
| 0.6 | 87 | 42 | 144 | 90 | 363 | drops mid-confidence modal (I7) and desire/expectation (F5/F6) |
| 0.7 | 67 | 19 | 131 | 36 | 253 | only high-confidence cues: had+PP, will/shall, if/unless, pretence |

Raise the per-track gate toward precision (0.6-0.7 keeps only the strongest cues); lower it toward
recall (0.4 turns on the inferred Allen-overlap present rules). The gates are the single set of
tunables and can be set independently per track in `run.py`.
