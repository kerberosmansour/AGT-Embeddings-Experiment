# Experiment 1 — Structural Auto-Block Ceiling

**Bottom line:** a fully-automated, **no-human-review** filter blocks **81% of
prompt-injection attacks at 0% false-positives** on our test set — up from **14%
two experiments ago**. It's promising and low-noise. The figures still need more
data and independent review before any production claim.

## The story in three numbers

| Experiment | What we added | Catch rate | False-positives |
|---|---|---:|---:|
| Round 4 | kNN embedding detector, alone | 14% | 0% |
| Round 6 | + **Gate-0 normalizer** (clean the text first) | **43%** | 0% |
| **This one** | + **R1** structural rule (block on facts) | **81%** | **0%** |

*Frozen synthetic test set (9,408 rows), detector at its conservative
zero-false-positive setting. AGT = Microsoft's Agent Governance Toolkit, where
these controls would live.*

## The three pieces, one line each

- **kNN embedding detector** — flags text whose *meaning* sits closest to known
  attacks. Probabilistic, so we run it at zero-false-positives: it only fires when
  sure.
- **Gate-0 normalizer** — un-disguises text first (`1gn0re`→"ignore", strips
  hidden characters, decodes, fixes spacing). Attackers disguise injections;
  cleaning first **tripled** the detector's catch (14% → 43%).
- **R1 rule** — *block any tool action triggered by untrusted content.* Reads
  **who sent it + what it's trying to do**, never the words. This is what took
  43% → **81%**.

---

## Result by attack technique (the hero table)

Block rate per family. `embedding` = Gate-0 + kNN at zero-FP.

| Attack family | embedding | R1 | **combined** | Caught by |
|---|---:|---:|---:|---|
| indirect_injection | 29% | **100%** | **100%** | R1 |
| output_exfiltration | 47% | **100%** | **100%** | R1 |
| data_boundary_abuse | 49% | **100%** | **100%** | R1 |
| tool_abuse | 33% | **100%** | **100%** | R1 |
| direct_override | 63% | 0% | 63% | embedding |
| memory_poisoning | 48% | 0% | 48% | embedding (gap) |
| tool_result_injection | 37% | 0% | 37% | embedding (gap) |
| prompt_leakage | 0% | 0% | **0%** | nothing (gap) |
| **All** | **~43%** | 64% | **81%** | |

**R1 takes the four "action" families to 100%** — the exact families detection
couldn't catch. And because R1 reads provenance not words, it's **language-proof**:
it blocked a French and a space-stripped attack the embedding missed.

## The safety finding — one rule we kept, one we threw out

We tested four rules. The point of the experiment was to measure each against
**legitimate** traffic, not assume it's safe.

| Rule | Condition | Attacks caught | False-blocks on benign | Verdict |
|---|---|---|---:|---|
| **R1** | untrusted source + tool call | 4 action families @ 100% | **0%** | **KEEP** |
| R2 | sensitive sink + non-user source | 0 extra | **14%** (100% on two legit categories) | **DROP** |

**R2 sounds obvious but is a trap** — legitimate high-entropy data and tool-policy
docs trip it, for zero added attack coverage. *Lesson: never trust a structural
rule until you've measured its false-blocks.*

## Why R1 shows 0% false-positives — and why it will rise

R1 only fires on **untrusted + tool-call**. In our benign data that combination
**never occurs**:

| benign rows | no tool call | tool call |
|---|---:|---:|
| **untrusted** | 4,400 | **0** |
| trusted | 928 | 400 |

That empty cell *is* the 0%. **In production it's not empty** — "read this
untrusted web page, then click next" is a normal agent action R1 would block. So
the 0% is a ceiling from **missing benign data**, and it's the number most likely
to move. Fix: more realistic benign examples, and scope R1 to *sensitive* tools
(send/delete/pay) not all tools.

## The three families it misses (each has a known fix)

| Family | Combined | Why it slips | Fix |
|---|---:|---|---|
| prompt_leakage | 0% | it's an output, not a tool call | IFC rule: label the system prompt secret, block it leaving |
| tool_result_injection | 37% | source is `tool_output`, not `untrusted` | R1′: treat tool output as not-fully-trusted |
| memory_poisoning | 48% | write isn't flagged as an untrusted tool call | taint-on-write to memory |

---

## Where this is **not** perfect (known, and partly deliberate)

| Limitation | What it means |
|---|---|
| Synthetic, labels-perfect data | R1 is only as good as the `trust_level` / tool labels a real deployment produces. This is a **ceiling**, not a forecast. |
| Empty benign quadrant | No legitimate "untrusted + tool" examples → R1's 0% false-block is optimistic. |
| Multilingual only partly handled | 320 multilingual attacks: detection catches **0%**, R1 recovers **25%**, **75% still escape** (Gate-0 has no translation, by design). |
| Prompt injection only | 1 of the 6 *AI Agent Traps* categories (Google DeepMind). Semantic-manipulation, multi-agent, human-in-the-loop: **not tested**. |
| Single-input, single-agent | Attacks that assemble across many inputs/agents are invisible here. |
| Not independently verified | Every number is ours, on our data. No external review or real-traffic check yet. |

These bound the result; they don't sink it. The honest claim is **"promising on
the slice we can measure."**

## What's next

1. **Invest in data** — more synthetic coverage (other categories, multilingual)
   *and* sanitized real-world examples, especially the missing **benign** patterns
   that make false-positive numbers honest.
2. **Turn it into a maintained benchmark** — versioned checks, held-out splits,
   leakage controls.
3. **Tune controls against it and keep chipping** — close the residual families,
   narrow R1 to sensitive tools, re-measure. It's a dial, not a one-time setting.
4. **Independent review** before any deployment claim.

**Hypothesis worth exploring:** an **agent skill / MCP server** that helps
engineering teams dial their AGT to the right setting for their own traffic —
carrying both the benchmark data + statistical analysis (to *recommend* operating
points and rules) and the capabilities/best-practices we advocate. A way to make
these lessons reusable instead of re-derived per team.

---

## Appendix — verdicts, prior rounds, reproduce

**Pre-registered bars:** rule-safety ≤1% false-block → **PASS for R1** (R2/R4
correctly rejected); containment lift ≥30pt → **PASS** (tool_abuse +67, exfil
+53); combined floor ≥60%/family → **PARTIAL** (3 named residuals); handle-rate
reported → **PASS**.

**Prior rounds:** round-4 governance gate ~65% unsafe-action prevention (no
breakdown); round-6 detection-only capped at tool_abuse 38% / exfil 42%; this
experiment hits those families at 100% via R1, 81% overall @ 0% FP
(labels-perfect ceiling).

**Reproduce:** harness `meta/harness/exp1-structural/`; artifacts
`artifacts/exp1-structural/`; `validate-exp1.py` recomputes every table from the
per-row file. No model run — reuses `artifacts/round6-cascade/m1-gate0/`.
