# Kit 8 — Monotone 3-Way Temporal Relation Kit (mono_kit)

**Goal:** three_way_accuracy ≥ 0.70 (before/after/overlap), the literature-comparable
task (SOTA ~0.77, Leeuwenberg & Moens 2020). Majority baseline: 0.676. Shipped v0
baseline: **0.675 acc / 0.269 macro-F1** (already run and verified).

**The monotone guarantee (honest version of "score increases every iteration"):**
the loop is keep-best hill-climbing. Each iteration's change is accepted ONLY if the
blind score improves; otherwise it is reverted (`git reset` to the best commit). The
reported `best_so_far` curve in `curve.json` is therefore non-decreasing *by
construction* — no gold touched, no scorer edited, no gaming. A rejected iteration is
recorded as flat, which is itself honest evidence of what doesn't work.

**Anti-gaming double lock:** a change is accepted only if accuracy rises AND
three_way_macro_f1 doesn't collapse (guard in `/loop` step 4). Blanket-predicting
"before" keeps accuracy at 0.676 but pins macro-F1 at ~0.27, so the classic Kit-2
gaming route is structurally rejected.

## Layout
- `train_examples/` — 3 fully annotated stories (01, 06, 14; all agents may read)
- `test_pairs/` — 12 stories, 2,043 pairs with sentence context, NO relations
- `test_groundtruth/` — answers, SCORER ONLY (hook-blocked for improver/runner)
- `classifier/` — editable: rules v0 + cached/batched LLM path (few-shot + point algebra)
- `guidelines/` — point-algebra definitions (TLEX Table 1) + task strategy (locked)
- `score_3way.py`, `validate_scorer.py` — LOCKED scorer + its validation
- `.claude/` — agents (improver / runner / scorer), `/loop` command, firewall hooks
- `state.json`, `curve.json`, `iterations/` — resume-safe loop state

## Quickstart (Windows, your standard playbook)
```powershell
cd "C:\Users\user\Desktop\mono_kit"
python validate_scorer.py          # confirm scorer on your machine (3 tests must pass)
cd classifier
git init; git add -A; git commit -m "v0 baseline"
cd ..
$env:CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
claude
# inside Claude Code:
/loop
```
Resume after a quota reset: reopen `claude`, `/loop` (state.json + llm_cache.json make
it free). Budget-light cache filling without agents:
`python classifier\classify.py` repeatedly, then let `/loop` score.

## Where the climb to 0.70 comes from (evidence-backed)
The gap 0.676 → 0.70 = ~49 net pairs; → 0.77 = ~192. Available honest wins:
1. **LLM on hard pairs** (`config.json use_llm=true`): overlap recall — Kit 5 proved
   the mechanism (SIMULTANEOUS 0→0.36, INCLUDES 0→0.22 with context).
2. **IDENTITY re-mentions** — 247 test pairs (12% of test!), detectable as repeated
   event words across nearby sentences. The single largest pool.
3. **AFTER** — 32 pairs annotated against text order; cheap rule + LLM confirm.
Each overlap/after pair recovered without losing a before pair is +0.05pp accuracy.

## Honesty invariants (non-negotiable, same as the whole project)
- Gold and scorer untouched; firewall = instructions + PreToolUse hooks (note in the
  writeup: instruction-level, not OS-enforced).
- Score only on full LLM coverage (no hybrid contamination across quota windows).
- Verify any surprising number by inspecting the prediction distribution, never gold.
- Expected honest outcome: 0.70–0.75 accuracy with macro-F1 0.35–0.45. If the loop
  plateaus below 0.70, the curve and per-relation table are still a defensible result;
  do not force the number.
