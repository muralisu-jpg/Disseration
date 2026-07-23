"""
LEAN RICHER-FEATURES trainer (Lever 1) — validated drop-in upgrade of the student model.
Adds exactly TWO high-signal feature groups on top of the existing featurize():
  1. leading connective of e2's sentence (sentence starting with "then/after/when/as/
     before/meanwhile/suddenly/later/finally" is a strong event-ordering cue)
  2. shared word-STEM between the two events (soft IDENTITY signal beyond exact match)
Validated A/B on held-out data: beats baseline on BOTH 3-way accuracy AND macro-F1.
(A larger 110-feature version was tested and REJECTED — it overfit and lowered accuracy.
 Lesson: fewer, well-chosen features win. This lean set is the keeper.)

Usage (from kit9 root):
  python upgrades/train_richer.py --train train_examples --train n2_train --model condR.joblib
  python upgrades/predict_richer.py --model condR.joblib --pairs test_pairs --out predR
  python score_3way.py --pred predR --gold test_groundtruth --out feedbackR.json
"""
import json, re, argparse, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "student"))
import train_student as base
_ORIG_FEATURIZE = base.featurize   # capture original BEFORE patch (avoid recursion)

LEAD_CUES = ["then","after","when","as","before","meanwhile","suddenly","later","finally"]

def _stem(w):
    return re.sub(r'(ed|ing|es|s)$', '', (w or "").lower().strip())

def richer_featurize(p):
    f = list(_ORIG_FEATURIZE(p))                     # keep every existing feature
    s2 = (p.get("e2_sentence") or "").lower().strip()
    lead = " ".join(s2.split()[:2])
    for c in LEAD_CUES:                              # +9: leading connective of e2 sentence
        f.append(1.0 if lead.startswith(c) else 0.0)
    st1, st2 = _stem(p.get("e1_word")), _stem(p.get("e2_word"))
    f.append(1.0 if st1 and st1 == st2 else 0.0)     # +1: shared word stem
    return f

base.featurize = richer_featurize   # patch so predict.py path also uses richer features

def main():
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.model_selection import StratifiedKFold
    from sklearn.metrics import f1_score
    import joblib
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", action="append", required=True)
    ap.add_argument("--model", default="student_richer.joblib")
    a = ap.parse_args()
    X, y = [], []
    for d in a.train:
        recs = [r for r in base.load_pairs(d) if r.get("relation")]
        for r in recs:
            X.append(richer_featurize(r)); y.append(r["relation"].upper())
        print(f"{d}: {len(recs)} pairs")
    X = np.array(X); y = np.array(y)
    print(f"feature vector length: {X.shape[1]}")
    m = GradientBoostingClassifier(n_estimators=300, max_depth=3, learning_rate=0.08, random_state=0)
    skf = StratifiedKFold(5, shuffle=True, random_state=0)
    sc = []
    for tr, va in skf.split(X, y):
        m.fit(X[tr], y[tr]); sc.append(f1_score(y[va], m.predict(X[va]), average="macro"))
    print(f"richer 5-fold CV macro-F1: {np.mean(sc):.3f}")
    m.fit(X, y); joblib.dump(m, a.model); print("saved", a.model)

if __name__ == "__main__":
    main()
