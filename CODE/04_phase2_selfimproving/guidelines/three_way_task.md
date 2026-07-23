# The 3-way task (PRIMARY metric)
Fine labels collapse (fixed, locked in the scorer):
  before  = BEFORE, IBEFORE
  after   = AFTER, IAFTER
  overlap = SIMULTANEOUS, IDENTITY, INCLUDES, IS_INCLUDED, DURING, DURING_INV,
            BEGINS, BEGUN_BY, ENDS, ENDED_BY

Test distribution is imbalanced (~2/3 before). Majority baseline: accuracy 0.676.
Published SOTA on the collapsed 3-way task: ~0.77 (Leeuwenberg & Moens 2020; Zhang & Xue 2018 = 0.76).
Kit target: three_way_accuracy >= 0.70 while three_way_macro_f1 also rises
(macro-F1 is the anti-gaming check: blanket-predicting "before" keeps acc at 0.676
but leaves macro-F1 at ~0.27 -- a real climb must lift BOTH numbers).

Where the honest gains are (evidence from Kits 4-7):
1. OVERLAP recall. Rules cannot detect simultaneity/containment; the LLM with sentence
   context + point-algebra definitions can (Kit 5 lifted SIMULTANEOUS 0 -> 0.36).
   Every overlap pair correctly recovered adds accuracy above the 0.676 floor.
2. IDENTITY (247 test pairs, all "overlap"): re-mentions of the same event -- repeated
   verb/description across nearby sentences. Highest-volume single win available.
3. AFTER is rare (32 pairs): pairs annotated against text order. Small but cheap.
FORBIDDEN: blanket-prediction of any label; touching test_groundtruth or the scorer.
