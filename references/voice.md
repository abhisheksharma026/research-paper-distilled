# The voice of the guide

Distilled from 13 recent teaching posts: six of Sebastian Raschka's (Ahead of AI) and seven of Eugene Yan's on recommender systems, read and measured in 2026. Both write short sentences (median 17 to 18 words) in short paragraphs (about two sentences). Both speak as "we" for the work done with the reader. Use their order and their voice. Do not copy their text or code.

## The order of every explanation

1. **The problem first.** Say what the old way does and where it fails, before the new idea appears. Yan opens on the failure ("Recommender systems work well when we have a lot of data on user-item preferences."). Raschka gives the history of why a mechanism was invented.
2. **The answer in one sentence, then its cost.** Start the sentence with "In short,". Give the cost or the downside in the next sentence.
3. **Each term once, defined by its role.** Say what the thing does, not what it is called: "The query for a token represents what that token is looking for". When a section needs several terms, define them together at the top: "(i) action/arm: ..., (ii) reward: ...".
4. **One tiny running example, with the real size stated.** Use toy sizes (three tokens, three dimensions) and say how large they are in the paper. Keep the same example through the part.
5. **What each setting does when it gets larger or smaller.** "A higher ε leads to more exploration while a lower ε leads to more exploitation."
6. **Each figure read in words.** Say what is where, the order to read it ("each request flows left to right") and what to compare. A caption must make sense on its own.
7. **Code in numbered steps, after the concept.** One sentence says what the step adds. Then the code, then one sentence of reason ("The reason for ... is that ...").
8. **A check that the result is right.** Compare with a reference: a library function, a number worked by hand, or the paper's own value. Say what the match proves.
9. **The limits, then numbered lessons.** "First, ...", "Second, ...", each with its "because" and an "In contrast" where there is one.

## Sentence-level rules

- **"We" for the shared work, "I" only for the writer's choices.** Never use "I" to say where a number or a reading came from: write "These values come from the graph", not "I read these values from the graph". A derived number shows its arithmetic, not a label such as "my calculation".
- **One to three sentences per paragraph.** Keep most sentences under 25 words. Split a sentence over 35 words.
- **One signpost word for each job:**
  - "Note that" for a detail that is easy to miss.
  - "For example" for an instance.
  - "In short" for a summary.
  - "However" for a limit.
  - "So" for a consequence.
  - "Next" for the next step.
- **A bold claim opens a paragraph that argues one point,** so a reader who reads only the bold text still gets the argument. Use it in results and lessons, not on every paragraph.
- **Parentheses for numbers and short asides:** "(from millions to hundreds, a 99.99% reduction)".
- **Paired contrasts with the same shape:** "a fast—but coarse—step" and "a slower—but more precise—step".
- **A caveat where it applies,** not in a section of its own: "optimized for code readability and not ... for runtime speed".

## How the voice lands on each part of a guide

These shapes apply to any paper. The examples come from two guides built with this skill, one on GPT-3 ("Language Models are Few-Shot Learners") and one on the Transformer ("Attention Is All You Need"); they illustrate the shape and are not rules about those papers.

- **A part's opening:** the old way and its cost first, then the answer with its own cost. Transformer: "In 2017, the best translation models read a sentence one position at a time ... In short, the Transformer keeps the attention and drops the chain." GPT-3: "Before GPT-3, a model needed a separate training run for each task ... The cost is that all of this, and the new input, must fit in a prompt of at most 2,048 tokens [p. 8]."
- **Each results section opens with a short lead,** before its figures and cards: the task in one sentence, the result in an "In short" sentence, the limit in a "However" sentence. "Here the model answers general-knowledge questions from its weights alone. In short, few-shot GPT-3 beats a fine-tuned system with retrieval on TriviaQA. However, it stays behind on Natural Questions." The reading card beside the figure then holds only how to read it.
- **A math box opens on what the formula is for,** then the formula and its derivation, then "For example" with real numbers, then the "Why": "The power law does not directly show what more compute buys. In short, the log of both sides turns it into a straight line ..."
- **A term is defined by what it does:** "Its query (Q) is what the token looks for, its key (K) is what other queries match against, and its value (V) is what it passes on."
- **Code comes after its concept, with its reason:** "The reason for <code>transpose(1, 2)</code> is that matrix multiplication works on the last two dimensions ..."
- **Two things compared get the same sentence shape:** "Before filtering, the compressed text was 45 TB. After filtering, it was 570 GB."
- **A summary opens each bullet with a bold claim,** and opposite findings come as a matched pair ("The best results come from ..." and "The weakest results come from ...").
- **"We" walks through the work with the reader:** "Let's put one encoder layer together and count the base model."
- **A reflection answer opens with its answer,** then the reason, then its `[p. N]` marker, which the build hides.

As a guide to density, not a quota: about one "In short", one "However", one "Note that" and one "For example" per section, and at most about 5% of sentences over 25 words.

## What stays out

- Idioms, small talk and personal news ("sweet spot", "Needless to say", "Happy reading!").
- Any of their sentences, paragraphs or code. The quotes above are short examples of the patterns only.
