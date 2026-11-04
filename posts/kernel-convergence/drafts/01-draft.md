<!--
DRAFT 1 (rev. 2: convergence-led framing), 2026-11-02. Standalone GAUSS post, not part
of the numbered series. Source of truth for every number: 00-outline.md in this folder.
Timings are from the 2026-10-30 to 2026-11-01 sessions and must be re-timed on an idle
machine before publishing (see the outline's "To re-run before publishing").
[TBD] markers are deliberate.
-->

# Is That Really the Maximum? How GAUSS 27's Kernel Procs Made Convergence Checking Affordable

Your optimiser reports convergence. The gradient is small, the iterations have stopped and the log likelihood looks reasonable. *How do you know it found the maximum, and not just a maximum?*

The honest answer for most of us is that we don't, because checking costs too much. The only real test is to run the optimisation again from many different starting points and see whether they agree. If one optimisation takes minutes and you have dozens of series and a bootstrap on top, you start once, maybe twice, and move on.

That's where I was with a Markov-switching likelihood. GAUSS 27 adds a feature that changed the arithmetic. Put the word `kernel` in front of `proc`, and GAUSS compiles the procedure to machine code (it ships LLVM/Clang to do this). Combined with some old-fashioned vectorisation, it made one likelihood call roughly **15–20× faster** than the code I started with.

The speed-up matters here mainly for what it paid for. Once multistart was cheap, I could finally test whether my estimates had converged to the right place. In 58 of 77 countries, the answer was: *probably not, from a single start.*

## The problem: a likelihood with many hills

**The model.** The model is a Markov-switching, ADF-type model of current account balances, estimated separately for 77 countries' quarterly series (39–260 quarters each). It has three independent two-state chains: one each for the mean, the variance and the persistence. That makes 8 combined states and 20 parameters, estimated by maximum likelihood with OPTMUM (BFGS with numerical gradients).

If you haven't met a Hamilton-style filter, think of reading a thermometer one day at a time. Each reading updates your belief about which "season" (regime) you're in, and you carry that belief into tomorrow. You can't read day 50 before day 49, so the core of the likelihood is a loop that can't be vectorised away.

**Why convergence is hard here.** Mixture-type likelihoods like this one are notoriously multimodal. Swap which regime is "high" and which is "low", let one state soak up a handful of outliers, and you get several distinct hills, each with a perfectly respectable peak. A gradient-based optimiser climbs whichever hill it starts on. Reporting "converged" tells you it reached a top. It doesn't tell you it reached *the* top.

**Why checking was unaffordable.** Almost all the run time is likelihood evaluations, and they multiply quickly:

- a numerical gradient costs about 21 evaluations;
- an optimisation takes hundreds of iterations;
- the bootstrap repeats all of that about 1,000 times per country.

With the code I inherited, which did everything inside one per-quarter loop, a full bootstrap was projected at **18–22 days** of serial computation. That was with one start per estimate. Adding multistart on top of that wasn't a realistic option.

## Buying starts: three steps to a faster likelihood

### Step one, with no new features: vectorise

I computed all 8 state densities for all quarters at once, before the loop. Only the genuinely sequential part stays inside: `pred = PIG*bigP`, an elementwise multiply by that quarter's densities, then a sum, a log and a normalisation.

On the 77-country workload, each call got **6.4× faster** for `ofn` (the log likelihood) and **5.4× faster** for `tofn` (the per-observation version used for gradients). Across 616 test points, the largest scaled gap from the original was 1.4e-15. The points included all 77 saved estimates, random points, and "stress" points that trigger the model's density cutoff and penalty branches.

This step works in any GAUSS version, and it was the largest single gain. Do it first.

### Step two: one keyword

I moved the remaining loop into a self-contained proc that takes and returns plain matrices and touches no globals. Then I wrote it twice with the same body, once as `proc` (the GAUSS 26 fallback) and once as `kernel proc`, with a `#define` choosing between them.

```gauss
// Illustrative structure only: the real filter body is supplied separately.
#define USE_KERNEL_PROC

#ifdef USE_KERNEL_PROC
kernel proc (1) = filterLoop(PIG, dens);
    // ... recursion body ...
endp;
#else
proc (1) = filterLoop(PIG, dens);
    // ... identical recursion body ...
endp;
#endif
```

[SNIPPET 1: cleaned excerpt of the real recursion proc, signature plus loop skeleton. Eric to supply from the research repo.]

On a simulated demo (200 quarters, same model, fixed seed):

| | Original | Plain | Kernel |
|---|---|---|---|
| ms per likelihood call | 1.068 | 0.186 | 0.110 |
| OPTMUM iterations to the optimum | 106 | 98 | 98 |
| OPTMUM seconds | 5.32 | 0.79 | 0.48 |

[TBD: re-time demo on an idle machine; add the full-kernel version from Step three as a fourth column.]

On the real 77-country workload the keyword gave 1.4× for both `ofn` and `tofn` (0.013 s → 0.009 s per pass, against 0.083 s and 0.069 s for the original). [TBD: re-time; report medians.] The gain is modest because of Amdahl's law: by this point the loop was the only interpreted code left, at least about 30% of a call, and the keyword can't speed up the rest. [TBD: loop-only micro-benchmark, plain vs kernel.]

**From a convergence point of view, the iteration row matters most.** In the default exact mode, the kernel and plain versions were **bit-for-bit identical at all 616 points**. So OPTMUM took the *identical* path with both: 98 iterations to the same optimum, −269.717143. The 1.63× end-to-end gain is pure speed, with no change in where the optimiser goes. As the next sections show, that isn't guaranteed. A faster floating-point mode (`reorder`) is opt-in, and I left it off. [TBD: optional re-run with `reorder` on vs off, and whether optimisation paths still match.]

### Step three: the whole likelihood as a kernel

[TBD: attribution. Draft assumes Eric approves naming Jason; otherwise "an engineer at Aptech".] Jason at Aptech suggested a v3 that puts the densities *and* the recursion into one kernel proc, written as plain scalar loops. That reverses the usual GAUSS advice: inside a kernel proc, scalar loops are fine, even preferred.

On the 77-country workload, v3 was **1.98× faster than v2 per `ofn` call** and 1.95× per `tofn` call, or 1.6–2.2× per optimiser iteration. Jason measured about 3.5× on simulated data. My real workload gained less, and both numbers are worth knowing. [TBD: re-time v2/v3 on an idle machine. v2's absolute times in the v3 run were about double the earlier v2 run, which suggests machine load, so only the within-run ratios are reliable for now.]

v3 is *not* bit-identical to v2. It matches exactly at 548 of 616 points, and the rest differ by rounding: at most 3.4e-16 in the log likelihood and 1.3e-14 in the residual output, because sums accumulate in a different order. That sounds negligible. On a likelihood with many hills, it may not be, for reasons that will become clear. v3 also has no GAUSS 26 fallback, so v2 stays as the 26.1 path behind the same `#define`.

[FIGURE 1: horizontal bar chart of ms per likelihood call: original → vectorised → kernel loop → full kernel, with multipliers labelled. Second panel: optimisations per hour, to bridge to the next section. TBD: build after re-timing.]

## What the speed bought: convergence you can actually check

For convergence, this is the game changer. The point isn't that each estimate finishes sooner. It's that checking whether an estimate has really converged went from out of reach to routine.

- A full 77-country run with **10 starts each** took **288 seconds**.
- The bootstrap projection fell from 18–22 serial days to about 2–2.5 days with v2, and roughly 1–1.5 days with v3 (projected, not yet run). [TBD: confirm v3 projection after re-timing.]

Then I ran the experiment I'd never been able to afford.

**Most single starts don't find the best maximum.** In 58 of 77 countries, only 1 of 10 starts reached the best value. The estimates I'd saved earlier, each from a single start, were often *not* the global maximum. OPTMUM had reported convergence every time. It just converged to a different hill.

So the search grew to 100 random starts plus 5 independent perturbation chains per country, which takes about 3–4 hours for all 77. At the original speed, that would have been unthinkable.

**Rounding-level differences change which hill you climb.** The original and vectorised likelihoods agree to 1e-15 at every point I checked. Yet from the same start, OPTMUM converged to *different* optima with each of them. A plausible mechanism is that on a likelihood this multimodal, a tiny difference early in the search can tip a line search toward a different ridge, and the paths never meet again. I haven't traced that step by step, so treat it as a hypothesis. The practical consequence holds either way: **exact replication across code versions is the wrong convergence standard here.** The right one is *the same best value across many starts.* The same logic is why I'd re-run multistart after switching to v3, or before turning on `reorder`, instead of assuming those rounding gaps don't matter.

**"Best" isn't the same as "converged".** Some end points with the highest log likelihood had gradients around 1e9. Those weren't maxima at all, just places where the search stopped. Before you rank starts, or compare optimisers, check the gradient at every end point with one common rule. Otherwise the winner may be a point that never converged.

**Unseeded optimisers make convergence irreproducible.** When a line search fails, OPTMUM takes a random step (`_oprteps`) drawn from the global random number generator. Without a seed, the same start gave different results from run to run in one country. The fix is cheap: call `rndseed` before every optimiser call, with a seed fixed by country and start. If you run multistart with OPTMUM, check this today.

[SNIPPET 3 (optional): seeding before each OPTMUM call, keyed by country and start index. Eric to supply or approve.]

None of this is about current accounts as such. These are properties of this class of likelihood: mixture-type, regime-switching, multimodal. If your model looks anything like that, the same questions probably apply, and a faster likelihood is how you get to ask them.

## Would a different optimiser converge better? (An honest null)

With starts now cheap, it was natural to ask whether a different optimiser would find better maxima. `minimize` (L-BFGS-B by default) arrived in GAUSS 26 and was improved in 27, which adds a derivative-free Nelder–Mead option. Jason suggested it might beat OPTMUM.

**On the simulated demo, no.** L-BFGS-B took 163 iterations and 7,585 function evaluations. It stopped at −269.717148, just short of OPTMUM's −269.717143, and took 0.84 s against OPTMUM's 0.48 s with the same kernel likelihood. Its time is almost exactly the number of evaluations × 0.11 ms.

**On real data, also no.** I ran 5 hard countries × 10 starts × 5 optimiser variants:

- OPTMUM found the best genuine optimum in 4 of the 5 countries;
- L-BFGS-B, with default or tight tolerances, never beat it and was 1.5–4× slower;
- Nelder–Mead hit its 4,000-evaluation limit in every run. Used as a *starting-point generator* followed by OPTMUM, it did find the best value for one country.

"Genuine" carries weight in that first bullet. The comparison only means something after the gradient check above.

In fairness, `minimize` ships with base GAUSS, so anyone replicating the work doesn't need an OPTMUM licence, and it has a clean `bounds` option. Those are real advantages. They don't change the result: **the new optimiser didn't improve convergence on this problem.** That's a statement about this likelihood, not about `minimize`.

## Gotchas we hit

> **Practical notes for converting your own code**
>
> - **Dataframes are rejected.** The error reads: `G0165: kernel proc ...: argument 3 is a dataframe; kernel procs do not take dataframes yet: pass asmatrix(...)`. I hit it twice: first with the data series loaded by `loadd`, then with a parameter vector that had *also* come from `loadd`. Fix: convert everything with `asmatrix()` at the wrapper boundary, so no caller can pass a dataframe in. Jason's simulated data were plain matrices, so he never saw this. *Anyone loading real data with `loadd` will.*
> - **Other limits I saw in error messages:** arguments must be real matrices or scalars (no strings, no empty matrices); some functions aren't allowed inside a kernel proc; an index of 0 isn't supported.
> - **Watch for the silent fallback.** If the JIT is unavailable, GAUSS warns `kernel proc compiled as regular proc` and runs the code as an ordinary proc. The results are correct, just not faster. Look for that line before you believe a "no speed-up" benchmark.
> - **Documentation.** When I did this work there was no official `kernel proc` documentation. I worked from a minimal example and the error messages. [TBD: cite current Aptech docs for `kernel proc`, if published by release.]
> - **`csvWriteM` precision.** GAUSS 27's `csvWriteM` accepts at most 15 significant digits, not quite enough to round-trip a double. For resumable multistart checkpoints I wrote 17 digits with `sprintf`. Given how much rounding mattered above, that wasn't pedantry.
> - **Design so the conversion is trivial.** Make the hot loop a pure function of matrices, with no globals, strings or dataframes. Keep a plain-`proc` twin behind a `#define`, and test the two against each other.

[SNIPPET 2: cleaned call-site excerpt showing `asmatrix()` applied to every argument at the wrapper boundary. Eric to supply.]

## Takeaways

- **Vectorise first.** It's version-independent, and it was the largest single gain here (about 6×).
- **Then compile the loop you can't vectorise.** One keyword, identical results and an identical optimisation path, 1.4–1.7× on this problem.
- **Then consider the whole hot path as a scalar kernel.** That gave about another 2× here, at the cost of the GAUSS 26 fallback and exact bit-for-bit agreement.
- **Spend the speed on convergence.** Run many starts, seed your optimisers, check gradients before ranking end points, and judge success by the same best value across starts, not by a single "converged" message.

The keyword earned its place. The convergence checks it paid for earned more. Faster code didn't give me the answer sooner. It told me I didn't have the answer yet.

---

*[TBD: code availability line. Depends on Eric's decision about publishing `kernel_demo.gss`, which contains co-authored likelihood code.]*

---

## Notes for Eric

1. **Open questions are still unanswered** (your earlier answers came through as template brackets). The draft still assumes: computational story only, moderate GAUSS background, and Jason named with a TBD flag at first mention. Timing/embargo and Aptech review are open.
2. **Tone shift (rev. 2).** Convergence is now the through-line: the hook asks whether a "converged" estimate is the maximum, and the speed sections are framed as "buying starts". I used "game changer" once, tied directly to the measured change (18–22 days → 1–2.5 days; 10 starts × 77 countries in 288 s). I kept it to one use so the post doesn't drift into the press-release framing CLAUDE.md warns against.
3. **New interpretive claims, all marked as hypotheses or advice, not findings:** (a) the paragraph on why mixture likelihoods are multimodal (label switching, outlier-absorbing states) is general background, not something measured here; (b) the mechanism for why rounding changes the optimum is labelled a hypothesis; (c) "re-run multistart after switching to v3 or turning on `reorder`" is advice. v3's convergence behaviour was *not* tested.
4. **Country names are still left out** (Albania/Bolivia/UK speed-ups, US Nelder–Mead values). Add them back if you're comfortable.
5. **Cut for length:** the 77-country speed table became one sentence, and the per-country OPTMUM 8.2–10.7× range was dropped. I moved the `minimize` section after the convergence section so it reads as "would a different optimiser converge better?". That departs from the outline's order.
6. **Snippet 1 is schematic.** Check the `#ifdef`/`#else` pattern against your real file. Figure 1 should wait for the re-timed numbers.
