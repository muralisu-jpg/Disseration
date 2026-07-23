#!/usr/bin/env python3
"""
FIXED, documented scorer for non-iconicity detection.
This is the single ruler the loop optimises against. The improver never sees it.

Method (locked):
  - Parse .sty: event layer (offsets, tense) + timelink layer (TEMPORAL + SUBORDINATING).
  - Map each gold relation to one of the four tracks (mapping below).
  - A gold relation's "anchor" = the EARLIER event's line number (body coordinates).
  - A prediction HITS a gold item of the same track if its earlier-event line is within
    +/-1 line of the gold anchor (line-level, +/-1 tolerance). Each gold item matched once.
  - Report per-track precision / recall / F1 + overall, aggregates ONLY.

Usage:
  python fixed_scorer.py --pred predictions --gold groundtruth --split-file split.json \
                         --split dev --stories stories --out feedback.json
"""
import re, os, json, glob, html, argparse, bisect

# ---- gold relation -> track mapping (the documented four-track scheme) ----
# Non-iconic subset only. EVIDENTIAL (reported speech) and ASPECTUAL excluded.
TEMPORAL_MAP = {
    "BEFORE":"past", "IBEFORE":"past",          # anterior  -> flashback
    "AFTER":"future", "IAFTER":"future",        # posterior -> prolepsis
    "SIMULTANEOUS":"present", "INCLUDES":"present",
    "IS_INCLUDED":"present", "DURING":"present", "IDENTITY":"present",
}
SUBORD_MAP = {
    "MODAL":"imaginary", "CONDITIONAL":"imaginary",
    "COUNTER_FACTIVE":"imaginary", "FACTIVE":"imaginary",
    # EVIDENTIAL deliberately excluded (plain reported speech is not irrealis)
}
TRACKS = ["past","present","future","imaginary"]

def gold_char_text(sty):
    m = re.search(r'<rep id="edu\.mit\.story\.char".*?<desc id="0"[^>]*>(.*?)</desc>', sty, re.S)
    return html.unescape(m.group(1)) if m else ""

def body_text(txt):
    s = open(txt, encoding="utf-8").read()
    m = re.search(r'\*/', s)
    return s[m.end():].lstrip() if m else s

def parse_gold(sty_path, body):
    x = open(sty_path, encoding="utf-8").read()
    # events: id -> char offset
    ev_block = re.search(r'<rep id="edu\.mit\.semantics\.rep\.event".*?</rep>', x, re.S).group(0)
    ev_off = {}
    for m in re.finditer(r'<desc id="(\d+)" len="(\d+)" off="(\d+)">', ev_block):
        ev_off[m.group(1)] = int(m.group(3))
    # delta: align gold-char coordinates to body coordinates via a stable anchor
    gc = gold_char_text(x)
    anchor = body[50:90]
    gi = gc.find(anchor)
    delta = (gi - 50) if gi >= 0 else 0
    # line starts in body
    line_starts = [0]
    for i, ch in enumerate(body):
        if ch == "\n":
            line_starts.append(i+1)
    def off2line(o):
        return bisect.bisect_right(line_starts, o)
    # timelinks -> gold (track, earlier_line)
    tl = re.search(r'<rep id="edu\.mit\.semantics\.rep\.timelink".*?</rep>', x, re.S).group(0)
    gold = {t: [] for t in TRACKS}
    for m in re.finditer(r'<desc[^>]*>([^<]*)</desc>', tl):
        p = m.group(1).split("|")
        if len(p) < 4: continue
        cls, rel, a, b = p[0], p[1], p[2], p[3]
        track = TEMPORAL_MAP.get(rel) if cls == "TEMPORAL" else (SUBORD_MAP.get(rel) if cls == "SUBORDINATING" else None)
        if not track: continue
        ea = ev_off.get(a)
        if ea is None: continue
        gold[track].append(off2line(ea - delta))
    return gold

def pred_line(p):
    for k in ("earlier","earlier_event"):
        e = p.get(k)
        if isinstance(e, dict):
            l = e.get("approx_line") or e.get("line")
            if l: return int(l)
            o = e.get("char_offset") or e.get("offset") or e.get("off")
            if o is not None: return ("off", int(o))
    return None

def load_preds(pred_dir, sid):
    for name in (sid+"_predictions.json", sid+".json"):
        f = os.path.join(pred_dir, name)
        if os.path.exists(f):
            x = json.load(open(f, encoding="utf-8"))
            return x if isinstance(x, list) else x.get("predictions", x)
    return []

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", default="predictions")
    ap.add_argument("--gold", default="groundtruth")
    ap.add_argument("--stories", default="stories")
    ap.add_argument("--split-file", default="split.json")
    ap.add_argument("--split", default="dev")
    ap.add_argument("--out", default="feedback.json")
    ap.add_argument("--tol", type=int, default=1)
    a = ap.parse_args()

    stories = json.load(open(a.split_file))[a.split]
    tp = {t:0 for t in TRACKS}; pred_n = {t:0 for t in TRACKS}; gold_n = {t:0 for t in TRACKS}

    for sid in stories:
        sty = os.path.join(a.gold, sid + ".sty")
        txt = os.path.join(a.stories, sid + ".txt")
        if not (os.path.exists(sty) and os.path.exists(txt)): continue
        body = body_text(txt)
        gold = parse_gold(sty, body)
        for t in TRACKS: gold_n[t] += len(gold[t])

        preds = load_preds(a.pred, sid)
        # need line for each pred; if pred carries offset, convert with same line map
        line_starts = [0]
        for i,ch in enumerate(body):
            if ch=="\n": line_starts.append(i+1)
        def o2l(o): return bisect.bisect_right(line_starts, o)

        used = {t:set() for t in TRACKS}
        for p in preds:
            t = p.get("track")
            if t not in TRACKS: continue
            pred_n[t] += 1
            pl = pred_line(p)
            if pl is None: continue
            ln = o2l(pl[1]) if isinstance(pl, tuple) else pl
            best=None; bestd=a.tol+1
            for i,gl in enumerate(gold[t]):
                if i in used[t]: continue
                d=abs(gl-ln)
                if d<bestd: bestd=d; best=i
            if best is not None and bestd<=a.tol:
                tp[t]+=1; used[t].add(best)

    def prf(t):
        P = tp[t]/pred_n[t] if pred_n[t] else 0.0
        R = tp[t]/gold_n[t] if gold_n[t] else 0.0
        F = 2*P*R/(P+R) if (P+R) else 0.0
        return round(P,2), round(R,2), round(F,2)

    out = {"overall_f1": 0.0}
    TPt=sum(tp.values()); PR=sum(pred_n.values()); GD=sum(gold_n.values())
    oP = TPt/PR if PR else 0; oR = TPt/GD if GD else 0
    out["overall_f1"] = round(2*oP*oR/(oP+oR),2) if (oP+oR) else 0.0
    for t in TRACKS:
        P,R,F = prf(t)
        note = "balanced"
        if R < 0.15: note = "recall low; track under-detected"
        elif P < 0.2: note = "precision low; likely over-firing"
        out[t] = {"precision":P,"recall":R,"f1":F,"note":note,
                  "_gold":gold_n[t],"_pred":pred_n[t],"_tp":tp[t]}
    json.dump(out, open(a.out,"w"), indent=2)
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
