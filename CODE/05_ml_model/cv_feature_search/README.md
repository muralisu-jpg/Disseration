# Iterative ML Model — honest CV-driven improvement

An iterative temporal-relation classifier that improves itself each iteration by trying a new
feature or hyperparameter, keeping a change ONLY if it improves 5-fold CROSS-VALIDATION
macro-F1 on the training data. The TEST set is scored exactly ONCE, at the end, on the final
model — so the improvement is real, not test-set overfitting.

## Why this design (important)
A loop that keeps whatever raises the TEST score would climb forever and be MEANINGLESS
(it memorises the test set). This loop instead optimises cross-validation and touches the test
set once. That is the standard, honest way to iterate — and it means the curve plateaus
rather than fake-climbing.

## What it found
- iter 0 baseline (base features):        CV macro-F1 0.6172
- iter 1 +distance:                        0.6785  KEPT
- iter 2 +sameword:                        0.7149  KEPT
- iter 3-11 (more features + hyperparams): ALL REJECTED (plateau)
- FINAL test set (scored once): accuracy 0.7792, macro-F1 0.5290

The model improves for two iterations, then plateaus — every later change is rejected because
none improves cross-validation. This empirically confirms the feature ceiling: systematic
iteration finds the few features that matter (distance, word-identity) and cannot improve past
them. See out/improvement_curve.png.

## Honest notes
- This is NOT a new best model. The prior condAD model (0.788 acc / 0.645 macro-F1) is better
  on macro-F1; this loop picked a smaller feature set optimised for CV macro-F1 and traded some
  rare-class performance. The VALUE here is the honest *process* and the plateau finding.
- 3-way metric (before/after/overlap), matching Kit 8/9. Switch collapse() for 4-way.
- Green points = kept (improved CV); grey = rejected. Blue line = best-kept; dashed = all trials.

## Run
  pip install scikit-learn numpy matplotlib
  python iterative_model.py        # runs the loop, scores test once, saves iterative_result.json

## Files
  iterative_model.py            the loop (feature blocks + hyperparameter candidates)
  out/improvement_curve.png     the honest improvement curve
  out/iterative_result.json     full per-iteration log + final test score
