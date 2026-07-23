# Project: AI temporal-relation classifier (match human TimeML links)

## The task
For each EVENT PAIR the human annotators linked, CLASSIFY the temporal relation between
the two events — exactly as the humans did. The pairs are GIVEN to you (you do NOT decide
which events to link). You only classify the relation for each given pair.

Relation labels (TimeML): BEFORE, AFTER, IBEFORE, IAFTER, SIMULTANEOUS, INCLUDES,
IS_INCLUDED, IDENTITY, DURING, DURING_INV, BEGINS, BEGUN_BY, ENDS, ENDED_BY.

## The setup (one-shot learning)
- LEARN from ONE example: example/09_The_Witch.sty (+ example/09_The_Witch_pairs.json and
  example/09_The_Witch_worked_relations.json — the pairs WITH their correct relations and
  the two events' tenses) and guidelines/.
- BUILD a general classifier in classifier/ that, given a story's event pairs, predicts
  the relation for each.
- TESTED on 14 other stories (test_pairs/) whose answer keys you must NOT look at.

## Input you get per test story: test_pairs/<story>.json
  [ {"pair_id":0, "e1":{"word":"said","off":32}, "e2":{"word":"went","off":40}}, ... ]
## Output you write: predictions/<story>.json
  [ {"pair_id":0, "relation":"BEFORE"}, ... ]   (one relation per pair_id)

## How it's scored (score_relations.py — fixed, locked)
- accuracy: fraction of pairs classified correctly
- macro_f1: average per-relation F1 (rare relations count equally — THIS is where real
  improvement shows; guessing BEFORE gives accuracy ~0.51 but macro_f1 only ~0.06)
- per_relation breakdown so improvement is visible per relation type

## IMPROVEMENT GUIDANCE (important)
The majority-class baseline is accuracy 0.51 / macro_f1 0.06 (always guess BEFORE).
Beating accuracy is easy-ish; the real goal is raising MACRO_F1 by correctly classifying
the non-BEFORE relations (IBEFORE, IDENTITY, SIMULTANEOUS, INCLUDES, AFTER, ...).
Each iteration should target a specific relation type that's scoring low and improve it.
DO NOT just predict BEFORE everywhere — that floors macro_f1. Build genuine distinctions
using event tense/aspect, signal words, and the guidelines.

## Hard rules (every agent)
- ALL agents may read: example/ (pairs + answers), guidelines/, CLAUDE.md.
- ONLY the scorer may read test_groundtruth/.
- improver + runner read test_pairs/ (pairs, NO relations) — NEVER test_groundtruth/.
- scorer emits ONLY aggregate scores to feedback.json.
- Build a GENERAL classifier. Never hard-code story-specific pairs.

## Folders
- example/  the ONE teaching story (pairs + correct relations) — all agents read
- guidelines/  official annotation guides — all agents read
- classifier/  the classifier code (improver builds/edits, runner runs)
- test_pairs/  14 test stories' event pairs, NO relations (improver/runner read)
- test_groundtruth/  14 answer keys — SCORER ONLY
- predictions/  runner writes, scorer reads
- iterations/  checkpoints
- score_relations.py  fixed scorer (locked)
- state.json, feedback.json
