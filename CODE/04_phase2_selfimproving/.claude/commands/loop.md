Run the Kit 8 keep-best improvement loop. You are the orchestrator.

STATE: `state.json` holds {iteration, best_three_way_accuracy, best_three_way_macro_f1,
best_commit, status}. `curve.json` holds the per-iteration record incl. best_so_far.
Resume-safe: always read state.json first and continue from there.

ITERATION 0 (only if state.iteration == 0 and no baseline recorded):
  runner -> scorer (out to iterations/iter_00/feedback.json) -> record as best,
  commit "iter0 baseline" in classifier/, append curve.json, set iteration=1.

EACH ITERATION N >= 1:
 1. improver: one focused change + git commit in classifier/.
 2. CACHE RULE: if the change altered the LLM prompt or few-shot examples, archive
    classifier/llm_cache.json into iterations/iter_NN/ and delete it before running,
    so the score reflects the new prompt. Routing/rules-only changes keep the cache.
 3. runner: python classifier/classify.py. If PARTIAL COVERAGE (LLM quota died):
    do NOT score. Set status="awaiting_quota", save state, STOP and tell the user to
    resume with /loop after the quota reset (the cache makes the re-run free).
 4. scorer: score into iterations/iter_NN/feedback.json; report aggregates.
 5. KEEP-BEST DECISION (this is what makes the reported curve monotone, honestly):
    ACCEPT iff three_way_accuracy > best AND three_way_macro_f1 >= best_macro - 0.01
      (the macro guard rejects blanket-prediction gaming: accuracy gained by
       collapsing predictions to one class will not carry macro-F1 and is reverted).
    Tie or drop on accuracy: accept iff three_way_macro_f1 improves and accuracy
    stays within 0.005 of best (macro-F1 gains matter for the current target).
    On ACCEPT: update best_* and best_commit in state.json.
    On REJECT: cd classifier && git reset --hard <best_commit> - the change is undone.
 6. Append to curve.json: {iter, attempted_change, accuracy, macro_f1, decision,
    best_so_far_accuracy}. best_so_far NEVER decreases - by construction, not by fiat.
 7. Checkpoint feedback + decision into iterations/iter_NN/.

STOP RULE: stop when best three_way_accuracy >= 0.77 AND three_way_macro_f1 >= 0.70,
or after 3 consecutive REJECTed iterations (plateau), or at 15 total iterations -
whichever comes first. On plateau, report the best curve and the per-class F1 table
identifying which class binds.

HONESTY INVARIANTS (never override): gold and scorer are untouchable; the improver
never sees per-pair answers; a flat iteration is recorded as flat; if a number jumps
suspiciously, inspect the prediction DISTRIBUTION (not the gold) before accepting.
