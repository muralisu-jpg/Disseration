"""Step 6: timeline string + irrealis sub-timelines with a fate."""
from . import common as C  # noqa: F401

_FATE = {
    "counterfactual": "never_actual",
    "averted": "never_actual",
    "factive": "realized",
    "conditional": "open",
    "fear": "open",
    "wish": "open",
    "plan": "open",
    "generic": "open",
    "habitual": "open",
    "belief": "open",
    "embedded": "open",
    "imagined": "open",
    "ability": "open",
    "possibility": "open",
    "obligation": "open",
    "hypothetical": "open",
}

def build_timeline(full_text, events, preds):
    """A finite-state-style timeline string + one irrealis sub-timeline per imaginary prediction."""
    snaps = [f"[{e['text']}]" for e in events if not e["is_aux"]]
    timeline_string = "".join(snaps)
    subs = []
    for p in preds:
        if p["track"] != "imaginary":
            continue
        force = p["modal_force"] or "hypothetical"
        fate = _FATE.get(force, "open")
        # a prophecy/plan that is later echoed by a real event is 'realized'
        trig = (p["earlier"] or {}).get("trigger", "")
        subs.append({
            "anchor": p["earlier"], "modal_force": force, "slink": p["slink"],
            "fate": fate, "branch_string": f"[{trig}]",
        })
    return {"timeline_string": timeline_string, "sub_timelines": subs}
