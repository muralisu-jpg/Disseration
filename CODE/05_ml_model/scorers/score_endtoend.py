"""
End-to-end chain scorer. Matches predicted (pair->relation) to gold by WORD PAIR
(order-independent, case-insensitive) — no offsets needed. Gives the real compounding number:
of all gold pair->relation facts, how many did the full chain recover from raw story text.
"""
from collections import Counter
FOURWAY={"BEFORE":"before","IBEFORE":"before","AFTER":"after","IAFTER":"after",
         "MODAL":"imaginary","CONDITIONAL":"imaginary","COUNTER_FACTIVE":"imaginary"}
def to4(l): return FOURWAY.get((l or "").upper(),"overlap")

def wp(w1, w2):
    """order-independent word-pair key, lowercased, first token of each word."""
    a=(w1 or "").lower().split()[0] if (w1 or "").strip() else ""
    b=(w2 or "").lower().split()[0] if (w2 or "").strip() else ""
    return frozenset((a,b))

def score_chain(pred_pairs, pred_relations, gold_pairs, gold_relations):
    """
    pred_pairs: [{e1_word,e2_word, key?}]  pred_relations: {key: LABEL}
    gold_pairs: [{e1_word,e2_word,e1_off,e2_off}]  gold_relations: {offkey: LABEL}
    Returns end-to-end pairing + relation recovery, matched by word-pair.
    """
    # gold: word-pair -> gold relation
    gold_by_wp = {}
    for g in gold_pairs:
        offkey=f'{g["e1_off"]}_{g["e2_off"]}'
        gold_by_wp[wp(g["e1_word"],g["e2_word"])] = gold_relations.get(offkey)
    gold_wps=set(gold_by_wp)
    # pred: word-pair -> pred relation
    pred_by_wp={}
    for p in pred_pairs:
        key=p.get("key") or f'{p.get("e1_off","")}_{p.get("e2_off","")}'
        # relations may be keyed by idx or offset; try to look up by the pair's own key
        rel = pred_relations.get(key) or pred_relations.get(f'{p.get("e1_idx","")}_{p.get("e2_idx","")}')
        pred_by_wp[wp(p["e1_word"],p["e2_word"])] = rel
    pred_wps=set(pred_by_wp)

    # PAIRING (did the chain find the right links?)
    tp=len(gold_wps & pred_wps); fp=len(pred_wps-gold_wps); fn=len(gold_wps-pred_wps)
    P=tp/(tp+fp) if tp+fp else 0; R=tp/(tp+fn) if tp+fn else 0
    pairF=2*P*R/(P+R) if P+R else 0

    # END-TO-END RELATION: of gold pairs the chain also found, how many relations right?
    matched=gold_wps & pred_wps
    rel_correct_4=sum(1 for k in matched if to4(pred_by_wp[k])==to4(gold_by_wp[k]))
    # full end-to-end: correct relation on ALL gold pairs (missed pairs = wrong)
    e2e_4 = rel_correct_4/len(gold_wps) if gold_wps else 0
    # relation accuracy on matched only (isolates relation quality from pairing loss)
    rel_acc_on_matched = rel_correct_4/len(matched) if matched else 0
    return {
      "pairing": {"precision":round(P,4),"recall":round(R,4),"f1":round(pairF,4),
                  "tp":tp,"fp":fp,"fn":fn},
      "end_to_end_4way_accuracy": round(e2e_4,4),   # THE compounding number (raw story -> relation)
      "relation_acc_on_found_pairs": round(rel_acc_on_matched,4),
      "gold_pairs": len(gold_wps), "found_pairs": tp
    }
