"""Kit 8 classifier - EDITABLE by the improver agent.

Task: for each given event pair (from test_pairs/*.json), predict the fine-grained
TimeML temporal relation (one of the 14 order labels). The scorer collapses to
before/after/overlap. PRIMARY metric: three_way_accuracy (target >= 0.70, SOTA 0.77).

Structure (v0):
  - rules_classify(pair): simple honest baseline (text order).
  - llm_classify_story(...): batched LLM path with per-story cache, few-shot examples
    from train_examples/ and point-algebra definitions from guidelines/.
    Enabled via config.json {"use_llm": true}. Windows: uses shell=True because
    `claude` is claude.ps1, not an .exe.
  - Hard-pair routing: LLM is spent only on pairs the rules are unsure about.

FIREWALL: this file must NEVER read test_groundtruth/ or score_3way.py.
Only story text, test_pairs, train_examples and guidelines are allowed inputs.
"""
import json, os, subprocess, sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEST_PAIRS = ROOT / "test_pairs"
TRAIN = ROOT / "train_examples"
GUIDE = ROOT / "guidelines"
PRED = ROOT / "predictions"
CACHE_FILE = ROOT / "classifier" / "llm_cache.json"
CONFIG_FILE = ROOT / "classifier" / "config.json"

LABELS = ["BEFORE","IBEFORE","AFTER","IAFTER","SIMULTANEOUS","IDENTITY","INCLUDES",
          "IS_INCLUDED","DURING","DURING_INV","BEGINS","BEGUN_BY","ENDS","ENDED_BY"]

def load_config():
    cfg = dict(use_llm=False, llm_batch_size=25, llm_on="hard",  # "hard" | "all"
               llm_timeout=180)
    if CONFIG_FILE.exists():
        cfg.update(json.loads(CONFIG_FILE.read_text(encoding="utf-8")))
    return cfg

# ---------------------------------------------------------------- rules (v0)
def is_identity(p):
    """Deterministic IDENTITY detector: a re-mention of the SAME event.
    Predicate (tuned on train_examples only): the two triggers are the SAME
    normalized token, NEITHER is a REPORTING event (repeated "said" = distinct
    speech acts, sequential not identical), and they are in DIFFERENT sentences
    (same-sentence repeats like "ran and ran" are sequential IBEFORE/BEFORE).
    Train precision = 9/9 = 1.00 for IDENTITY (all overlap), coverage 9 pairs."""
    w1 = p["e1_word"].strip().lower()
    w2 = p["e2_word"].strip().lower()
    if not w1 or w1 != w2:
        return False
    if p["e1_class"] == "REPORTING" or p["e2_class"] == "REPORTING":
        return False
    if p["same_sentence"]:
        return False
    return True

def is_stative_overlap(p):
    """Deterministic OVERLAP detector based on lexical aspect (measured on
    train_examples only). A STATE event as E2, or either trigger in the
    PROGRESSIVE grammatical aspect, denotes an ongoing/durative situation that
    the other event coincides with or is contained in -- an overlap relation
    rather than a strict sequence.
    Predicate: e2_class == "STATE" OR (e1_aspect or e2_aspect) == "PROGRESSIVE".
    TRAIN: fires 21, overlap precision 17/21 = 0.810 (dist overlap=17, before=3,
    after=1), capturing SIMULTANEOUS/IDENTITY/IS_INCLUDED/BEGINS/ENDS/ENDED_BY."""
    if p["e2_class"] == "STATE":
        return True
    if p["e1_aspect"] == "PROGRESSIVE" or p["e2_aspect"] == "PROGRESSIVE":
        return True
    return False

def rules_classify(p):
    """Honest baseline: narrative order, with deterministic IDENTITY and
    stative-overlap rules. Improver: refine me, but never by blanket-predicting
    a label to chase recall."""
    if is_identity(p):
        return "IDENTITY"
    if is_stative_overlap(p):
        return "SIMULTANEOUS"
    if p["text_order"] == "e2_first":
        return "AFTER"
    return "BEFORE"

def is_hard(p):
    """Pairs where rules are least trustworthy -> route to LLM when enabled."""
    if p["same_sentence"]:
        return True
    if p["e1_word"].lower() == p["e2_word"].lower():
        return True  # possible IDENTITY (repeated mention)
    if p["e1_tense"] != p["e2_tense"]:
        return True
    return False

