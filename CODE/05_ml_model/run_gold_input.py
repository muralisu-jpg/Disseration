#!/usr/bin/env python3
"""EVAL 1 — GOLD INPUT per stage. Each stage gets perfect input, measured in isolation.
  Stage1: story -> pred events   (vs gold events)
  Stage2: GOLD events -> pred pairs   (vs gold pairs)
  Stage3: GOLD pairs -> pred relations (vs gold relations)
Cached + resumable. Run repeatedly across quota windows; it skips done stories.
"""
import json, os, sys, glob
sys.path.insert(0,"stages"); sys.path.insert(0,"scorers")
from stage1_events import predict_events
from stage2_pairs import predict_pairs
from stage3_relations import predict_relations
from llm import load_cache, save_cache
import score_all as S

def load(d,sid): return json.load(open(f"data/{d}/{sid}.json",encoding="utf-8"))
split=json.load(open("data/split.json")); TEST=split["test"]

def main():
    c1=load_cache("s1_gold"); c2=load_cache("s2_gold"); c3=load_cache("s3_gold")
    r1=[]; r2=[]; r3=[]
    for sid in TEST:
        # Stage 1: story -> events
        story=load("stories",sid)["text"]
        ev=predict_events(sid,story,c1); save_cache("s1_gold",c1)
        if ev is None: print(f"S1 {sid}: quota — cache saved, rerun."); break
        json.dump(ev,open(f"out/events/{sid}.json","w"),ensure_ascii=False)
        r1.append((sid,S.score_events(ev,load("gold_events",sid))))
        print(f"S1 {sid}: events F1 {r1[-1][1]['f1']}")
    for sid in TEST:
        # Stage 2: GOLD events -> pairs
        gold_ev=load("gold_events",sid)
        pr=predict_pairs(sid,gold_ev,c2); save_cache("s2_gold",c2)
        if pr is None: print(f"S2 {sid}: quota — cache saved, rerun."); break
        json.dump(pr,open(f"out/pairs/{sid}.json","w"),ensure_ascii=False)
        r2.append((sid,S.score_pairs(pr,load("gold_pairs",sid))))
        print(f"S2 {sid}: pairs F1 {r2[-1][1]['f1']}")
    for sid in TEST:
        # Stage 3: GOLD pairs -> relations
        gold_pairs=load("gold_pairs",sid)
        for p in gold_pairs: p["key"]=f'{p["e1_off"]}_{p["e2_off"]}'
        rl=predict_relations(sid,gold_pairs,c3); save_cache("s3_gold",c3)
        if rl is None: print(f"S3 {sid}: quota — cache saved, rerun."); break
        json.dump(rl,open(f"out/relations/{sid}.json","w"),ensure_ascii=False)
        r3.append((sid,S.score_relations(rl,load("gold_relations",sid))))
        print(f"S3 {sid}: rel 4-way acc {r3[-1][1]['four_way_accuracy']}")
    # aggregate
    def agg(rs,key): 
        vals=[s[key] for _,s in rs if key in s]; return round(sum(vals)/len(vals),4) if vals else None
    summary={"EVAL_1_GOLD_INPUT":{
        "stage1_events":{"macro_f1":agg(r1,"f1"),"stories":len(r1)},
        "stage2_pairs":{"macro_f1":agg(r2,"f1"),"stories":len(r2)},
        "stage3_relations":{"four_way_accuracy":agg(r3,"four_way_accuracy"),
                            "four_way_macro_f1":agg(r3,"four_way_macro_f1"),"stories":len(r3)}}}
    json.dump(summary,open("out/eval1_gold_input.json","w"),indent=2)
    print("\n=== EVAL 1 (GOLD INPUT) ==="); print(json.dumps(summary,indent=2))

if __name__=="__main__": main()
