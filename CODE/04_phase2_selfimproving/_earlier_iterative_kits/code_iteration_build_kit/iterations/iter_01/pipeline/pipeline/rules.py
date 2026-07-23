"""Step 3 -- the deciding step.

For each sentence we run regular-expression detectors grouped by track:
  past       (BEFORE)        -- the event is told later than it happens
  present    (SIMULTANEOUS/INCLUDES) -- told in sequence but overlapping in time
  future     (after speech time) -- told before it happens
  imaginary  (SLINK)         -- modal / conditional / counter-factive / factive / habitual

Every prediction records: rule, track, TimeML tlink/slink, earlier/later refs,
cue_type (explicit_marker vs inferred), a confidence, a rationale, and modal_force.
An EVIDENTIAL guard keeps plain reported speech out of the imaginary track.
"""
import re
from . import common as C


def _abs(base, m, grp=0):
    return base + m.start(grp)


def _matrix_after(events, off):
    e = C.nearest_verb_after([x for x in events if not x["is_aux"]], off)
    return C.ref_from_event(e) if e else None


def _matrix_before(events, off):
    e = C.nearest_verb_before([x for x in events if not x["is_aux"]], off)
    return C.ref_from_event(e) if e else None


def _reported_context(sent_text, rel_off):
    """True if a reporting verb precedes this point with a quote/'that' between -> evidential."""
    pre = sent_text[:rel_off].lower()
    if not any(rv in pre.split() for rv in C.REPORTING):
        return False
    # is there a quote mark or ' that ' after the last reporting verb?
    last = max((pre.rfind(rv) for rv in C.REPORTING if rv in pre), default=-1)
    seg = sent_text[last:rel_off]
    return ('"' in seg) or ('\u201c' in seg) or (" that " in seg.lower())


class Collector:
    def __init__(self, full_text):
        self.t = full_text
        self.out = []

    def add(self, rule, track, off, length, tlink=None, slink=None,
            earlier=None, later=None, cue_type="explicit_marker", confidence=0.6,
            rationale="", modal_force=None):
        self.out.append({
            "rule": rule, "track": track, "tlink": tlink, "slink": slink,
            "earlier": earlier or C.ref(self.t, off, length, rule),
            "later": later,
            "cue_type": cue_type, "confidence": round(confidence, 2),
            "rationale": rationale, "modal_force": modal_force,
        })


