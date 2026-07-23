#!/usr/bin/env python3
"""Run the non-iconicity pipeline over every story in ./texts and write ./predictions.

Usage:  python run.py            # process texts/ -> predictions/ + run_report.md
        python run.py texts out  # custom input / output folders

The pipeline is deterministic and blind: it reads only the plain story text.
"""
import os, sys, json, glob
from collections import Counter
from pipeline.events import split_sentences, extract_events
from pipeline.rules import run_sentence
from pipeline.selfcheck import selfcheck
from pipeline.predictions import to_predictions
from pipeline.timeline import build_timeline

# per-track confidence gates (the single set of tunables; raise to favour precision)
THRESHOLDS = {"past": 0.5, "present": 0.5, "future": 0.5, "imaginary": 0.5}


def process_story(path):
    story_id = os.path.splitext(os.path.basename(path))[0]
    text = open(path, encoding="utf-8").read()
    all_events, raw_preds = [], []
    for sent in split_sentences(text):
        events = extract_events(sent)
        all_events.extend(events)
        raw_preds.extend(run_sentence(text, sent, events))
    preds = selfcheck(text, raw_preds, THRESHOLDS)
    rows = to_predictions(story_id, preds)
    timeline = build_timeline(text, all_events, preds)
    return story_id, rows, timeline


def main(in_dir="texts", out_dir="predictions"):
    os.makedirs(out_dir, exist_ok=True)
    grand = Counter()
    cue = Counter()
    report = ["# Run report -- non-iconicity extraction (v5)",
              "",
              "Pipeline: sentences -> events -> rules -> selfcheck -> predictions -> timeline. "
              "Deterministic; reads only the plain text; no answer key, no network at inference.",
              "",
              "| story | total | past | present | future | imaginary | explicit | inferred |",
              "|---|---|---|---|---|---|---|---|"]
    for path in sorted(glob.glob(os.path.join(in_dir, "*.txt"))):
        story_id, rows, timeline = process_story(path)
        json.dump({"predictions": rows, "timeline": timeline},
                  open(os.path.join(out_dir, story_id + ".json"), "w"), indent=2)
        c = Counter(r["track"] for r in rows)
        cc = Counter(r["cue_type"] for r in rows)
        for k, v in c.items():
            grand[k] += v
        for k, v in cc.items():
            cue[k] += v
        report.append("| {} | {} | {} | {} | {} | {} | {} | {} |".format(
            story_id, len(rows), c["past"], c["present"], c["future"], c["imaginary"],
            cc["explicit_marker"], cc["inferred"]))
    report.append("| **TOTAL** | **{}** | **{}** | **{}** | **{}** | **{}** | **{}** | **{}** |".format(
        sum(grand.values()), grand["past"], grand["present"], grand["future"], grand["imaginary"],
        cue["explicit_marker"], cue["inferred"]))
    open("run_report.md", "w").write("\n".join(report) + "\n")
    print("Done. {} predictions across {} stories -> {}/".format(
        sum(grand.values()), len(glob.glob(os.path.join(in_dir, '*.txt'))), out_dir))
    print("Tracks:", dict(grand), "| cue:", dict(cue))


if __name__ == "__main__":
    args = sys.argv[1:]
    main(*(args or []))
