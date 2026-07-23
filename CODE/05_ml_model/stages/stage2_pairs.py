"""STAGE 2: events -> predicted pairs. LLM judges which event pairs are temporally linked.
Uses locality (consecutive events) as candidates to keep cost sane, then LLM YES/NO."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from llm import call, load_cache, save_cache

def predict_pairs(sid, events, cache, window=6):
    """events: list of {off?,word,...}. Judge candidate pairs within a sliding window."""
    if sid in cache: return cache[sid]
    n = len(events)
    # candidate pairs: each event with the next `window` events (narrative locality)
    cands = [(i,j) for i in range(n) for j in range(i+1, min(i+1+window, n))]
    linked = []
    for b in range(0, len(cands), 25):
        chunk = cands[b:b+25]
        lines = []
        for k,(i,j) in enumerate(chunk):
            lines.append(f'#{k}: A="{events[i]["word"]}"  B="{events[j]["word"]}"')
        prompt = ("For each pair of narrative events, does a human annotator link them with a "
                  "DIRECT temporal relation (one causes/enables/immediately precedes/overlaps the "
                  "other)? Most are NO. Reply '#<n> YES' or '#<n> NO'.\n\n" + "\n".join(lines))
        out = call(prompt)
        if not out: return None
        got = {int(m.group(1)):(m.group(2).upper()=="YES") for m in re.finditer(r'#(\d+)\s+(YES|NO)',out)}
        for k,(i,j) in enumerate(chunk):
            if got.get(k):
                p = {"e1_idx":i,"e2_idx":j,"e1_word":events[i]["word"],"e2_word":events[j]["word"]}
                if "off" in events[i]: p["e1_off"]=events[i]["off"]
                if "off" in events[j]: p["e2_off"]=events[j]["off"]
                linked.append(p)
    cache[sid] = linked
    return linked
