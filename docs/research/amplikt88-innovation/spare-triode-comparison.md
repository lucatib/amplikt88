# Spare V1 triode: parallel, cascode, cathode follower and tail CCS, plus the C15/R26 fix

Simulation study of four ways to use V1's unused ECC83 section (pins 6/7/8): parallel, cascode, cathode follower and V2 tail current sink, compared against the current schematic. A separate change came out of the work: moving the HF lag compensation from V2's anodes to V1's anode. **That change is the one worth building first, and it does not need the spare triode.** Simulation only; the production schematic and PCB are unchanged.

Detail on the parallel option: [v1-parallel-results.md](v1-parallel-results.md). Options as first proposed: [innovation review §3](../../amplikt88-innovation-review.md#3-using-the-unused-v1-triode).

## Summary table

All variants: ideal B+ 450 V and bias −65 V, RC driver rails as drawn, KT88 bias re-trimmed to 60 mA, 8 Ω resistive load. THD figures are at matched output power. PM is the phase margin at the upper unity-gain crossing of the loop.

| | **Baseline** | **Parallel** (scaled) | **Cascode** (raw) | **Cascode** + 150k/100p | **Cathode follower** | **Lag at V1** (no spare triode) | **Follower + lag at V1** | **Parallel + lag at V1** |
|---|---|---|---|---|---|---|---|---|
| Variant name | `baseline` | `parallel_scaled` | `cascode` | `cascode_comp` | `follower` | `baseline_lag_damped` | `follower_lag_damped` | `parallel_scaled_lag_damped` |
| Compensation | C15/R26 at V2 anodes | C15/R26 | C15/R26 | C15/R26 + step at V1_A | C15/R26 | 15k + 180p at V1_A | 15k + 220p at V1_A | 5.6k + 430p at V1_A |
| V1 output resistance | 159 k | 80 k | ~470 k | ~470 k | ~2 k (follower) | 159 k | ~2 k | 80 k |
| Loop gain @1 kHz | 17.4 dB | 17.8 dB | **27.2 dB** | 26.7 dB | 18.1 dB | 17.4 dB | 18.0 dB | 17.7 dB |
| −3 dB bandwidth (0 Ω source) | 38 kHz | 42 kHz | 76 kHz (peaking) | 32 kHz | 46 kHz | 32 kHz | 30 kHz | 31 kHz |
| Bandwidth with 47 k source | 41 kHz | **36 kHz** | 135 kHz (peaking) | 33 kHz | 51 kHz | 30 kHz | 29 kHz | 27 kHz |
| PM, resistive load | 94° | 83° | 46° | 94° | 70° | 102° | 107° | 103° |
| PM, 100 nF | 76° | 55° | **11°** | 69° | **35°** | 94° | 92° | 96° |
| PM, 1 µF | 55° | 49° | **−2° (unstable)** | 53° | 41° | 62° | 67° | 63° |
| PM, low-frequency crossing | 83° | 82° | 57° | 57° | 81° | 83° | 81° | 82° |
| 10 kHz square overshoot, 1 µF | 15.4 % | 15.2 % | 38.3 % | 11.2 % | 13.8 % | 15.5 % | 10.0 % | 13.3 % |
| THD 1 kHz, 1 W | 0.024 % | 0.023 % | 0.008 % | 0.011 % | 0.022 % | 0.025 % | 0.023 % | 0.024 % |
| THD 1 kHz, 37 W | 0.107 % | 0.106 % | 0.034 % | 0.056 % | 0.101 % | 0.093 % | 0.091 % | 0.096 % |
| THD 1 kHz, 60 W | 0.77 % | 0.76 % | 0.56 % | 0.71 % | 0.72 % | 0.76 % | 0.76 % | 0.78 % |
| THD 10 kHz, 10 W | 2.24 % | 2.25 % | 1.30 % | 2.36 % | 2.00 % | **0.35 %** | **0.32 %** | **0.36 %** |
| THD 10 kHz, 37 W | clips at ~16 W | clips | clips at ~17 W | clips at ~17 W | clips at ~16 W | **0.56 %** | **0.58 %** | **0.63 %** |
| THD 20 kHz, 1 W | 0.59 % | 0.56 % | 0.33 % | 0.58 % | 0.50 % | **0.12 %** | **0.11 %** | **0.12 %** |
| 10 kHz power at 1 % THD | ~6 W | ~6 W | ~8 W | ~6 W | ~7 W | **~46 W** | **~45 W** | **~44 W** |
| 10 kHz clipping power | ~17 W | ~17 W | ~16 W | ~17 W | ~17 W | **~58 W** | **~57 W** | **~57 W** |
| V2 LTP_K across ECC83 spread (+25 % / nominal / −20 % emission) | 84 / 91 / 98 V | 84 / 91 / 98 V | **68 / 91 / 132 V** | same as cascode | 86 / 92 / 99 V | 84 / 91 / 98 V | 86 / 92 / 99 V | 84 / 91 / 98 V |
| Extra HT current | — | +0.56 mA | +0.17 mA (divider) | +0.17 mA | +1.0 mA | — | +1.0 mA | +0.56 mA |
| Parts changed | — | 6 values, 3 pin links | 3 values, divider + cap, 1 trimmed resistor | as raw + 2 parts | 3 parts, R5 re-routed | remove 2, add 2 | follower + lag parts | parallel values + lag parts |

Bandwidth-matched versions of the lag fix (`baseline_lag` 15k/150p, `follower_lag` 12k/180p) give 38 kHz bandwidth and almost the same THD. However, they ring 23 % into 1 µF, against 15 % for the baseline, so the damped values are the ones recommended. All variants are in `summary.json`.

## What each option does

### Parallel (both sections tied, values scaled)

R3 235k, R4 750, R22 75k, C12 44 µF, R9 90k, C6 24 pF. Each section runs at the same current as now.

- V1 output resistance halves, and the white-noise floor drops about 2 dB with a low-impedance source.
- THD, power and loop gain are unchanged. The stage gain is the same by design.
- Input capacitance doubles, so with a 47 k source the bandwidth is narrower than now. The capacitive-load margin is also lower (55° vs 76° at 100 nF).
- Tying the pins without rescaling (`parallel_direct`) drops V1_A by 20 V, drags V2's operating point with it, and nearly triples the THD at 37 W.

**Verdict: neutral. Not worth a board change.**

### Cascode (spare section stacked on top of the active one)

The active section stays at the bottom: grid = input, cathode = R4 and feedback. Its anode drives the cathode of the spare section, pin 8. The spare's grid, pin 7, is held at ~47 V by 2.2 M / 263.7 k from B_DRV, with 10 µF to ground. Its anode, pin 6, takes R3 and feeds V2 as now.

- **Fitting it in:** V2 is DC-coupled and needs V1_A ≈ 89 V. With R4 = 1.5 k the lower triode alone needs ~88 V, so R4 must drop to 680 Ω (R9 82 k, C6 27 pF, keeping β). Each triode then has only ~42–47 V across it, at about −0.3 V grid bias.
- **Benefits:** loop gain rises 10 dB, so mid-band THD falls about 3× (0.034 % at 1 kHz/37 W). Input Miller capacitance becomes negligible.
- **Stability:** as built it is unstable into 1 µF (PM −2°), at 11° into 100 nF, and peaking to 76 kHz. Compensating it at V1_A (150 k + 100 pF) restores the margins. It keeps about half of the mid-band THD gain (0.056 %), but 10 kHz performance is no better, because the C15/R26 limit (below) remains. The low-frequency margin stays at 57°, against 83° for the baseline. Coupling-cap and real-PSU motorboating margins would need checking.
- **DC drift:** this is the deal-breaker. The lower triode has little cathode degeneration and the stack has no spare voltage, so V1_A swings −24/+42 V across normal valve spread, against ±7 V today.
  - A strong valve saturates the upper triode (20 V across it, grid at +0.26 V, drawing grid current).
  - A weak one lifts V2's cathodes to 132 V and drops its anodes to 267 V.
  - A 1 % change in the divider moves V1_A by about 2 V.
  - Under HF overload the average V1_A moved from 89 V to 103 V.

  With the DC-coupled V2 this would need per-valve trimming or a DC servo.

**Verdict: the best THD on paper, but impractical with this DC-coupled topology.**

### Cathode follower (spare section between V1 and V2)

R5 (1 k) becomes the follower's grid stopper from V1_A. Its cathode, pin 8, drives V2's grid directly, with 91 k to ground (~1 mA). Its anode, pin 6, has its own dropper: 100 k + 22 µF from B_DRV gives ~338 V, ~247 V anode–cathode, ~0.25 W. Its cathode sits at ~90 V, below the 180 V heater–cathode limit and the same as V2's cathodes today. V2's tail current rises about 1 % (LTP_K 92.2 V vs 91.1 V).

- It isolates V1 from V2's ~44 pF Miller load. V1 now sees only a few pF.
- **Stability without retuning:** removing that V1→V2 pole costs phase margin (35° into 100 nF), so the compensation must be retuned.
- **THD, power, noise:** barely changed. 10 kHz is still limited by C15/R26.
- **DC:** it drifts with valve spread no more than the baseline does, which is the follower's advantage over the cascode.
- It adds 1 mA of HT and 3 parts. Both sections share one envelope, so they warm up together; the cold-start behaviour matches today's direct coupling.

**Verdict: safe and sound, but the problem it was meant to fix was not the bottleneck.**

## The real HF bottleneck: C15/R26 on V2

In every variant that keeps C15 330 pF + R26 10 k across V2's anodes, the amp clips near 16–17 W at 10 kHz with the KT88 grids still at −20 V. The loop is demanding grid swing that V2 cannot deliver.

At 10 kHz C15 + R26 is about 49 k across the anodes. At ~60 V differential it takes ~1.2 mA peak, on top of the ~0.45 mA drawn by R6/R7 and R11/R12. That reaches the ~1.17 mA standing current per LTP side, so one side cuts off. The LTP differential THD reaches 8.6 % at 60 V peak, against 1 % at 93 V peak once the network is removed.

### Fix: move the lag to V1's anode

Remove C15 and R26. Add **R 15 k in series with C 180 pF from V1_A (V1 pin 1) to ground**. The step network then sits on a node that swings only ~1–3 V, so its current is a few tens of µA. V2's anodes are left to drive only R6/R7, R11/R12 and the KT88 input.

At 10 kHz:

| | Baseline (C15/R26) | Lag at V1_A |
|---|---|---|
| 10 W | 2.24 % | 0.35 % |
| 37 W | clips at ~16 W | 0.56 % |
| Clipping | ~17 W | ~58 W, the same KT88 grid-limited ceiling as at 1 kHz |
| Power at 1 % THD | ~6 W | ~46 W |

Stability is at least as good as the baseline on every measure:

| | Baseline | Lag at V1_A |
|---|---|---|
| PM, resistive / 100 nF / 1 µF | 94° / 76° / 55° | 102° / 94° / 62° |
| 1 µF square overshoot | 15.4 % | 15.5 % |
| Bandwidth | 38 kHz | 32 kHz |

THD at 1 kHz/37 W improves slightly (0.093 % vs 0.107 %), and 20 kHz/1 W falls from 0.59 % to 0.12 %.

Parts:
- **Capacitor:** C0G or silver mica, rated ≥250 V (V1_A sits at 89 V DC and the rail can reach ~355 V while V1 is cold).
- **Resistor:** ordinary 0.25 W.
- **Removed:** C15 and R26.

The R15k/150p version keeps the original 38 kHz bandwidth, but rings 23 % into 1 µF.

The cathode follower adds almost nothing on top of this fix: 0.32 % vs 0.35 % at 10 kHz/10 W, 0.091 % vs 0.093 % at 1 kHz/37 W. The lag fix alone gets ~95 % of the benefit with no extra valve section, HT current or supply branch.

### Parallel V1 plus the lag fix

Paralleled V1 (`parallel_scaled` values) halves V1's output resistance to 80 k. To keep the same corner frequencies, the lag network is rescaled to half R and double C, then tuned for margins equal to `baseline_lag_damped`. Result: 5.6 k + 430 pF from V1_A to ground (`parallel_scaled_lag_damped`).

| | Lag at V1 (single triode) | Parallel + lag at V1 |
|---|---|---|
| THD 1 kHz, 37 W / 60 W | 0.093 / 0.76 % | 0.096 / 0.78 % |
| THD 10 kHz, 10 W / 37 W | 0.35 / 0.56 % | 0.36 / 0.63 % |
| THD 20 kHz, 1 W | 0.12 % | 0.12 % |
| 10 kHz power at 1 % THD / clipping | ~46 / ~58 W | ~44 / ~57 W |
| PM: resistive / 100 nF / 1 µF | 102° / 94° / 62° | 103° / 96° / 63° |
| 1 µF square overshoot | 15.5 % | 13.3 % |
| Bandwidth, 0 Ω / 10 k / 47 k source | 32 / 32 / 30 kHz | 31 / 30 / **27 kHz** |
| White-noise floor (analytic) | 1.26 µV | 0.98 µV (−2.2 dB) |
| Extra parts / HT current | — | 6 value changes, 3 pin links / +0.56 mA |

A bandwidth-leaning version (5.6 k + 360 pF, `parallel_scaled_lag`) gives 36 kHz bandwidth, 0.090 % at 1 kHz/37 W and 0.60 % at 10 kHz/37 W. Like `baseline_lag`, it rings 22 % into 1 µF.

**Verdict:** the combination works, and it is equivalent to the lag fix alone within simulation resolution. THD is very slightly higher, the stability trade is almost identical, and the bandwidth is narrower with a high-impedance source because of the doubled input capacitance. The only real gain is about 2 dB less white noise with a low-impedance source, which hum will mask in a power amplifier. Like parallel alone, it is not worth the extra changes.

## Spare triode as V2 tail current sink

The spare section replaces R8 (39 k, ~2.33 mA from LTP_K ≈ 91 V). Its anode goes to LTP_K and its cathode to ground through 4.7 k. Its grid is held at a fixed reference from a B_DRV divider (1 M over ~16–25 k, bypassed with 10 µF). Both variants are built on top of the lag fix and tuned to the same margins as `baseline_lag_damped`.

**The headroom problem.** The ECC83 is a low-current valve. In the model, sinking 2.33 mA needs a grid bias of +0.23 V at 90 V across the valve and +0.39 V at 80 V. That is a positive grid, so the valve cannot carry today's tail current in the ~90 V available.

Returning the cathode resistor to the −65 V bias rail is the usual escape, but it is ruled out here. The README records that the tail was moved *off* that rail: the half-wave bias supply sagged to −43 V under an 8 mA load. A CCS fault would also load the KT88 bias rail. That leaves two all-valve designs:

| | `ccs_low_lag` | `ccs_raised_lag` |
|---|---|---|
| Idea | Keep all DC levels; tail cut to 1.5 mA | Lift V1_A, and so V2's grids/cathodes, to ~155 V so the full 2.33 mA fits |
| Changes | R8 removed; R6/R7 100k → 150k (LTP anodes 329 V); CCS 4.7k + 1M/15.79k + 10µF | R8 removed; V1 rebiased: R3 362k, R4 2.65k, R9 318k, C6 6.8p (β and R9·C6 kept); CCS 4.7k + 1M/24.58k + 10µF |
| CCS operating point | 85 V, 1.5 mA, grid **−0.19 V** (−0.08 V with a weak valve: grid-current risk), 0.13 W | 145 V, 2.33 mA, grid −0.42 V (−0.24…−0.57 V across spread), 0.34 W |
| CCS output impedance ra + (µ+1)·Rk | ~420 k (11× R8) | ~515 k (13× R8) |
| Lag at V1_A | 15k + 180p | 15k + 120p (V1 has 2.2 dB less gain) |
| V2 heater–cathode | ~92 V | **~156 V**, 162 V with a weak V1 (limit 180 V) |

Results, with the recommended lag fix (`baseline_lag_damped`, R8 tail) as reference:

| | Lag fix, R8 tail | `ccs_low_lag` (1.5 mA) | `ccs_raised_lag` (2.33 mA) |
|---|---|---|---|
| LTP output imbalance (closed loop, 100 Hz–20 kHz) | 1.54 % | 0.19 % | **0.11 %** |
| Tail current across ECC83 spread (strong / nominal / weak) | 2.16 / 2.34 / 2.52 mA | 1.52 / 1.50 / 1.48 mA | 2.36 / 2.33 / 2.29 mA |
| LTP_K across spread | 84 / 91 / 98 V | 85 / 92 / 100 V | 150 / 156 / 162 V |
| Loop gain @1 kHz | 17.4 dB | 17.1 dB | 15.2 dB |
| PM: resistive / 100 nF / 1 µF; 1 µF overshoot | 102° / 94° / 62°; 15.5 % | 101° / 94° / 62°; 15.5 % | 99° / 93° / 62°; 15.9 % |
| Bandwidth (0 Ω / 47 k source) | 32 / 30 kHz | 32 / 30 kHz | 34 / 32 kHz |
| THD 1 kHz, 1 W | 0.025 % | **0.009 %** | **0.013 %** |
| THD 100 Hz, 37 W | 0.083 % | 0.167 % | 0.096 % |
| THD 1 kHz, 37 W | 0.093 % | **0.183 %** | 0.094 % |
| THD 1 kHz, 60 W | 0.76 % | **1.10 %** | 0.80 % |
| THD 10 kHz, 10 W | 0.35 % | 0.28 % | 0.33 % |
| THD 10 kHz, 37 W | 0.56 % | 0.84 % | 0.55 % |
| THD 20 kHz, 1 W | 0.12 % | 0.08 % | 0.09 % |
| 10 kHz power at 1 % THD | ~46 W | ~40 W | ~45 W |

**What it does:**
- The sink makes the LTP far better balanced: imbalance falls from 1.5 % to 0.1–0.2 %. Even-order products cancel better, so low-level THD falls 2–3×.
- The tail current stops depending on V1's anode voltage. That removes the ±8 % tail drift that valve spread causes today.

**`ccs_low` loses at high level.** At 0.75 mA per side, the LTP must swing ~±60 V into ~86 k of load near full power. That demands ~0.7 mA peak, so one side approaches cutoff, and THD at 37–60 W roughly doubles. Its −0.19 V grid bias also leaves almost no margin to grid current. Rejected.

**`ccs_raised` is the only workable valve CCS.** It halves low-level THD and gives the best LTP balance, and it matches the lag fix everywhere else despite 2.2 dB less loop gain. The price is a larger redesign:
- V1 is rebiased with 4 values changed, and V2 runs ~65 V higher above ground. Its heaters then come within ~20 V of the 180 V heater–cathode limit across valve spread. Heater elevation, the review's +40…+60 V proposal, would then be needed rather than optional.
- Five parts are added, including a non-standard divider value: a fixed part with a trimmer, or a 24.3 k + 270 Ω series pair.

The improvement shows mainly at levels where the amplifier is already at 0.01–0.03 %. Compare a semiconductor CCS (review item P2, ~2.3 mA in ~90 V): it gives the same balance benefit with no V1 rebias or heater-cathode penalty, but it is no longer all-valve.

**Verdict:** the tail sink is the only spare-triode use that measurably improves distortion once the lag is moved, and only in the `ccs_raised` form. It is a second-stage refinement: build and verify the lag fix first, and then decide whether a 2× lower low-level THD justifies raising V2 and elevating the heaters.

## Recommendation

1. **Build the lag move first:** remove C15/R26 and add 15 k + 180 pF from V1_A to ground. It removes the 10 kHz power limit, uses two fewer parts and no new supply, and leaves the spare triode free. Confirm on the bench with the real OT: square waves into resistive, 100 nF and 1 µF loads, and 10 kHz power at 1 % THD. Retune R/C there if needed, using the sweeps below as the starting map.
2. **Spare triode:** once the lag is moved, neither the cathode follower nor the scaled parallel connection buys measurable THD, power or stability. The parallel version gives only ~2 dB less white noise. The cascode is excluded by its DC drift. Leaving the section unused (pins 7/8 grounded as now) remains a valid choice. If the follower is built anyway, use `follower_lag_damped` (15 k + 220 pF at V1_A).
3. **Optional second step, tail current sink (`ccs_raised_lag`):** the one spare-triode use that measurably helps. It cuts LTP imbalance from 1.5 % to 0.1 % and halves low-level THD. However, it needs V1 rebiased to put V2 at ~155 V, plus heater elevation. Do not use the low-current version: it doubles THD at full power.
4. **Avoid** the cascode in this topology, and parallel without rescaling.

## Tuning map for the lag network (no follower)

| R / C at V1_A | PM: resistive / 100 nF / 1 µF | 1 µF overshoot | Bandwidth |
|---|---|---|---|
| 15k / 150p | 96° / 86° / 54° | 23.4 % | 38.0 kHz |
| **15k / 180p** | **102° / 94° / 62°** | **15.5 %** | **32.4 kHz** |
| 22k / 180p | — / — / 65° | 13.1 % | 31.6 kHz |
| 22k / 220p | 109° / 95° / 73° | 6.9 % | 26.9 kHz |
| 10k / 180p | — / — / 57° | 19.4 % | 34.7 kHz |

Higher C damps capacitive loads further at the cost of bandwidth; higher R raises the crossover. A dash means that margin wasn't simulated for those values.

## Reproduce

```text
cd spice
kicad-cli sch export netlist --format spice -o results/v1-parallel/source-export.cir ../amplikt88.kicad_sch
python3 parallel_v1.py --netlist results/v1-parallel/source-export.cir --variants baseline parallel_direct parallel_scaled cascode
python3 parallel_v1.py --netlist results/v1-parallel/source-export.cir --out results/v1-parallel-x --variants cascode_comp follower follower_lag follower_lag_damped baseline_lag baseline_lag_damped parallel_scaled_lag parallel_scaled_lag_damped ccs_low_lag ccs_raised_lag
python3 merge_results.py                     # folds results/v1-parallel-*/ into results/v1-parallel/summary.json
python3 parallel_v1_checks.py cascode cascode_comp follower follower_lag follower_lag_damped baseline_lag baseline_lag_damped parallel_scaled_lag parallel_scaled_lag_damped ccs_low_lag ccs_raised_lag
EXTRA_PLAN=hf python3 parallel_v1_extra.py baseline parallel_scaled cascode cascode_comp follower follower_lag follower_lag_damped baseline_lag baseline_lag_damped parallel_scaled_lag parallel_scaled_lag_damped ccs_low_lag ccs_raised_lag
python3 parallel_v1_spread.py
python3 parallel_v1_tail.py                  # LTP balance and tail spread, R8 vs triode CCS
python3 test_parallel_v1.py
```

Variants are defined in `variant()` in [spice/parallel_v1.py](../../../spice/parallel_v1.py). Results are in [spice/results/v1-parallel/](../../../spice/results/v1-parallel/):
- `summary.json`: DC, AC, loop, square-wave and THD for every variant.
- `checks.json` and `checks-variants.json`: source-impedance and capacitive-load loop checks.
- `extra.json` and `extra-hf.json`: THD sweeps with per-stage probes.
- `spread.json`: valve-spread DC check.
- `tail.json`: LTP balance and tail-current spread for the CCS variants.

## Limitations

- Ideal B+ and bias supplies; PSU sag, ripple and LF interaction with the real supply are not modelled. This matters most for the cascode's reduced low-frequency margin.
- Simplified OT model (40 H primary, 24 mH leakage; the procurement target is ≤15 mH). The HF behaviour and the lag values must be re-verified with the real transformer.
- Koren valve models: no noise, flicker, grid emission, microphony or section mismatch. The valve-spread check scales both sections of V1 together.
- The loop gain uses single voltage injection at the secondary (Zout ≪ Z_feedback). It is not a full return-ratio measurement.
- The cascode divider (263.7 k) is solved for the nominal model valve; a real build would need a trimmer.
