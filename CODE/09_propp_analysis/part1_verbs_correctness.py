#!/usr/bin/env python3
"""
PART 1 — Important verbs per Propp function + correctness breakdown.
For every Propp function across all stories:
  - extract its IMPORTANT VERB (the anchoring event word)
  - determine if it is TOLD in the correct canonical position (correct) or out of place (wrong)
Then aggregate:
  - per FUNCTION TYPE: which functions are most often correctly vs wrongly placed
  - per STORY: which narratives have more correct vs wrong function placements
No LLM needed — uses gold Propp annotations + canonical order.
"""
import json
from collections import defaultdict

data=json.load(open("data/propp_functions.json",encoding="utf-8"))

func_stats=defaultdict(lambda:{"correct":0,"wrong":0,"verbs":[]})
story_stats=defaultdict(lambda:{"correct":0,"wrong":0})
rows=[]

for sid,funcs in data.items():
    valid=[f for f in funcs if f["canonical_order"]<99]
    for i,f in enumerate(valid):
        # a function is "correct" if every earlier-told function has <= canonical order
        # and every later-told function has >= canonical order (locally in-sequence)
        prev_ok=all(valid[j]["canonical_order"]<=f["canonical_order"] for j in range(i))
        next_ok=all(valid[j]["canonical_order"]>=f["canonical_order"] for j in range(i+1,len(valid)))
        correct = prev_ok and next_ok
        key=f["name"]
        func_stats[key]["correct" if correct else "wrong"]+=1
        func_stats[key]["verbs"].append(f["important_verb"][:30])
        story_stats[sid]["correct" if correct else "wrong"]+=1
        rows.append({"story":sid,"function":f["name"],"code":f["code"],
                     "important_verb":f["important_verb"][:40],"placed":"correct" if correct else "wrong"})

# per-function summary
print("=== PART 1a: which PROPP FUNCTIONS are most often correctly vs wrongly placed ===")
print(f"{'function':<28} {'correct':>8} {'wrong':>6} {'accuracy':>9}   example verb")
print("-"*80)
func_out={}
for name,st in sorted(func_stats.items(), key=lambda kv:-(kv[1]['correct']+kv[1]['wrong'])):
    tot=st['correct']+st['wrong']; acc=st['correct']/tot if tot else 0
    ex=st['verbs'][0] if st['verbs'] else ""
    func_out[name]={"correct":st['correct'],"wrong":st['wrong'],"accuracy":round(acc,3),"example_verb":ex}
    print(f"{name:<28} {st['correct']:>8} {st['wrong']:>6} {acc:>8.0%}   \"{ex[:28]}\"")

# per-story summary
print("\n=== PART 1b: which STORIES (narratives) have more correct vs wrong placements ===")
print(f"{'story':<36} {'correct':>8} {'wrong':>6} {'accuracy':>9}")
print("-"*64)
story_out={}
for sid,st in sorted(story_stats.items(), key=lambda kv:-(kv[1]['correct']/(kv[1]['correct']+kv[1]['wrong']) if (kv[1]['correct']+kv[1]['wrong']) else 0)):
    tot=st['correct']+st['wrong']; acc=st['correct']/tot if tot else 0
    story_out[sid]={"correct":st['correct'],"wrong":st['wrong'],"accuracy":round(acc,3)}
    print(f"{sid[:34]:<36} {st['correct']:>8} {st['wrong']:>6} {acc:>8.0%}")

json.dump({"per_function":func_out,"per_story":story_out,"detail":rows},
          open("out/part1_verbs_correctness.json","w"),indent=1,ensure_ascii=False)
print("\nsaved out/part1_verbs_correctness.json")
