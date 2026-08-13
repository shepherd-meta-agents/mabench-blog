# Tabulated results

All scores are sealed-test accuracy (fraction correct; τ² = task reward). "Δ" is
best-by-dev candidate minus the genesis (seed) agent, scored as the source posthoc batch
paired them. Test splits: 66 sealed items (GPQA/CharXiv), 55 (τ²); 3 reps per digest.
Dev splits: 67/66/55 items × 3 reps. **One full test or dev eval carries SE ≈ 0.035–0.05**
— single-cell deltas under ~4 pts are within one sigma. Machine-readable versions:
[data/sealed_test_luna.csv](data/sealed_test_luna.csv),
[data/worker_swap_haiku.csv](data/worker_swap_haiku.csv).

Setup: worker `gpt-5.6-luna` during optimization; meta model `gpt-5.6-sol` (sol arm) or
`claude-opus-5` (opus5 arm); τ² user-sim `gpt-5.4-mini`; CharXiv judge `gpt-5.4-mini`;
~72 h wallclock budget per run; seed tiers minimal / medium / strong; methods GEPA,
Meta-Harness (MH), AdaEvolve (minimal tier only). Cell suffixes s0/s1 are run seeds.

## 1. Sealed test, luna worker (primary metric)

### GPQA-Diamond

| cell | sol dev | sol: gen → best (Δ) | opus5 dev | opus5: gen → best (Δ) |
|---|---|---|---|---|
| minimal-gepa | .866 | .874 → .833 (**−4.0**) | .881 | .874 → .854 (−2.0) |
| minimal-mh | .891 | .854 → .894 (**+4.0**) | .891 | .854 → .848 (−0.5) |
| minimal-adaevolve | .866 | .838 → .859 (+2.0) | .886 | .838 → .864 (+2.5) |
| medium-gepa | .891 | .869 → .843 (−2.5) | .891 | .869 → .859 (−1.0) |
| medium-mh | .905 | .884 → .874 (−1.0) | .896 | .884 → .864 (−2.0) |
| strong-gepa | .905 | .869 → .874 (+0.5) | .915 | .869 → .884 (+1.5) |
| strong-mh | .866 | .869 → .904 (**+3.5**) | .915 | .869 → .869 (0.0) |

Mean Δ: sol **+0.4**, opus5 **−0.2**. Opus5 posts the higher dev peaks (.915 on both
strong cells) with nothing to show on test.

### τ²-bench

| cell | sol dev | sol: gen → best (Δ) | opus5 dev | opus5: gen → best (Δ) |
|---|---|---|---|---|
| minimal-gepa | .679 | .564 → .545 (−1.8) | .661 | .606 → .594 (−1.2)¹ |
| minimal-mh | .667 | .503 → .521 (+1.8) | .648 | .606 → .618 (+1.2)¹ |
| minimal-adaevolve | .739 | .515 → .576 (**+6.1**) | — | (run incomplete) |
| medium-gepa | .685 | .533 → .533 (0.0) | — | (run incomplete) |
| medium-mh | .691 | .545 → .473 (**−7.3**) | — | (run incomplete) |
| strong-gepa | .655 | .424 → .485 (**+6.1**) | .679 | .558 → .606 (+4.8)¹ |
| strong-mh | .673 | .436 → .521 (**+8.5**) | .709 | .558 → .582 (+2.4)¹ |

