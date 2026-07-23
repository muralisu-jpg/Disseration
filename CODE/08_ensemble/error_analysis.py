#!/usr/bin/env python3
"""Diagnose where the LLM fails by true-relation class. Run in the llm_benchmark folder."""
import json, glob
from collections import Counter, defaultdict
def c3(r):
    r=(r or "").upper()
    if r in ('BEFORE','IBEFORE'): return 'before'
    if r in ('AFTER','IAFTER'): return 'after'
    return 'overlap'
gt={}
for f in glob.glob("test_groundtruth/*.json"): gt.update(json.load(open(f)))
llm={}
for f in glob.glob("predictions/*.json"): llm.update(json.load(open(f)))
by=defaultdict(lambda:[0,0]); err=Counter()
for pid,pr in llm.items():
    if pid not in gt: continue
    g=c3(gt[pid]); p=c3(pr); by[g][1]+=1
    if g==p: by[g][0]+=1
    else: err[f"{g}->{p}"]+=1
for c,(ok,t) in sorted(by.items()): print(f"{c}: {ok}/{t} = {ok/t:.1%}")
print("errors:", err.most_common())
