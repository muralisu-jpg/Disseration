# Propp Morphology + Narrative Time Analysis

Implements two analyses your professor requested, both using the GOLD Propp-function
annotations already in the ProppLearner .sty files (rep.function layer). No LLM/quota needed.

## PART 1 — Important verbs + correct/wrong per function and per story
part1_verbs_correctness.py
- Extracts the IMPORTANT VERB (anchoring event) of every Propp function across all 15 stories.
- Determines whether each function is TOLD in its correct canonical position (correct) or
  out of sequence (wrong).
- Aggregates: which FUNCTIONS are most often correctly vs wrongly placed, and which STORIES
  (narratives) have more correct vs wrong placements.
Output: out/part1_verbs_correctness.json

## PART 2 — Narrative ordering vs Propp's canonical sequence (non-iconicity)
part2_ordering.py
- For each story, compares the TOLD order of Propp functions to Propp's CANONICAL order.
- Measures how well told-order matches canonical (91.3% overall), and counts INVERSIONS
  = pairs of functions told out of canonical sequence = narrative-level NON-ICONICITY.
Output: out/part2_ordering.json

## Run
  python part1_verbs_correctness.py
  python part2_ordering.py

## Data
  data/propp_functions.json  — extracted functions (code, readable name, important verb,
                                canonical order, linked event ids) for all 15 stories.

## Key findings (from the gold annotations)
- 91.3% of Propp-function pairs are told in canonical order; 8.7% are non-iconic (101 inversions).
- Functions best-placed: Initial situation (100%), Mediation (86%), Wedding (80%).
- Functions worst-placed: Interdiction/Absentation/Transfiguration (0%), Receipt of magical agent (8%).
- Narratives most canonical: Shabarsha, Ivanko, Frolka (100%); least: Runaway Soldier (7%),
  Bukhtan (18%) — these tell the story most out-of-sequence (most non-iconic).
