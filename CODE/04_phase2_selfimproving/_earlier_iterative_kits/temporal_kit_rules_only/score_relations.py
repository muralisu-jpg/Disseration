#!/usr/bin/env python3
"""
Relation-CLASSIFICATION scorer (TimeML temporal links).

Task: the human annotators linked certain EVENT PAIRS with a temporal relation
(BEFORE/AFTER/SIMULTANEOUS/IBEFORE/INCLUDES/...). We GIVE the annotator those same
pairs (by their character offsets) and ask it to CLASSIFY the relation for each pair.
This is standard TimeML relation evaluation — no detection of which pairs to link,
so it can't be gamed by blanket-predicting.

Metric:
  - accuracy: fraction of pairs classified correctly
  - macro-F1: average per-relation F1 (so rare relations count, not just BEFORE)
  - per-relation breakdown (shows improvement even when overall moves slowly)

Input the annotator gets: pairs.json per story = list of
  {"pair_id":0, "e1":{"word","off"}, "e2":{"word","off"}}
Annotator outputs predictions/<story>.json = list of
  {"pair_id":0, "relation":"BEFORE"}

Usage:
  python score_relations.py --pred predictions --gold groundtruth --pairs pairs --out feedback.json
"""
import re, os, json, html, argparse, glob
from collections import defaultdict, Counter

VALID = ["BEFORE","AFTER","IBEFORE","IAFTER","SIMULTANEOUS","INCLUDES","IS_INCLUDED",
         "IDENTITY","DURING","DURING_INV","BEGINS","BEGUN_BY","ENDS","ENDED_BY"]

def gold_relations(sty):
    """Return dict: (e1_off, e2_off) -> relation, using event offsets as the pair key."""
    ev_block = re.search(r'<rep id="edu\.mit\.semantics\.rep\.event".*?</rep>', sty, re.S).group(0)
    ev_off = {}
    for m in re.finditer(r'<desc id="(\d+)" len="(\d+)" off="(\d+)">', ev_block):
        ev_off[m.group(1)] = int(m.group(3))
    tl = re.search(r'<rep id="edu\.mit\.semantics\.rep\.timelink".*?</rep>', sty, re.S).group(0)
    rels = {}
    for m in re.finditer(r'<desc[^>]*>([^<]*)</desc>', tl):
        p = m.group(1).split("|")
        if len(p) >= 4 and p[0]=="TEMPORAL" and p[1] in VALID:
            a, b = ev_off.get(p[2]), ev_off.get(p[3])
            if a is not None and b is not None:
                rels[(a,b)] = p[1]
    return rels

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", default="predictions")
    ap.add_argument("--gold", default="groundtruth")
    ap.add_argument("--pairs", default="pairs")
    ap.add_argument("--out", default="feedback.json")
    a = ap.parse_args()

    stories = [f[:-4] for f in os.listdir(a.gold) if f.endswith(".sty")]
    correct=0; total=0
    per_rel_tp=Counter(); per_rel_fp=Counter(); per_rel_fn=Counter()
    confusion=Counter()

    for sid in stories:
        sty_p=os.path.join(a.gold,sid+".sty")
        pairs_p=os.path.join(a.pairs,sid+".json")
        pred_p=os.path.join(a.pred,sid+".json")
        if not (os.path.exists(sty_p) and os.path.exists(pairs_p)): continue
        sty=open(sty_p,encoding="utf-8").read()
        gold=gold_relations(sty)
        pairs={p["pair_id"]:(p["e1"]["off"],p["e2"]["off"]) for p in json.load(open(pairs_p,encoding="utf-8"))}
        preds={}
        if os.path.exists(pred_p):
            for pr in json.load(open(pred_p,encoding="utf-8")):
                preds[pr["pair_id"]]=pr.get("relation","").upper()
        for pid,(o1,o2) in pairs.items():
            g=gold.get((o1,o2))
            if g is None: continue  # only score pairs we have gold for
            p=preds.get(pid,"_NONE_")
            total+=1
            if p==g:
                correct+=1; per_rel_tp[g]+=1
            else:
                per_rel_fp[p]+=1; per_rel_fn[g]+=1
                confusion[(g,p)]+=1

    acc = correct/total if total else 0
    # macro-F1 over relation types that appear in gold
    f1s=[]
    per_rel={}
    rel_types=set(per_rel_tp)|set(per_rel_fn)
    for r in rel_types:
        tp=per_rel_tp[r]; fp=per_rel_fp[r]; fn=per_rel_fn[r]
        P=tp/(tp+fp) if (tp+fp) else 0
        R=tp/(tp+fn) if (tp+fn) else 0
        F=2*P*R/(P+R) if (P+R) else 0
        per_rel[r]={"f1":round(F,3),"p":round(P,3),"r":round(R,3),"gold":tp+fn}
        if (tp+fn)>0: f1s.append(F)
    macro=sum(f1s)/len(f1s) if f1s else 0

    out={"accuracy":round(acc,3),"macro_f1":round(macro,3),"_total_pairs":total,
         "_correct":correct,"per_relation":per_rel}
    json.dump(out,open(a.out,"w"),indent=2)
    print(json.dumps({"accuracy":out["accuracy"],"macro_f1":out["macro_f1"],
                      "total_pairs":total,"per_relation_f1":{k:v["f1"] for k,v in per_rel.items()}},indent=2))

if __name__=="__main__":
    main()
