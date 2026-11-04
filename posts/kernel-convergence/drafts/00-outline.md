<!--
Status: OUTLINE for hand-off, 2026-11-01. Not yet a draft.
Source: Eric's cab-persistency project (Markov-switching current-account model), sessions of
2026-10-30 to 2026-11-01. The numbers below were measured in those sessions unless marked
"to re-run" or "projected".
Not part of the forecasting-methods series numbering (no NN prefix); it is a standalone
GAUSS post. No notebook/results pair: the benchmark is GAUSS code, see "Code for the post".
-->

# Outline: what GAUSS 27's kernel procs bought on a real estimation problem

## Notes for the drafting agent

- **Voice:** use the series voice in the root `CLAUDE.md`. This post fits it well:
  - the honest answer is mixed and interesting;
  - the keyword helps, but it was not the largest gain;
  - the biggest pay-off was what the speed let us discover.
  - Candidate motif: *does one keyword earn its place?*
- **Audience:** applied econometricians and GAUSS users who write their own likelihoods. Assume they know GAUSS procs and OPTMUM, but not Markov-switching filters in detail.
- **Check with Eric before drafting** (open items at the end): whether GAUSS 27 is public yet, whether Jason at Aptech should be named or reviewed, and how much of the unpublished research to mention. The research results themselves (country estimates, label changes) **stay out**. Only the computational story goes in.
- **Numbers:** quote the simulated-data demo as the reproducible headline. Use the 77-country project figures as supporting "real workload" evidence. Re-time both on an idle machine before publishing (see "To re-run").

---

## Working titles

1. *One Keyword, Nine Times Faster? What GAUSS 27's Kernel Procs Actually Bought Me*
2. *Compiling the Loop: GAUSS 27 Kernel Procs on a Markov-Switching Likelihood*
3. *The Speed-Up Was the Easy Part*. This one leans on the "speed exposed the science" section.

## Hook (question up front)

- Every applied econometrician has a likelihood with a loop in it that can't be vectorised away. In this one, a filter recursion runs over time.
- GAUSS 27 adds `kernel proc`: put one word in front of `proc`, and GAUSS compiles the procedure to machine code (it ships LLVM/Clang for this).
- *Does that actually matter on a real estimation problem, or only on toy loops?*
- The short answer:
  - the keyword gave a real but modest 1.4–1.7× on top of ordinary vectorisation;
  - a fully compiled rewrite gave about 2× more;
  - together, a likelihood call became roughly 15–20× faster than the original code.
- The more interesting answer: the speed changed which questions we could afford to ask, and some of the answers were uncomfortable.

## 1. The problem (short setup)

- **The model:** a Markov-switching ADF-type model of current account balances, estimated for 77 countries' quarterly series (39–260 quarters each).
  - It has three independent two-state chains (mean, variance, persistence), so 8 combined states and 20 parameters.
  - It is estimated by maximum likelihood with OPTMUM (BFGS with numerical gradients), from many starting values, plus a bootstrap.
- **Where the time goes:** almost all of it is likelihood evaluations.
  - A numerical gradient costs about 21 evaluations.
  - An optimisation takes hundreds of iterations.
  - The bootstrap repeats all of that about 1,000 times per country.
- **Starting point:** the inherited code computed everything inside one per-quarter loop: the densities, the 8×8 prediction step and the update.
  - A full bootstrap was projected at **18–22 serial days**.
- *Analogy option:* the Hamilton filter as reading a thermometer one day at a time, where each reading updates your belief about which "season" (regime) you are in. You can't read day 50 before day 49.

## 2. Step one, no new features: vectorise what can be vectorised

- **What changed:** compute all 8 state densities for all quarters at once, before the loop. Only the genuinely sequential step stays in the loop: `pred = PIG*bigP`, an elementwise multiply by that quarter's densities, then a sum, a log and a normalisation.
- **Result on 77 countries:** each call is 6.4× faster (`ofn`, the log likelihood) and 5.4× faster (`tofn`, per-observation, used for gradients) than the original.
- **Same numbers:** the largest scaled gap from the original was 1.4e-15 across 616 parameter points. The points covered all 77 saved estimates, random points, and "stress" points chosen to trigger the model's density cutoff and penalty branches.
- **Point for readers:** do this first. It is version-independent, and it is where most of the gain was.

