# Full Pipeline Kit — story -> events -> pairs -> relations (LLM, both evaluations)

Three LLM operations chained into the full annotation pipeline, evaluated TWO ways.

## The three stages
  Stage 1:  story text        -> predicted EVENTS      (word + class/tense/aspect)
  Stage 2:  events            -> predicted PAIRS        (which events link)
  Stage 3:  pairs             -> predicted RELATIONS    (before/after/overlap/imaginary)

## The two evaluations (you asked for BOTH)
  EVAL 1 — GOLD INPUT per stage (run_gold_input.py):
    each stage gets PERFECT input, measured in isolation.
      Stage1: story      -> pred events    (vs gold events)
      Stage2: GOLD events-> pred pairs      (vs gold pairs)
      Stage3: GOLD pairs -> pred relations  (vs gold relations)
    -> tells you how good each stage is ON ITS OWN.

  EVAL 2 — TRUE CHAIN (run_chain.py):
    errors compound: story -> PRED events -> PRED pairs -> PRED relations.
    -> tells you how good the REAL end-to-end system is.

  The GAP between EVAL 1 and EVAL 2 = the cost of error compounding.

## Run (Windows PowerShell, from the kit folder)
  python run_gold_input.py     # EVAL 1 — rerun across quota windows (cached, resumable)
  python run_chain.py          # EVAL 2 — rerun across quota windows (cached, resumable)
  python summarize.py          # prints both side by side

Each stage is CACHED separately (cache/*.json). If the LLM hits quota it stops and saves;
just rerun the same command after reset — it skips finished stories/stages.

## Cost (honest)
This is the biggest LLM job in the project: Stage 1 reads every story in chunks, Stage 2
judges windowed candidate pairs, Stage 3 classifies. Across 12 test stories, BOTH evals,
expect MANY quota windows. Caching means no work is ever lost.

## Data
  data/stories/       raw story text (Stage 1 input)
  data/gold_events/   gold events (Stage 2 gold input + Stage 1 scoring)
  data/gold_pairs/    gold pairs  (Stage 3 gold input + Stage 2 scoring)
  data/gold_relations/ gold relations (Stage 3 scoring)
  data/split.json     3 train (few-shot) + 12 test

## What you get
Six numbers total: each of the 3 stages, under each of the 2 evaluations — plus the
compounding gap. This is the complete honest picture of the story->relations pipeline.
