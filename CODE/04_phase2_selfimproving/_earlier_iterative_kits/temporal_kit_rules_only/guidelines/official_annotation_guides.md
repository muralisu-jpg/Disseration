# Official ProppLearner annotation guidelines (extracted)

These are the authoritative relation definitions from the corpus's own annotation guides.


## TIME LINKS — relation types (from 03_Time_Links_v2.0.1)

Time Link Annotation Guide
Time Links
Adapted from the “TimeML Annotation Guidelines version 1.2.1” by Roser Saurí et al., 2006.
What is a Time Link?
A time link is a relationship between two times, two events, or an event and a time. It indicates that
a particular relationship in time holds between the two, that, for example, they happen at the same
time (1) or one happens for the duration of the other (2). Other less intuitive examples of time links
between two events include if one event is temporally related to a specific subpart of another event
(3), or imposes a truth-condition on another event (4).
(1) The train [arrived] at (8:10 p.m).
(2) He [was stuck] on that island for (almost a year).
(3) John [started] (to read).
(4) John [forgot] (to buy) some wine.
Here, as in all examples in this guide, the word that signals the time link (if any) is underlined, and
the events or times that participate in the relationship are surrounded by brackets or parentheses.
You will annotate the following items for every time link:
• Link Type – the type of link, either Temporal, Aspectual, or Subordinating
• Relation Type – The specific relation type, which depends on the link type
• Subject – the time or event in the “subject” position of the relationship
• Object – the time or event in the “object” position of the relationship
In addition, some temporal expressions may require additional information
• Signal – is there a word or set of words that specifically signals the relationship?
Link and Relation Type
Each time link needs to be assigned a link type and a relation type. Valid link types are Temporal,
Aspectual, and Subordinating. The link type determines the relation type that may be assigned to
the link.
Temporal
A temporal time link may hold between two events, two times, or an event and a time. This is the
only link type that may hold between a time expression and something else. It indicates a concrete
temporal relationship between two events. Valid relationship types for a temporal link include
Version 2.0.1 / February 8, 2012 1
Time Link Annotation Guide
Before (5), After, Immediately Before, Immediately After (6), Includes (7), Included By, During
(8), Subsumes, Beginning, Begun By (9), Ending, Ended By (10), and Identity (11). These
(5) The police have investigated [the slayings], and suspects already (have been arrested).
(6) They [died] when the plane (crashed) into the mountain.
(7) John [arrived] in Boston (last Thursday).
(8) John [was CTO] for (two years).
(9) John was [in the gym] starting at (6:00pm).
(10) John was [in the gym] until (7:00pm).
(11) John [drove] to Boston. During his (drive) he ate a donut.
Of the 13 temporal relationships, 6 are inverses of another 6, as shown in the left two columns of
Table 1.
Aspectual
An aspectual link holds only between two events. Valid relation types are Initiates, Culminates,
Terminates, Continues, and Reinitiates. If you are familiar with the Event annotation guidelines,
then the subject event (the event that occurs in the “subject” position of the relationship), should be
of the Aspectual event class.
(12) John [started] (to read).
(13) John [finished] (reading).
Subordinating
A subordinating link holds only between two events. Valid relation types are Modal (14), Factive
(15), Counter-Factive (16), Evidential (17), Negative Evidential (18), and Conditional (19). If you
are familiar with the Event annotation guidelines, then the subject event should be of the
Perception, Intensional Action, Intensional State, or Reporting event class.
(14) Mary [wanted] John (to buy) some wine.
(15) John [managed] (to buy) some wine.
(16) John [forgot] (to buy) some wine.
(17) John [said] he (bought) some wine.
(18) John [denied] he (bought) some wine.
(19) If John [buys] the wine, Mary (will thank) him.
Temporal Aspectual Subordinating
After Before Initiates Modal
Immediately After Immediately Before Culminates Factive
Includes Included by Terminates Counter-Factive
During Inverse During Continues Evidential
Begins Begun By Reinitiates Negative Evidental
Ends Ended By Conditional
Simultaneous
Identity
Table 1: Temporal Link relation types
Version 2.0.1 / February 8, 2012 2
Time Link Annotation Guide
Temporal Link Relation Types
As noted above, the temporal link type can hold between two events, two times, or an event and a
time. The relations are described below, and illustrated graphically in Figure 1.
Simultaneous
Two event instances are judged simultaneous if they happen at the same time, or are temporally
indistinguishable in context, i.e., occur close enough to the same time that further distinguishing
their times makes no difference to the temporal interpretation of the text.
Identity
Event identity indicates that two event mentions refer to the same event. It is a co-referential
relationship, as in (20).
(20) John [drove] to Boston. During his [drive] he ate a donut.
After & Before
One event B is After another event A if A precedes B in time, as in (21). Before is the direct
inverse of After, except with the subject and object reversed. These two relationship merely
indicate an order, and do not imply immediacy to the relationship, as in Immediately After and
Immediately Before. In the case of (21), we have Before(slayings, arrested).
(21) The police looked into the [slayings] of 14 women. In six of the cases suspects have already
been (arrested).
Immediately After & Immediately Before
These two relationships are like After and Before, but they imply an immediacy to the relationship.
In cases where the subsequent event could not possibly be separated from the preceding event by
any amount of time, choose this relationship over the plain After or Before. The difference between
these two sets of relationships is analogous to the difference between “less than” and “less than or
equals”. In the case of (22), we have ImmediatelyAfter(died, crashed)
(22) All passengers [died] when the plane (crashed) into the mountain.
Includes & Included by
These relationships indicate a subset relationship, that (in the case of Includes) an event or time A
starts after another event or time B, and A also ends before B. In the case of (23), we have
IncludedBy(arrived, last Thursday). A preposition that suggests this relationship is “on” – if you
can insert “on” between the two related events or times and the semantics are unchanged, then it is
probably an Includes relationship.
(23) John [arrived] in Boston (last Thursday).
During & Inverse During
These two relationships are specifically applicable to states or events that persist throughout a
duration, as in (24) and (25). Use During and During Inverse only to link an event and a time, and
Version 2.0.1 / February 8, 2012 3
Time Link Annotation Guide
only when the time specifically indicates a duration. Triggering words here, in contrast to Includes
and its inverse, are “for” and “during”. So is DURING like SIMULTANEOUS?
(24) James [was CTO] for (two years).
(25) John [taught] for (20 minutes) on Monday.
Begins & Begun by
These two relationships indicate that the two related events or times start simultaneously, but that
one of the events or times ends before the other, as in (26). Thus these are more specialized
relationships than Includes or Included by. In (26), we have BegunBy(at the gym, 6:00pm).
(26) John was [at the gym] between (6:00 pm) and 7:00 pm.
Ends & Ended by
These relationships are the same as the previous set, but the restriction is at the end of the relevant
time periods. In (26), we have EndedBy(at the gym, 7:00pm).
Figure 1: Illustration of temporal relationships between events or times located on a timeline,
relative to an event or time A.
Subordinating Link Relation Types
As noted above, the subordinating link type is used for relationships between two events.
Factive
Certain verbs introduce an entailment (or presupposition) of their argument’s veracity. They
include forget (with a tensed complement), regret or manage, as in (15). MORE EXPLANATION.
MAKE THIS OUR DEFAULT SUBORD. LINK
Counter-Factive
Contrary to the Factive relation, the Counter-Factive marks the case where an event introduces a
presupposition about the non-veracity of its argument, such as forget (to), unable (to), prevent,
cancel, avoid decline, etc, as in (16).
Evidential
Evidential relationships are typically introduced by Reporting or Perception events, as in (17).
Version 2.0.1 / February 8, 2012 4
Time Link Annotation Guide
Negative-Evidential
As for Evidential, Negative-Evidential is usually introduced by Reporting or Perception events, and
conveys a negative polarity, as in (18).
Conditional
A condition relationship can occur between any two event instances and is generally accompanied
by a signal such as if. The antecedent of the conditional takes the place of the introducing event
instance
Modal
A modal relation is brought up by events introducing a reference to a possible world – mainly
Intensional Actions and Intensional States, as in (14).
When to Annotate Temporal & Aspectual Links
Every event and time should be linked by either a temporal or aspectual time link to another event
or time. This allows us to determine, in the narrative world, the proper order of events.
Rule NN: Every event and time should participate in a temporal or aspectual link.
In particular, every non-Aspectual event and every time expression should be involved in a
Temporal Time Link to another event or time expression. On the other hand, Aspectual events
should participate in an Aspectual time link to another event to which it is aspectually related.
Rule NN: Every non-Aspectual event and every time expression should participate in a
temporal link.
Rule NN: Every Aspectual event should participate in an aspectual link.
When to Annotate a Subordinating Link
Every Intensional Action, Intensional State, Perception, and Reporting event should be involved in
a Subordinating time link. These events generally take a clausal complement (such as a purpose
clause or conditional) or a noun phrase headed by an event-denoting nominal. The Subordinating
time link is between those events and the one denoted by the complement.
Rule NN: Perception events always introduce subordinating links of type evidential or negative
evidential.
Rule NN: Intensional Action or Intensional States may introduce subordinating links of type modal,
factive, or counter factive.
Rule NN: Reporting events can introduce subordinating links of any type.
Version 2.0.1 / February 8, 2012 5
Time Link Annotation Guide
Notes
• First convention: Maintain links going forward whenever possible. If you have a choice
between After and Before, choose the one where the subject occurs before the object in text
order.
• Does “not” on an event change factive relationship?
• John did not forget that he bought the wine.  Factive relationship
• John forgot that he bought the wine.  also Factive relationship
• Problematic example
• He seized her and dragged her to his lair, but did not devour her.
• Before(seized, dragged)  not problematic, but what about Before(seized, did not devour)
or Before(dragged, did not devour) ? First might be because he could have devoured her
right after seizing her, but did not. Second because the text is making sure to point out that
she was not devoured at the time when the author expects the reader to expect it. Jared’s
point is good that “he did not devour her” at all points in the story, so this makes us prefer
the second. The question is what is the “policy of the dragon” – does he usually seize, take,
then devour (take-out) or seize then devour (dine-in)? Or perhaps the seizing begins the
“not devouring” which is then ended much later?
• Is a question identical to its answer? E.g., “What are you doing?” he asked. “I am weaving
a tackle” he said., do we have Identity(doing, weaving)
Version 2.0.1 / February 8, 2012 6
Time Link Annotation Guide
Summary of Rules
Temporal Expressions
# Rule
1 One possibility for a rule is to set one column of the temporal links as “default”, and always
choose that one as long as the inverse is not explicitly signaled.
Or, we could say the link type which preserves X R Y, with X is before Y in the text.
Advantage here is that when you annotate a relation, the related event is already
highlighted, so you can just move directly to the next relation, saving keystrokes
Version 2.0.1 / February 8, 2012 7
Time Link Annotation Guide
Glossary
word a definition for lay people
Notes
• #2, line 20, "She became absorbed in games" -> is "absorbed" a verb or an adjective?
• Question: If "she said "x, y, z", then do we do Sub(said, x) & Sub(said, y) & Sub(said, z) or
do we do Sub(said,x) & Before(x, y) & Before(y,z)?
• What about commands? #2, line 31, "She saw a stove; 'Tell me, stove, where have they
gone?'"
• Should we introduce an Identity relationship between the two hides? "'Please hide me!', and
the river hid her."
• If the "saying" event is implicit, and not marked, should we introduce an Evidential link
between the last saying event for that character and the said thing? E.g., He said: "Have
you measured all his money, little fox?" The fox answered: "All of it. Now, tsar, I have
come for a good purpose: give your daughter in marriage to Bukhtan Bukhtanovich." "Very
well; show me the suitor."
• What about questions to the listener, should these be marked as events, and if so, how do
the connect via links? How about Before(vanished, was), Before(was, dare), Modal(dare,
appear) “The prince chased it; he galloped and galloped, but could not catch the goat, and
when he returned the princess had vanished. What was he to do? How could he dare to
appear before the king?”
• What about "When X, do Y", should this be Conditional? As in following example:
Before(be, comes), Conditional(comes, give), etc. "Very well," said the king, "be my
herdsman. When the three-headed dragon comes to your herd, give him three cows; when
the six-headed dragon comes, give him six cows; and when the twelve-headed dragon
comes, count off twelve cows."
• “The next day she gave Princess Maria the same crust, and sent her elder daughter with her,
saying: "Give an eye to what Princess Maria feeds herself with." Question: what is the
relationship between Give and Feeds? Factive? Evidential? Possibly include this as a
problematic sentence
Version 2.0.1 / February 8, 2012 8


