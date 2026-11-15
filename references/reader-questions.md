# Reader questions

A guide can cover every section of a paper and still miss what a reader needs. Two steps close that gap. The lens questions give breadth: they come from four kinds of reader. The grounded follow-up pass gives depth: it starts from the lens questions of each critical section and follows each answer with the next question. Both use only the paper and the cited works that were read.

## 1. Questions from four lenses (step 2, in the plan)

A request for "questions about the paper" gives shallow, generic questions. Ask as four readers instead, 3 to 5 questions each, about this paper only:

| Lens | Asks about |
|---|---|
| newcomer | what a term means, why a step exists, what problem the method solves |
| practitioner | when to use the method, what it costs, what it needs, where it fails |
| re-implementer | the order of operations, sizes, settings, initialization, what the paper leaves out |
| reviewer | whether the evidence supports the claim, which comparison is fair, what is not tested |

Map each question to the subsection that will answer it (its anchor, such as `sec-2-4`), or mark it "not in the paper". Put this table in the plan. A question with no home is a gap in the plan.

## 2. The grounded follow-up pass (step 4, after the full build, at full review depth)

For each critical section, take the lens questions that land in it as the opening questions. Send them to a fresh agent that reads only the paper's page text (`WORK/pages`) and the cited works that were read, never the guide. The agent answers each question with its page and a short phrase copied from that page, or says that the paper does not say. After each answer, it asks the one follow-up question a reader would ask next, and answers it the same way.

Then compare each answer with the guide:

- The paper answers the question and the guide does not: add the answer where the question lands, with its `[p. N]` marker.
- The paper does not answer it: say so where it lands ("The paper does not say ..."). When the gap limits what the results show, list it under Limitations too.
- The guide already answers it: change nothing.

Record every question and follow-up in `WORK/questions.json`:

```json
[{"lens": "re-implementer", "question": "Which beam size gives the reported scores?", "where": "sec-3-2",
  "status": "not in paper"},
 {"lens": "newcomer", "question": "Why read the sentence in both directions?", "where": "sec-2-3",
  "status": "answered", "page": 4, "evidence": "to summarize not only the preceding words",
  "followup": {"question": "Does the backward pass change the cost?", "where": "sec-2-3", "status": "not in paper"}}]
```

Then run `python3 -I scripts/check_questions.py GUIDE.html WORK/questions.json WORK/pages`. It fails when a lens has fewer than 3 questions, an anchor is not in the guide, an evidence phrase is not on its page, or the subsection of a "not in paper" question has no sentence saying that the paper does not give it. Add each new number or quote to the claims ledger as usual.
