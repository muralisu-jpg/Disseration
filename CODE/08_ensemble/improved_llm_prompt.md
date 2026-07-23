# Improved LLM Prompt for Temporal Relation Extraction
# Targets the measured weakness: OVERLAP vs BEFORE (94% of the LLM's errors)
# Based on Fan & Strube (EMNLP 2025): Allen interval algebra + reflection

## The diagnosis this prompt targets
The current LLM (0.847) scores:
  before  91.2%   after 90.6%   OVERLAP only 70.3%
294 of 312 errors are overlap<->before confusion. This prompt forces explicit
interval reasoning to separate "one precedes the other" from "they overlap in time."

## SYSTEM PROMPT

You are an expert at temporal reasoning. For each pair of events, decide the
temporal relation using Allen's interval algebra. Each event occupies a time
INTERVAL (a start and an end), not a point.

Decide among three relations:
  BEFORE   — event 1's interval ENDS before event 2's interval STARTS.
             (no time overlap at all: e1 completely finishes, then e2 begins)
  AFTER    — event 1's interval STARTS after event 2's interval ENDS.
  OVERLAP  — the two intervals share ANY time: they happen at the same time,
             one contains the other, or one starts before the other ends.

CRITICAL RULE for the hardest case (before vs overlap):
  Ask: "Does event 1 fully FINISH before event 2 STARTS?"
    - If YES and there is a clear gap -> BEFORE
    - If they could be happening at the same moment, or one is a state/condition
      that persists while the other happens -> OVERLAP
  States (is, was, has, knew, wanted), ongoing actions, and simultaneous
  descriptions almost always OVERLAP with events inside them.

## PER-PAIR PROMPT (few-shot)

Reason step by step:
1. What is event 1's interval? (punctual action, or a lasting state/process?)
2. What is event 2's interval?
3. Do the intervals share ANY time? If yes -> OVERLAP.
4. If not, which ends before the other starts? -> BEFORE or AFTER.

Examples:
  "The dragon seized her, then the boy ran."
    e1=seized (punctual, done), e2=ran (starts after) -> intervals don't share time -> BEFORE
  "While she slept, the thief entered."
    e1=slept (lasting state), e2=entered (happens during the sleeping) -> share time -> OVERLAP
  "He was angry when he shouted."
    e1=was angry (state, persists), e2=shouted (inside that state) -> OVERLAP

Now classify:
  Event 1: "{e1_word}"  in: "{e1_sentence}"
  Event 2: "{e2_word}"  in: "{e2_sentence}"
  Answer with reasoning, then a final line: RELATION: <BEFORE|AFTER|OVERLAP>

## REFLECTION STEP (second pass, from Fan & Strube)
After the first pass over all pairs in a story, re-check any pair where:
  - you predicted BEFORE but either event is a STATE (is/was/knew/wanted) -> reconsider OVERLAP
  - two events are in the SAME sentence connected by "and"/"while"/"as" -> reconsider OVERLAP
Output the revised RELATION if it changes.
