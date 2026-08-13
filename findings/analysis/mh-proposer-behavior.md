# Inside the Meta-Harness proposer: where the time, depth, and dollars go

*Evidence: proposer session traces (`workspace/.mab2/trace/events-*-meta.jsonl`) for six
MH runs — sol and opus5 GPQA-strong, sol and opus5 τ²-strong, opus5 GPQA-medium, and
opus5 CharXiv-medium (the 40/40-iteration run) — plus `workspace/history/`, per-session
token/spend events cross-checked against [data/run_stats.csv](../data/run_stats.csv)
(exact match on calls, out-tokens, and dollars). Companion to
[method-natures](method-natures.md) and [meta-model-axis](meta-model-axis.md): those docs
say what MH builds and how the two meta models differ in outcome; this one measures what
the coding agent actually *does* with its sessions.*

## 0. An observability asymmetry that is itself a finding

Sol's per-command record is empty: in every sol meta trace, `tool_call_started` events
carry `params: {}`, `tool_call_completed` carries `output: ""`, and effect timestamps are
backfilled in one batch at session end. The full codex transcripts live only on the
sweep machine's codex home. Sol's `proposals.json` is also overwritten each iteration
(final content on gpqa-strong: `{"candidates": []}` from the crashed last session), so
its per-proposal hypotheses are unrecoverable. Everything sol-specific below is therefore
session-level (token/cost/`commands_ok` stamps, 11 surviving final messages) plus the
seven `session_error` events — which, ironically, preserve sol's final commands verbatim
because they crashed. All per-command analysis is opus-only.

## 1. Where opus spends its actions and time

Every proposer tool call classified: (a) reading rollout traces, (b) reading candidate
source/prompts, (c) scores/frontier/history metadata, (d) writing/editing candidates and
proposals.json, (e) ad-hoc inline python analysis, (f) other (mostly harness spelunking).
Time = LLM gap before call + tool execution, over all attributed time.

| run (tool calls) | a traces | b cand src | c metadata | d write | e python | f other |
|---|---|---|---|---|---|---|
| opus5 gpqa-strong (514) — count | 16% | 17% | 8% | **34%** | 17% | 8% |
| — time | 11% | 16% | 24%¹ | 22% | 19% | 9% |
| opus5 gpqa-medium (486) — count | 14% | 20% | 8% | 27% | 22% | 6% |
| opus5 tau2-strong (346) — count | 10% | 12% | 5% | 30% | **39%** | 3% |
| opus5 charxiv-medium (890) — count | 11% | 17% | 5% | 33% | **30%** | 4% |
| — time | 6% | 12% | 6% | 16% | **54%** | 7% |

¹ inflated: the long first-turn think after the prompt lands on the session-opening
`cat scores.jsonl && cat frontier.json`.

- Category (e) *is* mostly failure analysis executed as code — e.g. a hedge-word counter
  regexing "however|ambiguous|probably" across failing vs passing traces to test whether
  worker uncertainty is detectable post-hoc (verdict: it isn't — failures hedge *less*,
  1.3 vs 3.4 mentions).
- The "throwaway analyzers" are all inline `python3 -c`/heredoc one-offs (85 on
  gpqa-strong, 271 on charxiv-medium); **zero standalone .py files were ever written**.
- Early→late shift: on gpqa-strong, python-analysis share falls (24%→10%) while direct
  reading rises (26%→38%) and re-orientation cost balloons — by the last third, up to
  ~39% of session time goes to re-surveying the 30+-candidate history before doing
  anything. On the cheap-eval tasks (tau2, charxiv) the analysis arm grows instead
  (32%→53% of time on tau2). Writing share declines everywhere: later sessions spend
  relatively more on evidence, not less.

## 2. How deep it reads