## EVENTS — tense, aspect, class (from 03_Events_v2.0.1)

Events Annotation Guide
Events
Adapted from the “TimeML Annotation Guidelines version 1.2.1” by Roser Saurí et al., 2006.
Contents
What is an Event? ................................................................................................................................... 2
What to Annotate .................................................................................................................................... 2
Identifying the Full Extent of an Event ................................................................................................... 3
What is NOT an Event ............................................................................................................................ 4
Identifying the Event Head Word(s) ....................................................................................................... 4
Event Classes .......................................................................................................................................... 5
Occurrence ...................................................................................................................................... 5
Reporting......................................................................................................................................... 6
Perception ....................................................................................................................................... 6
Aspectual......................................................................................................................................... 6
Intensional Action ........................................................................................................................... 6
State ................................................................................................................................................ 7
Intensional State .............................................................................................................................. 8
Polarity & its Signal ................................................................................................................................ 9
Cardinality & its Signal .......................................................................................................................... 9
Modality Signal ..................................................................................................................................... 10
Difficult Cases ...................................................................................................................................... 10
Aspectual Verbal Cluster .............................................................................................................. 10
Light Predicates ............................................................................................................................ 10
Causative Predicates ..................................................................................................................... 10
Distinguishing Adjectives from Participles .................................................................................. 11
Distinguishing Nouns from Present Participles ............................................................................ 11
Tense & Aspect ..................................................................................................................................... 12
Finite Verbs ................................................................................................................................... 12
Non-Finite Verbs .......................................................................................................................... 12
Verbs Preceeded by a Modal Auxiliar .......................................................................................... 13
Predicative or Copular Expressions .............................................................................................. 13
Glossary ................................................................................................................................................ 15
Summary ............................................................................................................................................... 15
Rules ..................................................................................................................................................... 16
Version 2.0.1 / March 15, 2012 1
Events Annotation Guide
What is an Event?
Events are things that happen or occur. Events can be punctual, as in (1), or they can last for a period
of time, as in (2). We will also, for the most part, consider states or circumstances in which something
obtains or holds true, such as (3), to be events.
(1) A fresh flow of lava, gas and debris erupted there Saturday.
(2) 11,024 people, including local Aeta aborigines, were evacuated to 18 disaster relief
centers.
(3) Israel has been scrambling to buy more masks abroad, after a shortage of several hundred
thousand.
In these examples, and the examples that follow, an underline will indicate all the words that indicate
the event. Annotating an event will not only involve identifying this underlined region, but other
portions of the expression that fulfill certain roles, and categorizing certain features of the event (for
example, the part of speech of the head word).
Note that, for purposes of clarity, not all “markable” events will be shown in the examples in this
guide. Sentences often communicate more than one event; in this guide a sentence is usually
introduced to illustrate a particular point, and so only the event relevant to that point will be marked in
the sentence.
What to Annotate
To fully annotate an event, you may need to mark or classify up to eleven different features. Six of
those features must be marked for every event; the rest may be marked or not, depending on how the
event is expressed. The features include:
Features that all events have:
 Full extent – all the words that are used to express the event. For example, in (2), “were