def run_sentence(full_text, sent, events):
    s = sent["text"]
    base = sent["start"]
    col = Collector(full_text)

    # ---------------------------------------------------------------- PAST
    # pluperfect: had (+adv) + past participle
    for m in re.finditer(r"\bhad\b\s+((?:not|never|already|just|soon|long)\s+){0,2}([A-Za-z]+)", s, re.I):
        if C.is_participle(m.group(2)):
            off = _abs(base, m, 2)
            col.add("P_pluperfect", "past", off, len(m.group(2)), tlink="BEFORE",
                    later=_matrix_after(events, off), confidence=0.9,
                    rationale="pluperfect (had + past participle) marks an event anterior to the narrative now")

    # present perfect: have/has + PP (event prior to speech time)
    for m in re.finditer(r"\b(have|has)\b\s+((?:not|never|just)\s+)?([A-Za-z]+)", s, re.I):
        if C.is_participle(m.group(3)):
            off = _abs(base, m, 3)
            col.add("P_present_perfect", "past", off, len(m.group(3)), tlink="BEFORE",
                    later=_matrix_after(events, off), confidence=0.7,
                    rationale="present perfect points back from the moment of speaking")

    # counterfactual past perfect: would/could/might/should + have + PP  (past AND imaginary)
    for m in re.finditer(r"\b(would|could|might|should)\b\s+have\s+([A-Za-z]+)", s, re.I):
        if C.is_participle(m.group(2)):
            off = _abs(base, m, 0)
            col.add("P_counterfactual", "past", off, len(m.group(0)), tlink="BEFORE",
                    later=_matrix_after(events, off), confidence=0.7,
                    rationale="counterfactual past perfect describes an unrealised prior event")
            col.add("I_counterfactual", "imaginary", off, len(m.group(0)), slink="COUNTER_FACTIVE",
                    confidence=0.75, modal_force="counterfactual",
                    rationale="'would/could have + PP' is contrary to fact")

    # temporal subordinator whose clause precedes the matrix
    for conj in C.SUBORD_BEFORE:
        for m in re.finditer(r"\b" + re.escape(conj) + r"\b", s, re.I):
            off = _abs(base, m, 0)
            col.add("P_subordinator", "past", off, len(conj), tlink="BEFORE",
                    later=_matrix_after(events, off), confidence=0.65,
                    rationale="temporal subordinator: the subordinate event precedes the matrix event")

    # retrospective adverbial (only if a past-tense verb is present in the sentence)
    if any(e["tense"] == "past" for e in events):
        for adv in C.RETRO_ADV:
            for m in re.finditer(r"\b" + re.escape(adv) + r"\b", s, re.I):
                off = _abs(base, m, 0)
                col.add("P_retrospective", "past", off, len(adv), tlink="BEFORE",
                        later=_matrix_after(events, off), confidence=0.55,
                        rationale="retrospective adverbial signals anteriority")

    # recollection / discovery embeds an earlier event
    for m in re.finditer(r"\b(remembered|recalled|realized|realised|discovered|learned)\b\s+(that\b|how\b)", s, re.I):
        off = _abs(base, m, 0)
        col.add("P_recollection", "past", off, len(m.group(0)), tlink="BEFORE",
                later=_matrix_after(events, off), confidence=0.5, cue_type="inferred",
                rationale="recollection/discovery introduces an event that pre-exists the discovery")

    # ---------------------------------------------------------------- PRESENT
    for conj in C.SIMUL_CONJ:
        for m in re.finditer(r"\b" + re.escape(conj) + r"\b", s, re.I):
            off = _abs(base, m, 0)
            col.add("R_simultaneity", "present", off, len(conj), tlink="SIMULTANEOUS",
                    earlier=_matrix_before(events, off), later=_matrix_after(events, off),
                    confidence=0.8, rationale="co-temporal connective: the two clauses overlap in time")

    # perception + V-ing (the perceived ongoing event overlaps the perceiving)
    for m in re.finditer(r"\b(saw|watched|heard|found|noticed|observed)\b\s+(?:\w+\s+){0,3}?([A-Za-z]+ing)\b", s, re.I):
        off = _abs(base, m, 2)
        col.add("R_perception", "present", off, len(m.group(2)), tlink="INCLUDES",
                earlier=_matrix_before(events, off), confidence=0.6,
                rationale="perception frame: the ongoing event is included in the act of perceiving")

    # present-participle adjunct clause: a comma-set "-ing" clause runs concurrently
    # with the matrix event (trailing "she left, smiling" or fronted "Smiling, she left").
    # Validate against VBG-tagged events so -ing nouns (morning, building) do not fire.
    vbg_offs = {e["off"] for e in events if e["tag"] == "VBG"}
    for pat in (r",\s+(?:and\s+|then\s+)?([A-Za-z]+ing)\b",
                r"(?:^|[.!?]\s+)([A-Za-z]+ing)\b[^.,!?;:]*,"):
        for m in re.finditer(pat, s):
            off = _abs(base, m, 1)
            if off not in vbg_offs:
                continue
            col.add("R_participle_adjunct", "present", off, len(m.group(1)),
                    tlink="SIMULTANEOUS",
                    earlier=_matrix_before(events, off), later=_matrix_after(events, off),
                    confidence=0.6, cue_type="inferred",
                    rationale="present-participle adjunct clause overlaps the matrix event in time")

    # progressive aspect: be + (adv) + V-ing names a durative, ongoing event that
    # overlaps a co-occurring (often punctual) event -- the textbook simultaneity cue
    # ("she was cooking when he arrived"). Validate the -ing against VBG events so that
    # be + -ing noun ("was nothing", "is evening) cannot fire.
    for m in re.finditer(r"\b(?:am|is|are|was|were|be|been|being)\b\s+(?:(?:not|still|already|just|now)\s+){0,2}([A-Za-z]+ing)\b", s, re.I):
        off = _abs(base, m, 1)
        if off not in vbg_offs:
            continue
        col.add("R_progressive", "present", off, len(m.group(1)),
                tlink="SIMULTANEOUS",
                earlier=_matrix_before(events, off), later=_matrix_after(events, off),
                confidence=0.55, cue_type="inferred",
                rationale="progressive aspect frames a durative ongoing event that overlaps a co-occurring event")

    # ---------------------------------------------------------------- FUTURE
    for m in re.finditer(r"\b(will|shall)\b\s+([A-Za-z]+)", s, re.I):
        off = _abs(base, m, 0)
        col.add("F_will", "future", off, len(m.group(0)), tlink="AFTER",
                confidence=0.8, rationale="'will/shall + V' projects an event after the moment of speaking")

    # contracted future: "'ll" (e.g. I'll, she'll, we'll) -- same force as 'will + V'
    for m in re.finditer(r"'ll\s+(?:(?:not|never|just)\s+)?([A-Za-z]+)", s, re.I):
        off = _abs(base, m, 0)
        col.add("F_will", "future", off, len(m.group(0)), tlink="AFTER",
                confidence=0.8, rationale="contracted 'll projects an event after the moment of speaking")

    for v in C.PREDICT_PRED:
        for m in re.finditer(r"\b" + re.escape(v) + r"\b", s, re.I):
            off = _abs(base, m, 0)
            col.add("F_prediction", "future", off, len(v), tlink="AFTER",
                    confidence=0.65, rationale="prediction/promise speech act foreshadows a later event")

    # 'would + V' inside reported speech reads as a future-in-the-past prediction
    if ('"' in s) or ('\u201c' in s):
        for m in re.finditer(r"\bwould\b\s+(?!have\b)([A-Za-z]+)", s, re.I):
            off = _abs(base, m, 0)
            col.add("F_would_prediction", "future", off, len(m.group(0)), tlink="AFTER",
                    confidence=0.45, cue_type="inferred",
                    rationale="'would + V' in dialogue is a prediction about a later event")

    # ---------------------------------------------------------------- IMAGINARY
    # modal + base verb (not 'have' -> that's the counterfactual above); evidential guard applies
    for m in re.finditer(r"\b(may|might|could|would|can|must|should)\b\s+(?!have\b)([A-Za-z]+)", s, re.I):
        rel = m.start(0)
        if _reported_context(s, rel):
            continue  # EVIDENTIAL guard: reported content, not a genuine modal branch
        off = _abs(base, m, 0)
        mod = m.group(1).lower()
        force = ("ability" if mod in ("can", "could") else
                 "obligation" if mod in ("must", "should") else
                 "possibility" if mod in ("may", "might") else "hypothetical")
        col.add("I_modal", "imaginary", off, len(m.group(0)), slink="MODAL",
                confidence=0.6, modal_force=force,
                rationale="modal verb places the event in the unreal / possible zone")

    # conditional
    for m in re.finditer(r"\b(if|unless)\b", s, re.I):
        off = _abs(base, m, 0)
        col.add("I_conditional", "imaginary", off, len(m.group(1)), slink="CONDITIONAL",
                later=_matrix_after(events, off), confidence=0.7, modal_force="conditional",
                rationale="conditional marker introduces a branch that depends on a condition")

    # desire / intention / fear (a wished, planned, or feared event)
    for v in C.DESIRE_PRED:
        for m in re.finditer(r"\b" + re.escape(v) + r"\b\s+(?:to\s+([A-Za-z]+)|that\b)", s, re.I):
            off = _abs(base, m, 0)
            force = ("wish" if v in ("wished", "wish", "hoped", "hope", "longed") else
                     "fear" if v in ("feared", "fear", "afraid") else "plan")
            col.add("I_desire", "imaginary", off, len(m.group(0)), slink="MODAL",
                    confidence=0.6, modal_force=force,
                    rationale="desire/intention/fear predicate introduces a non-actual event")

    # factive predicate ('realised that ...')
    for v in C.FACTIVE_PRED:
        for m in re.finditer(r"\b" + re.escape(v) + r"\b\s+that\b", s, re.I):
            off = _abs(base, m, 0)
            col.add("I_factive", "imaginary", off, len(m.group(0)), slink="FACTIVE",
                    confidence=0.55, modal_force="factive",
                    rationale="factive predicate presupposes the truth of its complement")

    # habitual / iterative / generic
    for h in C.HABITUAL:
        for m in re.finditer(r"\b" + re.escape(h) + r"\b", s, re.I):
            off = _abs(base, m, 0)
            col.add("I_habitual", "imaginary", off, len(h), slink="MODAL",
                    confidence=0.5, modal_force="generic",
                    rationale="habitual/iterative marker: a generic, non-single event")

    return col.out
