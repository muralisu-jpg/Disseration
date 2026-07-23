#!/usr/bin/env python3
"""
ITERATIVE ML MODEL — honest version.
Each iteration proposes a change (feature or hyperparameter) and keeps it ONLY if it improves
5-fold CROSS-VALIDATION macro-F1 on the TRAINING data. The TEST set is scored exactly ONCE,
at the end, on the final model. This gives a genuine improvement curve without overfitting the
test set (the standard, honest way to iterate).

3-way metric here matches Kit 8/9. (Switch to 4-way by editing collapse().)
"""
import json, glob, os, sys
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import f1_score, accuracy_score

CLASSES=['OCCURRENCE','STATE','REPORTING','I_ACTION','I_STATE','PERCEPTION','ASPECTUAL']
TENSES=['PAST','PRESENT','FUTURE','INFINITIVE','PRESPART','PASTPART','NONE']
ASPECTS=['NONE','PERFECT','PROGRESSIVE']
CONN=['then','after','before','when','while','as','once','until','since','during','later','then']
CUES=['while','when','as soon as','meanwhile','during','after','before','until']

def onehot(v,opts): return [1.0 if v==o else 0.0 for o in opts]
def collapse(r):
    r=r.upper()
    if r in ('BEFORE','IBEFORE'): return 'before'
    if r in ('AFTER','IAFTER'): return 'after'
    return 'overlap'

# ---- feature blocks that the loop can turn ON or OFF ----
def feat_base(p):
    f=[]; f+=onehot(p.get("e1_class"),CLASSES); f+=onehot(p.get("e2_class"),CLASSES)
    f+=onehot(p.get("e1_tense"),TENSES); f+=onehot(p.get("e2_tense"),TENSES)
    f+=onehot(p.get("e1_aspect"),ASPECTS); f+=onehot(p.get("e2_aspect"),ASPECTS)
    f.append(1.0 if p.get("same_sentence") else 0.0)
    f.append(1.0 if p.get("text_order")=="e1_first" else 0.0)
    return f
def feat_sameword(p):
    w1=(p.get("e1_word")or"").lower().strip(); w2=(p.get("e2_word")or"").lower().strip()
    return [1.0 if w1==w2 else 0.0]
def feat_distance(p):
    d=abs(int(p.get("e2_off",0))-int(p.get("e1_off",0)))
    return [1.0 if d<50 else 0.0,1.0 if 50<=d<200 else 0.0,1.0 if 200<=d<1000 else 0.0,1.0 if d>=1000 else 0.0]
def feat_connectives(p):
    s=((p.get("e1_sentence")or"")+" "+(p.get("e2_sentence")or"")).lower()
    return [1.0 if c in s else 0.0 for c in ['then','after','while','when']]
def feat_cues(p):
    s=(p.get("e2_sentence")or"").lower()
    return [1.0 if c in s else 0.0 for c in CUES]
def feat_leadconn(p):   # richer: leading connective of e2's sentence
    s=(p.get("e2_sentence")or"").lower().strip()
    first=s.split()[0] if s.split() else ""
    return [1.0 if first==c else 0.0 for c in ['then','after','when','while','so','and']]
def feat_sharedstem(p): # richer: shared word stem (soft identity)
    w1=(p.get("e1_word")or"").lower().strip()[:4]; w2=(p.get("e2_word")or"").lower().strip()[:4]
    return [1.0 if w1 and w1==w2 else 0.0]
def feat_tensematch(p):
    return [1.0 if p.get("e1_tense")==p.get("e2_tense") else 0.0]

BLOCKS={"base":feat_base,"sameword":feat_sameword,"distance":feat_distance,
        "connectives":feat_connectives,"cues":feat_cues,
        "leadconn":feat_leadconn,"sharedstem":feat_sharedstem,"tensematch":feat_tensematch}

def build_X(pairs, active):
    X=[]
    for p in pairs:
        row=[]
        for name in active:
            row+=BLOCKS[name](p)
        X.append(row)
    return np.array(X)

def load(folders):
    pairs=[]
    for fo in folders:
        for f in glob.glob(f"{fo}/*.json"):
            pairs+=json.load(open(f))
    X_lab=[collapse(p["relation"]) for p in pairs]
    return pairs, X_lab

def load_test(pairs_dir, gt_file_dir):
    pairs=[]; 
    for f in glob.glob(f"{pairs_dir}/*.json"): pairs+=json.load(open(f))
    gt={}
    for f in glob.glob(f"{gt_file_dir}/*.json"): gt.update(json.load(open(f)))
    return pairs, gt

