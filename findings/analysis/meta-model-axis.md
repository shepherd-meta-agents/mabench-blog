# The meta-model axis: gpt-5.6-sol vs claude-opus-5

*Evidence: Meta-Harness proposer sessions and `history/proposals.json` in the paired
GPQA-strong-mh and CharXiv-medium-mh runs; AdaEvolve paradigm logs; per-run spend from
event-trace stamps ([data/run_stats.csv](../data/run_stats.csv)).*

The blog draft reserved the model axis as "queued, not run." It is now run, and the
result is sharper than "which model is better": **the meta model determines how the
search behaves; the selection signal determines what it earns.**

## Same cell, two optimizer brains (GPQA-strong, Meta-Harness)

Sol's proposer runs in codex (a coding-agent harness); opus5's in an equivalent
Claude-driven harness.

| | sol | opus5 |
|---|---|---|
| productive iterations | 11 of 18 (7 session crashes) | 17 of 18 |
| candidates dev-scored | 22 | 34 |
| meta calls / out-tokens / cost | 11 / 56k / **$5.10** | 605 / 405k / **$28.53** |
| best dev → sealed test¹ | .920 → .879 (genesis .884) | .915 → .869 (genesis .889) |

¹ This row uses the *trace-best* digests with matched-batch genesis rescores. The
catalog's headline table ([results.md](../results.md)) reads sol **+3.5** and opus
**0.0** instead: for sol it scores a *different digest* (the posthoc-registered best,
dev .866 — results.md caveat 3); for opus, the same digest against a different genesis
rescore (caveat 1). The conclusions sit ±1σ apart.

Both arms posted 3–4 pt dev gains; under either pairing, neither produced a sealed-test
gain that clears the noise band — identical selection-gap physics at a 6× cost
difference.

**How they differ is the search itself:**

- **Trace forensics.** Opus reads like an investigator: 332 of 449 bash commands are
  cat/sed/grep/awk (142 of them over raw rollout traces, ~90 over candidate sources,
  the rest over history metadata — see [mh-proposer-behavior](mh-proposer-behavior.md)),
  189 references to 39 distinct rollouts, and it writes throwaway inline `python3`
  analyzers to *quantify* mechanisms — "across all 56 traces
  where VERIFY fired it changed the answer ZERO times — it anchors and rubber-stamps."
  Sol bulk-dumps every candidate's source in single giant execs — which is exactly
  what crashed 7 of its 18 codex sessions and killed both its CharXiv MH runs
  (medium-mh after iteration 8 of 40, minimal-mh after iteration 12).
- **Proposal style.** Sol tweaks prompts on a fixed topology (every candidate keeps the
  seed docstring; always exactly two prompt files). Opus refactors structure: named new
  pipeline stages (AUDIT, DUEL, RESCUE, ELIM, REFUTE), zero-token Python detectors,
  4,151-char PROPOSE prompts, and real ancestry chains (qualifier_filter →
  qf_blindvote → qf_confgate → qf_duel_gate → qf_rescue_gate).
- **Experimental hygiene.** Opus runs deliberate ablation controls ("byte-identical
  control flow… the entire ~700-token gap is PROPOSE.txt growing 1831→3429 chars") and
  targets frontier gaps ("filling the empty 900–1500 token frontier gap"). Sol's
  hypotheses are one-liners.
- **Failure response.** Neither is adaptive at the loop level: sol added nothing in 8
  of 18 iterations (including its 7 crashed sessions), opus spent ~$1.7/iteration for
  10 straight non-improving iterations producing variants of the same parent. No
  stagnation-triggered strategy change in either arm.

## The same gap appears inside AdaEvolve

On GPQA, the sol meta proposed ensembling/verification paradigms ~150 times without one
being accepted — corrected from checkpoint reads: only ~1% actually broke at 0.0; the
rest ran and scored at the program's true mean, below the champion's lucky noise peak
(see [adaevolve-dynamics](adaevolve-dynamics.md)). The opus meta landed a 133-line
program with a prompt-style bank, a capped verify→revise loop, and a self-consistency
vote fallback — the very ideas sol kept fumbling. Dev .886, test .884: executed
competently, still no lift over a shared-tier genesis that itself rescores at
.854–.874 (results.md caveat 1). The sharper
proposer-prior contrast runs the other way on τ²: sol proposed task-metadata
introspection 35/74 times and found the capsule winner; opus 3/65 on the same seed, and
stalled.

## CharXiv corroborates the cost/robustness split

**All three** sol CharXiv MH runs died to proposer crashes: medium-mh after iteration 8
of 40 (3 codex crashes; 17 dev-scored candidates, $4.26 meta), minimal-mh after
iteration 12 (4 crashes; 23 candidates), and strong-mh after 9 scored candidates
(absent from the results table for this reason). The cause is on the record — the run traces hold
`RuntimeError: codex session failed rc=1` events whose captured stdout tails show the
failure mode directly: single giant execs bulk-dumping candidate sources *including
base64-encoded chart images* until the session dies. The opus runs completed **40/40
iterations on both tiers** (81 dev-scored candidates each; $59.84 meta on medium-mh).
Sealed-test outcome on the paired medium-mh cell: sol best .727, opus .727 (s0,
recovered checkpoint) / .732 (s1), all vs genesis .727 — **flat everywhere**. The
robustness contrast is real; the outcome contrast is not — takeaway 1 in miniature.
The 6–14× meta-cost gap is mostly *session survival and turn count*, not per-token
price.

## Takeaways

1. **Dev-side, opus5 ≥ sol everywhere** (GPQA dev peaks .915 vs sol's .905 stamped /
   .920 unstamped trace-best (results.md caveat 3); CharXiv .742–.798 vs .737–.778) —
   but sealed-test deltas are statistically indistinguishable (mean +0.1 vs +0.0).
   Better proposals cannot beat a noisy selector.
2. **Robustness is a first-class result.** A method×model pair that crashes 40% of its
   proposer sessions has a different expected value than its completed-run mean
   suggests. Failure rates belong next to Δ (the draft's failure-analysis section).
3. **Where opus's extra spend would pay** is precisely where the selection signal is
   trustworthy — τ²-strong-style cells with real headroom. Under matched routes it
   posted +2.4/+4.8 there with far fewer session failures than sol.
4. **The optimizer-is-a-model-too thesis holds** — every capability the blog intro
   attributes to frontier meta models (read the trajectory, diagnose the failure,
   propose the edit) is visibly better executed by opus. What hasn't compounded yet is
   the *evaluation* half of the loop.
