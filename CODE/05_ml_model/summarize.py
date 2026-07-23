#!/usr/bin/env python3
"""Print EVAL 1 and EVAL 2 side by side once both have run."""
import json, os
def g(f): 
    try: return json.load(open(f))
    except: return None
e1=g("out/eval1_gold_input.json"); e2=g("out/eval2_chain.json")
print("="*60)
print("PIPELINE SUMMARY — story -> events -> pairs -> relations")
print("="*60)
if e1:
    s=e1["EVAL_1_GOLD_INPUT"]
    print("\nEVAL 1 — each stage on GOLD input (isolated quality):")
    print(f"  Stage 1 events      : F1 {s['stage1_events']['macro_f1']}")
    print(f"  Stage 2 pairs       : F1 {s['stage2_pairs']['macro_f1']}")
    print(f"  Stage 3 relations   : 4-way acc {s['stage3_relations']['four_way_accuracy']}, "
          f"macro-F1 {s['stage3_relations']['four_way_macro_f1']}")
if e2:
    print("\nEVAL 2 — true chain (errors compound):")
    for r in e2["EVAL_2_TRUE_CHAIN"]["per_story"]:
        print(f"  {r['story'][:30]:<30} events_f1 {r['events_f1']}, "
              f"pairs {r['pred_pairs']}/{r['gold_pairs']}")
print("\n(Gap between EVAL 1 and EVAL 2 = the cost of error compounding.)")
