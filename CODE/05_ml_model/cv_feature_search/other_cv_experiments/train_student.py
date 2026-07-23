"""Kit 9 - student model: featurize pair records and train/predict a classical classifier.
Same pair-record schema as Kit 8 (train_examples/test_pairs JSON).
Usage:
  python student/train_student.py --train <dir_or_file.json> [--train2 ...] --model out/model.joblib
  python student/predict.py --model out/model.joblib --pairs test_pairs --out predictions_student
"""
import json, re, argparse
from pathlib import Path
import numpy as np

CONNECTIVES = ["while", "when", "as", "after", "before", "then", "until", "during",
               "meanwhile", "once", "till"]
TENSES = ["PAST", "PRESENT", "FUTURE", "INFINITIVE", "PRESPART", "PASTPART", "NONE"]
CLASSES = ["OCCURRENCE", "STATE", "REPORTING", "I_ACTION", "I_STATE", "PERCEPTION", "ASPECTUAL"]
ASPECTS = ["NONE", "PERFECTIVE", "PROGRESSIVE", "PERFECTIVE_PROGRESSIVE", "BOTH", "PERFECT"]

def onehot(val, vocab):
    v = [0.0] * (len(vocab) + 1)
    val = (val or "NONE").upper()
    v[vocab.index(val) if val in vocab else len(vocab)] = 1.0
    return v

def between_text(p):
    """words between the two event mentions when they share a sentence"""
    if not p.get("same_sentence"):
        return ""
    s = (p.get("e1_sentence") or "").lower()
    w1, w2 = (p.get("e1_word") or "").lower().strip(), (p.get("e2_word") or "").lower().strip()
    i, j = s.find(w1), s.find(w2)
    if i < 0 or j < 0:
        return ""
    a, b = min(i, j), max(i, j)
    return s[a:b]

def featurize(p):
    f = []
    f += onehot(p.get("e1_class"), CLASSES)
    f += onehot(p.get("e2_class"), CLASSES)
    f += onehot(p.get("e1_tense"), TENSES)
    f += onehot(p.get("e2_tense"), TENSES)
    f += onehot(p.get("e1_aspect"), ASPECTS)
    f += onehot(p.get("e2_aspect"), ASPECTS)
    f.append(1.0 if p.get("same_sentence") else 0.0)
    f.append(1.0 if p.get("text_order") == "e1_first" else 0.0)
    w1 = (p.get("e1_word") or "").lower().strip()
    w2 = (p.get("e2_word") or "").lower().strip()
    f.append(1.0 if w1 == w2 else 0.0)
    dist = abs(int(p.get("e2_off", 0)) - int(p.get("e1_off", 0)))
    f += [1.0 if dist < 50 else 0.0, 1.0 if 50 <= dist < 200 else 0.0,
          1.0 if 200 <= dist < 1000 else 0.0, 1.0 if dist >= 1000 else 0.0]
    bt = between_text(p)
    for c in CONNECTIVES:
        f.append(1.0 if re.search(r'\b%s\b' % c, bt) else 0.0)
    s1 = (p.get("e1_sentence") or "").lower()
    for c in ["while", "when", "as soon as", "meanwhile", "at the same time"]:
        f.append(1.0 if c in s1 else 0.0)
    return f

def load_pairs(path):
    path = Path(path)
    files = sorted(path.glob("*.json")) if path.is_dir() else [path]
    out = []
    for fp in files:
        out += json.loads(fp.read_text(encoding="utf-8"))
    return out

def main():
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score
    import joblib
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", action="append", required=True,
                    help="dir(s)/file(s) of labelled pair JSON (records need a 'relation' field)")
    ap.add_argument("--model", default="student_model.joblib")
    a = ap.parse_args()

    recs = []
    for t in a.train:
        recs += [r for r in load_pairs(t) if r.get("relation")]
    X = np.array([featurize(r) for r in recs])
    y = np.array([r["relation"].upper() for r in recs])
    print(f"training on {len(recs)} labelled pairs, {len(set(y))} relation types")

    cands = {
        "logreg": LogisticRegression(max_iter=2000, C=1.0, class_weight="balanced"),
        "gboost": GradientBoostingClassifier(n_estimators=300, max_depth=3,
                                             learning_rate=0.08, random_state=0),
    }
    best, best_cv = None, -1
    for name, m in cands.items():
        cv = cross_val_score(m, X, y, cv=5, scoring="f1_macro").mean()
        print(f"  {name}: 5-fold CV macro-F1 = {cv:.3f}")
        if cv > best_cv:
            best, best_cv, best_name = m, cv, name
    best.fit(X, y)
    joblib.dump(best, a.model)
    print(f"selected {best_name} (CV {best_cv:.3f}); saved to {a.model}")

if __name__ == "__main__":
    main()
