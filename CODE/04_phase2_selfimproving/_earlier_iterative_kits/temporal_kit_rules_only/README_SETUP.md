# AI temporal-relation classifier kit (Level 3: the TimeML relation layer)

The AI learns from ONE example (The Witch's event pairs + their correct relations) +
guidelines, builds a general relation classifier, and is tested on 14 stories' pairs whose
answers it never sees. Given event pairs, it classifies the temporal relation for each.

## Why this task shows improvement
The majority-class floor is accuracy 0.51 but macro_f1 only 0.06 (guessing BEFORE).
So there is large honest headroom: real gains come from correctly classifying the
non-BEFORE relations, and macro_f1 rises as the loop improves them. Unlike the event
task (which started pinned at ceiling), this starts low with room to climb.

## What it scores (score_relations.py, fixed)
- accuracy: fraction of pairs correct
- macro_f1: average per-relation F1 (PRIMARY — where improvement shows)
- per-relation f1 breakdown

## 4 agents
improver, runner, scorer, orchestrator (/loop). At least 5 iterations, max 10.

## Setup (Windows PowerShell, from the kit folder)
  cd classifier ; git init ; git add -A ; git commit -m "empty baseline" ; cd ..
  $env:CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
  claude
then in Claude Code:  /loop

## Firewall
All agents see the example fully (the lesson). improver+runner see the 14 test PAIRS only
(no relations); scorer sees the 14 answer keys but emits only aggregate scores.

## Honest expectation
This is the hardest annotation level. Expect a LOW start (macro_f1 maybe 0.1-0.2) with
real room to climb as the loop learns to distinguish relation types. The CLIMB is the
result your supervisor wants to see — but it must be earned by the classifier, not forced.
