# Paper modes

Read at the plan step, to choose the structure of the substance.

## Paper modes

The mode sets the parts between the central idea and the limitations. All modes use the same style, cards and checks.

| Mode | The substance, as parts in order |
|---|---|
| Empirical (benchmarks) | **Setup**: method, data, compute, how evaluation works, and one example end to end. **Evidence**, by the paper's own grouping: figures, tables, a real item per dataset, reading cards. **Scoreboard** against chance. **Data checks** (contamination, leakage) when the paper has them. |
| Theory | **Definitions and notation**, each with a small instance. **Main results**: each theorem with its assumptions, its statement in words, the proof idea, one worked case and one case where it fails. **How the results fit together**: which lemma feeds which theorem. **Experiments**, if any, read as empirical evidence. |
| Survey | **Scope**: inclusion criteria and how the authors searched. **Taxonomy matrix**: categories against defining properties. **Comparison** of approaches along the taxonomy, with the evidence the survey cites. **Disagreements and gaps**. **Open problems**. |
| Explainer (tutorial, blog post, lecture notes) | **The concepts in the author's order**, each image read in words. **The math, mapped step by step:** one small worked example with real numbers carried through every equation in order, each step beside its equation and its image, so the reader follows one input from start to end. **Build it in code:** a from-scratch implementation, checked against a library's own module. **Variants and extensions**, as the author presents them. |
| Systems | **Problem and requirements**. **Architecture**: components, data flow, and one request traced end to end. **Evaluation**: workloads, baselines, resources, ablations. **Failure modes and deployment assumptions**. |
| Method (the contribution is a mechanism of several steps: a generative process, a training objective, a sampler, an algorithm) | **The mechanism, one part per natural step**, in the order the mechanism runs (for example, the noise process, then the reverse process, then sampling). Each part opens with the question the part before left open, climbs the ladder, and ends with what the next part uses. **Completing the picture**: the design choices and their ablations, the architecture, and the links to related methods, each tied to the step it changes. **How the steps connect**: one intuition diagram from the first step to the result. **Evidence**, read as in empirical mode. |

Choose the mode by the paper's main contribution, not by whether it reports benchmarks. A paper that proposes a mechanism and then tests it on benchmarks takes method mode, and its benchmarks become the Evidence part.

A paper that mixes modes takes the parts of its main mode, plus the parts of another mode for the sections that need them (for example, a theory paper's experiments).

## Engineering posts

Everything above is for a research paper or a tutorial and applies unchanged to them. This section adds one more kind of source: an **engineering post**, which describes the author's own system, product, outage or practice. Its evidence is the company's own numbers, diagrams and configs, and it has few or no equations. Cloudflare, Netflix, system-design and DevOps blogs are typical. A blog post that teaches an existing technique with equations or code is not an engineering post; it stays in Explainer mode.

Decide by what the source contains, not by where it is hosted, and state the kind and its evidence in one line of the plan. When a source fits both, decide by its main contribution. A new method, model or result, argued with derivations or benchmarks, takes the paper modes, even on a company blog. A description of the company's own system, outage or setup takes the engineering modes, even when it shows an equation or a results table. An engineering post takes one of three modes:

- **Mechanism**: how a request, a packet or a piece of data moves through the system. A product launch that explains how the feature works is a mechanism post.
- **Incident**: an outage or a security event, told with a timeline and a cause.
- **How-to**: the steps to set something up, deploy it or migrate to it.

A post that mixes them takes the parts of its main mode, plus a short part from another for the sections that need it (a launch post that ends with setup steps gets a short how-to part).

| Mode | The substance, as parts in order |
|---|---|
| Mechanism | **The big picture**: what the system does and what it replaces, in plain words, with one diagram of the whole flow. **The mechanism, one part per natural step**, following one request end to end. Each step says the problem it solves, what the system does, why it follows from the step before, and what it means for the user. One running example (one connection, one user, one request with concrete values) goes through every step. **Completing the picture**: context from earlier posts in the series, the design trade-offs, the product claims and whether each one is backed, links to related ideas, and announced future work. **How the pieces connect**: one diagram from the first step to what the user notices, then a cheat sheet of the terms, one plain line each. |
| Incident | **What happened**: who was affected, what they saw, for how long, with the post's own numbers. **Timeline**: a table of times as the post gives them, with the time zone. **The failure, traced like a request**: the trigger, how it spread, and how it was detected. **Why the existing protection did not stop it.** **The fix and the follow-ups**, each marked as done or as promised. |
| How-to | **The goal and the prerequisites**. **The steps**, each with what it changes and how to check that it worked. **Common mistakes** the post warns about. **Costs and limits**: plan tiers, quotas, what the setup does not cover. |

Rules that apply to every engineering mode. Copy them into `WORK/brief.md`, because the part writers read the brief, not this file. Where they or the mode table above differ from `references/writing.md`, the guide contract in `SKILL.md` or `references/common-mistakes.md`, they win for an engineering post; the Mechanism cheat sheet, for example, stands despite the rule against a glossary:

- **Part 1's toolkit is titled "Concepts this guide uses".** It lists, as Fact A, Fact B and so on, each concept that a step of the mechanism uses and the reader's assumed knowledge does not cover: a protocol, an address range, a routing rule. Each fact has one plain sentence, and a formula only when a real one exists. A concept the whole post depends on gets the structural explainer from `references/writing.md`. List only facts a step uses, and use each one at least once.

- **The running example uses the post's own values** where it gives any: its addresses, hostnames, counts and timings. Where the post gives none, say so in a plain sentence and pick a value ("The post gives no client address; this guide uses 10.0.0.5"). Use the same values in every step.
- **Maths only where it governs the behaviour**: an address count, a bitmask, a probability, a timeout budget. Each such formula goes in the concepts list and is worked once with the running example. A step with no such formula skips rung 4 of the ladder in `references/writing.md`, and its rung 6 shows the running example's values from the post, or the stated example values, in place of numbers from a formula.
- **A product claim is evidence only when the post backs it.** In the claim-evidence table, say for each claim whether the post backs it with its own measurement, with a link, or not at all. "Up to 30% faster" with no data is the vendor's claim, and the guide says so.
- **Limitations become "What the post does not say".** A company post rarely states its limits. List what a reader would need and the post leaves out, such as failure behaviour, costs, quotas, or numbers behind a claim. Say only that it is missing; do not fill it in.
- **Key references are the works the post links to**: its earlier posts, the product docs and the standards it names. When the post links to no other work, leave the section out; the link audit allows that only when `links.json` is empty.
- **No Evaluation part, Scoreboard or Metrics section** unless the post reports measurements. A config snippet from the post is shown as a numbered Code block; a from-scratch build is not required.
