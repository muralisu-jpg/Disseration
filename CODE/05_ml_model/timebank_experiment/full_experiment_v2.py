#!/usr/bin/env python3
"""
FULL EXPERIMENT v2 — TimeBank training + Propp timeline, with PROPER alignment.
Fixes the key-space bug: model predicts on event OFFSETS; we map offset->event_id via
event_offsets so the model's predictions live in the same id-space as gold + functions.
Then the three timelines (MODEL / PROPP-MODEL / GROUND-TRUTH) are genuinely comparable.
"""
import json, glob, os
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score
from itertools import combinations
from collections import defaultdict

K=os.environ.get("KIT9","../training_data"); TB=os.environ.get("TB","timebank_pairs"); PROPP=os.environ.get("PROPP","../../09_propp_analysis/data")
CLASSES=['OCCURRENCE','STATE','REPORTING','I_ACTION','I_STATE','PERCEPTION','ASPECTUAL']
TENSES=['PAST','PRESENT','FUTURE','INFINITIVE','PRESPART','PASTPART','NONE']
ASPECTS=['NONE','PERFECT','PROGRESSIVE']
def oh(v,o): return [1.0 if v==x else 0.0 for x in o]
def c3(r):
    r=r.upper()
    if r in ('BEFORE','IBEFORE'): return 'before'
    if r in ('AFTER','IAFTER'): return 'after'
    return 'overlap'
def feat(p):
    f=oh(p.get("e1_class"),CLASSES)+oh(p.get("e2_class"),CLASSES)
    f+=oh(p.get("e1_tense"),TENSES)+oh(p.get("e2_tense"),TENSES)
    f+=oh(p.get("e1_aspect"),ASPECTS)+oh(p.get("e2_aspect"),ASPECTS)
    f.append(1.0 if p.get("same_sentence") in (True,"True") else 0.0)
    f.append(1.0 if p.get("text_order")=="e1_first" else 0.0)
    d=abs(int(p.get("e2_off",0))-int(p.get("e1_off",0)))
    f+=[1.0 if d<50 else 0,1.0 if 50<=d<200 else 0,1.0 if 200<=d<1000 else 0,1.0 if d>=1000 else 0]
    return f
def load(folders):
    P=[]
    for fo in folders:
        for fp in glob.glob(f"{fo}/*.json"): P+=json.load(open(fp))
    return P
def train(wtb):
    folders=[f"{K}/train_examples",f"{K}/n2_train"]+([TB] if wtb else [])
    P=load(folders)
    X=np.array([feat(p) for p in P]); y=np.array([c3(p["relation"]) for p in P])
    m=GradientBoostingClassifier(n_estimators=300,max_depth=3,learning_rate=0.08,random_state=0)
    m.fit(X,y); return m,len(P)

fd=json.load(open(f"{PROPP}/functions_events_relations.json"))
FUNCS=json.load(open(f"{PROPP}/propp_functions.json"))
def canon(sid,off):
    for f in FUNCS.get(sid,[]):
        if f["off"]==off: return f["canonical_order"]
    return 99

def predict_story_rel(model, sid):
    """Predict relations for a story, keyed by EVENT ID (aligned via offset->id map)."""
    d=fd[sid]
    off2id={off:eid for eid,off in d["event_offsets"].items()}
    fp=f"{K}/test_pairs/{sid}.json"
    if not os.path.exists(fp): return {}
    rel={}
    for p in json.load(open(fp)):
        e1=off2id.get(p.get("e1_off")); e2=off2id.get(p.get("e2_off"))
        if e1 and e2:
            rel[f"{e1}_{e2}"]=model.predict(np.array([feat(p)]))[0]
    return rel

def rl(rel,a,b):
    if f"{a}_{b}" in rel: return rel[f"{a}_{b}"]
    if f"{b}_{a}" in rel:
        r=rel[f"{b}_{a}"]; return {"before":"after","after":"before"}.get(r,r)
    return None
def order_flat(events,rel):
    sc=defaultdict(int)
    for a,b in combinations(events,2):
        r=rl(rel,a,b)
        if r=="before": sc[a]+=1; sc[b]-=1
        elif r=="after": sc[a]-=1; sc[b]+=1
    return sorted(events,key=lambda e:-sc[e])
def order_propp(sid,d,rel):
    out=[]
    for f in sorted([f for f in d["functions"] if f["event_ids"]],key=lambda f:canon(sid,f["off"])):
        out+=order_flat(f["event_ids"],rel)
    return out
def agree(oa,ob):
    pa={e:i for i,e in enumerate(oa)}; pb={e:i for i,e in enumerate(ob)}
    common=[e for e in oa if e in pb]
    if len(common)<2: return None
    ag=tot=0
    for a,b in combinations(common,2):
        tot+=1
        if (pa[a]<pa[b])==(pb[a]<pb[b]): ag+=1
    return ag/tot if tot else None

def experiment(model):
    """For each story: build 3 timelines from MODEL predictions, score vs ground truth."""
    mA=[]; pB=[]; gt_test_acc=[]
    for sid,d in fd.items():
        if not os.path.exists(f"{K}/test_pairs/{sid}.json"): continue  # only test stories
        gold=d["event_relations"]
        events=list(dict.fromkeys([e for f in d["functions"] if f["event_ids"] for e in f["event_ids"]]))
        if len(events)<3: continue
        mrel=predict_story_rel(model,sid)   # MODEL's predictions, id-keyed
        if not mrel: continue
        gt=order_flat(events,gold)                    # C: ground truth order
        A=order_flat(events,mrel)                     # A: model timeline
        B=order_propp(sid,d,mrel)                     # B: propp-model timeline
        a=agree(A,gt); b=agree(B,gt)
        if a is not None: mA.append(a)
        if b is not None: pB.append(b)
    return (np.mean(mA) if mA else 0), (np.mean(pB) if pB else 0), len(mA)

def test_acc(model):
    gt={}
    for fp in glob.glob(f"{K}/test_groundtruth/*.json"): gt.update(json.load(open(fp)))
    yt=[];yp=[]
    for fp in glob.glob(f"{K}/test_pairs/*.json"):
        for p in json.load(open(fp)):
            if p.get("pair_id") in gt:
                yt.append(c3(gt[p["pair_id"]])); yp.append(model.predict(np.array([feat(p)]))[0])
    return accuracy_score(yt,yp), f1_score(yt,yp,average='macro')

print("="*68)
print("FULL EXPERIMENT v2 — TimeBank training + Propp timeline (ALIGNED)")
print("="*68)
out={}
for wtb in [False,True]:
    model,n=train(wtb)
    acc,f1=test_acc(model)
    mA,pB,ns=experiment(model)
    tag="+TimeBank" if wtb else "baseline"
    print(f"\n[{tag}] trained on {n} pairs")
    print(f"  relation model:  acc {acc:.4f}  macroF1 {f1:.4f}")
    print(f"  (A) MODEL timeline vs ground truth:       {mA:.1%}")
    print(f"  (B) PROPP-MODEL timeline vs ground truth: {pB:.1%}   ({pB-mA:+.1%} vs model)")
    print(f"      [{ns} test stories]")
    out[tag]={"pairs":n,"rel_acc":round(acc,4),"rel_f1":round(f1,4),
              "model_timeline":round(mA,4),"propp_timeline":round(pB,4)}
json.dump(out,open("experiment_result.json","w"),indent=1)
print("\nsaved experiment_result.json")