¹ Opus5 bests were served via the `openai/responses` route (default sampling); their
genesis baselines are the matched-route (`-lunaresp`) rescores. See
[caveats](#measurement-caveats) — the route alone moves genesis by +8–13 pts.

Sol mean Δ **+1.9** — the only benchmark with real transfer, concentrated in the
strong tier (weakest genesis, most headroom).

### CharXiv

| cell | sol dev | sol: gen → best (Δ) | opus5 dev | opus5: gen → best (Δ) |
|---|---|---|---|---|
| minimal-gepa-s0 | .747 | .722 → .727 (+0.5) | .788 | .722 → .732 (+1.0) |
| minimal-mh-s0 | .763 | .722 → .697 (−2.5) | .793 | .722 → .687 (−3.5) |
| minimal-mh-s1 | .742 | (= genesis, Δ 0) | .758 | .722 → .712 (−1.0) |
| minimal-ada-s0 | .778 | .722 → .682 (**−4.0**) | .753 | .722 → .722 (0.0)² |
| minimal-ada-s1 | .758 | .722 → .697 (−2.5) | — | |
| medium-gepa-s0 | .763 | .727 → .697 (−3.0) | .778 | .727 → .727 (0.0) |
| medium-gepa-s1 | .737 | .727 → .732 (+0.5) | .753 | .727 → .687 (**−4.0**) |
| medium-mh-s0 | .763 | .727 → .727 (0.0) | .773 | .727 → .727 (0.0)³ |
| medium-mh-s1 | — | (= genesis) | .742 | .727 → .732 (+0.5) |
| strong-gepa-s0 | .778 | .727 → .682 (**−4.5**) | .798 | .727 → .768 (**+4.0**) |

² digest identical to sol's minimal-ada-s1 best. ³ recovered checkpoint (corrupt trace).

Mean Δ: sol **−2.0**, opus5 **−0.3**. Dev gains of +2 to +7 pts across the board;
essentially nothing survives the sealed test. The one positive outlier (opus5
strong-gepa +4.0) is within 1σ.

### Grid-level summary (luna worker)

| | mean dev gain | mean test Δ | n cells |
|---|---|---|---|
| sol arm | +4.1 | **+0.0** | 22 |
| opus5 arm | +4.4 | **+0.1** | 20 |
| by method (sol): GEPA | +3.4 | −0.8 | 10 |
| Meta-Harness | +4.2 | +0.9 | 8 |
| AdaEvolve | +5.7 | +0.4 | 4 |

## 2. Worker-swap ablation (haiku-4.5 worker, same frozen digests)

Baseline effect of the swap: GPQA genesis drops .86→.61, CharXiv .72→.57, τ² .51→.47.
Δ below is best minus genesis, both under haiku.

| cell | sol Δ | opus5 Δ |
|---|---|---|
| gpqa medium-gepa / medium-mh | +2.5 / +3.5 | +3.5 / +4.5 |
| gpqa minimal-gepa / minimal-mh / ada | −0.7 / +0.8 / +1.9 | −1.5 / −1.5 / +1.9 |
| gpqa strong-gepa / strong-mh | −4.0 / −3.5 | −1.5 / −1.0 |
| τ² minimal-gepa / minimal-mh / ada | +1.8 / 0.0 / **+13.3** | −1.2 / −0.6 / — |
| τ² medium-gepa / medium-mh | +1.8 / +1.2 | — / — |
| τ² strong-gepa / strong-mh | **+6.1** / +4.8 | **+6.7** / **+7.9** |
| charxiv medium (gepa-s0/s1, mh-s0/s1) | +4.0 / −2.5 / +4.0 / — | +3.0 / −2.0 / +2.0 / **+7.1** |
| charxiv minimal (gepa/mh/ada) | −3.5 / +1.0 / −4.5 | −2.5 / −1.5 (s0) · −0.5 (s1) / −2.0 |
| charxiv strong-gepa | −2.5 | −2.5 |

Pattern: τ²-strong gains and GPQA-medium gains survive the swap in both arms; GPQA-strong
gains *invert*; AdaEvolve's structural τ² rewrite gains more under the weaker worker than
under the one it was optimized with. Details: [worker-portability](analysis/worker-portability.md).

## 3. Search statistics (from event traces, completed seed-0 runs)

Full table: [data/run_stats.csv](data/run_stats.csv). Representative rows:

| run | candidates | dev evals | $ total | $ meta | best found at |
|---|---|---|---|---|---|
| sol gpqa medium **gepa** | 197 | 88 | $59 | $7 | 68% of budget |
| sol gpqa medium **mh** | 34 | 27 | $42 | $6 | 48% |
| sol gpqa minimal **gepa** | 223 | 211 | $58 | $17 | 80% |
| sol gpqa minimal **mh** | 32 | 25 | $26 | $5 | 60% |
| sol gpqa minimal **ada** | 306 | 3 | $74 | $22 | 61% |
| sol tau2 strong **mh** | 21 | 19 | $29 | $4 | 93% |
| opus5 gpqa strong **gepa** | 117 | 61 | $131 | $8 | 66% |
| opus5 gpqa strong **mh** | 43 | 35 | $101 | $29 | 53% |
| opus5 charxiv minimal **gepa** | 524 | 191 | $55 | $22 | 83% |
| opus5 charxiv minimal **mh** | 88 | 81 | $88 | $58 | 20% |

Signatures: GEPA = many candidates, eval-dominated spend, winner timing a lottery
(from under 10% to over 90% of budget; best-dev moves in only 1–5 discrete jumps per
run), 40–60% of
proposals rejected in healthy runs but 96–98% *accepted* in the derailed memorizers
([gepa-run-anatomy](analysis/gepa-run-anatomy.md)). MH = few candidates, meta-heavy
spend (up to 66% for opus), winner early then plateau. AdaEvolve = hundreds of program
candidates, train-only selection (dev touched ~2–6× for stamping), champion-parent
hill-climb whose accepted steps (mostly +1 train task) sit below per-eval noise
([adaevolve-dynamics](analysis/adaevolve-dynamics.md)).

## Measurement caveats

1. **Test noise is ~1σ = 3.6 pts.** Same-digest rescores disagree by up to 2 pts (GPQA
   minimal genesis: .874 and .854 in the same batch). One documented sign flip: sol
   gpqa-minimal-mh's best scored **+4.0 vs genesis** in the posthoc batch but **−1.0**
   in the run's own `test_curve` — same artifact, opposite conclusion. Train evals are
   just as noisy: identical AdaEvolve code scored .892–.954 across five GPQA train
   evals (a 4-task spread), and the identical τ² seed scored .481 in one run and .593
   in another.
2. **Route confound (τ²).** The `openai/responses` route with default sampling scores the
   *same genesis digest* +8 to +13 pts above the chat-completions route (.606 vs .527
   minimal; .558 vs .430 strong). Opus5 τ² comparisons use matched-route baselines; the
   sol-vs-opus τ² comparison is *not* route-matched and should not be read cell-vs-cell.
3. **Best-by-dev ≠ trace-best.** For sol gpqa-strong-mh, the trace's best stamp is dev
   .920 but the posthoc "best" digest carries dev .866 — the posthoc selection used the
   stamped/registered candidate set. Similar small mismatches likely elsewhere.
4. **Incomplete cells** (qualified after run-tree reads — earlier drafts overstated
   this). Opus5 τ²: medium-GEPA is a 3 h stub and medium-MH ran 63 h without ever
   improving; both τ² AdaEvolve runs were cut at ~82–88 of 200 planned iterations
   (unsealed); but τ² minimal/strong GEPA **completed** (86–95 candidates each). Opus5
   CharXiv: the seed-1 GEPA runs died at launch (`method_launch:TimeoutExpired`); the
   seed-0 GEPA runs completed full 72 h budgets (421–524 candidates); two opus5 CharXiv
   MH bests are checkpoints recovered from corrupt traces. All three sol CharXiv MH runs
   lost their codex proposer to session crashes mid-run (strong-mh after 9 scored
   candidates — hence no strong-mh row in the CharXiv table; medium-mh after iteration
   8 of 40; minimal-mh after 12) — the surviving "best" candidates predate the crashes.
   All seed-1 runs are 1–2 h stubs; only the CharXiv seed-1 stubs registered scoreable
   bests (kept in the table above).
5. **AdaEvolve's genesis** is its own stamped iter-1 program, not the shared tier genesis
   — its Δ baselines differ from GEPA/MH in the same tier.
6. **CharXiv judge** is `gpt-5.4-mini` throughout; judge noise is inside the reported SE.
