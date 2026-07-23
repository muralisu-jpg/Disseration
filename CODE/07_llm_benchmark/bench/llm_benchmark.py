#!/usr/bin/env python3
"""
PURE-LLM BENCHMARK — Claude Opus 4.8 classifies ALL test pairs directly.
Few-shot from the 3 training stories + point-algebra definitions. Batched + cached.
No rules, no ML — this is the clean 'what does the LLM alone score' number.

Run:  python bench/llm_benchmark.py         (fills cache, resumable across quota windows)
Then: python score_bench.py --pred predictions --gold test_groundtruth --out feedback.json
"""
import json, os, re, glob, subprocess, random
HERE=os.path.dirname(__file__); ROOT=os.path.dirname(HERE)
CACHE=os.path.join(HERE,"llm_bench_cache.json")
VALID=["BEFORE","AFTER","IBEFORE","IAFTER","SIMULTANEOUS","IDENTITY","INCLUDES",
       "IS_INCLUDED","DURING","DURING_INV","BEGINS","BEGUN_BY","ENDS","ENDED_BY"]

def load_cache():
    try: return json.loads(open(CACHE,encoding="utf-8").read())
    except: return {}
def save_cache(c): open(CACHE,"w",encoding="utf-8").write(json.dumps(c))

def llm(prompt,timeout=180):
    try:
        r=subprocess.run('claude -p --model claude-opus-4-8',shell=True,input=prompt,
                         capture_output=True,text=True,timeout=timeout)
        return r.stdout.strip()
    except Exception: return ""

def fewshot():
    ex=[]
    for f in glob.glob(os.path.join(HERE,"fewshot_*.json")):
        for p in json.load(open(f,encoding="utf-8")):
            ex.append(p)
    random.seed(0); random.shuffle(ex)
    # ~2 per relation for a balanced, compact few-shot
    by={}
    for p in ex: by.setdefault(p["relation"],[]).append(p)
    shots=[]
    for r,items in by.items(): shots+=items[:2]
    return shots

def defs():
    try: return open(os.path.join(HERE,"point_algebra.md"),encoding="utf-8").read()
    except: return ""

def build_prompt(batch,shots,defn):
    lines=["Classify the TimeML temporal relation of EVENT1 to EVENT2 for each pair.",defn,
           "Examples:"]
    for s in shots:
        lines.append(f'  E1="{s["e1_word"]}" E2="{s["e2_word"]}" -> {s["relation"]}')
    lines.append("\nNow classify these. Reply ONLY '#<id> <LABEL>' per line, labels from: "+", ".join(VALID))
    for i,p in enumerate(batch):
        lines.append(f'#{i}: E1="{p["e1_word"]}" (in: "{p.get("e1_sentence","")[:140]}")  '
                     f'E2="{p["e2_word"]}" (in: "{p.get("e2_sentence","")[:140]}")')
    return "\n".join(lines)

def main(batch_size=25):
    shots=fewshot(); defn=defs(); cache=load_cache()
    for tf in sorted(glob.glob(os.path.join(ROOT,"test_pairs","*.json"))):
        sid=os.path.basename(tf)[:-5]
        pairs=json.load(open(tf,encoding="utf-8"))
        ck=cache.get(sid,{})
        result={}; todo=[]
        for p in pairs:
            if p["pair_id"] in ck: result[p["pair_id"]]=ck[p["pair_id"]]
            else: todo.append(p)
        for b in range(0,len(todo),batch_size):
            chunk=todo[b:b+batch_size]
            out=llm(build_prompt(chunk,shots,defn))
            got={int(m.group(1)):m.group(2) for m in re.finditer(r'#(\d+)\s+([A-Z_]+)',out) if m.group(2) in VALID}
            if not got:
                cache[sid]=ck; save_cache(cache)
                json.dump(result,open(os.path.join(ROOT,"predictions",sid+".json"),"w"))
                print(f"{sid}: LLM stopped (quota) — {len(result)}/{len(pairs)} cached. Rerun after reset.")
                return
            for i,p in enumerate(chunk):
                if i in got: result[p["pair_id"]]=got[i]; ck[p["pair_id"]]=got[i]
            cache[sid]=ck; save_cache(cache)
        json.dump(result,open(os.path.join(ROOT,"predictions",sid+".json"),"w"))
        print(f"{sid}: {len(result)}/{len(pairs)} classified")
    print("benchmark complete — all stories classified")

if __name__=="__main__": main()
