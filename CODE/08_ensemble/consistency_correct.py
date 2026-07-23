#!/usr/bin/env python3
"""
Apply TEMPORAL CONSISTENCY CORRECTION to the LLM's predictions (inspired by Fan & Strube 2025,
Allen's interval algebra). Idea: the LLM predicts each pair independently, so it makes
CONTRADICTIONS (says A<B, B<C, but C<A). Enforcing transitivity can fix some errors.
If the corrected predictions beat 0.8473, we've improved on the raw LLM.
"""
import json, glob
import os
from collections import defaultdict
from itertools import combinations

def c3(r):
    r=(r or "").upper()
    if r in ('BEFORE','IBEFORE'): return 'before'
    if r in ('AFTER','IAFTER'): return 'after'
    return 'overlap'

gt={}
for f in glob.glob("test_groundtruth/*.json"): gt.update(json.load(open(f)))

# Load LLM predictions per story, keyed by index (pair_id '#N')
def acc(preds):
    ok=tot=0
    for pid,p in preds.items():
        if pid in gt:
            tot+=1
            if c3(p)==c3(gt[pid]): ok+=1
    return ok,tot

# raw accuracy
raw={}
for f in glob.glob("predictions/*.json"): raw.update(json.load(open(f)))
ok,tot=acc(raw)
print(f"RAW LLM accuracy: {ok}/{tot} = {ok/tot:.4f}")

# For consistency: need to map each pair to its two events. Use kit9 test_pairs (has offsets).
K=os.environ.get("PAIRS", "../07_llm_benchmark/test_pairs")
def correct_story(sid):
    """Enforce transitivity on one story's predictions via a simple constraint-propagation."""
    lp=f"predictions/{sid}.json"; kp=f"{K}/{sid}.json"
    import os
    if not os.path.exists(lp) or not os.path.exists(kp): return {}
    preds=json.load(open(lp)); k9=json.load(open(kp))
    # map index -> (e1_off, e2_off)
    idx2ev={}
    for i,p in enumerate(k9):
        idx2ev[i]=(p.get("e1_off"),p.get("e2_off"))
    # build a directed graph of 'before' edges from LLM preds
    rel={}  # (a,b) -> before/after/overlap
    for pid,pr in preds.items():
        i=int(pid.split("#")[1])
        if i not in idx2ev: continue
        a,b=idx2ev[i]; r=c3(pr)
        rel[(a,b)]=r
    # transitive closure on 'before': if a<b and b<c, infer a<c
    befores=defaultdict(set)
    for (a,b),r in rel.items():
        if r=="before": befores[a].add(b)
        elif r=="after": befores[b].add(a)
    # propagate
    changed=True; it=0
    while changed and it<5:
        changed=False; it+=1
        for a in list(befores):
            for b in list(befores[a]):
                for c in befores.get(b,()):
                    if c not in befores[a]:
                        befores[a].add(c); changed=True
    # Override a prediction where the transitive closure implies before/after.
    corrected={}
    for pid,pr in preds.items():
        i=int(pid.split("#")[1])
        if i not in idx2ev: corrected[pid]=pr; continue
        a,b=idx2ev[i]
        if b in befores.get(a,()): corrected[pid]="BEFORE"
        elif a in befores.get(b,()): corrected[pid]="AFTER"
        else: corrected[pid]=pr
    return corrected

corrected_all={}
for f in glob.glob("predictions/*.json"):
    sid=f.split("/")[-1].replace(".json","")
    corrected_all.update(correct_story(sid))
ok2,tot2=acc(corrected_all)
print(f"CONSISTENCY-corrected accuracy: {ok2}/{tot2} = {ok2/tot2:.4f}")
print(f"  change: {(ok2-ok)/tot:+.4f}")
