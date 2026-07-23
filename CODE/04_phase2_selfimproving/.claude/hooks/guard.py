import json, sys
data = json.load(sys.stdin)
tool = data.get("tool_name", "")
ti = data.get("tool_input", {}) or {}
path = str(ti.get("file_path", "")) + " " + str(ti.get("path", ""))
cmd = str(ti.get("command", ""))
LOCKED_WRITE = ["test_groundtruth", "test_pairs", "train_examples", "score_3way.py",
                "validate_scorer.py", "guidelines", "state.json.lock"]
def deny(msg):
    print(msg, file=sys.stderr); sys.exit(2)
if tool in ("Read", "Grep", "Glob") and "test_groundtruth" in path:
    deny("FIREWALL: test_groundtruth is scorer-only. Blocked.")
if tool in ("Edit", "Write", "NotebookEdit"):
    for p in LOCKED_WRITE:
        if p in path:
            deny(f"FIREWALL: {p} is locked. Blocked.")
if tool == "Bash" and "test_groundtruth" in cmd and "score_3way.py" not in cmd:
    deny("FIREWALL: only the locked scorer may touch test_groundtruth. Blocked.")
sys.exit(0)