evacuated” comprises the full extent of the event.
 Head word(s) – an event expression usually has one, sometimes two or more, head words
which express the core nature of the event. In (2), “evacuated” is the head word.
 Part of Speech – the part of speech of the head word; “evacuated” in (2) is a verb.
 Class – a tag which indicates the type of the event. There are eight possibilities, including
“unknown.” (2) is of the type Occurrence.
 Polarity – this is either true or false, and indicates whether the event is negated. The polarity
of the underlined event in (2) is true.
 Cardinality – the number of occurrences that are expressed by the event. The event “were
evacuated” (2) expresses a single event, the evacuation.
Features that only some events have:
Version 2.0.1 / March 15, 2012 2
Events Annotation Guide
 Tense – if the event is expressed with a verb, or as the predicate of a copular verb, then its
tense (past, present, future) must be marked. In (2), “evacuated” is in the past tense.
 Aspect – if the event is a verb (or a copular predicate), then its aspect (perfect, progressive,
etc.) must be marked. In (2), “evacuated” has the perfect aspect.
 Polarity Signal – if there is a particular word or set of words that signals the polarity of the
event (e.g., the word “not” often signals an event that did not occur), then it must be marked.
 Cardinality Signal – if there is a particular word or set of words that expresses the number of
events that occurred (e.g., “twice”, “every”, etc.), this must be marked.
 Modality Signal – if the event has a modal modifier (“would”, “could”, etc.), this must be