## 3. Step two: the `kernel` keyword

- **What we did:** we moved the remaining loop into a self-contained proc that takes and returns plain matrices and uses no globals. Then we wrote it twice with the same body:
  - `proc` (the GAUSS 26 fallback);
  - `kernel proc` (GAUSS 27).
  - A `#define USE_KERNEL_PROC` line picks between them, so one file runs on both versions.
- **Accuracy:** in the default exact mode, the kernel and plain versions were **bit-for-bit identical at all 616 points**. Faster floating-point reordering (`reorder`) is opt-in, and we left it off.
- **Speed, 77 countries, one call per country summed:**

  | | Original | Vectorised, `proc` | Vectorised, `kernel proc` | Kernel vs plain |
  |---|---|---|---|---|
  | `ofn` | 0.083 s | 0.013 s | 0.009 s | 1.4× |
  | `tofn` | 0.069 s | 0.013 s | 0.009 s | 1.4× |

- **Speed, simulated demo (200 quarters, same model, fixed seed):**

  | | Original | Plain | Kernel |
  |---|---|---|---|
  | ms per likelihood call | 1.068 | 0.186 | 0.110 |
  | OPTMUM iterations to the optimum | 106 | 98 | 98 |
  | OPTMUM seconds | 5.32 | 0.79 | 0.48 |

  - The plain and kernel versions took the *identical* optimisation path (98 iterations, the same optimum, −269.717143). So the end-to-end gain of 1.63× is attributable to the kernel alone.
  - Against the original code: 9.7× per call and 11× per optimisation.
