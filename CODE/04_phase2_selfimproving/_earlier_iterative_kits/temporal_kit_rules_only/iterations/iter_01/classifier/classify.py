#!/usr/bin/env python3
"""
Temporal-relation classifier (TimeML).

Reads a story's event-pair file and writes one relation per pair:
    python classifier/classify.py <input_pairs.json> <output_predictions.json>

Input  pair: {"pair_id":N, "e1":{"word","off"}, "e2":{"word","off"}}
Output item: {"pair_id":N, "relation":"LABEL"}

IMPORTANT: at test time the pairs carry NO tense field and we have no access to the
story text. So everything must be inferred from the `word` strings (which are also
truncated: the final character is stripped, e.g. "said"->"sai", "floated"->"floate",
"went"->"wen") plus the character offsets / text order of e1 and e2.
"""
import sys, json, re


# ----------------------------------------------------------------------------
# Tense / aspect inference from the raw `word` string.
# ----------------------------------------------------------------------------
def infer_tense(word):
    w = word.strip()
    low = w.lstrip('"\'').strip().lower()

    # Quoted speech / long spans carry no verb tense of their own.
    if w.startswith('"'):
        return "NONE"

    # FUTURE: will / shall / 'll / shan't
    if ("'ll" in low or low.startswith("will") or " will " in low
            or low.startswith("shall") or "shan't" in low or low.startswith("shan")):
        return "FUTURE"

    # INFINITIVE: "to X"
    if low.startswith("to "):
        return "INFINITIVE"

    # Present participle / perfect participle gerund: "having ...", "...ing"(->"...in")
    if low.startswith("having"):
        return "PRESPART"

    # Very long spans -> treat as untensed content (quote-like).
    if len(low.split()) > 6:
        return "NONE"

    toks = re.findall(r"[a-z']+", low)
    if not toks:
        return "NONE"

    # Gerund: token ends in "in" (the "g" of "-ing" was truncated).
    if any(t.endswith("in") and len(t) >= 4 for t in toks):
        # but not future contractions
        return "PRESPART"

    # Past perfect / past: "had X", or token ending in -e (truncated -ed) /
    # known irregular pasts.
    if "had" in toks:
        return "PAST"

    return "PAST"  # default; precise tense is not load-bearing for the rules below


# ----------------------------------------------------------------------------
# Token / stem helpers.
# ----------------------------------------------------------------------------
AUX = {"to", "i", "you", "he", "she", "it", "we", "they", "do", "did", "didn",
       "had", "has", "have", "was", "were", "is", "are", "will", "shall",
       "my", "your", "his", "her", "the", "a", "an", "that", "just", "on",
       "of", "out", "up", "off", "down", "back", "in", "no", "not", "never",
       "ll", "s", "t", "ve", "m", "re", "there", "here", "and", "but", "so"}

BLOCK_STEM = {"there", "here"}  # existential "there's" repeats are NOT identity


def content_tokens(word):
    low = word.strip().strip('"').lower()
    toks = re.findall(r"[a-z]+", low)
    return [t for t in toks if t not in AUX]


def tokens_match(a, b):
    """Do two single tokens refer to the same (truncated) lemma?"""
    if a in BLOCK_STEM or b in BLOCK_STEM:
        return False
    if a == b:
        return True
    short, long_ = (a, b) if len(a) <= len(b) else (b, a)
    # one a prefix of the other, with the shorter at least 3 chars
    if len(short) >= 3 and long_.startswith(short):
        return True
    # both reasonably long and share a 4-char prefix
    if len(a) >= 4 and len(b) >= 4 and a[:4] == b[:4]:
        return True
    return False


def same_event(w1, w2):
    """IDENTITY heuristic: the two mentions share a content lemma."""
    t1 = content_tokens(w1)
    t2 = content_tokens(w2)
    for a in t1:
        for b in t2:
            if tokens_match(a, b):
                return True
    return False


# Speech / reporting lemmas (truncated forms accounted for via prefix match).
SPEECH_PREFIXES = ("said", "sai", "say", "call", "cri", "cry", "repl", "answ",
                   "repe", "ask", "tol", "tel", "spok", "spea", "shout",
                   "exclaim", "whisper", "cried")


def is_speech(word):
    w = word.strip()
    if w.startswith('"'):
        return True  # quoted utterance content
    for t in content_tokens(word):
        for p in SPEECH_PREFIXES:
            if t.startswith(p) or p.startswith(t) and len(t) >= 3:
                return True
    return False


# ----------------------------------------------------------------------------
# Main relation rule.
# ----------------------------------------------------------------------------
def classify_pair(e1, e2):
    w1, w2 = e1["word"], e2["word"]
    o1, o2 = e1.get("off", 0), e2.get("off", 0)
    t1, t2 = infer_tense(w1), infer_tense(w2)

    # 1) Conjoined infinitive list at the same offset ("to eat, and drink, and live")
    #    -> the sub-events are SIMULTANEOUS.
    if o1 == o2 and t1 == "INFINITIVE" and t2 == "INFINITIVE":
        return "SIMULTANEOUS"

    # 2) IDENTITY: the two mentions refer to the same event (shared lemma).
    if same_event(w1, w2):
        return "IDENTITY"

    # 3) AFTER: e2 is a perfect participle ("having fed ...") -> the prior event,
    #    so e1 happens AFTER e2.
    if t2 == "PRESPART" and w2.strip().lower().startswith("having"):
        return "AFTER"

    # 4) Reversed text order: object precedes subject -> AFTER.
    if o2 < o1:
        return "AFTER"

    # 5) IBEFORE: one utterance/report immediately followed by another
    #    (both events are speech / reporting / quoted content).
    if is_speech(w1) and is_speech(w2):
        return "IBEFORE"

    # 6) Default: chronological narrative order.
    return "BEFORE"


def main():
    if len(sys.argv) != 3:
        print("usage: classify.py <input_pairs.json> <output_predictions.json>")
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        pairs = json.load(f)
    out = [{"pair_id": p["pair_id"], "relation": classify_pair(p["e1"], p["e2"])}
           for p in pairs]
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
