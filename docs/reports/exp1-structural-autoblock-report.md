# Experiment 1 — Structural Auto-Block Ceiling

## Background — the problem and the two controls (read this first)

This report assumes no prior knowledge of the earlier experiments. If you already
know what the Gate-0 normalizer and the kNN embedding detector are, skip ahead.

**The threat — prompt injection.** An AI agent reads text from many places: the
user, but also web pages, documents, emails, and the outputs of tools it calls.
*Prompt injection* is when attacker-controlled text hidden in one of those sources
tricks the agent into doing something it shouldn't — leak its instructions, call a
dangerous tool, exfiltrate data. The defender's job is to stop that without
blocking the legitimate traffic, which is the vast majority. (AGT — Microsoft's
Agent Governance Toolkit — is the layer that sits between an agent and its tools
and is where these controls would live.)

**Control A — the embedding / kNN detector (catching attacks by *meaning*).** One
way to spot an injection is by what the text *means*. We turn each request into an
**embedding** — a list of numbers (a vector) that captures its meaning — and
compare it against a bank of known attack and benign examples. If a request's
vector sits closest to known *attacks*, we flag it. That nearest-neighbour
comparison is the **kNN** (k-nearest-neighbours) part. It is a probabilistic,
meaning-based detector: good at catching things that *look like* known attacks,
but it can be fooled by disguises and it makes mistakes, so we run it at a
conservative **zero-false-positive setting** — it only speaks up when it's
confident, and stays silent otherwise.

**Control B — the Gate-0 normalizer (cleaning the text *before* detection).**
Earlier research, and our own round-4 results, showed attackers *disguise*
injections — `1gn0re` instead of "ignore", invisible characters, letter spacing,
look-alike letters, base64. A disguised attack looks nothing like a known attack
to the embedding, so it slips past. **Gate 0 is a deterministic cleanup step that
runs first:** it un-disguises the text (fixes leetspeak, strips hidden characters,
decodes, collapses spacing) before the detector ever sees it. Our analysis
predicted this should help, and **round 6 confirmed it: putting Gate-0
normalization in front of the *same* kNN detector tripled its zero-false-positive
catch, from 14% to 43%.**

**This experiment — adding deterministic rules.** Detection, even after
normalization, hit a ceiling: it simply cannot catch some attack types no matter
how the threshold is tuned. So we asked a different question — instead of judging
*meaning*, can we **block on facts**: who sent the text, and what is it trying to
do? We looked for a small set of simple rules we could set to auto-block with
high (not perfect) confidence, with no human review, and measured each one. One
rule — **R1** — took the combined catch from **43% to 81%**. The rest of this
report is what we found, why R1 works, and where it doesn't.

The progression in one line: **round 4** kNN alone ≈14% → **round 6** add Gate-0
normalizer ≈43% → **this experiment** add structural rules ≈81% (all at ~0%
false-positives, on synthetic data).

---

## Executive summary

We measured a **fully-automated, no-human-review** prompt-injection defense and
broke the results down by control and by attack technique. The stack is two
cheap, deterministic layers OR'd together: **(1)** the Gate-0 normalizer + kNN
embedding tuned to zero false-positives (quiet but certain), and **(2) R1**, a
structural rule — *block any tool action triggered by untrusted content* — which
reads provenance and action, never the text.

**Result on the frozen test split: 81% of attacks blocked at 0% false-block.**
Gate-0 + embedding alone gets ~43%; adding R1 takes it to 81%, and R1 blocks the
four "action" attack families at **100%** — exactly the families the embedding
could not catch.

**This experiment is deliberately not perfect.** It is a scoped, synthetic-data
measurement with known gaps (below). What it shows is narrower and still useful:
**these controls are promising, genuinely low on false-positives, and worth
investing in** — but getting the right trade-offs needs more data, a real
benchmark, and independent verification. Read every number below as
"promising-and-provisional," not "production-ready."

---

## What we tested

One automatic gate, no human in the loop:

