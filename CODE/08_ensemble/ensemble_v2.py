#!/usr/bin/env python3
"""Ensemble LLM + model, correctly aligned (both in #index space via the LLM benchmark's own test_pairs)."""
import json, glob, os, numpy as np
from sklearn.ensemble import GradientBoostingClassifier
def c3(r):
    r=(r or "").upper()
    if r in ('BEFORE','IBEFORE'): return 'before'
    if r in ('AFTER','IAFTER'): return 'after'
    return 'overlap'
gt={}
for f in glob.glob("test_groundtruth/*.json"): gt.update(json.load(open(f)))
llm={}
for f in glob.glob("predictions/*.json"): llm.update(json.load(open(f)))

CLASSES=['OCCURRENCE','STATE','REPORTING','I_ACTION','I_STATE','PERCEPTION','ASPECTUAL']
TENSES=['PAST','PRESENT','FUTURE','INFINITIVE','PRESPART','PASTPART','NONE']; ASPECTS=['NONE','PERFECT','PROGRESSIVE']
def oh(v,o): return [1.0 if v==x else 0.0 for x in o]
def feat(p):
    f=oh(p.get("e1_class"),CLASSES)+oh(p.get("e2_class"),CLASSES)+oh(p.get("e1_tense"),TENSES)+oh(p.get("e2_tense"),TENSES)
    f+=oh(p.get("e1_aspect","NONE"),ASPECTS)+oh(p.get("e2_aspect","NONE"),ASPECTS)
    f.append(1.0 if p.get("same_sentence") in (True,"True") else 0.0)
    f.append(1.0 if p.get("text_order")=="e1_first" else 0.0)
    f+=[0,0,0,0]
    return f
K=os.environ.get("KIT9", "../05_ml_model/training_data")
tr=[]
for f in glob.glob(f"{K}/train_examples/*.json")+glob.glob(f"{K}/n2_train/*.json"): tr+=json.load(open(f))
m=GradientBoostingClassifier(n_estimators=300,max_depth=3,learning_rate=0.08,random_state=0)
m.fit(np.array([feat(p) for p in tr]),np.array([c3(p["relation"]) for p in tr]))

# model predictions over the benchmark test pairs (shared pair_id space)
modelpred={}; modelconf={}
for f in glob.glob("test_pairs/*.json"):
    for p in json.load(open(f)):
        pid=p["pair_id"]
        pr=m.predict_proba(np.array([feat(p)]))[0]
        modelpred[pid]=m.classes_[pr.argmax()]; modelconf[pid]=pr.max()

def score(fn):
    ok=tot=0
    for pid,lr in llm.items():
        if pid not in gt: continue
        tot+=1
        if fn(c3(lr), c3(modelpred.get(pid,"overlap")), modelconf.get(pid,0))==c3(gt[pid]): ok+=1
    return ok/tot
print(f"LLM alone:                 {score(lambda L,M,c:L):.4f}")
print(f"Model alone:               {score(lambda L,M,c:M):.4f}")
for th in [0.90,0.95,0.98,0.99]:
    print(f"Model overrides if conf>{th}: {score(lambda L,M,c: M if c>th else L):.4f}")
