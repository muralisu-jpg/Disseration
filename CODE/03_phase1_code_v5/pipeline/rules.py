"""Step 3 -- the deciding step (consolidated best-of rule set).

This merges the strongest *general* rules from the prior rule sets into one engine --
  past      P1..P10   (had+PP, having+PP fan-out, adverbials, modal-perfect, reported
                       pasts, after/from + V-ing, present-perfect-in-dialogue, discovery+stative)
  present   R1..R5    (while, temporal as, reduplication, until, co-occurring statives)
  future    F1..F6    (will/shall/going-to, imperative, prediction verbs, prospective
                       aspect, expectation/desire, if...will)
  imaginary I1..I8    (mental-state, optative, conditional, pretence, modal-perfect,
                       embedded narration, modal + base, desire/fear) with the EVIDENTIAL guard.

No story-specific phrases are hard-coded: every rule is a general construction.
Each prediction carries: rule, track, tlink/slink, earlier/later, cue_type, confidence,
rationale, modal_force.
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
    """EVIDENTIAL guard: True if a say/perceive verb precedes with a quote or 'that' between."""
    pre = sent_text[:rel_off].lower()
    last = max((pre.rfind(rv) for rv in C.SAY_PERCEIVE
                if re.search(r"\b" + re.escape(rv) + r"\b", pre)), default=-1)
    if last < 0:
        return False
    seg = sent_text[last:rel_off]
    return ('"' in seg) or ('\u201c' in seg) or (" that " in seg.lower())


class Collector:
    def __init__(self, full_text):
        self.t = full_text
        self.out = []
    def add(self, rule, track, off, length, tlink=None, slink=None, earlier=None, later=None,
            cue_type="explicit_marker", confidence=0.6, rationale="", modal_force=None):
        self.out.append({
            "rule": rule, "track": track, "tlink": tlink, "slink": slink,
            "earlier": earlier or C.ref(self.t, off, length, rule), "later": later,
            "cue_type": cue_type, "confidence": round(confidence, 2),
            "rationale": rationale, "modal_force": modal_force,
        })


def run_sentence(full_text, sent, events):
    s = sent["text"]
    base = sent["start"]
    col = Collector(full_text)
    has_past = any(e["tense"] == "past" for e in events)
    quote_spans = [(mm.start(), mm.end()) for mm in re.finditer(r'"[^"]*"', s)]
    in_quote = lambda p: any(a <= p <= b for a, b in quote_spans)

    # POS context for the sentence (lets participle rules consult the tagger instead of
    # a loose suffix, and lets the absolute/adjunct rules see surrounding tags).
    toks = C.pos_tokens(s, base)
    vbn_off = {o for _, tag, o in toks if tag == "VBN"}

    def pp_ok(word, abs_off):
        """A real past participle: POS-confirmed VBN, or a member of the closed
        irregular list. Rejects loose suffix hits like 'seven'/'often'/'golden'."""
        return abs_off in vbn_off or word.lower() in C.IRREG_PP

    # ============================================================ PAST
    # P1 had + PP   (P9 if a relative pronoun precedes 'had')
    for m in re.finditer(r"\bhad\b\s+((?:not|never|already|just|long|soon)\s+){0,2}([A-Za-z]+)", s, re.I):
        if pp_ok(m.group(2), _abs(base, m, 2)):
            off = _abs(base, m, 0)
            pre = s[max(0, m.start() - 12):m.start()].lower()
            rule = "P9" if re.search(r"\b(who|which|that)\s*$", pre) else "P1"
            col.add(rule, "past", off, len(m.group(0)), tlink="BEFORE",
                    later=_matrix_after(events, off), confidence=0.9,
                    rationale="past perfect (had + participle): completed before the reference past")

    # P2 having + PP  -> attach to the matrix verb of its own clause (nearest after)
    for m in re.finditer(r"\bhaving\b\s+([A-Za-z]+)", s, re.I):
        if pp_ok(m.group(1), _abs(base, m, 1)):
            off = _abs(base, m, 0)
            col.add("P2", "past", off, len(m.group(0)), tlink="BEFORE",
                    later=_matrix_after(events, off), confidence=0.75,
                    rationale="perfect participle ('having + PP') precedes the matrix verb")

    # P3 retrospective adverbials (general -- no corpus idioms)
    if has_past:
        for m in re.finditer(r"\b(long ago|years ago|days? ago|some time ago|previously|formerly|earlier)\b", s, re.I):
            off = _abs(base, m, 0)
            later = _matrix_after(events, off) or _matrix_before(events, off)
            if later is None:        # needs a finite verb to back-date
                continue
            col.add("P3", "past", off, len(m.group(0)), tlink="BEFORE",
                    later=later, confidence=0.6,
                    rationale="retrospective adverbial back-dates the event")

    # P4 would/could/might/should have + PP  (past AND imaginary counterfactual)
    for m in re.finditer(r"\b(would|could|might|should)\s+have\s+([A-Za-z]+)", s, re.I):
        off = _abs(base, m, 0)
        col.add("P4", "past", off, len(m.group(0)), tlink="BEFORE",
                later=_matrix_after(events, off), confidence=0.7,
                rationale="modal-perfect names an unrealised prior event")
        col.add("P4i", "imaginary", off, len(m.group(0)), slink="COUNTER_FACTIVE",
                confidence=0.75, modal_force="counterfactual",
                rationale="'modal + have + PP' is contrary to fact")

    # P5 reported / recalled pasts (inferred, low-confidence -> behind the gate)
    for m in re.finditer(r"\b(dreamed|dreamt|remembered|recalled|overheard)\b(.*?)\bthat\b", s, re.I):
        off = _abs(base, m, 0)
        col.add("P5", "past", off, len(m.group(1)), tlink="BEFORE",
                later=_matrix_after(events, _abs(base, m, 2)), confidence=0.45, cue_type="inferred",
                rationale="recollection/report introduces an event prior to the telling")

    # P6 after + V-ing ; P8 from + V-ing  (need a finite main clause to be anterior to)
    for tag, pat in (("P6", r"\bafter\s+([A-Za-z]+ing)\b"), ("P8", r"\bfrom\s+([A-Za-z]+ing)\b")):
        for m in re.finditer(pat, s, re.I):
            off = _abs(base, m, 0)
            later = _matrix_after(events, off)
            if later is None:
                continue
            col.add(tag, "past", off, len(m.group(0)), tlink="BEFORE",
                    later=later, confidence=0.65,
                    rationale="subordinate -ing clause names an action prior to the main clause")

    # P7 present perfect inside dialogue
    for m in re.finditer(r"\b(have|has|hath)\s+([A-Za-z]+)\b", s, re.I):
        if in_quote(m.start()) and pp_ok(m.group(2), _abs(base, m, 2)):
            off = _abs(base, m, 0)
            col.add("P7", "past", off, len(m.group(0)), tlink="BEFORE",
                    later=_matrix_after(events, off), confidence=0.65,
                    rationale="present perfect in dialogue points back from speech time")

    # P10 discovery verb + pre-existing stative (inferred)
    disc = r"(saw|found|met|noticed|discovered|heard|beheld|spied)"
    stat = r"(" + "|".join(sorted(C.STATIVE_PART)) + r")"
    for m in re.finditer(disc + r"\b(.{0,60}?)\b" + stat + r"\b", s, re.I):
        off = _abs(base, m, 3)
        col.add("P10", "past", off, len(m.group(3)), tlink="BEFORE",
                later=C.ref(full_text, _abs(base, m, 1), len(m.group(1)), "discovery verb"),
                confidence=0.45, cue_type="inferred",
                rationale="the state pre-exists the moment it is discovered")

    # P11 preposed / absolute participial clause ("the work done, he left"; "his sword drawn, he charged"):
    # a participle whose clause holds only a noun phrase before it (no subject pronoun / finite verb)
    # and a comma after it heads an adjunct that names a prior action.
    NP_ONLY = {"DT", "NN", "NNS", "NNP", "NNPS", "JJ", "PRP$", "CC", "POS"}
    for i, (w, tag, off) in enumerate(toks):
        if tag != "VBN":
            continue
        # tokens from the last clause boundary up to this participle
        b = i - 1
        while b >= 0 and toks[b][0] not in (",", ";", ".", ":", "—"):
            b -= 1
        clause_before = toks[b + 1:i]
        if any(t[0].lower() in C.HAVE or t[0].lower() in C.BE or t[0].lower() in C.MODALS
               for t in clause_before):
            continue  # periphrastic verb -> covered by P1/P4/P7
        if any(t[1] not in NP_ONLY for t in clause_before):
            continue  # a non-NP token (pronoun subject, finite verb...) -> not an absolute clause
        ci = next((j for j in range(i + 1, min(len(toks), i + 4)) if toks[j][0] == ","), None)
        if ci is None or ci + 1 >= len(toks):
            continue  # absolute clause closes with a comma
        if toks[ci + 1][1] != "PRP":
            continue  # a true absolute is followed by an independent clause with its own subject
        later = _matrix_after(events, off)
        if later is None:
            continue
        col.add("P11", "past", off, len(w), tlink="BEFORE", later=later,
                confidence=0.55, cue_type="inferred",
                rationale="preposed/absolute participial clause names an action prior to the main clause")

    # ============================================================ PRESENT
    for tag, pat, why in (
        ("R1", r"\bwhile\b", "'while' marks co-temporal events"),
        ("R2", r"\bas\s+(?:he|she|they|it|the|i|we|you)\b", "temporal 'as' marks overlap"),
        ("R4", r"\buntil\b", "'until' bounds a co-temporal span"),
    ):
        for m in re.finditer(pat, s, re.I):
            off = _abs(base, m, 0)
            earlier, later = _matrix_before(events, off), _matrix_after(events, off)
            if earlier is None or later is None:
                continue  # need a verb on each side -> two events that actually overlap
            col.add(tag, "present", off, len(m.group(0)), tlink="SIMULTANEOUS",
                    earlier=earlier, later=later,
                    confidence=0.75, rationale=why)

    # R3 reduplication = one extended event
    for m in re.finditer(r"\b(\w+?)(ed|ing)\s+(?:and\s+|or\s+)?\1\2\b", s, re.I):
        off = _abs(base, m, 0)
        col.add("R3", "present", off, len(m.group(0)), tlink="SIMULTANEOUS",
                confidence=0.6, rationale="reduplicated verb describes one extended event")

    # R5 co-occurring statives (inferred)
    statives = [e for e in events if e["text"].lower() in C.STATIVE_FIN
                or e["text"].lower() in C.STATIVE_PART]
    if len(statives) >= 2:
        a, b = statives[0], statives[1]
        col.add("R5", "present", a["off"], len(a["text"]), tlink="SIMULTANEOUS",
                earlier=C.ref_from_event(a), later=C.ref_from_event(b),
                confidence=0.45, cue_type="inferred", rationale="co-occurring statives overlap")

    # R6 depictive / manner -ing adjunct: "she sang, weaving a cloth" -- the -ing event
    # runs simultaneously with its matrix verb (Allen DURING/overlaps). A bare present
    # participle, not under be/aux and not governed by a subordinator that re-times it.
    _RETIME = {"after", "before", "from", "by", "on", "upon", "in", "of", "since", "without", "while", "when"}
    for i, (w, tag, off) in enumerate(toks):
        if tag != "VBG":
            continue
        prev2 = [toks[j][0].lower() for j in range(max(0, i - 2), i)]
        if any(a in C.BE or a in C.HAVE for a in prev2):
            continue  # progressive / perfect-progressive, not an adjunct
        if prev2 and prev2[-1] in _RETIME:
            continue  # subordinator re-times the clause (handled elsewhere / not overlap)
        clause_start_comma = i > 0 and toks[i - 1][0] == ","
        earlier = _matrix_before(events, off)
        later = _matrix_after([e for e in events if e["off"] > off and not e["is_aux"]], off)
        matrix = earlier or later
        if matrix is None or not clause_start_comma:
            continue  # require the adjunct comma so we only take clear depictive/manner uses
        col.add("R6", "present", off, len(w), tlink="SIMULTANEOUS",
                earlier=matrix, later=C.ref(full_text, off, len(w), "ing-adjunct"),
                confidence=0.55, cue_type="inferred",
                rationale="a participial (-ing) adjunct runs simultaneously with its matrix verb")

    # R7 durative/stative includes a punctual event within one clause: a stative finite verb
    # plus a punctual (past/present) event sharing the clause -> the punctual falls inside the state.
    clause_bounds = [0] + [j for j, t in enumerate(toks) if t[0] in (",", ";", ":", ".")] + [len(toks)]
    for a0, a1 in zip(clause_bounds, clause_bounds[1:]):
        span = toks[a0:a1]
        stat = next(((w, o) for w, tg, o in span if w.lower() in C.STATIVE_FIN), None)
        if not stat:
            continue
        punct = next(((w, o) for w, tg, o in span
                      if tg in ("VBD", "VBZ", "VBP") and w.lower() not in C.STATIVE_FIN
                      and w.lower() not in C.BE and w.lower() not in C.HAVE), None)
        if not punct:
            continue
        col.add("R7", "present", stat[1], len(stat[0]), tlink="SIMULTANEOUS",
                earlier=C.ref(full_text, stat[1], len(stat[0]), "stative"),
                later=C.ref(full_text, punct[1], len(punct[0]), "punctual"),
                confidence=0.45, cue_type="inferred",
                rationale="a durative state includes a punctual event told within the same clause")

    # ============================================================ FUTURE
    for m in re.finditer(r"\b(will|shall|'ll)\s+([A-Za-z]+)\b|\bgoing to\s+([A-Za-z]+)\b", s, re.I):
        off = _abs(base, m, 0)
        col.add("F1", "future", off, len(m.group(0)), tlink="AFTER",
                confidence=0.8, rationale="future auxiliary projects a not-yet event")

    # F2 imperative WITH fulfilment: a sentence-initial bare verb is a command, but it counts
    # as told-before-it-happens only when that act is actually carried out later in the text.
    first = next((e for e in events if not e["is_aux"]), None)
    if (first and first["tag"] == "VB" and (first["off"] - base) <= 2
            and not s.rstrip().endswith("?")):
        stem = re.sub(r"(e|ed|ing|s)$", "", first["text"].lower())
        fulfilled = len(stem) >= 3 and re.search(
            r"\b" + re.escape(stem) + r"(?:e|ed|es|ing|s)?\b",
            full_text[sent["end"]:], re.I)
        if fulfilled:
            col.add("F2", "future", first["off"], len(first["text"]), tlink="AFTER",
                    later=C.ref(full_text, fulfilled.start() + sent["end"], len(fulfilled.group(0)), "fulfilment"),
                    confidence=0.6, cue_type="inferred",
                    rationale="imperative whose commanded act is carried out later in the text")

    for m in re.finditer(r"\b(predicted|foretold|prophesied|promised|swore|vowed|warned|threatened)\b", s, re.I):
        off = _abs(base, m, 0)
        col.add("F3", "future", off, len(m.group(0)), tlink="AFTER",
                later=_matrix_after(events, off), confidence=0.65,
                rationale="prediction/promise speech act foretells a later event")

    for m in re.finditer(r"\b(?:was|were)\s+about to\s+([A-Za-z]+)|\b(?:set out to|meant to|intended to)\s+([A-Za-z]+)", s, re.I):
        off = _abs(base, m, 0)
        col.add("F4", "future", off, len(m.group(0)), tlink="AFTER",
                confidence=0.55, rationale="prospective aspect names an imminent action")

    for m in re.finditer(r"\b(awaited|expected|longed to|wanted to|hoped|wished to)\b", s, re.I):
        off = _abs(base, m, 0)
        col.add("F5", "future", off, len(m.group(0)), tlink="AFTER",
                confidence=0.5, rationale="expectation/desire projects a wished or feared future")

    for m in re.finditer(r"\bif\b[^.!?]*?\b(will|shall|'ll)\b", s, re.I):
        off = _abs(base, m, 0)
        col.add("F6", "future", off, min(len(m.group(0)), 80), tlink="AFTER",
                confidence=0.55, rationale="open conditional projects a contingent future")

    # ============================================================ IMAGINARY  (EVIDENTIAL guard applies)
    for m in re.finditer(r"\b(dreamed|dreamt|imagined|wished|supposed|believed|thought|fancied)\b(.*?)\bthat\b", s, re.I):
        if _reported_context(s, m.start()):
            continue
        off = _abs(base, m, 0)
        v = m.group(1).lower()
        force = ("imagined" if v in ("dreamed", "dreamt", "imagined", "fancied")
                 else "wish" if v == "wished" else "belief")
        col.add("I1", "imaginary", off, len(m.group(1)), slink="MODAL",
                later=_matrix_after(events, _abs(base, m, 2)), confidence=0.65, modal_force=force,
                rationale="a mental-state verb opens an irrealis sub-world")

    for m in re.finditer(r"\b(would that|if only|i wish)\b", s, re.I):
        off = _abs(base, m, 0)
        col.add("I2", "imaginary", off, len(m.group(0)), slink="MODAL",
                confidence=0.65, modal_force="wish", rationale="optative marks a wished, unreal state")

    for m in re.finditer(r"\b(if|unless)\b", s, re.I):
        off = _abs(base, m, 0)
        col.add("I3", "imaginary", off, len(m.group(1)), slink="CONDITIONAL",
                later=_matrix_after(events, off), confidence=0.7, modal_force="conditional",
                rationale="a conditional marker opens a hypothetical sub-timeline")

    for m in re.finditer(r"\b(pretended|feigned|made believe)\b", s, re.I):
        off = _abs(base, m, 0)
        col.add("I4", "imaginary", off, len(m.group(0)), slink="COUNTER_FACTIVE",
                confidence=0.7, modal_force="counterfactual",
                rationale="a pretence verb marks a false/counterfactual state")

    for m in re.finditer(r"\b(could|might|may|must)\s+have\b", s, re.I):
        off = _abs(base, m, 0)
        col.add("I5", "imaginary", off, len(m.group(0)), slink="MODAL",
                confidence=0.6, modal_force="possibility", rationale="epistemic modal-perfect is irrealis")

    for m in re.finditer(r"\b(told|related|recounted|narrated)\b[^.!?]*?\b(story|tale|how (?:he|she|they|it))\b", s, re.I):
        off = _abs(base, m, 0)
        col.add("I6", "imaginary", off, min(len(m.group(0)), 80), slink="MODAL",
                confidence=0.55, modal_force="embedded", rationale="an embedded story runs on its own sub-timeline")

    _FREQ = {"often", "always", "sometimes", "usually", "ever", "never", "occasionally",
             "regularly", "repeatedly", "constantly", "sooner", "rather"}
    for m in re.finditer(r"\b(may|might|could|would|can|must|should)\b\s+(?!have\b)([A-Za-z]+)", s, re.I):
        if _reported_context(s, m.start()):
            continue
        mod = m.group(1).lower()
        if mod == "would" and m.group(2).lower() in _FREQ:
            continue  # habitual 'would often ...' is not predictive -> handled by I9
        off = _abs(base, m, 0)
        force = ("ability" if mod in ("can", "could") else
                 "obligation" if mod in ("must", "should") else
                 "possibility" if mod in ("may", "might") else "hypothetical")
        col.add("I7", "imaginary", off, len(m.group(0)), slink="MODAL",
                confidence=0.55, modal_force=force,
                rationale="a modal verb places the event in the unreal/possible zone")

    for v in (C.WISH_VERBS | C.PLAN_VERBS | {"feared", "fear", "afraid"}):
        for m in re.finditer(r"\b" + re.escape(v) + r"\b\s+(?:to\s+[A-Za-z]+|that\b)", s, re.I):
            off = _abs(base, m, 0)
            force = ("wish" if v in C.WISH_VERBS else "fear" if v in ("feared", "fear", "afraid") else "plan")
            col.add("I8", "imaginary", off, len(m.group(0)), slink="MODAL",
                    confidence=0.6, modal_force=force,
                    rationale="a desire/intention/fear predicate introduces a non-actual event")

    # I9 habitual / iterative / generic: a recurring event has no single place on the timeline.
    for m in re.finditer(r"\b(used to|would\s+(?:often|always|sometimes|usually)|each time|every "
                         r"time|whenever|day after day|night after night|again and again|"
                         r"over and over|time and again)\b", s, re.I):
        if _reported_context(s, m.start()):
            continue
        off = _abs(base, m, 0)
        col.add("I9", "imaginary", off, len(m.group(0)), slink="MODAL",
                later=_matrix_after(events, off), confidence=0.6, modal_force="habitual",
                rationale="a habitual/iterative marker describes a generic, non-singular event")

    # I10 negation of occurrence: an event explicitly said not to happen is only on a counterfactual
    # branch ("never did X", "without V-ing", "failed to V", "no longer V").
    for m in re.finditer(r"\bnever\s+([A-Za-z]+ed|[A-Za-z]+)\b|\bwithout\s+([A-Za-z]+ing)\b|"
                         r"\bfailed to\s+([A-Za-z]+)\b|\bno longer\s+([A-Za-z]+)\b", s, re.I):
        if _reported_context(s, m.start()):
            continue
        off = _abs(base, m, 0)
        col.add("I10", "imaginary", off, len(m.group(0)), slink="COUNTER_FACTIVE",
                confidence=0.6, modal_force="averted",
                rationale="an event under negation of occurrence stays on a non-actual branch")

    return col.out
