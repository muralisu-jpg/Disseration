#!/usr/bin/env python3
"""EVAL 2 — TRUE CHAIN with real end-to-end scoring.
  story -> PRED events -> PRED pairs -> PRED relations, errors compound.
Scored against gold by WORD-PAIR matching (no offsets needed):
  - pairing F1 (did the chain find the right event links?)
  - END-TO-END 4-way accuracy (of ALL gold pair->relation facts, how many the chain got
    right starting from raw story text) <- THE compounding number.
Cached + resumable.
"""
import json, os, sys
sys.path.insert(0,"stages"); sys.path.insert(0,"scorers")
from stage1_events import predict_events
from stage2_pairs import predict_pairs
from stage3_relations import predict_relations
from llm import load_cache, save_cache
from score_endtoend import score_chain

def load(d,sid): return json.load(open(f"data/{d}/{sid}.json",encoding="utf-8"))
split=json.load(open("data/split.json")); TEST=split["test"]

def main():
    c1=load_cache("s1_chain"); c2=load_cache("s2_chain"); c3=load_cache("s3_chain")
    rows=[]; tot_e2e=[]; tot_pair=[]
    for sid in TEST:
        story=load("stories",sid)["text"]
        ev=predict_events(sid,story,c1); save_cache("s1_chain",c1)
        if ev is None: print(f"chain S1 {sid}: quota — rerun."); break
        pr=predict_pairs(sid,ev,c2); save_cache("s2_chain",c2)
        if pr is None: print(f"chain S2 {sid}: quota — rerun."); break
        # give each predicted pair a stable key + word context, so stage3 relations line up
        for p in pr: p["key"]=f'{p["e1_idx"]}_{p["e2_idx"]}'
        rl=predict_relations(sid,pr,c3); save_cache("s3_chain",c3)
        if rl is None: print(f"chain S3 {sid}: quota — rerun."); break
        json.dump({"events":ev,"pairs":pr,"relations":rl},open(f"out/chain/{sid}.json","w"),ensure_ascii=False)
        # SCORE end-to-end (word-pair match)
        res=score_chain(pr, rl, load("gold_pairs",sid), load("gold_relations",sid))
        res["story"]=sid; rows.append(res)
        tot_e2e.append(res["end_to_end_4way_accuracy"]); tot_pair.append(res["pairing"]["f1"])
        print(f"chain {sid}: pairing F1 {res['pairing']['f1']}, "
              f"END-TO-END 4way acc {res['end_to_end_4way_accuracy']} "
              f"(rel-on-found {res['relation_acc_on_found_pairs']})")
    summary={"EVAL_2_TRUE_CHAIN":{
        "mean_pairing_f1": round(sum(tot_pair)/len(tot_pair),4) if tot_pair else None,
        "mean_end_to_end_4way_accuracy": round(sum(tot_e2e)/len(tot_e2e),4) if tot_e2e else None,
        "stories_done": len(rows),
        "per_story": rows,
        "note":"end_to_end_4way_accuracy = of ALL gold pair->relation facts, fraction the full "
               "chain (raw story -> events -> pairs -> relations) recovered correctly. Missed "
               "pairs count as wrong. Compare to EVAL 1 stage3 (relations on GOLD pairs) to see "
               "how much the upstream event+pair errors cost."}}
    json.dump(summary,open("out/eval2_chain.json","w"),indent=2)
    print("\n=== EVAL 2 (TRUE CHAIN, end-to-end) ===")
    print(json.dumps({k:v for k,v in summary["EVAL_2_TRUE_CHAIN"].items() if k!="per_story"},indent=2))

if __name__=="__main__": main()
