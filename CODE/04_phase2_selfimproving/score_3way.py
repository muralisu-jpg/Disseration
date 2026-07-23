"""LOCKED SCORER - Kit 8 (Monotone 3-Way Kit).
DO NOT EDIT. The improver/runner must never read or modify this file's data inputs.

Scores fine-grained TimeML temporal relation predictions against gold, and reports:
  - three_way_accuracy  (PRIMARY metric: before / after / overlap, collapse map fixed below)
  - three_way_macro_f1  (tie-breaker / honesty metric)
  - fine_macro_f1       (14-way diagnostic, continuity with Kits 4-7)
  - per-relation F1     (mechanism evidence)
Unpredicted pairs count as wrong (label "NONE"). Predictions for unknown pair_ids are ignored.

Usage:
  python score_3way.py --pred predictions --gold test_groundtruth --out feedback.json
"""
import json, argparse, sys
from pathlib import Path
from collections import Counter, defaultdict

# FIXED collapse map (locked). Any fine label not listed collapses to "overlap".
COLLAPSE = {
    "BEFORE": "before", "IBEFORE": "before",
    "AFTER": "after", "IAFTER": "after",
    "SIMULTANEOUS": "overlap", "IDENTITY": "overlap", "INCLUDES": "overlap",
    "IS_INCLUDED": "overlap", "DURING": "overlap", "DURING_INV": "overlap",
    "BEGINS": "overlap", "BEGUN_BY": "overlap", "ENDS": "overlap", "ENDED_BY": "overlap",
}
FINE_LABELS = sorted(COLLAPSE.keys())

def c3(label):
    if label is None or label == "NONE":
        return "NONE"
    return COLLAPSE.get(label.upper().strip(), "overlap")

def f1_scores(gold, pred, labels):
    labels = [lab for lab in labels if lab in gold] or labels  # only labels with gold support
    per = {}
    for lab in labels:
        tp = sum(1 for g, p in zip(gold, pred) if g == lab and p == lab)
        fp = sum(1 for g, p in zip(gold, pred) if g != lab and p == lab)
        fn = sum(1 for g, p in zip(gold, pred) if g == lab and p != lab)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        per[lab] = dict(precision=round(prec, 3), recall=round(rec, 3), f1=round(f1, 3),
                        support=sum(1 for g in gold if g == lab))
    macro = sum(v["f1"] for v in per.values()) / len(labels) if labels else 0.0
    return per, macro

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", default="predictions")
    ap.add_argument("--gold", default="test_groundtruth")
    ap.add_argument("--out", default="feedback.json")
    a = ap.parse_args()

    gold_all, pred_all = {}, {}
    for gp in sorted(Path(a.gold).glob("*.json")):
        gold_all.update(json.loads(gp.read_text(encoding="utf-8")))
    for pp in sorted(Path(a.pred).glob("*.json")):
        try:
            pred_all.update(json.loads(pp.read_text(encoding="utf-8")))
        except Exception as e:
            print(f"WARN: could not read {pp}: {e}", file=sys.stderr)

    ids = sorted(gold_all.keys())
    g_fine = [gold_all[i].upper() for i in ids]
    p_fine = [(pred_all.get(i) or "NONE").upper().strip() for i in ids]
    g3 = [c3(x) for x in g_fine]
    p3 = [c3(x) for x in p_fine]

    n = len(ids)
    covered = sum(1 for x in p_fine if x != "NONE")
    acc3 = sum(1 for g, p in zip(g3, p3) if g == p) / n if n else 0.0
    per3, macro3 = f1_scores(g3, p3, ["before", "after", "overlap"])
    perF, macroF = f1_scores(g_fine, p_fine, FINE_LABELS)
    pred_dist = Counter(p3)

    fb = dict(
        n_gold_pairs=n,
        n_predicted=covered,
        coverage=round(covered / n, 4) if n else 0,
        three_way_accuracy=round(acc3, 4),
        three_way_macro_f1=round(macro3, 4),
        three_way_per_class=per3,
        fine_macro_f1=round(macroF, 4),
        fine_per_relation=perF,
        prediction_distribution_3way=dict(pred_dist),
        primary_metric="three_way_accuracy",
        baselines=dict(majority_three_way_accuracy=0.676, majority_three_way_macro_f1=0.269,
                       sota_three_way_accuracy=0.77),
    )
    Path(a.out).write_text(json.dumps(fb, indent=1), encoding="utf-8")
    print(json.dumps({k: fb[k] for k in
                      ["n_gold_pairs", "coverage", "three_way_accuracy",
                       "three_way_macro_f1", "fine_macro_f1",
                       "prediction_distribution_3way"]}, indent=1))

if __name__ == "__main__":
    main()