- **On real data, one full OPTMUM start:** 8.2× (Albania), 9.3× (Bolivia) and 10.7× (UK) faster than the original. These compare the original with the kernel version only; we didn't time OPTMUM with the plain version on real data.
- **Why only 1.4–1.7×? (Amdahl's law)**
  - By the time the keyword was added, the loop was the only interpreted code left. Plain minus kernel time implies it was at least about 30% of a call.
  - The rest is vectorised density code and call overhead, which the keyword doesn't touch.
  - **The loop's own speed-up is larger, but we never measured it in isolation.** That benchmark is worth adding for the post (see "To re-run").
- **Verdict line:** the keyword earned its place. It cost one word, and it changed no results.

## 4. Step three: write the whole thing as a kernel

- **Jason's v3 (Aptech):** Jason suggested a v3 that puts the densities *and* the recursion into one kernel proc, written as plain scalar loops so the whole likelihood runs compiled.
  - This is the opposite of usual GAUSS advice: in a kernel proc, scalar loops are fine, even preferred.
- **Result on 77 countries:**
  - 1.98× faster than v2 per `ofn` call, and 1.95× per `tofn` call;
  - 1.6–2.2× faster per optimiser iteration;
  - Jason measured about 3.5× on simulated data. Report both, and say plainly that the real workload gained less.
- **Accuracy:**
  - the log likelihood was bit-identical to v2 at 548 of 616 points;
  - the rest differed only by rounding (at most 3.4e-16 in the log likelihood, and 1.3e-14 in the residual output), because sums are accumulated in a different order.
- **Cumulative:** one likelihood call is roughly 15–20× faster than the original code.
- **Caveat to state:** v2's absolute times in the v3 test run were about double those in the earlier v2 run, which suggests machine load. The within-run ratios are the reliable figures. Re-time before quoting absolute numbers.
- **Trade-off:** v3 has no GAUSS 26 fallback. We kept v2 as the 26.1 path behind the same `#define`.

## 5. Gotchas we hit (a practical box for readers)

- **Dataframes are rejected.** The error was `G0165: kernel proc ...: argument 3 is a dataframe; kernel procs do not take dataframes yet: pass asmatrix(...)`.
  - We hit it twice. First the data series loaded with `loadd`, then a parameter vector that had also come from `loadd`.
  - Fix: convert everything with `asmatrix()` at the wrapper boundary, so no caller can pass a dataframe.
  - Jason's simulated data were plain matrices, so he never saw it. *Anyone loading real data with `loadd` will.*
- **Other limits we saw in error messages:**
  - arguments must be real matrices or scalars (no strings or empty matrices);
  - some functions are not allowed inside a kernel proc;
  - an index of 0 is not supported.
- **Silent fallback:** if the JIT is unavailable, GAUSS warns `kernel proc compiled as regular proc` and runs the proc as ordinary code. Results are still correct, just not faster, so watch for that line when benchmarking.
- **Documentation:** at the time there was no official `kernel proc` documentation. We worked from a minimal working example and the error messages. The drafting agent should check current Aptech docs and cite them.
- **Design advice that made the conversion trivial:**
  - make the hot loop a pure function of matrices: no globals, no strings, no dataframes;
  - keep a plain-`proc` twin behind a `#define`, and test the two against each other.

## 6. The other GAUSS 27 feature we tried: `minimize` (an honest null)

- **Background:**
  - `minimize` (L-BFGS-B by default) arrived in GAUSS 26 and was improved in 27;
  - GAUSS 27 adds a derivative-free Nelder–Mead option;
  - Jason suggested it might beat OPTMUM.
- **Simulated demo:**
  - L-BFGS-B took 163 iterations and 7,585 function evaluations, and stopped at −269.717148, just short of OPTMUM's −269.717143;
  - it took 0.84 s against OPTMUM's 0.48 s, with both using the kernel likelihood;
  - its time is almost exactly the number of evaluations × 0.11 ms.
- **Real data, 5 hard countries × 10 starts × 5 optimizer variants:**
  - OPTMUM found the best genuine optimum in 4 of 5 countries;
  - L-BFGS-B, with default or tight tolerances, never beat it and was 1.5–4× slower;
  - Nelder–Mead hit its 4,000-evaluation limit in every run, but as a *starting-point generator* followed by OPTMUM it found the best value for one country (US: −44.05 vs −45.96).
- **A lesson worth a sentence:**
  - some "best" end points had gradients around 1e9, so they were not maxima at all;
  - compare optimizers only after checking the gradient at the end point with one common rule.
- **Upside to mention fairly:** `minimize` ships with base GAUSS, so replicators don't need an OPTMUM licence, and it has a clean `bounds` option.
- **Framing:** the new optimizer didn't earn its place *on this problem*. That is a statement about this likelihood, not about `minimize`.

## 7. The real pay-off: what the speed let us find (the section that makes the post)

- **What changed in practice:**
  - a full 77-country run with 10 starts each took **288 seconds**;
  - the bootstrap projection fell from 18–22 serial days to about 2–2.5 days with v2, and roughly 1–1.5 with v3 (projected);
  - experiments that used to be unaffordable became routine.
- **With multistart affordable, we found:**
  - **Many local maxima.**
    - In 58 of 77 countries, only 1 of 10 starts reached the best value.
    - The previously saved (single-start) estimates were often not the global maximum.
    - The search grew to 100 random starts plus 5 independent perturbation chains: about 3–4 hours for all 77 countries, unthinkable at the old speed.
  - **Rounding-level differences change the answer.**
    - The original and vectorised likelihoods agree to 1e-15 at every point, yet from the same start OPTMUM converged to different optima.
    - So *exact* replication across code versions is the wrong standard here. The right one is "the same best value across many starts".
- **A non-GAUSS-27 reproducibility trap the speed work surfaced:**
  - on a failed line search, OPTMUM takes a random step (`_oprteps`), drawn from the global RNG;
  - unseeded, the same start gave different results run to run in one country;
  - fix: `rndseed` before every optimizer call, with a seed fixed by country and start.
  - A short, useful aside for anyone running multistart.
- **Small related note:** GAUSS 27's `csvWriteM` accepts at most 15 significant digits. That is not quite enough to round-trip a double, so resumable checkpoints were written with 17 digits via `sprintf`. Optional detail; include only if the post has a "practical notes" box.
- **Takeaway paragraph:**
  - the speed-up isn't the result, it's the instrument;
  - 10× faster didn't save me time so much as reveal that I'd been answering the question with too few starts.
- **Keep it generic.** Describe the discoveries as properties of this class of likelihood (mixture-type, multimodal), not as findings about specific countries' current accounts.

## 8. Takeaways (parallel-form list)

- **Vectorise first:** it is version-independent and was the largest single gain (about 6×).
- **Then compile the loop that can't be vectorised:** one keyword, identical results, 1.4–1.7× here; more if the loop dominates the call.
- **Then consider writing the whole hot path as a scalar kernel:** about another 2× on our workload; it costs the GAUSS 26 fallback.
- **Spend the speed on robustness, not just wall-clock time:** more starts, seeded optimizers, checks that the answer doesn't depend on which maximum the search found.

## Closing line options

- "The keyword earned its place. The multistart it paid for earned more."
- "Faster code didn't give me the answer sooner. It told me I didn't have the answer yet."

---

## Code for the post

- **Candidate code to share:** `kernel_demo/kernel_demo.gss` in the cab-persistency repo (`updated_2025/code/markov-switching/kernel_demo/`).
  - It is self-contained, simulates its own data (fixed seed) and runs from any working directory.
  - It prints the original, plain and kernel likelihoods and their timing, plus OPTMUM (all three versions) and `minimize` L-BFGS-B from the same start.
  - Its README describes the structure.
  - **Eric to decide** whether to publish it. It contains a copy of the project's original likelihood code, which is co-authored.
- **Snippet for the post:** a trimmed version of the kernel recursion signature and loop, showing that the body is ordinary GAUSS:

  ```gauss
  kernel proc (5) = __ms_filter_kernel(PIG, bigP, yu, dya, pas0, pas1, a_s, sig_s, eq_s);
      local n, lf, filt, t, i, ...;
      n = rows(dya) - 4;
      lf = zeros(n, 1);
      for t(1, n, 1);
          // residuals, the 8 state densities (0 beyond 15 sd), the prediction step,
          // the update and normalisation, all as scalar loops
      endfor;
      retp(...);
  endp;
  ```

  plus the call-site guard:

  ```gauss
  { ... } = __ms_filter_kernel(PIG, bigP, asmatrix(yu), asmatrix(dya), ...);
  ```

- **Suggested figure:** a horizontal bar chart of ms per likelihood call (original → vectorised → kernel loop → full kernel), with the multiplier labelled on each bar. A second panel could show "what fits in an hour" (optimisations per hour) to bridge to Section 7.

## To re-run before publishing

1. **Re-time on an idle machine.** Run the demo and the 77-country v2/v3 timing test, and report the medians of several runs.
   - `hsec` has 0.01 s resolution. Earlier figures averaged 50 calls (about ±5% on totals).
2. **Add a loop-only micro-benchmark:** time the recursion proc alone, plain vs kernel, on the same inputs. This gives the pure compile speed-up that Section 3 says we never isolated.
3. **v3 in the demo:** add Jason's full-kernel version as a fourth column, so the demo table shows all four stages on the same data.
4. **Optional:** `reorder` on vs off, to show what the opt-in mode buys and whether results still match exactly.

## Open questions for Eric

- **Timing:** is GAUSS 27 publicly released, or is a publish date or embargo tied to the release? Should Aptech (Jason) review the draft before it goes out?
- **Attribution:** name Jason, and credit him for the v3 full-kernel version and the `minimize` suggestion?
- **Research findings:** how much of the research context to include? The suggestion is the computational story only, with the model described generically and no country results.
- **Placement:** Medium alongside the forecasting series, or the Aptech blog? This affects how much GAUSS background to assume.