def make_model(hp):
    if hp["type"]=="gb":
        return GradientBoostingClassifier(n_estimators=hp["n"],max_depth=hp["depth"],learning_rate=hp["lr"],random_state=0)
    return LogisticRegression(C=hp["C"],max_iter=1000)

def cv_macro(pairs,labels,active,hp):
    X=build_X(pairs,active); y=np.array(labels)
    m=make_model(hp)
    skf=StratifiedKFold(n_splits=5,shuffle=True,random_state=0)
    scores=cross_val_score(m,X,y,cv=skf,scoring='f1_macro')
    return scores.mean()

def main():
    K=os.environ.get("KIT9", "../training_data")
    train_pairs,train_labels=load([f"{K}/train_examples",f"{K}/n2_train"])
    print(f"loaded {len(train_pairs)} training pairs (ProppLearner + N2)")

    # ---- ITERATIVE LOOP (CV-driven) ----
    active=["base"]                       # start minimal
    hp={"type":"gb","n":100,"depth":3,"lr":0.1,"C":1.0}
    best=cv_macro(train_pairs,train_labels,active,hp)
    curve=[{"iter":0,"change":"baseline(base only)","cv_macro_f1":round(best,4),"features":list(active)}]
    print(f"\niter 0: baseline CV macro-F1 = {best:.4f}  (features: {active})")

    # candidate feature blocks to try adding, in order
    feature_candidates=["distance","sameword","connectives","cues","tensematch","leadconn","sharedstem"]
    # candidate hyperparameter settings to try
    hp_candidates=[{"type":"gb","n":200,"depth":3,"lr":0.08},{"type":"gb","n":300,"depth":3,"lr":0.08},
                   {"type":"gb","n":300,"depth":2,"lr":0.05},{"type":"gb","n":400,"depth":3,"lr":0.05}]

    it=0
    # Phase 1: greedily add features that improve CV
    for cand in feature_candidates:
        it+=1
        trial=active+[cand]
        sc=cv_macro(train_pairs,train_labels,trial,hp)
        keep = sc>best+0.0005   # must improve meaningfully
        tag="KEPT" if keep else "rejected"
        print(f"iter {it}: +feature '{cand}' -> CV {sc:.4f}  [{tag}]")
        if keep: active=trial; best=sc
        curve.append({"iter":it,"change":f"+feature {cand}","cv_macro_f1":round(sc,4),
                      "kept":bool(keep),"features":list(active)})
    # Phase 2: try hyperparameters on the chosen feature set
    for hpc in hp_candidates:
        it+=1
        sc=cv_macro(train_pairs,train_labels,active,hpc)
        keep = sc>best+0.0005
        tag="KEPT" if keep else "rejected"
        print(f"iter {it}: hp {hpc['n']}t/d{hpc['depth']}/lr{hpc['lr']} -> CV {sc:.4f}  [{tag}]")
        if keep: hp=hpc; best=sc
        curve.append({"iter":it,"change":f"hp n={hpc['n']} depth={hpc['depth']} lr={hpc['lr']}",
                      "cv_macro_f1":round(sc,4),"kept":bool(keep)})

    print(f"\nFINAL chosen features: {active}")
    print(f"FINAL chosen hyperparams: {hp}")
    print(f"BEST CV macro-F1: {best:.4f}")

    # ---- SCORE TEST SET ONCE, at the very end ----
    test_pairs,gt=load_test(f"{K}/test_pairs",f"{K}/test_groundtruth")
    # align labels by pair id
    Xtr=build_X(train_pairs,active); ytr=np.array(train_labels)
    model=make_model(hp); model.fit(Xtr,ytr)
    # build test X + y in matching order
    tX=[]; ty=[]
    for p in test_pairs:
        pid=p.get("pair_id") or p.get("id")
        if pid in gt:
            tX.append([v for name in active for v in BLOCKS[name](p)])
            ty.append(collapse(gt[pid]))
    tX=np.array(tX); ty=np.array(ty)
    pred=model.predict(tX)
    test_acc=accuracy_score(ty,pred); test_f1=f1_score(ty,pred,average='macro')
    print(f"\n=== TEST SET (scored ONCE, final model) ===")
    print(f"  test pairs scored: {len(ty)}")
    print(f"  accuracy: {test_acc:.4f}")
    print(f"  macro-F1: {test_f1:.4f}")

    json.dump({"cv_curve":curve,"final_features":active,"final_hp":hp,
               "best_cv_macro_f1":round(best,4),
               "test_accuracy":round(test_acc,4),"test_macro_f1":round(test_f1,4),
               "test_pairs":len(ty),
               "note":"CV-driven feature+hp selection; test scored once at end. Honest: no test-set tuning."},
              open("iterative_result.json","w"),indent=1)
    print("\nsaved iterative_result.json")

if __name__=="__main__": main()
