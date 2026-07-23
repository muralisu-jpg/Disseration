"""Step 4: self-check -- verify triggers, de-duplicate, apply per-track confidence gates."""
from . import common as C


# ----------------------------------------------------------------------------- step 4
def selfcheck(full_text, preds, thresholds=None):
    """Verify each trigger is real text, de-duplicate, and apply per-track confidence gates."""
    thresholds = thresholds or {"past": 0.5, "present": 0.5, "future": 0.5, "imaginary": 0.5}
    seen, kept = set(), []
    for p in preds:
        e = p["earlier"]
        # trigger must actually occur at the recorded offset
        if e and full_text[e["off"]:e["off"] + len(e["trigger"])] != e["trigger"]:
            continue
        if p["confidence"] < thresholds.get(p["track"], 0.5):
            continue
        key = (p["track"], p["slink"], p["tlink"], e["off"] if e else None,
               (p["later"] or {}).get("off"))
        if key in seen:
            continue
        seen.add(key)
        kept.append(p)
    return kept
