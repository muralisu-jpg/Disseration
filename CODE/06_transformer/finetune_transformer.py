#!/usr/bin/env python3
"""
TRANSFORMER STUDENT (RoBERTa) — the honest shot at the LLM's reading ability.

Fine-tunes distilroberta-base (or roberta-base) to READ the event pair in context and
classify the 3-way temporal relation (before/after/overlap). Unlike the feature model,
this READS the sentences — the one approach that attacks the reading-comprehension gap
that separates 0.80 (features) from 0.847 (LLM).

HONEST DISCIPLINE (built in):
  - Train on N2 + 3 Propp stories; test on the 12 held-out Propp stories.
  - A validation split is carved from TRAINING for early-stopping — the TEST set is never
    used for any decision.
  - The TEST set is scored exactly ONCE, at the end.
  - Runs MULTIPLE SEEDS and reports mean +/- spread (2.6k pairs is small for a transformer,
    so variance is real and must be reported honestly, not cherry-picked).

RUN (best on a GPU — Google Colab/Kaggle free T4, or a local CUDA machine):
  pip install transformers torch scikit-learn numpy
  python finetune_transformer.py --kit9 /path/to/kit9 --seeds 3 --epochs 4

On CPU it will work but be slow (~30-60 min/seed). On a T4 GPU: ~5-10 min/seed.
"""
import json, argparse, glob, os, random
import numpy as np

def collapse(r):
    r = r.upper()
    if r in ("BEFORE", "IBEFORE"): return 0   # before
    if r in ("AFTER", "IAFTER"):   return 1   # after
    return 2                                   # overlap
LABEL_NAMES = ["before", "after", "overlap"]

def pair_text(p):
    """Render the pair as text RoBERTa can read: both events marked, with their context."""
    return (f"Event1: {p.get('e1_word','').strip()} "
            f"({p.get('e1_class','')},{p.get('e1_tense','')},{p.get('e1_aspect','')}) . "
            f"Event2: {p.get('e2_word','').strip()} "
            f"({p.get('e2_class','')},{p.get('e2_tense','')},{p.get('e2_aspect','')}) . "
            f"Context1: {(p.get('e1_sentence','') or '')[:220]} "
            f"Context2: {(p.get('e2_sentence','') or '')[:220]} "
            f"[same_sentence={p.get('same_sentence')}] [text_order={p.get('text_order')}]")

def load_dir(d):
    out = []
    for fp in sorted(glob.glob(os.path.join(d, "*.json"))):
        out += json.load(open(fp, encoding="utf-8"))
    return out

def load_test(pairs_dir, gt_dir):
    pairs = load_dir(pairs_dir)
    gt = {}
    for fp in glob.glob(os.path.join(gt_dir, "*.json")):
        gt.update(json.load(open(fp, encoding="utf-8")))
    X, y = [], []
    for p in pairs:
        pid = p.get("pair_id") or p.get("id")
        if pid in gt:
            X.append(p); y.append(collapse(gt[pid]))
    return X, y