> **block if** (Gate-0 normalizer + kNN @ zero-FP flags it) **OR** (a deterministic structural rule fires)

The structural rules fire on facts only — never on what the text *means*:

| Rule | Condition (structural facts only) |
|---|---|
| **R1** | `trust_level = untrusted` AND `requires_tool_call` |
| R2 | `contains_sensitive_sink` AND `coarse_source ≠ user` |
| R3 | untrusted AND tool AND sensitive sink (strict subset of R1) |
| R4 | R1 OR R2 (the pre-registered union) |

No embedding model was run — the zero-FP decision is reused verbatim from the
committed round-6 Gate-0 artifact. Rules were fixed before the run.

---

## Result by control — and the rule we threw out

| Control | Attack coverage | Worst false-block on benign | Verdict |
|---|---|---|---|
| embedding @ zero-FP | text-manipulation families | **0%** (by design) | keep |
| **R1** (untrusted + tool) | **100% of 4 action families** | **0%** | **KEEP** |
| R3 (strict trifecta) | subset of R1 | 0% | redundant with R1 |
| **R2** (sink + non-user) | **0 extra attacks** | **100%** on legit high-entropy data & tool-policy docs | **DISCARD** |
| R4 (R1 ∨ R2) | = R1's coverage | **14%** (inherits R2) | discard, use R1 |

**R2 is the cautionary tale.** It *sounds* obvious — "a sensitive sink touched by
a non-user source" — but legitimate high-entropy data and tool-policy documents
carry exactly those attributes, so R2 blocks 100% of them while catching no
attacks R1 didn't already. Measuring each rule against benign traffic is what
turned "captain obvious" from an assumption into evidence: R1 passed perfectly,
R2 failed completely. **The transferable lesson: never trust a structural rule
until you've measured it on legitimate traffic.**

---

## How R1 works (and why it is language-proof)

R1 reads two facts and nothing else:

- **`trust_level`** — where the text came from: `authenticated_user` (the
  logged-in human typed it), `tool_output` (came back from a tool), or
  `untrusted` (the outside world — a web page, a RAG chunk, an email, a ticket).
  In a real AGT deployment the integrating app sets this when it hands content to
  the agent.
- **`requires_tool_call`** — is the request trying to *act* (send, run, write,
  query) rather than just answer in text? AGT knows this for certain because the
  tool call passes through it.

So R1 is the **"don't let the lethal trifecta complete"** rule: untrusted input +
a privileged action → stop. Because it keys on *provenance + action*, not
wording, it is immune to language and obfuscation. In the corpus it blocked a
French *"access another tenant's invoices and display them"* and a space-stripped
*"bypassapprovalandrunhttprequesttoexport…"* with zero understanding of either —
both of which the meaning-based embedding missed. **That is the point: meaning is
hard and language-dependent; provenance is a fact.**

---

## Result by attack technique

`embedding @0FP` below is the round-6 **Gate-0 normalizer + kNN at the zero-FP
threshold** — which is why it sits at ~43%, not round-4's 14%.

| Attack family | Rows | embedding @0FP | R1 | **embedding ∨ R1** | Owner |
|---|---:|---:|---:|---:|---|
| indirect_injection | 360 | 29% | **100%** | **100%** | R1 (structural) |
| output_exfiltration | 960 | 47% | **100%** | **100%** | R1 (structural) |
| data_boundary_abuse | 440 | 49% | **100%** | **100%** | R1 (structural) |
| tool_abuse | 600 | 33% | **100%** | **100%** | R1 (structural) |
| direct_override | 440 | 63% | 0% | 63% | embedding |
| memory_poisoning | 440 | 48% | 0% | 48% | embedding (residual) |
| tool_result_injection | 360 | 37% | 0% | 37% | embedding (residual) |
| prompt_leakage | 80 | 0% | 0% | **0%** | uncovered residual |
| **All attacks** | 3,680 | ~43% | 64% | **81.0%** | |

