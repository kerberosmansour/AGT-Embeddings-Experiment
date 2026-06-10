# AGT Upstream Baseline Refresh

Status: PR 1 preflight evidence
Date: 2026-06-10
AgentBus task: `t_mq7bhzm8_168_3e583d5e`
Freshness follow-up: `t_mq7s8pwk_148_c5892b65`

This note records the current AGT upstream anchor for the rules-only baseline
used by the prompt-injection evaluation fixture. It is a benchmark preflight,
not a runtime change and not an embedding feature proposal.

## Upstream Pin

| Item | Value |
|---|---|
| AGT repository | `https://github.com/microsoft/agent-governance-toolkit` |
| Fresh `origin/main` observed | `730ffbb060c44362485b786c63aa08439c49d7e1` |
| Local checkout HEAD during read | `1bf359397df64aeb5285bdf5d609ade291c329b9` |
| Local checkout state | Behind `origin/main` by two commits; unrelated untracked local docs present. |
| Detector file | `agent-governance-rust/agentmesh/src/prompt_injection.rs` |
| Last detector-touching commit | `7c89582420b667fa93b3030180b618b7c208a02f` |
| Detector SHA-256 at fresh `origin/main` | `92ac1f855e03502886fffdfb8cf9eece8ce7c2bea268ecacb4ff6386cb345ab3` |
| Vendored experiment detector SHA-256 | `92ac1f855e03502886fffdfb8cf9eece8ce7c2bea268ecacb4ff6386cb345ab3` |

The upstream branch moved after the earlier local pin, but the prompt-injection
detector file still did not change. The experiment's vendored Rust scorer still
matches the detector blob at fresh upstream `origin/main`.

## Commands

```bash
git -C <local-agt-checkout> fetch origin main --prune
git -C <local-agt-checkout> rev-parse origin/main
git -C <local-agt-checkout> \
  show origin/main:agent-governance-rust/agentmesh/src/prompt_injection.rs \
  | shasum -a 256

cargo run --manifest-path tools/agt-rules-baseline/Cargo.toml -- \
  corpus/round4/injection-round4-large.jsonl \
  --per-row corpus/round4/rules-baseline-large.jsonl \
  --summary corpus/round4/rules-baseline-large-summary.json

python3 corpus/round4/summarize-baseline.py \
  corpus/round4/rules-baseline-large-summary.json \
  --out corpus/round4/rules-baseline-large-metrics.json
```

The Rust scorer emitted existing vendored dead-code warnings only.

## Corpus And Artifact Hashes

| Artifact | SHA-256 |
|---|---|
| `corpus/round4/manifest-large.json` | `6532ddd1ff8487147cbdb451f9d280775c7f2ccf49fd700434c5f6cba745f078` |
| `corpus/round4/injection-round4-large.jsonl` | `33a02ac2b22e68970b3b808c5ba95bc119dc87dd93ae6dbc90546c074a5980ed` |
| `corpus/round4/rules-baseline-large.jsonl` | `12b1897e83059d58209b3557aeeb4a1fc036c5d622fa5143fe2065a1db7bd23b` |
| `corpus/round4/rules-baseline-large-summary.json` | `5284051deb59da57f0e717bb4a8a39565ec642513724a4299691504b76ae3b82` |
| `corpus/round4/rules-baseline-large-metrics.json` | `a082e99bde0eab841987e99bae264b1310a9c6cb8621ad1ada222cde3a5ceab3` |

The large baseline rerun against the current detector-equivalent snapshot
produced no git diff in the committed artifacts.

## Rules-Only Result

| Metric | Value |
|---|---:|
| Rows processed | 44,800 |
| Attack rows | 17,600 |
| Attack rows caught | 180 |
| Attack recall | 0.010227 |
| Attack recall Wilson 95% interval | 0.008844 to 0.011824 |
| Benign rows | 27,200 |
| Benign rows flagged | 2,136 |
| Benign false-positive rate | 0.078529 |
| Benign false-positive Wilson 95% interval | 0.075392 to 0.081786 |
| False positives per 1,000 benign rows | 78.529 |
| Base-rate precision, 1 attack per 100 benign | 0.001301 |
| Base-rate precision, 1 attack per 1,000 benign | 0.000130 |

## Interpretation

The current "about 1%" rules-only catch rate is tied to this exact synthetic
Round-4 corpus, this detector blob, and the command above. It should not be
presented as a general statement about AGT's detector. AGT's rules-only layer is
high-precision/low-recall by design; this benchmark is testing whether a
separate optional evidence signal might add useful reviewer signal on examples
that deterministic rules miss.

If upstream `origin/main` moves again before PR 1 is opened, repeat this
preflight and update the commit, detector hash, artifact hashes, and metrics.
