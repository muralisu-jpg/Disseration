"""Shared helpers for the non-iconicity pipeline.

Deterministic, self-contained: no answer key, no network at inference time
(NLTK data is fetched once on first run), no story-specific content.
"""
import re

# ----------------------------------------------------------------------------- NLTK bootstrap
_READY = False
def ensure_nltk():
    global _READY
    if _READY:
        return
    import nltk
    needed = [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("taggers/averaged_perceptron_tagger", "averaged_perceptron_tagger"),
        ("taggers/averaged_perceptron_tagger_eng", "averaged_perceptron_tagger_eng"),
    ]
    for path, pkg in needed:
        try:
            nltk.data.find(path)
        except LookupError:
            try:
                nltk.download(pkg, quiet=True)
            except Exception:
                pass
    _READY = True


def sentences_with_offsets(text):
    """Split into sentences, keeping absolute character offsets."""
    ensure_nltk()
    from nltk.tokenize import PunktSentenceTokenizer
    tok = PunktSentenceTokenizer()
    out = []
    for i, (s, e) in enumerate(tok.span_tokenize(text)):
        out.append({"sent_id": i, "start": s, "end": e, "text": text[s:e]})
    return out


def pos_tokens(sent_text, base_off):
    """Return [(token, POS_tag, absolute_offset), ...] for one sentence."""
    ensure_nltk()
    from nltk.tokenize import TreebankWordTokenizer
    from nltk import pos_tag
    tw = TreebankWordTokenizer()
    spans = list(tw.span_tokenize(sent_text))
    toks = [sent_text[s:e] for s, e in spans]
    tags = pos_tag(toks) if toks else []
    return [(toks[i], tags[i][1], base_off + spans[i][0]) for i in range(len(toks))]


# ----------------------------------------------------------------------------- lexicons
MODALS        = {"will", "shall", "would", "could", "might", "may", "must", "should", "can"}
HAVE          = {"have", "has", "had"}
BE            = {"be", "is", "are", "was", "were", "been", "being", "am"}
REPORTING     = {"said", "say", "says", "tell", "told", "ask", "asked", "reply", "replied",
                 "answer", "answered", "cry", "cried", "call", "called", "shout", "shouted",
                 "exclaim", "exclaimed", "add", "added", "speak", "spoke", "whisper", "whispered"}
PERCEPTION    = {"saw", "see", "sees", "watched", "watch", "heard", "hear", "found", "find",
                 "noticed", "notice", "felt", "observed"}
FACTIVE_PRED  = {"realized", "realised", "knew", "know", "discovered", "noticed", "forgot",
                 "forgotten", "regretted", "remembered", "recalled", "understood"}
DESIRE_PRED   = {"wanted", "want", "wished", "wish", "hoped", "hope", "intended", "intend",
                 "decided", "decide", "planned", "plan", "tried", "try", "longed", "meant",
                 "feared", "fear", "afraid", "hoped"}
PREDICT_PRED  = {"promised", "promise", "vowed", "vow", "predicted", "predict", "foretold",
                 "foretell", "warned", "warn", "threatened", "threaten", "swore", "swear"}
RETRO_ADV     = ["earlier", "beforehand", "previously", "already", "long ago", "formerly",
                 "by then", "the day before", "once upon a time", "in the old days"]
SUBORD_BEFORE = ["after", "once", "as soon as", "by the time"]
SIMUL_CONJ    = ["while", "meanwhile", "at the same time", "all the while", "even as",
                 "as long as", "during which"]
HABITUAL      = ["used to", "would often", "each time", "every time", "whenever",
                 "day after day", "again and again"]

# irregular past participles (for "had/have + PP" detection)
IRREG_PP = {
    "been","gone","done","seen","taken","given","eaten","known","grown","thrown","drawn",
    "flown","written","ridden","broken","spoken","stolen","frozen","chosen","fallen","run",
    "come","become","begun","sung","swum","won","found","told","sold","held","brought",
    "bought","caught","taught","thought","fought","sought","made","said","laid","paid","met",
    "set","put","cut","let","read","lost","left","kept","slept","felt","dealt","meant","sent",
    "spent","built","lit","hit","hurt","gotten","got","stood","understood","bound","wound",
    "ground","struck","stuck","dug","hung","swung","flung","clung","stung","shot","lain",
    "gnawed","forgotten","hidden","bitten","beaten","driven","risen","shaken","worn","torn",
    "sworn","born","drunk","rung","sunk","shrunk","sat","slain","wept","crept","bred","fed","led",
}
_PP_SUFFIX = re.compile(r"(ed|en|wn|ne|ought|aught|ung|own|unk|ept|elt)$", re.I)

def is_participle(word):
    w = word.lower()
    return w in IRREG_PP or bool(_PP_SUFFIX.search(w))


# ----------------------------------------------------------------------------- references
def ref(text, off, length, construction):
    """A lightweight event reference: verbatim trigger + absolute offset."""
    return {"trigger": text[off:off + length], "off": off, "construction": construction}

def ref_from_event(e):
    return {"trigger": e["text"], "off": e["off"], "construction": "matrix verb"}

def nearest_verb_after(events, off):
    cand = [e for e in events if e["off"] >= off]
    return cand[0] if cand else None

def nearest_verb_before(events, off):
    cand = [e for e in events if e["off"] < off]
    return cand[-1] if cand else None

def line_of(text, off):
    return text.count("\n", 0, off) + 1

# ----------------------------------------------------------------------------- merged rule lexicons
# EVIDENTIAL guard: a complement governed by one of these is reported speech, never imaginary.
SAY_PERCEIVE = {"said","say","says","tell","tells","told","ask","asks","asked","answer","answers",
                "answered","reply","replies","replied","cry","cries","cried","shout","shouted",
                "call","called","speak","spoke","exclaimed","whispered","remarked","added","began",
                "saw","see","sees","hear","hears","heard"}
WISH_VERBS  = {"want","wants","wanted","wish","wishes","wished","hope","hopes","hoped","long",
               "longed","desire","desired","crave","craved"}
PLAN_VERBS  = {"intend","intended","plan","planned","mean","meant","decide","decided","resolve",
               "resolved","prepare","prepared"}
MENTAL_IRR  = {"dreamed","dreamt","imagined","wished","supposed","believed","thought","fancied"}
PRETENCE    = {"pretended","feigned"}
DISCOVERY   = {"saw","found","met","noticed","discovered","heard","spied","beheld","espied",
               "perceived","came upon"}
STATIVE_PART = {"lying","sitting","sleeping","waiting","weeping","standing","hanging","kneeling",
                "crying","burning","resting","asleep","seated","wandering","sobbing","bound","tied","dead"}
STATIVE_FIN  = {"sat","stood","lay","slept","wept","knelt","hung","rested","waited","watched","gazed","listened"}
