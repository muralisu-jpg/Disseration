"""Step 5: assemble the final prediction schema."""

def to_predictions(story_id, preds):
    """Final output schema."""
    rows = []
    for p in preds:
        rows.append({
            "story": story_id,
            "rule": p["rule"], "track": p["track"],
            "tlink": p["tlink"], "slink": p["slink"],
            "earlier": p["earlier"], "later": p["later"],
            "cue_type": p["cue_type"], "confidence": p["confidence"],
            "modal_force": p["modal_force"], "rationale": p["rationale"],
        })
    return rows