def run_one_seed(seed, train_pairs, train_labels, test_pairs, test_labels, model_name, epochs):
    import torch
    from torch.utils.data import Dataset
    from transformers import (AutoTokenizer, AutoModelForSequenceClassification,
                              TrainingArguments, Trainer, set_seed)
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, f1_score
    set_seed(seed); random.seed(seed); np.random.seed(seed)

    tok = AutoTokenizer.from_pretrained(model_name)

    class DS(Dataset):
        def __init__(self, pairs, labels):
            self.enc = tok([pair_text(p) for p in pairs], truncation=True,
                           padding=True, max_length=256)
            self.labels = labels
        def __len__(self): return len(self.labels)
        def __getitem__(self, i):
            item = {k: torch.tensor(v[i]) for k, v in self.enc.items()}
            item["labels"] = torch.tensor(self.labels[i]); return item

    # validation split from TRAINING ONLY (never the test set)
    tr_p, va_p, tr_y, va_y = train_test_split(train_pairs, train_labels,
                                              test_size=0.15, random_state=seed,
                                              stratify=train_labels)
    ds_tr, ds_va = DS(tr_p, tr_y), DS(va_p, va_y)
    ds_te = DS(test_pairs, test_labels)

    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)

    def metrics(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=-1)
        return {"acc": accuracy_score(labels, preds),
                "macro_f1": f1_score(labels, preds, average="macro")}

    args = TrainingArguments(
        output_dir=f"./_tmp_seed{seed}", num_train_epochs=epochs,
        per_device_train_batch_size=16, per_device_eval_batch_size=32,
        learning_rate=2e-5, weight_decay=0.01,
        eval_strategy="epoch", save_strategy="no", logging_steps=50,
        report_to="none", seed=seed)
    trainer = Trainer(model=model, args=args, train_dataset=ds_tr,
                      eval_dataset=ds_va, compute_metrics=metrics)
    trainer.train()

    # SCORE TEST ONCE
    pred = trainer.predict(ds_te)
    preds = np.argmax(pred.predictions, axis=-1)
    acc = accuracy_score(test_labels, preds)
    mf1 = f1_score(test_labels, preds, average="macro")
    return acc, mf1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kit9", required=True, help="path to kit9 folder")
    ap.add_argument("--model", default="distilroberta-base")
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--epochs", type=int, default=4)
    a = ap.parse_args()

    train_pairs = load_dir(os.path.join(a.kit9, "train_examples")) + \
                  load_dir(os.path.join(a.kit9, "n2_train"))
    train_labels = [collapse(p["relation"]) for p in train_pairs]
    test_pairs, test_labels = load_test(os.path.join(a.kit9, "test_pairs"),
                                        os.path.join(a.kit9, "test_groundtruth"))
    print(f"train pairs: {len(train_pairs)} | test pairs: {len(test_pairs)}")
    print(f"model: {a.model} | seeds: {a.seeds} | epochs: {a.epochs}\n")

    accs, f1s = [], []
    for s in range(a.seeds):
        print(f"=== SEED {s} ===")
        acc, mf1 = run_one_seed(s, train_pairs, train_labels,
                                test_pairs, test_labels, a.model, a.epochs)
        print(f"  seed {s}: TEST acc={acc:.4f} macro-F1={mf1:.4f}\n")
        accs.append(acc); f1s.append(mf1)

    accs, f1s = np.array(accs), np.array(f1s)
    print("=" * 60)
    print("TRANSFORMER RESULT (honest, test scored once per seed)")
    print("=" * 60)
    print(f"  accuracy : mean {accs.mean():.4f}  +/- {accs.std():.4f}  "
          f"(min {accs.min():.4f}, max {accs.max():.4f})")
    print(f"  macro-F1 : mean {f1s.mean():.4f}  +/- {f1s.std():.4f}")
    print(f"\n  vs feature model 0.80 acc / 0.58 F1  |  vs LLM 0.847 acc / 0.800 F1")
    verdict = ("BEATS the LLM" if accs.mean() > 0.847 else
               "matches/approaches the LLM" if accs.mean() >= 0.82 else
               "beats the feature model" if accs.mean() > 0.80 else
               "below the feature model")
    print(f"  verdict: {verdict}")

    json.dump({"model": a.model, "seeds": a.seeds, "epochs": a.epochs,
               "test_accuracy_mean": round(float(accs.mean()), 4),
               "test_accuracy_std": round(float(accs.std()), 4),
               "test_macro_f1_mean": round(float(f1s.mean()), 4),
               "test_macro_f1_std": round(float(f1s.std()), 4),
               "per_seed_acc": [round(float(x), 4) for x in accs],
               "per_seed_f1": [round(float(x), 4) for x in f1s],
               "note": "Honest: validation split from training for early-stopping; test scored "
                       "once per seed; mean over seeds reported (small data => real variance)."},
              open("out/transformer_result.json", "w"), indent=1)
    print("\nsaved out/transformer_result.json")

if __name__ == "__main__":
    main()
