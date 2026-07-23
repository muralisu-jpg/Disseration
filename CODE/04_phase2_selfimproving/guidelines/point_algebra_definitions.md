# Point-algebra definitions of TimeML temporal relations (TLEX, Ocal/Xie/Finlayson, Table 1)
Each event is an interval with a START point and an END point. E1 rel E2:

- BEFORE:        E1.end  <  E2.start   (E1 finishes strictly before E2 begins)
- IBEFORE:       E1.end  =  E2.start   (E1 ends exactly as E2 begins; immediate sequence)
- AFTER:         E1.start >  E2.end    (E1 begins strictly after E2 finishes)
- IAFTER:        E1.start =  E2.end    (E1 begins exactly as E2 ends)
- SIMULTANEOUS:  E1.start = E2.start AND E1.end = E2.end (same span)
- IDENTITY:      SIMULTANEOUS and the SAME event (a re-mention/coreferent description)
- INCLUDES:      E1.start < E2.start AND E1.end > E2.end (E2 happens inside E1)
- IS_INCLUDED:   E1.start > E2.start AND E1.end < E2.end (E1 happens inside E2)
- DURING:        E1 holds throughout E2 (stative E1 contained by/coextensive with E2)
- DURING_INV:    inverse of DURING
- BEGINS:        E1.start = E2.start AND E1.end < E2.end (E1 is the beginning phase of E2)
- BEGUN_BY:      inverse of BEGINS
- ENDS:          E1.end = E2.end AND E1.start > E2.start (E1 is the final phase of E2)
- ENDED_BY:      inverse of ENDS

Decision procedure: first fix the order of the two STARTs, then the two ENDs,
then match to exactly one definition. If E1 and E2 are the same real-world event
mentioned twice, the relation is IDENTITY, not SIMULTANEOUS.
