"""Weighted / filtered training - extract value from AI labels without dilution.
Usage examples (from kit9 root):
  # AI labels down-weighted to 0.25:
  python upgrades/train_weighted.py --train train_examples:1.0 --train n2_train:1.0 ^
         --train teacher_labels:0.25 --model condW.joblib
  # AI labels: only the classes A+D is weak on, at moderate weight:
  python upgrades/train_weighted.py --train train_examples:1.0 --train n2_train:1.0 ^
         --train "teacher_labels:0.5:SIMULTANEOUS,IDENTITY,INCLUDES,IS_INCLUDED,AFTER,IAFTER" ^
         --model condF.joblib
Then predict + score as usual with student/predict.py (model file is compatible).
"""
import json, argparse, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent.parent / "student"))
from train_student import featurize, load_pairs

def main():
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.model_selection import StratifiedKFold
    import joblib
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", action="append", required=True,
                    help="dir[:weight[:CLASS1,CLASS2,...]]")
    ap.add_argument("--model", default="student_weighted.joblib")
    a = ap.parse_args()
    X, y, w = [], [], []
    for spec in a.train:
        parts = spec.split(":")
        d = parts[0]; weight = float(parts[1]) if len(parts) > 1 else 1.0
        only = set(parts[2].upper().split(",")) if len(parts) > 2 else None
        recs = [r for r in load_pairs(d) if r.get("relation")]
        if only:
            recs = [r for r in recs if r["relation"].upper() in only]
        for r in recs:
            X.append(featurize(r)); y.append(r["relation"].upper()); w.append(weight)
        print(f"{d}: {len(recs)} pairs at weight {weight}" + (f" (classes {sorted(only)})" if only else ""))
    X = np.array(X); y = np.array(y); w = np.array(w)
    m = GradientBoostingClassifier(n_estimators=300, max_depth=3, learning_rate=0.08,
                                   random_state=0)
    # quick weighted CV report (train-only)
    skf = StratifiedKFold(5, shuffle=True, random_state=0)
    from sklearn.metrics import f1_score
    scores = []
    for tr, va in skf.split(X, y):
        m.fit(X[tr], y[tr], sample_weight=w[tr])
        scores.append(f1_score(y[va], m.predict(X[va]), average="macro"))
    print(f"weighted 5-fold CV macro-F1: {np.mean(scores):.3f}")
    m.fit(X, y, sample_weight=w)
    joblib.dump(m, a.model)
    print("saved", a.model)

if __name__ == "__main__":
    main()
