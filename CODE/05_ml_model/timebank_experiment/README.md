# TimeBank Training + Propp Timeline Experiment

Tests two questions with the ML relation model, scored against GROUND TRUTH:
  1. Does adding TimeBank 1.2 (183 news articles, 3,481 temporal pairs) to training help?
  2. Does using Propp's canonical function order improve the event timeline?

## Files
  parse_timebank.py       parses TimeBank .tml -> training pairs (run first)
  full_experiment_v2.py   trains (with/without TimeBank), predicts, builds 3 timelines,
                          scores MODEL and PROPP-MODEL timelines vs ground truth
  experiment_result.json  the results

## Findings (all honest, all negative-transfer)
1. TimeBank HURTS the model: 0.779 -> 0.774 acc, 0.637 -> 0.547 macro-F1.
   News temporal patterns don't transfer to folktales (cross-genre dilution).
2. Propp HURTS the timeline: model 88.6% -> propp-model 76.7% vs ground truth.
   Forcing canonical function order erases the genuine non-iconicity.
3. The MODEL ALONE builds an 88.6%-accurate timeline vs ground truth (good on its own).

## Run
  python parse_timebank.py          # needs TimeBank at /tmp/timebank/... (edit path)
  python full_experiment_v2.py

## Alignment note
Model predicts on event OFFSETS; gold + functions use event IDs. The kit maps offset->id
via event_offsets so all three timelines share one id-space (this was the key fix that made
the timeline comparison real rather than circular).
