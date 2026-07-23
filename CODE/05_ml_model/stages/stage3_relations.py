"""STAGE 3: pairs -> predicted relations. LLM classifies each pair's TimeML relation."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from llm import call, load_cache, save_cache

VALID=["BEFORE","AFTER","IBEFORE","IAFTER","SIMULTANEOUS","IDENTITY","INCLUDES","IS_INCLUDED",
       "DURING","DURING_INV","BEGINS","BEGUN_BY","ENDS","ENDED_BY","MODAL","CONDITIONAL","COUNTER_FACTIVE"]
DEFS=("TEMPORAL: BEFORE(A ends before B starts), AFTER, IBEFORE(meets), SIMULTANEOUS(same span), "
      "INCLUDES(A contains B), IS_INCLUDED, IDENTITY(same event), BEGINS/ENDS(shared endpoint). "
      "IMAGINARY: MODAL(wish/order/ability 'wanted to'), CONDITIONAL('if..then'), "
      "COUNTER_FACTIVE(did NOT happen: 'refused to','forgot to').")

def predict_relations(sid, pairs, cache):
    if sid in cache: return cache[sid]
    rels = {}
    for b in range(0, len(pairs), 25):
        chunk = pairs[b:b+25]
        lines=[]
        for k,p in enumerate(chunk):
            s1=p.get("e1_sentence","")[:120]; s2=p.get("e2_sentence","")[:120]
            lines.append(f'#{k}: E1="{p["e1_word"]}" (in:"{s1}") E2="{p["e2_word"]}" (in:"{s2}")')
        prompt=(f"Classify EVENT1's relation to EVENT2. {DEFS}\nReply '#<n> <LABEL>' from: "
                +", ".join(VALID)+"\n\n"+"\n".join(lines))
        out=call(prompt)
        if not out: return None
        got={int(m.group(1)):m.group(2) for m in re.finditer(r'#(\d+)\s+([A-Z_]+)',out) if m.group(2) in VALID}
        for k,p in enumerate(chunk):
            key=p.get("key") or f'{p.get("e1_idx","")}_{p.get("e2_idx","")}' or f'{p.get("e1_off","")}_{p.get("e2_off","")}'
            rels[key]=got.get(k,"BEFORE")
    cache[sid]=rels
    return rels