marked.
Identifying the Full Extent of an Event
Events may be expressed by means of tensed (4) or untensed verbs (5), nominalizations (6), adjectives
(7), predicative clauses (8), or prepositional phrases (9):
(4) John taught on Monday.
(5) Prime Minister Benjamin Netanyahu called the prime minister of the Netherlands to thank
him for thousands of gas masks his country has already contributed.
(6) Israel will ask the United States to delay a military strike against Iraq until the Jewish state
is fully prepared for a possible Iraqi attack.
(7) A Philippine volcano, dormant for six centuries, began exploding with searing gases, thick
ash and deadly debris.
(8) ”There is no reason why we would not be prepared,” Mordechai told the Yediot Ahronot
daily.
(9) All 75 people on board the Aeroflot Airbus died.
Once you have decided that an event has been expressed, you must decide what words are to be
included in the event’s “full extent”. For verbs, you may notice that helping or auxiliary verbs such as
“was” “were,” or “have”, and the infinite “to” are included in the event extent. For events expressed
by a noun, generally only the single word expression, and not its modifiers, are marked: for example,
in (6), “attack” is the event, not “Iraqi attack.” A similar principle holds for verbs, in that verbal
arguments (such as subjects and objects) are not marked as part of the event.. What unifies these two
approaches (and the approach to the other parts of speech) is that we are attempting to find the
minimum set of words that leaves the values of all eleven features unchanged. This lead us to Rule #1
Mark the event full extent to be the minimum set of words that, when considered alone, retains
the values of all eleven features.
Note that sometimes an event expression may be sequentially discontinuous. In (10), the word “fully”
is not necessary to maintain any of our features, so we can eliminate it. In (11), the word “it” is the
object of the event, and so must not be included in the full extent
(10) There is no reason why we would not be prepared.
There is no reason why we would not be fully prepared.
(11) They will definitely take into consideration our readiness.
They will definitely take it into consideration.
Version 2.0.1 / March 15, 2012 3
Events Annotation Guide
What is NOT an Event
Not everything that looks like an event is actually an event. There are two important cases: generics
and redundant expressions.
Generic event expressions will be not be tagged. A generic event is when a property is ascribed to a
class of events, or a relation is asserted between a class of events and members of a set of entities, but
no single event instance, or set of event instances, in this class is positioned in time, or in relation to
other temporally located events. For example, the event expressions in the following sentences will
not be tagged:
(12) Use of corporate jets for political travel is legal.
(13) Businesses are emerging on the Internet so quickly that no one, including government
regulators, can keep track of them.
(14) Jews are prohibited from killing one another.
In between examples such as the preceding pure generics and others which express a single event,
clearly positioned in time, and hence clearly taggable, such as:
(15) On June 7, Mr. Sununu used a jet provided by Fiber Materials Inc.
are less clear cut cases such as
(16) Mr. Sununu has resorted to regular use of corporate planes for political travel.
Sentences such as (16) express typical patterns of activity, but do not explicitly refer to specific
events. These examples will also not be tagged. This lead us to Rule #2: Do not mark references to
generic events that do not explicitly refer to particular happenings or states, clearly positioned
in time.
The second case of event look-alikes are redundant expressions. For example, an event
nominalization that provides no information beyond that supplied by the verb to which it is bound
need not be tagged. For example, in (17), said is tagged as an event, and the word “reports” is not
tagged. Thus Rule #3: Do not mark redundant expressions as events.
(17) Newspaper reports have said that Israel has a shortage of gas masks.
Identifying the Event Head Word(s)
Once you have identified the full extent of an expression, the next feature to determine is the head
word of the event. The head word, in linguistics parlance, is the word (or words) in a phrase that
serves the same grammatical or syntactic function as the phrase as a whole. In the examples below,
the full event extent is underlined, while the event head words are marked in boldface. Strategies for
specific parts of speech are outlined below.
If the event is expressed by a verbal phrase, as in (18) “has been scrambling” or (19)
“were reported”, the head word of the event is the non-auxiliary verb that carries the phrase. This is
so even if the verb falls within the scope of a modal auxiliary, as in (20) “could”, or a negative
particle as in (21) “not.” Rule #4: The head of a verb phrase is the non-auxiliary, non-modal verb
that expresses the core meaning of the phrase.
Version 2.0.1 / March 15, 2012 4
Events Annotation Guide
(18) Israel has been scrambling to buy more masks abroad.
(19) No injuries were reported.
(20) The private sector could establish a private agency.
(21) Kaufman did not disclose details of the deal.
Sometimes an event expressed by a phrase (be it a noun phrase, verb phrase, prepositional phrase, or
what-have-you) will not have a clear head (it is “exocentric”). In these cases, mark the whole phrase
as the head of event. Rule #5: For phrasally expressed events with no clear head, mark the whole
phrase as the head.
If the event is a predicative clause, only the predicative element (the adjective or the nominal in the
following examples) will be tagged. Similar rules apply to the predicate as to the phrases identified
above. If the predicate has a head, as in (22) or (23), then we will tag the head only. If the predicative
element has no single head, as in (24), then we will mark the entire predicate as the head.
(22) If, in spite of everything, we will not be ready, we will ask the United States to delay.
(23) James Pustejovsky was CTO of LingoMotors for several years.
(24) All 75 people were on board at 9:00 a.m.
Event Classes
You have now identified the extent of the event, it’s head word(s), and, and in so doing, its part of
speech. The next step is to assign an event class. There are eight possible classes, and they can be
roughly organized into the following hierarchy.
I. Occurrence (1)
a. Reporting (2)
b. Perception (3)
c. Aspectual (4)
d. Intensional Action (5)
II. State (6)
a. Intensional State (7)
III. Unknown (8)
First decide if an event is an Occurrence, a State, or Unknown. If the event is one of the two former,
decide if the event additionally falls into the one of the subcategories. Explanations of all the classes
follow.
Occurrence
This class is a catch-all for events that happens or occurs in the world. Some examples are given as
illustration:
(25) The Defense Ministry said 16 planes have landed so far with protective equipment against
biological and chemical warfare.
(26) Mordechai said all the gas masks from abroad would arrive soon and be distributed to the
public, adding that additional distribution centers would be set up next week.
(27) Two moderate eruptions shortly before 3 p.m. Sunday appeared to signal a larger explosion.
Some examples from financial journals:
Version 2.0.1 / March 15, 2012 5
Events Annotation Guide
(28) Ralston said its restructuring costs include the phase-out of a battery facility in Greenville.
(29) Its cereal division realized higher operating profit on volume increases, but also spent
more on promotion.
Reporting
Reporting events are an occurrence where a person or an organization declares something, narrates an
event, informs about an event, etc. Some examples of verbs that fall into this class are “say”, “report”,
“tell”, “explain”, “state”, and “cite.”
(30) Punongbayan said that the 4,795-foot-high volcano was spewing gases up to 1,800 degrees.
(31) No injuries were reported over the weekend.
(32) Citing an example, ...
Perception
Perception events are any occurrence that involves the physical perception of another event.
Perception events are typically expressed by verbs like “see”, “watch”, “glimpse”, “behold”, “view”,
“hear”, “listen”, or “overhear”.
(33) Witnesses tell Birmingham police they saw a man running.
(34) “You can hear the thousands of small explosions down there”, a witness said.
Aspectual
In languages such as English and French there is a grammatical device of aspectual predication, which
focuses on different facets of event history.
 Initiation: begin, start, commence, set out, set about, lead off, originate, initiate.
 Reinitiation: restart, reinitiate, reignite (metaphorically)
 Termination: stop, cancel, end, halt, terminate, cease, discontinue, interrupt, quit, give up,