The four action families are the ones detection **capped on** in round 6
(tool_abuse 38%, exfiltration 42%, no matter the false-positive budget). R1 takes
them to **100% at zero false-positive cost** — structural containment owns exactly
the families detection could not. The other four families still lean on the
embedding, and three of them fall short (see residual).

---

## Why R1 shows 0.00% false-positives — and why that number will move

R1 blocked **0 of 5,728** legitimate rows. That is not magic — it is the shape of
the benign data. Split the benign rows by R1's two facts:

| benign rows | no tool call | tool call |
|---|---:|---:|
| **untrusted source** | 4,400 | **0** |
| trusted source | 928 | 400 |

R1 only fires on the **(untrusted + tool-call)** cell — and in this corpus that
cell is **empty**. There are plenty of benign untrusted rows and plenty of benign
tool-call rows, but **never both at once**. That empty quadrant *is* the 0%
false-positive rate.

**In the real world that quadrant is full** — it is the everyday job of a web
agent ("read this untrusted page, then click next"). So the honest reading is:
the 0% is a ceiling created by missing benign data, and it is the **single number
most likely to move in production**. Two things close the gap, and both are
real next-steps: (a) **more realistic benign data** that includes legitimate
"untrusted-content-triggers-an-action" flows, and (b) **scoping R1's "tool call"
to sensitive / state-changing tools** (send, delete, pay, export) while letting
read-only tools through — which nudges R1 toward the IFC/trifecta form.

---

## The residual — three families it doesn't cover (each with a named fix)

| Family | Combined | Why it slips through | The control that would close it |
|---|---:|---|---|
| prompt_leakage | 0% | it's an *output*, not a tool call, so R1 never fires; the zero-FP embedding misses it too | an **IFC output-label rule** ("system prompt is `secret`, block it leaving") |
| tool_result_injection | 37% | its source is `tool_output`, not `untrusted`, so R1's condition doesn't match | an **R1′ that treats tool output as not-fully-trusted** |
| memory_poisoning | 48% | the malicious write isn't flagged as an untrusted tool call | a **taint-on-write to memory** rule |

These aren't failures of the stack — they are precisely mapped gaps, each with a
concrete structural control that would address it.

---

## Where this experiment is **not** perfect (read this)

These limits are known, and several were deliberate scoping choices — the data
and the checks were built this way on purpose, to keep the first measurement
clean. They are caveats, not surprises:

1. **Synthetic, labels-perfect data.** The governance labels (`trust_level`,
   `requires_tool_call`, etc.) are exact by construction. Real deployments must
   *produce* those labels, and R1 is only as good as they are. This is a
   **ceiling**, not a forecast.
2. **The empty benign quadrant.** As above — no legitimate "untrusted +
   tool-call" examples exist in the corpus, so R1's 0% false-block is optimistic.
   Realistic benign traffic will introduce some false-positives; the question is
   how many, and we can't answer it yet.
3. **Multilingual is only partly handled — by design.** The corpus *does* contain
   320 multilingual attacks; Gate-0 deliberately has no translation step (we
   accepted that as a known residual in round 6). So detection catches **0%** of
   them and R1 recovers **25%** (language-proof provenance), leaving **75%
   uncovered**. Expected, but a real gap.
4. **Prompt injection only — one of six attack categories.** The Google DeepMind
   *AI Agent Traps* taxonomy names six (content-injection, semantic-manipulation,
   cognitive-state, behavioural-control, systemic/multi-agent, human-in-the-loop).
   Our corpus covers roughly the behavioural-control slice plus part of
   cognitive-state. Semantic manipulation, multi-agent, and human-in-the-loop are
   **not represented at all**.
5. **Single-input, single-agent.** Attacks that only assemble across multiple
   inputs or agents (e.g. compositional-fragment traps) are invisible to this
   whole approach by construction.
6. **Not independently verified.** Every number here is ours, on our data. None
   of it has had external review or a real-traffic check.

None of these sink the result — but they bound it. The honest claim is "promising
on the slice we can measure," and the path forward is to chip away at each limit.