# ---------------------------------------------------------------- few-shot
def build_fewshot(max_per_label=3):
    by_label = {}
    for tp in sorted(TRAIN.glob("*.json")):
        for r in json.loads(tp.read_text(encoding="utf-8")):
            by_label.setdefault(r["relation"], []).append(r)
    lines = []
    for lab in LABELS:
        for r in by_label.get(lab, [])[:max_per_label]:
            lines.append(
                f'- E1="{r["e1_word"]}" in "{r["e1_sentence"][:120]}" | '
                f'E2="{r["e2_word"]}" in "{r["e2_sentence"][:120]}" '
                f'| tenses {r["e1_tense"]}/{r["e2_tense"]} -> {lab}')
    return "\n".join(lines)

def point_algebra():
    f = GUIDE / "point_algebra_definitions.md"
    return f.read_text(encoding="utf-8") if f.exists() else ""

# ---------------------------------------------------------------- LLM path
def llm_call(prompt, timeout):
    # Pass the prompt on stdin, not as an argv string: the few-shot + point-algebra
    # prompt is ~12k chars and exceeds the Windows command-line length limit
    # ("The command line is too long."), which silently produced empty output and
    # forced a rules-only fallback. stdin has no such limit.
    r = subprocess.run('claude -p --model claude-opus-4-8', shell=True, input=prompt,
                       capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip()

def parse_llm_json(raw):
    m = re.search(r'\{.*\}', raw, re.S)
    if not m:
        return {}
    try:
        d = json.loads(m.group(0))
        return {k: str(v).upper().strip() for k, v in d.items()
                if str(v).upper().strip() in LABELS}
    except Exception:
        return {}

def llm_classify_batch(pairs, fewshot, defs, cfg):
    items = []
    for p in pairs:
        items.append(
            f'{p["pair_id"]}: E1="{p["e1_word"]}" [{p["e1_tense"]},{p["e1_class"]}] '
            f'sentence: "{p["e1_sentence"][:160]}" ||| '
            f'E2="{p["e2_word"]}" [{p["e2_tense"]},{p["e2_class"]}] '
            f'sentence: "{p["e2_sentence"][:160]}" '
            f'(same_sentence={p["same_sentence"]}, text_order={p["text_order"]})')
    prompt = (
        "You are a TimeML temporal relation annotator for folktales.\n"
        "For each event pair, decide the temporal relation of E1 to E2 using these "
        "exact point-algebra definitions:\n" + defs +
        "\nLabels: " + ", ".join(LABELS) +
        "\nWorked examples from annotated stories:\n" + fewshot +
        "\nNow classify these pairs. Reason about the START and END points of each "
        "event, then answer. Respond ONLY with a JSON object mapping each pair id to "
        "one label, no other text.\n\n" + "\n".join(items))
    return parse_llm_json(llm_call(prompt, cfg["llm_timeout"]))

# ---------------------------------------------------------------- main
def main():
    cfg = load_config()
    cache = json.loads(CACHE_FILE.read_text(encoding="utf-8")) if CACHE_FILE.exists() else {}
    fewshot = build_fewshot()
    defs = point_algebra()
    PRED.mkdir(exist_ok=True)

    for sp in sorted(TEST_PAIRS.glob("*.json")):
        pairs = json.loads(sp.read_text(encoding="utf-8"))
        preds, n_cache, n_fresh, n_rule = {}, 0, 0, 0
        llm_queue = []
        for p in pairs:
            pid = p["pair_id"]
            if pid in cache:
                preds[pid] = cache[pid]; n_cache += 1
            elif cfg["use_llm"] and (cfg["llm_on"] == "all" or is_hard(p)):
                llm_queue.append(p)
            else:
                preds[pid] = rules_classify(p); n_rule += 1
        # batched LLM on the queue
        bs = cfg["llm_batch_size"]
        for i in range(0, len(llm_queue), bs):
            batch = llm_queue[i:i+bs]
            try:
                got = llm_classify_batch(batch, fewshot, defs, cfg)
            except Exception as e:
                print(f"  LLM error ({e}); falling back to rules for this batch")
                got = {}
            for p in batch:
                pid = p["pair_id"]
                if pid in got:
                    preds[pid] = got[pid]; cache[pid] = got[pid]; n_fresh += 1
                else:
                    preds[pid] = rules_classify(p); n_rule += 1
            CACHE_FILE.write_text(json.dumps(cache, indent=0), encoding="utf-8")
        (PRED / sp.name).write_text(json.dumps(preds, indent=1), encoding="utf-8")
        print(f"{sp.stem}: {n_cache} from cache, {n_fresh} fresh from LLM, {n_rule} rule fallback")

if __name__ == "__main__":
    main()
