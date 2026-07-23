#!/usr/bin/env python3
"""
Thin wrapper around the v5 pipeline that runs ONLY the stories in a named split.

Usage:
    python pipeline/run_split.py --split dev  --stories stories --out predictions
    python pipeline/run_split.py --split test --stories stories --out predictions

Reads split.json at the project root to decide which stories belong to the split,
then runs the v5 pipeline on just those, writing one JSON per story to --out.
This is what the `runner` agent calls. It never touches groundtruth/.
"""
import os, sys, json, glob, argparse, shutil, tempfile, subprocess

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", required=True, choices=["dev", "test"])
    ap.add_argument("--stories", default="stories")
    ap.add_argument("--out", default="predictions")
    ap.add_argument("--split-file", default="split.json")
    args = ap.parse_args()

    split = json.load(open(args.split_file))[args.split]      # list of story ids (no .txt)
    os.makedirs(args.out, exist_ok=True)

    # stage just the split's stories into a temp folder, then run v5 on it
    tmp = tempfile.mkdtemp(prefix=f"{args.split}_")
    staged = 0
    for sid in split:
        src = os.path.join(args.stories, sid + ".txt")
        if os.path.exists(src):
            shutil.copy(src, os.path.join(tmp, sid + ".txt"))
            staged += 1
        else:
            print(f"  WARNING: story not found: {src}")
    print(f"staged {staged}/{len(split)} {args.split} stories")

    # call the v5 entry point on the staged folder
    here = os.path.dirname(os.path.abspath(__file__))
    subprocess.run([sys.executable, os.path.join(here, "run.py"), tmp, args.out], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"done -> {args.out}/")

if __name__ == "__main__":
    main()
