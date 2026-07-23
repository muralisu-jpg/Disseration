#!/usr/bin/env python3
"""Ensemble LLM + model (Windows version). Run from inside the llm_benchmark folder."""
import json, glob, os, numpy as np, warnings
warnings.filterwarnings("ignore")
from sklearn.ensemble import GradientBoostingClassifier

# ============================================================
# EDIT THIS ONE PATH to your kit9 folder (has train_examples, n2_train):
K = r"C:\Users\user\Desktop\kit9"
# ============================================================

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
    f=oh(p.get("e1_class"),CLASSES)+oh(p.get("e2_class"),CLASSES)+oh(p.get("e1_tense"),TENSES)+oh(p.get("e2_tense"),TENSES)+oh(p.get("e1_aspect","NONE"),ASPECTS)+oh(p.get("e2_aspect","NONE"),ASPECTS)
    f.append(1.0 if p.get("same_sentence") in (True,"True") else 0.0); f.append(1.0 if p.get("text_order")=="e1_first" else 0.0); f+=[0,0,0,0]
    return f

# load training data from kit9
tr=[]
for sub in ("train_examples","n2_train"):
    for f in glob.glob(os.path.join(K,sub,"*.json")): tr+=json.load(open(f))
if not tr:
    print(f"ERROR: no training data found under {K}")
    print(f"  Looked in {os.path.join(K,'train_examples')} and {os.path.join(K,'n2_train')}")
    print("  Fix the K path at the top of this file to point to your kit9 folder.")
    raise SystemExit(1)
print(f"loaded {len(tr)} training pairs from {K}")

m=GradientBoostingClassifier(n_estimators=300,max_depth=3,learning_rate=0.08,random_state=0)
m.fit(np.array([feat(p) for p in tr]),np.array([c3(p["relation"]) for p in tr]))

# model predictions on the LLM-benchmark test pairs (same #index ids as gt + llm)
mp={}; mc={}
for f in glob.glob("test_pairs/*.json"):
    for p in json.load(open(f)):
        pr=m.predict_proba(np.array([feat(p)]))[0]
        mp[p["pair_id"]]=m.classes_[pr.argmax()]; mc[p["pair_id"]]=pr.max()

def score(fn):
    ok=tot=0
    for pid,lr in llm.items():
        if pid not in gt: continue
        tot+=1
        if fn(c3(lr),mp.get(pid,"overlap"),mc.get(pid,0))==c3(gt[pid]): ok+=1
    return ok/tot
print(f"\nLLM alone:                              {score(lambda L,M,c:L):.4f}")
print(f"Model alone:                            {score(lambda L,M,c:M):.4f}")
print(f"General ensemble (model conf>0.9):      {score(lambda L,M,c: M if c>0.9 else L):.4f}")
print(f"Targeted overlap/before fix (conf>0.85):{score(lambda L,M,c: M if (c>0.85 and {L,M}=={'before','overlap'}) else L):.4f}")
print("\n(LLM=0.8473; targeted fix should reach ~0.864)")
