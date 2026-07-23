# Pure-LLM Benchmark — Claude Opus 4.8 classifies ALL pairs directly

The clean "what does the LLM alone score" number. No rules, no ML — Opus 4.8 classifies
every one of the 2,043 test pairs, with few-shot from the 3 training stories + point-algebra
definitions. Reports BOTH metrics: 14-way (fine) and 3-way (before/after/overlap).

## Why both metrics
- 3-way (before/after/overlap): the LITERATURE-COMPARABLE number (published SOTA ~0.77) and
  the cross-corpus common denominator. This is how you claim "above SOTA".
- 14-way (fine): the honest, demanding number; corpus-specific, not comparable to other work.
- The gap between them (strong 3-way, weaker 14-way) is the "genuinely reading, not leaking"
  signature — evidence the result is real.

## Run (Windows PowerShell, from the kit folder)
  python bench\llm_benchmark.py
  # (batched 25/call, CACHED to bench\llm_bench_cache.json, resumable across quota windows;
  #  if the LLM hits quota it stops and saves — just rerun after reset to continue)
  python score_bench.py --pred predictions --gold test_groundtruth --out feedback.json
  Get-Content feedback.json

## Data
- bench/fewshot_*.json : the 3 training stories WITH relations (01, 06, 14) — the few-shot
- test_pairs/ : 12 stories, pairs WITH context but relations hidden (2,043 pairs)
- test_groundtruth/ : answer keys (scorer only)

## What this establishes
The pure-LLM ceiling on this task, to benchmark everything else against:
- rules ~0.72, feature-ML ~0.78, and now pure-LLM = (this run).
Kit 8's hybrid (rules+LLM) scored 0.848 3-way; this pure-LLM run tells you what the LLM does
on ALL pairs by itself. Expect it near or a bit below/above 0.848 depending on how the LLM
handles the easy pairs the rules previously took.

## Cost
2,043 pairs, batched 25/call = ~82 LLM calls per full pass. Much cheaper than the pairing
kit (this is classification of GIVEN pairs, not all-pairs judging). A few quota windows at most.
