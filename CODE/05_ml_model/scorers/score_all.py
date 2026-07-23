"""Scorers for all three stages, used by both eval modes."""
import json
from collections import Counter

# STAGE 1: event detection F1 (word-overlap match) + tense/class accuracy on matched
def _head(w):
    w=(w or "").lower().strip()
    return w.split()[0] if w else ""
def score_events(pred, gold):
    # match on HEAD word (first token) since gold events can be multi-word verb phrases
    gold_words = Counter(_head(g["word"]) for g in gold if _head(g["word"]))
    pred_words = Counter(_head(p["word"]) for p in pred if _head(p["word"]))
    tp = sum(min(pred_words[w], gold_words[w]) for w in pred_words)
    fp = sum(pred) if False else sum(max(0, pred_words[w]-gold_words[w]) for w in pred_words)
    fn = sum(max(0, gold_words[w]-pred_words[w]) for w in gold_words)
    P = tp/(tp+fp) if tp+fp else 0; R = tp/(tp+fn) if tp+fn else 0
    F = 2*P*R/(P+R) if P+R else 0
    return {"precision":round(P,4),"recall":round(R,4),"f1":round(F,4),"tp":tp,"fp":fp,"fn":fn}

# STAGE 2: pairing precision/recall/F1 (by offset pair, order-independent)
def score_pairs(pred, gold):
    def norm(p): return frozenset((p.get("e1_off"),p.get("e2_off")))
    gp = {norm(g) for g in gold if g.get("e1_off") is not None}
    pp = {norm(p) for p in pred if p.get("e1_off") is not None}
    tp=len(gp&pp); fp=len(pp-gp); fn=len(gp-pp)
    P=tp/(tp+fp) if tp+fp else 0; R=tp/(tp+fn) if tp+fn else 0
    F=2*P*R/(P+R) if P+R else 0
    return {"precision":round(P,4),"recall":round(R,4),"f1":round(F,4),"tp":tp,"fp":fp,"fn":fn}

# STAGE 3: relation 4-way + fine
FOURWAY={"BEFORE":"before","IBEFORE":"before","AFTER":"after","IAFTER":"after",
         "MODAL":"imaginary","CONDITIONAL":"imaginary","COUNTER_FACTIVE":"imaginary"}
def to4(l): return FOURWAY.get((l or "").upper(),"overlap")
def _macro(gold,pred,labels):
    tp=Counter();fp=Counter();fn=Counter()
    for g,p in zip(gold,pred):
        if g==p: tp[g]+=1
        else: fp[p]+=1; fn[g]+=1
    fs=[]
    for l in labels:
        P=tp[l]/(tp[l]+fp[l]) if tp[l]+fp[l] else 0
        R=tp[l]/(tp[l]+fn[l]) if tp[l]+fn[l] else 0
        if tp[l]+fn[l]>0: fs.append(2*P*R/(P+R) if P+R else 0)
    return sum(fs)/len(fs) if fs else 0
def score_relations(pred, gold):
    keys=[k for k in gold]  # score only pairs that exist in gold
    g=[gold[k].upper() for k in keys]; p=[(pred.get(k) or "BEFORE").upper() for k in keys]
    g4=[to4(x) for x in g]; p4=[to4(x) for x in p]
    acc4=sum(1 for a,b in zip(g4,p4) if a==b)/len(keys) if keys else 0
    mf4=_macro(g4,p4,["before","after","overlap","imaginary"])
    accf=sum(1 for a,b in zip(g,p) if a==b)/len(keys) if keys else 0
    return {"four_way_accuracy":round(acc4,4),"four_way_macro_f1":round(mf4,4),
            "fine_accuracy":round(accf,4),"n":len(keys)}
