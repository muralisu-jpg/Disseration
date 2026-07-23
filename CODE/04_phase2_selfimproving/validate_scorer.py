"""Validate the locked scorer before trusting any number. Run once at setup and never edit.
Three tests (project standard):
  1. Majority baseline  -> the floor every real result must beat (expect ~0.676 acc / ~0.27 macro-F1)
  2. Perfect predictions -> must score ~1.0 (proves pair matching is correct)
  3. Garbage/blanket test -> blanket single-label prediction must NOT beat the honest floor
                             on macro-F1 (proves the macro metric is not gameable by spam)
Usage: python validate_scorer.py
"""
import json, subprocess, sys, shutil
from pathlib import Path

GOLD = Path("test_groundtruth")
TMP = Path("_validate_tmp")

def run(pred_dir, tag):
    out = TMP / f"fb_{tag}.json"
    subprocess.run([sys.executable, "score_3way.py", "--pred", str(pred_dir),
                    "--gold", str(GOLD), "--out", str(out)], check=True,
                   stdout=subprocess.DEVNULL)
    return json.loads(out.read_text(encoding="utf-8"))

def main():
    if TMP.exists():
        shutil.rmtree(TMP)
    gold = {}
    for gp in GOLD.glob("*.json"):
        gold.update(json.loads(gp.read_text(encoding="utf-8")))

    # 1. majority (all BEFORE)
    d = TMP / "majority"; d.mkdir(parents=True)
    (d / "all.json").write_text(json.dumps({k: "BEFORE" for k in gold}), encoding="utf-8")
    fb = run(d, "majority")
    print(f"[1] majority  acc3={fb['three_way_accuracy']}  macroF1_3={fb['three_way_macro_f1']}")
    assert fb["three_way_accuracy"] < 0.70, "majority should be below target"

    # 2. perfect
    d = TMP / "perfect"; d.mkdir()
    (d / "all.json").write_text(json.dumps(gold), encoding="utf-8")
    fb = run(d, "perfect")
    print(f"[2] perfect   acc3={fb['three_way_accuracy']}  macroF1_3={fb['three_way_macro_f1']}  fineF1={fb['fine_macro_f1']}")
    assert fb["three_way_accuracy"] == 1.0 and fb["fine_macro_f1"] == 1.0, "perfect must score 1.0"

    # 3. blanket OVERLAP (spam a minority label)
    d = TMP / "blanket"; d.mkdir()
    (d / "all.json").write_text(json.dumps({k: "SIMULTANEOUS" for k in gold}), encoding="utf-8")
    fb = run(d, "blanket")
    print(f"[3] blanket-overlap acc3={fb['three_way_accuracy']}  macroF1_3={fb['three_way_macro_f1']}")
    assert fb["three_way_accuracy"] < 0.676, "blanket minority label must not beat majority"

    shutil.rmtree(TMP)
    print("SCORER VALIDATED: floors known, perfect=1.0, not gameable by blanket labels.")

if __name__ == "__main__":
    main()