Per session (opus, medians): **4–7 distinct rollout files opened**, ~3–6 candidate
sources inspected; over a whole run, 28–78 distinct rollouts get read. Read style splits
roughly evenly between full `cat`, head/tail, grep, and `sed -n` ranges; the standard
pattern is verdict-sidecar triage (which tasks failed, gold vs answer — often a python
sweep over *all* candidates' sidecars at once) followed by targeted full reads of 3–6
failing rollouts.

It systematically returns to old evidence: **47–71% of trace opens target candidates
evaluated ≥2 iterations earlier** (one charxiv propose-35 session reopened traces of a
candidate 34 iterations old), and it re-cites its own accumulated statistics ("VERIFY
overturned 0/56", "`:147` 0/23 candidates") many sessions after first measuring them.

Refinement of the claim in [meta-model-axis](meta-model-axis.md): the "332 of 449 bash
commands were cat/sed/grep/awk" figure reproduces exactly, but only **142 of those 332**
target rollout traces; ~90 target candidate sources and the rest metadata.

Sol, bounded from session stats: 9–16 tool calls per session (median 13), 75–165 s per
session, one long context of bulk-dumped files rather than iterative narrow probes
(input profile 180k–474k tokens/session at ~85–95% cache).

## 3. Where the dollars go

Per-session spend from lane events; totals match `run_stats.csv` exactly. Recovered
price coefficients: claude-opus-5 ≈ $5/M in, $0.5/M cache-read, $25/M out; gpt-5.6-sol ≈
$5/M uncached-in, $0.5/M cached, $30/M out.

| run | meta $ | meta % of run | cache-read tokens | out tokens | meta cost split (in/cache/out) |
|---|---|---|---|---|---|
| sol gpqa-strong | 5.10 | 10% of $50.25 | 3.4M | 0.056M | 34/33/33 |
| opus5 gpqa-strong | 28.53 | 28% of $101.09 | **26.7M** | 0.405M | 18/**47**/36 |
| sol tau2-strong | 4.11 | 14% of $29.39 | 2.7M | 0.039M | ~⅓ each |
| opus5 tau2-strong | 22.47 | 41% of $55.14 | 22.5M | 0.31M | 21/47/32 |
| opus5 charxiv-medium | 59.84 | **63%** of $94.94 | 54.4M | 0.774M | 21/37/42 |

Opus's meta bill is dominated by **re-reading its own growing session context** (~30
turns/session) plus 7–14× sol's generation. Sol's sessions cost a nearly flat $0.32–0.61.
Total proposer wall time on the paired gpqa-strong run: **18 minutes (sol) vs 3.3 hours
(opus)** — median opus session 8.9 min, max 25.6. On charxiv, the opus proposer cost more
than all evaluation combined ($59.8 vs $35.1 of worker spend).

## 4. Proposal grounding: 80% evidence-cited — and no dev payoff

Hypotheses recovered from proposals.json write params (opus only, see §0): 36 / 36 / 26 /
78 per run. Grounding markers: explicit rollout/task ids, or quantified trace evidence
("0/56", "50/55 traces"):

| run | cites ids | quantified | either | mean dev: grounded vs not |
|---|---|---|---|---|
| opus5 gpqa-strong | 20/36 | 24/36 | **81%** | .875 vs .879 |
| opus5 gpqa-medium | 18/36 | 20/36 | 83% | .850 vs .859 |
| opus5 tau2-strong | 16/26 | 15/26 | 81% | .594 vs .626 |
| opus5 charxiv-medium | 41/78 | 40/78 | 79% | .739 vs .732 |

Roughly 4 in 5 proposals quote specific observed failures, often verbatim (tau2:
"rollout-269 'Please go ahead and process that.###STOP###' … terminating with zero
writes"). The ungrounded residue is mostly deliberate ablation surgery ("isolate the
winning half of cand_instruction_is_consent"), not vagueness. **And grounding does not
correlate with dev score** — grounded means are flat-to-slightly-lower in 3 of 4 runs.
Diagnosis quality is not the binding constraint; this is the proposer-side corroboration
of the selection-gap story.

## 5. The feel of an iteration

A typical opus iteration (gpqa-strong propose-3: 27 turns, 7.4 min, $1.12): re-orient on
scores + frontier → dump the frontier candidate's run.py and prompts → python-sweep all
verdict sidecars of 3 candidates → a second one-off partitions failures into
agreement-path vs disagreement-path → the hedge-word study → full reads of 4 failing
rollouts → `cp -r` two forks, Write-tool rewrites, py_compile, proposals.json. One clean
analysis-to-writing pivot mid-session; a structured lab-notebook final message with a
Diagnosis section.

Verbatim gems:

- propose-3: *"the shared shape is: correctly eliminate two options, then choose between
  two near-identical survivors by plausibility (rollout-809 nails epithio-vs-epoxy then
  asserts stereodescriptors with zero derivation; gold was the runner-up)."*
- propose-12: *"Error is concentrated and correlated across all 23 candidates:
  gpqa_diamond:147 0/23, :167 0/23… Anchored verifiers are useless (56/56 no-ops)…
  only blind solvers dissent."*

Sol's session shape, by contrast: one LLM "call" driving 9–16 execs in ~90 s, ~4.6k
tokens out, closing with a terse note ("Created two candidates… No evaluations were
run.").

## 6. Sol's crash economics

The fatal move is preserved verbatim in the `session_error` snapshots — always a single
giant exec of the form
`for f in candidates/*/run.py; do echo "### $f"; sed -n 1,260p "$f"; done`
bulk-dumping every candidate's source (on charxiv, including trace enumerations and
question dumps). 7/18 gpqa-strong and 7/16 tau2-strong sessions died mid-dump
(`codex session failed rc=1`; the underlying codex error string is truncated, so
output-overflow vs timeout is not recoverable). MH tolerates skipped sessions, so those
runs limped on; on charxiv it was fatal — all three sol runs aborted with
`RuntimeError: proposer session failed 3x in a row` after 9/17/23 scored candidates
(strong/medium/minimal; the strong run never reached the results table).
Opus had zero session errors across all four analyzed runs. Note the failure is partly
harness-fixable (output caps / exec-size guards), so the observed robustness gap is an
upper bound.

## Limitations

- Sol per-command behavior and per-proposal hypotheses are unrecoverable from this repo
  (see §0); sol conclusions are session-level.
- charxiv candidate names don't match the `cand*` path convention, so path-based
  per-candidate read counts undercount there (python-glob sweeps dominate anyway).
- Opus per-turn token events carry zero counts; spend comes from one reconcile event per
  session (cross-checked against cumulative stamps).
