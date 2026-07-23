"""STAGE 1: story text -> predicted events. LLM reads the story, lists event words + features."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from llm import call, load_cache, save_cache

def predict_events(sid, text, cache):
    if sid in cache: return cache[sid]
    # chunk the story into ~1500-char windows so the LLM can read closely
    chunks = [text[i:i+1500] for i in range(0, len(text), 1500)]
    events = []
    for ci, ch in enumerate(chunks):
        prompt = ("List every EVENT in this story text (verbs of happening/state, and event "
                  "nouns like 'death','battle'). For each, give: the exact word, its class "
                  "(OCCURRENCE/STATE/REPORTING/I_ACTION/I_STATE/ASPECTUAL/PERCEPTION), tense "
                  "(PAST/PRESENT/FUTURE/INFINITIVE/PRESPART/NONE), aspect (NONE/PERFECT/PROGRESSIVE).\n"
                  "Reply one per line: WORD | CLASS | TENSE | ASPECT\n\nTEXT:\n" + ch)
        out = call(prompt)
        if not out:
            return None  # quota died
        for line in out.splitlines():
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 4 and parts[0] and " " not in parts[0][:20]:
                events.append({"word":parts[0].strip('"'),"class":parts[1],"tense":parts[2],"aspect":parts[3]})
    cache[sid] = events
    return events
