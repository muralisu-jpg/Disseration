# Implementation Demo — file map & 10-minute running order

Everything referenced in the presentation, organised in the order you present it.
Folder numbers match the demo sequence.

---

## 01_ground_truth/

**`sty_files/`** — all **15** ProppLearner `.sty` annotation files. These are the
expert human annotations — the ground truth every number in the talk is measured
against. Stand-off format: each layer points into the text by character offset.

**`raw_texts/`** — the 15 folktales as plain text.

> **Show:** open one `.sty` next to its `.txt`. That is the task in one screen —
> raw story on the left, expert answer on the right.

---

## 02_prompts/

- **`prompt_claude_code.md`** — what Claude Code was given: full pipeline spec.
- **`prompt_claude_code_v4.md`** — the later, tightened version.
- **`prompt_cowork.md`** — what Claude Cowork was given: **one paragraph**.
- **`prompt_code_v5_spec.md`** — the v5 specification.

> **Show:** the two prompts side by side. The asymmetry is the whole experiment
> and it is visible at a glance — no explanation needed.

---

## 03_phase1_code_v5/  — the detector (RUNNABLE)

Complete Claude Code v5 pipeline.

- `run.py` — entry point
- `pipeline/rules.py` — the 26 TimeML rules (P1 pluperfect, P9, P10 discovery…)
- `pipeline/events.py`, `timeline.py`, `predictions.py`, `selfcheck.py`
- `predictions/` — 15 stored output files (one per story)
- `predictions_baseline/` — the baseline run for comparison
- `CHANGELOG.md` — what changed v1 → v5
- `run_report.md` — the run summary

**Live command (~5 s):**
```
cd 03_phase1_code_v5
python run.py texts predictions_live
```
Deterministic — 536 predictions. Needs `nltk` with `punkt`.

> **Show:** `rules.py` — scroll to P1 (the "had + participle" rule). This is the
> concrete thing the whole "rules hit a ceiling" argument is about.

---

## 04_phase2_selfimproving/  — the multi-agent kit (RUNNABLE)

The self-improving loop, with the firewall.

**The agents (`.claude/`):**
- `agents/improver.md` — edits the classifier; reads teaching examples, never test answers
- `agents/runner.md` — runs the classifier over the test set
- `agents/scorer.md` — the firewalled scorer; returns aggregates only
- `commands/loop.md` — **the orchestrator**: the improve → run → score → decide loop
- `hooks/guard.py` — **the firewall itself**, blocking reads of the gold directory
- `settings.json` — hook wiring

**The data & code:**
- `classifier/` — the code the improver agent edited
- `score_3way.py` — the locked scorer
- `validate_scorer.py` — the three honesty tests
- `iterations/` — iter_00 … iter_03, each with its accepted/rejected rules + metrics
- `predictions/`, `test_pairs/`, `test_groundtruth/`, `train_examples/`
- `guidelines/`, `state.json`, `curve.json` — the loop's own record

**`_earlier_iterative_kits/`** — how the iterative coding developed:
- `code_iteration_build_kit/` — the Claude Code iteration kit: `iterations/iter_02…04`
  each holding a full `pipeline/` snapshot + `metrics.json` + `predictions/`.
  This is the clearest evidence of the loop editing real code round by round.
- `temporal_kit_rules_only/` — the rules-only kit that plateaued (8 of 12
  relations stuck at 0.00)

**Live commands (~5 s each):**
```
cd 04_phase2_selfimproving
python validate_scorer.py
python score_3way.py --pred predictions --gold test_groundtruth --out fb.json
```
First gives majority 0.676 / perfect 1.0 / spam 0.308. Second regenerates 0.848.

> **Run `validate_scorer.py` FIRST.** It earns trust in every number after it.

---

## 05_ml_model/  — the gradient-boosting model

- `stages/stage3_relations.py` — the 300-tree classifier and its features
- `stages/stage1_events.py`, `stage2_pairs.py` — event extraction and pairing
- `run_chain.py` — end-to-end chain
- `scorers/score_all.py`, `score_endtoend.py`
- `out/` — stored results (`chain/`, `events/`, `pairs/`, `relations/`)
- `training_data/` — `train_examples/`, `n2_train/`, `test_pairs/`, `test_groundtruth/`
- `timebank_experiment/` — the TimeBank test: hurt the pairs, helped the timeline
  (`experiment_result.json` holds the numbers)

> **Show:** the feature list in `stage3_relations.py`. "The model only sees
> numbers" becomes concrete here.

---

## 06_transformer/

- `finetune_transformer.py` — the distilRoBERTa fine-tune
- `Transformer_Colab.ipynb` — the notebook it ran in
- `README.md` — the result: **0.772, below the simple feature model**

> **Show:** 30 seconds. The point is that it *lost* — small data beats big models
> here.

---

## 07_llm_benchmark/  — the frozen benchmark

- `score_bench.py` — the scorer
- `bench/` — the benchmark harness
- `predictions/` — the LLM's stored answers
- `test_pairs/`, `test_groundtruth/`
- `README_BENCHMARK.md`

This is the 0.847 the model had to beat, and the source of the per-class
breakdown (before 91.2% / after 90.6% / **overlap 70.3%**).

---

## 08_ensemble/  — the contribution

- **`ensemble_v2.py`** — the confidence-gated stacking ensemble. **0.867 pairwise
  → 94.7% timeline.** This is your own design.
- `ensemble_v2_WINDOWS.py` — same, Windows paths
- `error_analysis.py` — reproduces the 70.3% overlap diagnosis
- `improved_llm_prompt.md` — the Allen interval prompt (written, unrun — needs quota)
- `consistency_correct.py` — the transitivity check (honest null: 0.8473 → 0.8473)

> **Show:** the confidence gate in `ensemble_v2.py` — the `predict_proba` max and
> the threshold. That single condition is the whole idea.

---

## 09_propp_analysis/

- `part1_verbs_correctness.py`, `part2_ordering.py`, `part3_check_claims.py`
- `out/` — the stored results, including the **91.3% adherence** and the
  **88.6% → 76.7%** timeline loss when Propp order is forced

---

# 10-minute running order

| # | Section | Time | Action |
|---|---------|------|--------|
| 1 | `01_ground_truth` | 1:00 | Open a `.sty` beside its `.txt` |
| 2 | `02_prompts` | 1:30 | Two prompts side by side |
| 3 | `03_phase1_code_v5` | 2:00 | Show `rules.py`, then **run `run.py`** |
| 4 | `04_phase2_selfimproving` | 2:30 | Show `.claude/agents/` + `hooks/guard.py`, then **run `validate_scorer.py`** and **`score_3way.py`** |
| 5 | `05_ml_model` | 1:30 | Feature list in `stage3_relations.py` |
| 6 | `06_transformer` | 0:30 | README — it lost |
| 7 | `07_llm_benchmark` + `08_ensemble` | 1:00 | 0.847 benchmark, then the gate in `ensemble_v2.py` |

**Only three commands run live.** Everything else is reading files. Test the
`nltk`/`punkt` install on the presentation machine beforehand.

**If a command fails live:** every folder already contains its stored outputs
(`predictions/`, `out/`, `iterations/*/metrics.json`), so you can show the result
without re-running.
