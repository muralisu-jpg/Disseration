# Transformer Student (RoBERTa) — the honest shot at the LLM

The feature model plateaus at ~0.80 because it CANNOT read sentences — only hand-crafted
numbers. This transformer READS the event pair in context, attacking the reading-comprehension
gap that separates 0.80 (features) from 0.847 (LLM). It is the one student that can, in
principle, approach the LLM.

## Honest discipline (built in)
- Train = N2 + 3 Propp stories (2,593 pairs); Test = 12 held-out Propp stories (2,043 pairs).
- Validation split carved from TRAINING for early-stopping — the TEST set drives NO decision.
- TEST scored exactly ONCE per seed, at the end.
- MULTIPLE SEEDS, mean +/- spread reported. 2.6k pairs is small for a transformer, so variance
  is real; we report the mean honestly rather than cherry-picking the best seed.

## Run (needs a GPU — free options: Google Colab / Kaggle)
### Colab (easiest)
Open Transformer_Colab.ipynb, set Runtime -> T4 GPU, upload kit9.zip + this script, run.

### Local (if you have CUDA)
  pip install transformers torch scikit-learn numpy
  python finetune_transformer.py --kit9 "C:\path\to\kit9" --seeds 3 --epochs 4

Options:
  --model distilroberta-base   (default, fast)  |  roberta-base (stronger, slower)
  --seeds 3                    (report mean over seeds)
  --epochs 4                   (try 6 for more training)

## What to expect (honest)
- Likely range on this small data: 0.78 - 0.85 accuracy. Real outcomes:
    * > 0.80  -> beats the feature model
    * ~ 0.82-0.85 -> approaches/matches the LLM (0.847)
    * > 0.847 -> beats the LLM (a strong result; verify with seeds)
- It MIGHT NOT clear the LLM on 2.6k pairs — that would itself be an honest finding
  (small-data transformers can underperform careful feature models). Report whatever it is.

## Files
  finetune_transformer.py   the fine-tuning script (honest: val-split, test-once, multi-seed)
  Transformer_Colab.ipynb   ready-to-run Colab notebook
  out/                      results land here (transformer_result.json)
