# Intake

## 0. First-run setup and the local config

Read `~/.config/research-paper-distilled/config.json`. It holds this user's own choices and is never part of the skill, so a shared copy of the skill carries none of them.

- **When it is valid,** use its reviewer and output folder, and name both in the defaults line. Valid means: it parses as JSON; `reviewer.kind` is one of the kinds below, with a `name` for an agent and a `command` and `env` for a command; and `output_dir` is set.
- **When it is missing or not valid,** ask only for the missing or invalid settings, in one round before intake, then create the folder and write the file, keeping every valid setting. The first run asks all three:
  1. **Reviewer for the independent review.** Offer only what this machine has: a fresh agent of the same model (recommended, always available); each installed agent type whose description says it reviews or critiques work, by its listed name; a command the user names, which takes the guide and the paper and prints a report; or no independent review. For a command, also ask for the name of the environment variable that holds its credentials, and say that the guide and the paper go to that command's provider.
  2. **Output folder** for guides (default `~/Research-Papers/`).
  3. **Model for locating passages in cited works:** the session's model (recommended), or a lighter model that the agent tool accepts, by the name it lists. That agent only downloads the works, extracts their pages and finds the sections this paper relies on. The session's model still reads every one of those sections and writes every key-reference bullet (`references/key-references.md`), so this choice changes the cost, not what the guide says. When `models` is missing from an existing config, ask this once and save the answer (`{}` for the session's model).

The file stores the choice only, never a key or a token:

```json
{
  "reviewer": {"kind": "agent", "name": "<agent type as listed>"},
  "second_reviewer": {"kind": "command", "command": "<command>", "env": "<VARIABLE_NAME>"},
  "output_dir": "~/Research-Papers",
  "models": {"cited_reader": "<model name as the agent tool lists it>"}
}
```

`kind` is `same-model`, `agent`, `command` or `none`. `none` turns the independent review off, and the delivery report says so. `models` is optional; a missing entry means the session's model. `second_reviewer` is optional: when it is set, it reviews the same scope after the first reviewer, and both reports are merged before any finding is confirmed. When a saved reviewer cannot run (the agent type is not listed, or a command fails as `references/verification.md` describes), use a fresh agent of the same model and say so at delivery. The user can change the file by asking, or by editing it.

## Intake questions

Ask these four questions in one round (AskUserQuestion, one question each). Put the recommended option first. Then state the remaining defaults in one line and say that the user can change any of them.

## 1. Length

Count the paper's pages up to the end of the main text and, separately, its appendices. For a web article, divide its prose words by 500. Then count the central derivations the guide must work through: a proof, a closed form, or an objective derived from another. Use the right-hand columns when there are three or more. Offer three options from the row that matches the main-text length:

| Main text | Few derivations: short | recommended | long | Three or more derivations: short | recommended | long |
|---|---|---|---|---|---|---|
| 1 to 10 pages | 8 | 10 | 12 | 18 | 24 | 30 |
| 11 to 30 pages | 12 | 16 | 20 | 24 | 30 | 36 |
| 31 to 80 pages | 20 | 26 | 32 | 30 | 36 | 42 |
| over 80 pages | 26 | 32 | 38 | 36 | 42 | 48 |

The derivation rules (the maths toolkit, one move per line, the smallest case first) make a derivation-heavy guide about two and a half times as long per page of main text as one with few derivations. For example, a 10-page paper with 12 derivation boxes and its appendix proofs needed 26 pages; guides of 9 to 15-page papers with few derivations needed 8 to 11. The right-hand columns rest on fewer guides than the left, so treat them as a starting point.

An engineering post (`references/modes.md`, last section) has few or no derivations and needs fewer pages than the table gives: multiply its unrounded page count by one and a half, two and three, round each result up, and offer those, with at least 4 pages. Recommend the middle one. For example, a 1,537-word post is 3.07 pages, so offer 5, 7 and 10, with 7 recommended. For the reader, recommend the junior software engineer row instead of the junior AI engineer row. This rule rests on no finished guide yet, so treat it as a starting point.

Appendix material must fit inside the chosen length. The paper's mode changes the structure of the guide; its number of derivations, not its mode, changes the length. The user's answer is a cap: the build fails above it. If the plan cannot fit what the user wants inside the cap, say so at the plan gate and ask again.

## 2. Level of breakdown

| Reader | Assumed known | Maths assumed | Explained |
|---|---|---|---|
| **Junior developer or junior AI engineer** (recommended) | tokens, prompts, training, gradient descent, softmax, accuracy, cross-entropy, standard architectures at a high level | undergraduate: algebra, derivatives, mean and variance, the normal distribution | the paper's own concepts, every metric, the math with its derivations, the datasets, how to read each figure, and every other maths fact a derivation uses, in the maths toolkit |
| ML researcher | the field's standard methods and benchmarks | graduate: probability, linear algebra, KL divergence, Bayes' rule | the paper's contribution, its evidence and its weaknesses; fewer worked examples; the toolkit only for facts outside that list |
| Junior software engineer (for an engineering post) | HTTP, DNS, TCP and UDP, IP addresses, clients and servers, what a load balancer and a VPN do | school: algebra, powers of two | the post's products and their own terms, every networking or infrastructure concept a step uses, and each step of the mechanism |
| Newcomer to ML | nothing beyond school mathematics | school: algebra and averages | also the basic terms, each at first use, and a toolkit that starts from the normal distribution |

## 3. Pilot and sources (multiple choice)

- **Build a pilot first**: two or three parts built and checked in full. Mark it recommended only when the recommended length is over 15 pages. The user can turn it on or off either way.
- **Fetch openly available cited works** to check the key references and later work (recommended). Without it, a key reference is checked only if the user supplies the work, and is otherwise marked unverified.

## 4. Review depth

- **Lean** (recommended for a main text of up to about 15 pages, or a plan with usage limits): no grounded follow-up pass. The guide is delivered once every script passes, and the user is then offered one independent review of the critical sections.
- **Full:** the grounded follow-up pass on each critical section after the build, and an independent review of the whole guide before delivery.

## Stated defaults (one line)

- Math: every central formula with its derivation, and every reported metric, each with one worked example.
- Figures and tables: every one in the main text that the guide discusses, captions word for word, with a personal-study notice. If the user plans to publish the guide, warn about reuse rights first.
- Appendices: those that define prompts, data, metrics, proofs, implementation or limits.
- Key references: at most 10, each checked in the cited work when question 3 allows fetching it.
- Output: HTML and PDF in `<output folder from the config>/<Paper-Title>/`, one folder per paper named after its title in hyphenated words (for example `Attention-Is-All-You-Need`), not committed. Markdown on request, for short papers without figures.
- Version: the supplied PDF, and its PDF page numbers. A link to the paper is downloaded into its own folder. For an arXiv paper, record the ID with its version (for example 2005.14165v4), use the versioned PDF URL as `paper_url`, and check the abstract page for a withdrawal notice. `extract_pages.py` pins the file by checksum, and the checks refuse any other version. A web article is pinned by `fetch_web.py`: the page's checksum and its fetch date (`references/web.md`).
