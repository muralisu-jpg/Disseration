# Verification log — all inputs, steps, and results double-checked

## Input (verified)
- 15/15 ProppLearner stories have Propp-function annotations (rep.function layer).
- 187 total functions, ALL 187 mapped to readable names + canonical order (0 unmapped).
- Important verbs verified against raw story text at their offsets (exact match, e.g.
  Villainy -> "seized her and dragged", Struggle -> "fought", Victory -> "defeated").

## Part 1 results (verified, reproduced)
- Per-function correct/wrong counts reproduce exactly.
- Initial situation 13/0 (100%), Villainy 10/3 (77%), Wedding 8/2 (80%),
  Mediation 6/1 (86%), Receipt of magical agent 1/11 (8%).
- Per-story: Shabarsha/Ivanko/Frolka 100%; Runaway Soldier 7%; Bukhtan 18%.
- Every function has a non-empty important verb (0 missing of 187).

## Part 2 results (verified, reproduced)
- Overall told-matches-canonical: 91.3% (reproduced exactly).
- 101 total inversions (non-iconic function pairs).
- 3 perfectly-canonical tales; Runaway Soldier most non-iconic (74.7%, 23 inversions).

## Cross-check
- All 10 headline claims in the report cross-checked against the JSON outputs: ALL PASS.

## Honest notes
- Rare functions (Delivery, Trickery, Complicity, Punishment) show 100% from only 1
  example each -- treat per-function accuracy as reliable only for common functions.
- "Correct/wrong" = told in canonical Propp order vs out of sequence. If a different
  definition of "narratime correct" is wanted, the criterion in part1 is one line to change.
- The function layer offsets align directly (no +1 shift), unlike the event layer; the
  extracted verbs were verified against raw text to confirm.