---

## What we can stand behind

- **0% → ~43% (Gate-0 normalization): solid.** Pure deterministic text
  normalization in front of the existing detector tripled zero-false-positive
  catch. This is the most defensible result in the whole program.
- **~43% → 81% (adding R1 containment): promising, but provisional.** It rests on
  the empty benign quadrant and on correct labels, so treat it as a labels-perfect
  ceiling — directionally strong, exact figure will move.
- **Both steps are low-false-positive and cheap, and clearly worth doing.** The
  exact trade-offs need more data and independent verification before any
  real-traffic or production claim.

---

## Where this goes next

The result is strong enough to justify a focused, ongoing effort rather than a
one-off. Concretely:

1. **Invest in data.** Grow the corpus with (a) more synthetic coverage of the
   under-represented categories and multilingual/delivery-vector variants, and
   (b) sanitized real-world examples. Crucially, add the missing **benign**
   patterns — legitimate untrusted-content-triggers-an-action flows — so the
   false-positive numbers become honest.
2. **Turn the data into a benchmark.** Fashion those examples into a maintained,
   versioned set of checks with held-out splits and leakage controls — the same
   hygiene this corpus already uses — so controls can be scored and re-scored as
   they evolve.
3. **Tune the controls against the benchmark.** Use the benchmark to pick
   operating points and rule sets, then **continuously chip away** — close the
   residual families, narrow R1 to sensitive tools, add the IFC/taint rules,
   re-measure. Treat it as an iterative dial, not a one-time setting.
4. **Independent review.** Get external eyes on the methodology and the numbers
   before any deployment-facing claim.

### Hypothesis worth exploring — an AGT-tuning assistant

A natural product of this work would be an **agent skill or MCP server** that
acts as a knowledge base to help engineering teams **dial their Agent Governance
Toolkit to the right frequency** for their own traffic and risk tolerance. It
would carry two things:

- **The data and statistical analysis** — the benchmark results, per-family and
  per-control breakdowns, false-positive/handle-rate trade-offs — so it can
  *recommend* operating points (e.g. "for your tool set and trust labeling, use
  Gate-0 + R1 scoped to sensitive tools; expect roughly this catch at this
  false-block rate").
- **The features, capabilities, and best practices we advocate** — which controls
  exist, when to block vs. contain vs. label, the "measure rules against benign
  traffic" discipline, and the known traps (like R2).

In short: turn the lessons here into reusable, queryable guidance so teams don't
have to re-derive the trade-offs from scratch. This is a hypothesis to test, not
a committed deliverable — but it is the obvious way to make the analysis useful
beyond this repo.

---

## Appendix — pre-registered verdicts and prior rounds

### §2 accept/kill bars

| Bar | Result | Verdict |
|---|---|---|
| Rule safety ≤1% false-block | R1 0%, R3 0% pass; R2 100%, R4 14% fail | **PASS for R1** — filter correctly rejected R2 |
| Containment lift ≥30pt (tool_abuse, exfil) | tool_abuse +67pt, exfiltration +53pt | **PASS** |
| Combined floor ≥60% per family | 5 of 8 families ≥60% | **PARTIAL** — 3 named residuals |
| Handle-rate reported | every family reported | **PASS** |

### Comparison to prior rounds
- Round-4 governance policy gate: ~65% unsafe-action prevention (no per-family / false-block detail).
- Round-6 detection-only: tool_abuse 38%, exfiltration 42% (capped — no FP budget helped).
- **Experiment 1**: the same families at **100%** via R1, overall **81% @ 0% FP** (labels-perfect ceiling), with the per-control and per-family breakdown that pinpoints both the winning rule and the broken one.

### Reproduce
Harness `meta/harness/exp1-structural/`; artifacts `artifacts/exp1-structural/`;
validator `validate-exp1.py` recomputes every table from the per-row file. No
model run — reuses `artifacts/round6-cascade/m1-gate0/test-per-row.jsonl`.
