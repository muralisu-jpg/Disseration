"""Step 1-2: sentence splitting and event extraction.

An *event* is one verb token, with its POS-derived tense and a few construction
flags inferred from the small preceding window (auxiliaries / modals).
"""
from .common import sentences_with_offsets, pos_tokens, MODALS, HAVE, BE


def split_sentences(text):
    return sentences_with_offsets(text)


def _tense(tag):
    return {"MD": "modal", "VBD": "past", "VBN": "participle",
            "VBG": "gerund", "VBZ": "present", "VBP": "present", "VB": "base"}.get(tag)


def extract_events(sent):
    """Return the list of event records for one sentence."""
    toks = pos_tokens(sent["text"], sent["start"])
    events = []
    for i, (w, tag, off) in enumerate(toks):
        t = _tense(tag)
        if t is None:
            continue
        prev = [toks[j][0].lower() for j in range(max(0, i - 3), i)]
        flags = []
        if tag == "VBN" and "had" in prev:
            flags.append("pluperfect")
        if tag == "VBN" and ("have" in prev or "has" in prev):
            flags.append("perfect")
        if tag in ("VB", "VBN") and any(m in prev for m in MODALS):
            flags.append("under_modal")
        if tag == "VB" and ("will" in prev or "shall" in prev):
            flags.append("future")
        if tag == "VB" and "to" in prev:
            flags.append("infinitive")
        is_aux = w.lower() in HAVE or w.lower() in BE or w.lower() in MODALS
        events.append({
            "sent_id": sent["sent_id"], "text": w, "off": off,
            "tag": tag, "tense": t, "flags": flags, "is_aux": is_aux,
        })
    return events
