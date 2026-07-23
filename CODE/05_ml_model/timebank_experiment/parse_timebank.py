#!/usr/bin/env python3
"""Parse TimeBank 1.2 .tml files into the training-pair format used by the ML model:
   {e1_word,e1_class,e1_tense,e1_aspect, e2_word,..., same_sentence,text_order, relation}."""
import re, glob, os, json

def parse_file(fp):
    x=open(fp,encoding="utf-8",errors="replace").read()
    # events: eid -> (word, class), and position of the event in text (for order/offset)
    ev_word={}; ev_class={}; ev_pos={}
    for m in re.finditer(r'<EVENT eid="(e\d+)" class="(\w+)"[^>]*>([^<]*)</EVENT>',x):
        eid=m.group(1); ev_class[eid]=m.group(2); ev_word[eid]=m.group(3).strip(); ev_pos[eid]=m.start()
    # makeinstance: eiid -> (eid, tense, aspect)
    mi={}
    for m in re.finditer(r'<MAKEINSTANCE eventID="(e\d+)" eiid="(ei\d+)"[^>]*tense="(\w+)"[^>]*aspect="(\w+)"',x):
        mi[m.group(2)]=(m.group(1),m.group(3),m.group(4))
    # sentence boundaries (rough: <s> tags or periods) — TimeBank uses <s> sometimes
    # tlinks between event instances
    pairs=[]
    for m in re.finditer(r'<TLINK[^>]*relType="(\w+)"[^>]*eventInstanceID="(ei\d+)"[^>]*relatedToEventInstance="(ei\d+)"',x):
        rel,ei1,ei2=m.group(1),m.group(2),m.group(3)
        if ei1 not in mi or ei2 not in mi: continue
        e1,t1,a1=mi[ei1]; e2,t2,a2=mi[ei2]
        if e1 not in ev_word or e2 not in ev_word: continue
        p1,p2=ev_pos.get(e1,0),ev_pos.get(e2,0)
        pairs.append({
            "pair_id":f"{os.path.basename(fp)}_{ei1}_{ei2}",
            "e1_word":ev_word[e1],"e1_class":ev_class[e1],"e1_tense":t1,"e1_aspect":a1,"e1_off":p1,
            "e2_word":ev_word[e2],"e2_class":ev_class[e2],"e2_tense":t2,"e2_aspect":a2,"e2_off":p2,
            "same_sentence": abs(p1-p2)<120,
            "text_order":"e1_first" if p1<p2 else "e2_first",
            "e1_sentence":"", "e2_sentence":"", "signal":"",
            "relation":rel
        })
    return pairs

def main():
    src=os.environ.get("TIMEBANK_SRC","timebank_1_2/data/timeml")
    out=os.environ.get("TB_OUT","timebank_pairs"); os.makedirs(out,exist_ok=True)
    total=0; from collections import Counter; dist=Counter()
    for fp in sorted(glob.glob(f"{src}/*.tml")):
        pairs=parse_file(fp)
        if pairs:
            json.dump(pairs,open(f"{out}/{os.path.basename(fp)}.json","w"),ensure_ascii=False)
            total+=len(pairs)
            for p in pairs: dist[p["relation"]]+=1
    print(f"parsed {total} event-event pairs from TimeBank into {out}")
    print(f"relation distribution: {dict(dist.most_common())}")

if __name__=="__main__": main()
