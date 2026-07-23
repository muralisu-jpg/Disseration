#!/usr/bin/env python3
"""
PART 2 — Anchor-based narrative ordering vs Propp's canonical sequence.
For each story: take the Propp functions in the order they're TOLD (text order),
compare to Propp's CANONICAL order. Measures:
  - how well the told order matches the canonical order (Kendall tau / inversions)
  - where NON-ICONICITY occurs (function told out of canonical sequence)
No LLM needed — uses the gold Propp annotations.
"""
import json
from itertools import combinations

data=json.load(open("data/propp_functions.json",encoding="utf-8"))

def kendall(seq):
    """fraction of correctly-ordered pairs (by canonical order) among all pairs."""
    pairs=list(combinations(range(len(seq)),2))
    if not pairs: return None,0,0
    correct=sum(1 for i,j in pairs if seq[i]<=seq[j])
    return correct/len(pairs), correct, len(pairs)-correct

report={}
print(f"{'story':<34} {'funcs':>5} {'told-matches-canon':>18} {'inversions':>11}")
print("-"*72)
tot_c=tot_w=0
for sid,funcs in data.items():
    # functions in TEXT (told) order = already in offset order; get their canonical ranks
    told=[f["canonical_order"] for f in funcs if f["canonical_order"]<99]
    score,c,w=kendall(told)
    tot_c+=c; tot_w+=w
    report[sid]={"n_functions":len(funcs),"order_match":round(score,3) if score else None,
                 "correct_pairs":c,"inversions":w,
                 "told_sequence":[{"code":f["code"],"name":f["name"],"canon":f["canonical_order"]} for f in funcs]}
    if score is not None:
        print(f"{sid[:32]:<34} {len(funcs):>5} {score:>17.1%} {w:>11}")
overall=tot_c/(tot_c+tot_w) if (tot_c+tot_w) else 0
print("-"*72)
print(f"{'OVERALL told-matches-canonical order':<40} {overall:>11.1%}  ({tot_w} total inversions = non-iconic pairs)")
report["_overall"]={"order_match":round(overall,3),"total_correct":tot_c,"total_inversions":tot_w,
                    "interpretation":"inversions = pairs of Propp functions TOLD out of canonical order = narrative-level non-iconicity"}
json.dump(report,open("out/part2_ordering.json","w"),indent=1,ensure_ascii=False)
print("\nsaved out/part2_ordering.json")
