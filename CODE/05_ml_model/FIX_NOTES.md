# FIX APPLIED — event offset bug

## What was wrong
The gold event words were extracted with a +1 offset error: every event word was shifted
by one character ("said" -> " sai", "went away" -> "went awa"). So the scorer could never
match the LLM's correct predictions -> events F1 showed ~0.007 (a bug, not a real score).

## What was fixed
1. data/gold_events, gold_pairs, gold_relations regenerated with the +1 shift corrected.
2. Event scorer now matches on the HEAD word (first token), since gold events can be
   multi-word verb phrases. Validated gold-vs-gold = 1.0.
3. Chain end-to-end scorer validated (perfect chain -> 1.0, degraded -> 0.23).

## IMPORTANT — clear your old cache before re-running
Your previous run cached LLM predictions AND was scored against the broken gold. The LLM
predictions themselves are fine, but to be safe and get clean scores, delete the cache and
old outputs, then rerun:
    Remove-Item cache\*.json
    Remove-Item out\events\*.json, out\pairs\*.json, out\relations\*.json, out\chain\*.json
    python run_gold_input.py
(The Stage-1 LLM event predictions will be re-fetched, but now they'll be scored correctly.)
