#!/usr/bin/env python3
"""Scores the pure-LLM benchmark: 14-way (fine) AND 3-way (collapsed) — both, as requested."""
import json, os, glob, argparse
from collections import Counter
COLLAPSE={"BEFORE":"before","IBEFORE":"before","AFTER":"after","IAFTER":"after"}
def c3(l): return COLLAPSE.get((l or "").upper().strip(),"overlap")
def f1_set(gold,pred,labels):
    tp=Counter();fp=Counter();fn=Counter()
    for g,p in zip(gold,pred):
        if g==p: tp[g]+=1
        else: fp[p]+=1; fn[g]+=1
    fs={}
    for l in labels:
        P=tp[l]/(tp[l]+fp[l]) if tp[l]+fp[l] else 0
        R=tp[l]/(tp[l]+fn[l]) if tp[l]+fn[l] else 0
        fs[l]=2*P*R/(P+R) if P+R else 0
    present=[l for l in labels if (tp[l]+fn[l])>0]
    return sum(fs[l] for l in present)/len(present) if present else 0, fs

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--pred",default="predictions"); ap.add_argument("--gold",default="test_groundtruth")
    ap.add_argument("--out",default="feedback.json")
    a=ap.parse_args()
    gold_all={}; pred_all={}
    for gp in glob.glob(os.path.join(a.gold,"*.json")): gold_all.update(json.load(open(gp,encoding="utf-8")))
    for pp in glob.glob(os.path.join(a.pred,"*.json")):
        d=json.load(open(pp,encoding="utf-8"))
        if isinstance(d,dict): pred_all.update(d)
    ids=list(gold_all)
    gfine=[gold_all[i].upper() for i in ids]
    pfine=[(pred_all.get(i) or "NONE").upper() for i in ids]
    g3=[c3(x) for x in gfine]; p3=[c3(x) for x in pfine]
    acc3=sum(1 for a_,b_ in zip(g3,p3) if a_==b_)/len(ids)
    accF=sum(1 for a_,b_ in zip(gfine,pfine) if a_==b_)/len(ids)
    mf3,_=f1_set(g3,p3,["before","after","overlap"])
    LAB=["BEFORE","AFTER","IBEFORE","IAFTER","SIMULTANEOUS","IDENTITY","INCLUDES","IS_INCLUDED","DURING","DURING_INV","BEGINS","BEGUN_BY","ENDS","ENDED_BY"]
    mfF,fsF=f1_set(gfine,pfine,LAB)
    cov=sum(1 for i in ids if i in pred_all)/len(ids)
    out={"n_pairs":len(ids),"coverage":round(cov,3),
         "three_way_accuracy":round(acc3,4),"three_way_macro_f1":round(mf3,4),
         "fine_14way_accuracy":round(accF,4),"fine_14way_macro_f1":round(mfF,4),
         "fine_per_relation_f1":{k:round(v,3) for k,v in fsF.items()}}
    json.dump(out,open(a.out,"w"),indent=2)
    print(json.dumps({k:v for k,v in out.items() if k!="fine_per_relation_f1"},indent=2))

if __name__=="__main__": main()