abandon, block, break off, lay off, call off, wind up.
 Culmination: finish, complete.
 Continuation: continue, keep, go on, proceed, go along, carry on, uphold, bear on, persist,
persevere.
Thus an aspectual event is an occurrence that concerns the beginning, ending, or other period of time
as part of an event. A couple of examples:
(35) The volcano began showing signs of activity in April for the first time in 600 years.
(36) All non-essential personnel should begin evacuating the base.
Intensional Action
An Intensional Action (I-Action) is a type of occurrence that introduces an event argument (which
must be in the text explicitly) describing an action or situation from which we can infer something
given its relation with the I-Action. For instance, the events introduced as arguments of the actions in
(a) have not necessarily occurred when the I-Action takes place. Explicit performative predicates (like
those in (e)-(g), below) are also included here. While the event argument of an I-Action may of any
event class, the I-Action label itself only applies to events that would otherwise be marked as one of
the Occurrence categories. Stative events that have ‘intensional’ character should not be marked as I-
Actions, but rather Intensional States (I-States: see below). The following list, where I-Actions are in
Version 2.0.1 / March 15, 2012 6
Events Annotation Guide
surrounded by square brackets, and the events they introduce are also underlined, is representative
(not exhaustive) of the types of events included in this class:
(a) attempt, try, scramble:
(37) Companies such as Microsoft or a combined Worldcom MCI [are trying] to monopolize
Internet access.
(38) Israel has been [scrambling] to buy more masks abroad.
(b) investigate, investigation, look at, delve:
(39) The Organization of African Unity [will investigate] the Hutu-organized genocide of more
than 500,000 minority Tutsis.
(40) A new Essex County task force began [delving] Thursday into the slayings of 14 black
women.
(c) delay, postpone, defer, hinder, set back:
(41) Israel will ask the United States [to delay] a military strike against Iraq.
(d) avoid, prevent, cancel:
(42) Palestinian police [prevented] a planned pro-Iraq rally by the Palestinian Professionals’
Union.
(e) ask, order, persuade, request, beg, command, urge, authorize:
(43) Iraqi military authorities [ordered] all Americans and Britons in Kuwait to assemble at a
hotel.
(44) They [were asked] to take along important papers.
(f) promise, offer, assure, propose, agree, decide:
(45) Germany [has agreed] to lend Israel 180,000 protective kits against chemical and biological
weapons.
(46) Switzerland [offered] to lend Israel another 25,000 masks.
(g) swear, vow, name, nominate, appoint, declare, proclaim, claim, allege, suggest.
State
States describe circumstances in which something obtains or holds true. Because everything is always
in one “state” or another, we will not annotate all possible states, only those that satisfy the following
rules:
Rule #6: Mark states that are identifiably changed over the course of the document. For instance,
in the first example below, in the expression the Aeroflot Airbus the relationship indicating that the
Airbus is run and operated by Aeroflot is not a STATE in the desired sense. Rather, because it is
persistent throughout the event line of the document, we factor it out and it is not marked up. On the
other hand, properties that are known to change during the events represented/reported in an article
will be marked as STATEs.
(47) All 75 people on board the Aeroflot Airbus died.
Version 2.0.1 / March 15, 2012 7
Events Annotation Guide
(48) Israel has been scrambling to buy more masks abroad, after a shortage of several hundred
thousand.
(49) No injuries were reported over the weekend.
Rule #7: Mark states that are directly related to a temporal expression. This criterion includes all
states that are linked to a TIMEX3 mark-able by means of a TLINK. In the following examples the
related temporal expression is set off in square brackets.
(50) James Pustejovsky was CTO of Lingo Motors for [several years].
(51) They lived in U.N.-run refugee camps for [2 1/2 years].
Rule #8: Mark states that are introduced by an Intensional Action, Intensional State, Reporting,
or Perception event. In the following examples, the introducing event is set off in square brackets.
(52) He [mediated] the crisis.
(53) Saddam Hussein [sought] peace on another front.
(54) Har-Shefi [told] police that Rabin [was a traitor].
(55) He [saw] the that the girl was sleeping.
Rule #9: Mark predicative states the validity of which is dependent on the document creation
time. The states introduced by are in the following examples will be tagged given that their validity is
relative to the point in time they have been asserted (the document creation time). This will also
include some quantitative statements such as those that appear in financial journals, as in (58). This
rule, will however apply only to predicative states. States that expression membership in a class
(“sortal” states, like President, CTO, etc.) won’t be marked up. Note that the current class, State, will
not contain states that have been tagged as I-States.
(56) A total of about 3,000 Americans and 3,000 Britons are in Iraq and Kuwait.
(57) Overall, more than 2 million foreigners are in both countries.
(58) Gas prices fell from a twenty-two dollar barrel level down to the fourteen dollars we’re
seeing today.
Intensional State
An Intensional State (I-State) class is similar to the I-Action class. This class includes states that refer
to alternative or possible worlds, (delimited by square brackets in the examples below), which can be
introduced by subordinated clauses (61), untensed verb phrases (71), or nominalizations (73). All I-
States will be annotated, whether they are persistent or not throughout the text being marked-up. Like
I-Actions, an I-State may take any sort of event type as an argument (although I-States differ from I-
Actions in that they do not require an event argument). As above, the following list of I-States is just
representative, not exhaustive:
(a) believe, think, suspect, imagine, doubt, feel, be conceivable, be sure:
(59) “We believe that [his words cannot distract the world from the facts of Iraqi aggression].”
(60) Analysts also suspect [suppliers have fallen victim to their own success].
(61) Russia now feels [the US must hold off at least until UN secretary general visits Baghdad].
(62) It is conceivable that [a larger eruption will take place in few hours].
(63) He said he was sure that [a larger eruption would happen].
Version 2.0.1 / March 15, 2012 8