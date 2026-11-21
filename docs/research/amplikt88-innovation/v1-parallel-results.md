# V1 spare triode in parallel: simulation results

Option B from [the innovation review](../../amplikt88-innovation-review.md#option-b--parallel-the-two-v1-triodes): tie the unused ECC83 section (pins 6/7/8) to the active one (pins 1/2/3). Simulation only. The production schematic and PCB are unchanged.

Plan: [docs/plans/v1-parallel-simulation.md](../../plans/v1-parallel-simulation.md). Scripts: [spice/parallel_v1.py](../../../spice/parallel_v1.py), [spice/parallel_v1_checks.py](../../../spice/parallel_v1_checks.py), [spice/parallel_v1_extra.py](../../../spice/parallel_v1_extra.py). Raw data: [spice/results/v1-parallel/](../../../spice/results/v1-parallel/) (`summary.json`, `checks.json`, `extra.json`).

## Variants

| Variant | Change | Per-section I_a | Notes |
|---|---|---|---|
| baseline | current schematic | 0.566 mA | V1_A 89.3 V, LTP_K 91.1 V |
| parallel_direct | sections tied, all values unchanged | 0.30 mA | V1_A drops to 69 V, LTP_K to 72 V, LTP anodes rise to 350 V. **V2's operating point is moved.** |
| parallel_scaled | tied, R3 470k→235k, R4 1.5k→750, R22 150k→75k, C12 22→44 µF, R9 180k→90k, C6 12→24 pF | 0.563 mA | Same per-section point as baseline; V1_A 88.7 V. β and the R9·C6 time constant are preserved |

Common conditions: ideal B+ 450 V and bias −65 V, RC driver rails as drawn, KT88 bias re-trimmed to 60 mA, 8 Ω resistive load, Koren valve models from `amplikt88.lib`, ngspice 44.2.

## Results

### Small signal (V1 from the model's own gm/ra at the solved operating point)

| | baseline | parallel_scaled |
|---|---|---|
| gm (stage) | 1.30 mA/V | 2.59 mA/V |
| ra (stage) | 81.5 k | 40.9 k |
| V1 open stage gain | 70.0 | 69.9 |
| **V1 output resistance** | **159 k** | **80 k** |
| Miller input capacitance (est.) | ~121 pF | ~241 pF |
| Grid-referred noise resistance (3/gm + R_k + R1) | 4.8 k | 2.9 k |
| Input noise, 20 Hz–20 kHz, thermal/shot only | 1.26 µV | 0.98 µV (−2.2 dB) |
| Closed-loop gain @1 kHz | 40.49 dB | 40.53 dB |
| −3 dB high, 0 Ω source | 38.0 kHz | 41.7 kHz |
| −3 dB high, 10 k source | 40.7 kHz | 50.1 kHz |
| −3 dB high, 47 k source | 40.7 kHz | **36.3 kHz** |
| Loop gain @1 kHz (voltage injection) | 17.4 dB | 17.8 dB |
| Upper unity crossing / PM, resistive load | 64 kHz / 94° | 88 kHz / 83° |
| Same, +100 nF load | 71 kHz / 76° | 98 kHz / 55° |
| Same, +1 µF load | 38 kHz / 55° | 45 kHz / 49° |
| 10 kHz square overshoot, open / 100 nF / 1 µF | 0.56 / 0.52 / 15.4 % | 0.43 / 0.40 / 15.2 % |

### THD at matched output power (8 Ω)

| Test | baseline | parallel_scaled | parallel_direct |
|---|---|---|---|
| 20 Hz, 10 W | 0.131 % | 0.126 % | — |
| 100 Hz, 37 W | 0.085 % | 0.084 % | — |
| 1 kHz, 1 W | 0.024 % | 0.023 % | — |
| 1 kHz, 37 W | 0.107 % | 0.106 % | **0.299 %** |
| 1 kHz, 60 W | 0.767 % | 0.756 % | **1.673 %** |
| 10 kHz, 10 W | 2.24 % | 2.25 % | — |
| 10 kHz, 37 W | not reachable (clips ~16 W) | not run (same limit) | — |
| 20 kHz, 1 W | 0.588 % | 0.559 % | — |

The 1 s / 512 points-per-cycle convergence runs agree with the 0.15 s runs to within 0.04 percentage points. Baseline: 1 kHz/37 W 0.109 %, 60 W 0.771 %, 10 kHz/10 W 2.20 %. parallel_scaled: 0.108 %, 0.761 %, 2.21 %.

The equal-input sweeps (`extra.json`) confirm this across levels. At 1, 10 and 20 kHz, parallel_scaled is within about ±10 % (relative) of the baseline THD at every level. It is marginally lower at low level and 10–20 kHz, and marginally higher near clipping. Clipping onset is the same, about 58 W at 1 kHz, where the KT88 grids reach 0 V.

## What this shows

1. **Direct parallel is harmful.** Without rebiasing, each section runs at half current, so V1's anode falls 20 V. Because V2 is DC-coupled, that drags the LTP down with it. THD at 37 W nearly triples. Do not simply tie the pins.
2. **Scaled parallel works but gives little.** V1's own gain and per-section linearity are unchanged by design, and the loop gain rises only 0.4 dB, so mid-band THD is the same. The gains are:
   - V1 output resistance halves (159 k → 80 k). This moves the V1→V2 Miller pole up, so there is ~4 kHz more closed-loop bandwidth and a higher loop crossover.
   - About 2 dB lower white-noise floor, if the source impedance is low. The amp is already roughly 105 dB below 60 W on this budget, so hum and flicker noise will dominate in practice.
3. **It brings real costs:**
   - Input capacitance doubles. With a 47 k source (passive pot at mid-travel) the bandwidth drops below baseline (36 kHz vs 41 kHz).
   - The higher loop crossover reduces phase margin into capacitive loads: 76°→55° at 100 nF and 55°→49° at 1 µF. C6/C15 would need retuning.
   - V1 draws twice the HT current (1.13 mA through a 75 k dropper).
4. **The HF power limit is downstream, not in V1.** At 10 kHz the amp reaches 1 % THD at only ~6 W and clips near 16 W, in both variants. Probing stage by stage, the V2 LTP differential output distorts first at HF (8.6 % at 60 V peak at 10 kHz vs 1.3 % at 77 V peak at 1 kHz), while the KT88 grids are still well short of 0 V. The loop is asking for more grid swing than the LTP can deliver. A rough estimate shows why: at 10 kHz, C15 330 pF + R26 10 k is about 49 k across the anodes. At 60 V differential that takes ~1.2 mA peak, on top of ~0.45 mA into R6/R7 and R11/R12. That reaches the ~1.17 mA standing current per side, so one LTP side cuts off. A lower-impedance V1 cannot fix that. V1's anode carries a larger corrective signal at HF only because the loop is working against the LTP's error.

## Verdict

Paralleling V1, correctly rebiased, is **electrically safe and roughly neutral**: slightly wider bandwidth and a little less noise, paid for with doubled input capacitance and less capacitive-load margin. It does not improve distortion or power.

The simulation suggests the weakness is **HF drive from V2**, not V1's output impedance.

**Follow-up:** this is confirmed in [spare-triode-comparison.md](spare-triode-comparison.md), which also simulates the cascode and the cathode follower. Moving the lag compensation from C15/R26 to V1's anode (15 k + 180 pF to ground) removes the 10 kHz power limit without using the spare triode. 10 kHz/37 W then measures 0.56 % THD; the baseline clips at ~16 W. Paralleled V1 combined with that fix (5.6 k + 430 pF) performs the same as the fix alone: 0.63 % at 10 kHz/37 W, with the same margins. That again leaves only the ~2 dB noise gain.

## Limitations

- Ideal B+ and bias supplies; the real PSU sag and ripple are not modelled.
- Simplified OT model (40 H primary, 24 mH leakage; the procurement target is ≤15 mH). The HF limit in point 4 depends on it and should be re-checked with measured OT data.
- Koren models have no noise or flicker; the noise figures are analytic (triode R_eq ≈ 3/gm). Section-to-section mismatch, microphony and heater–cathode leakage are not modelled.
- The loop gain uses single voltage injection at the secondary, valid because Zout ≪ Z_feedback. It is not a full return-ratio measurement.
- 10 kHz/37 W for parallel_scaled was not simulated. The drive search times out, and the baseline cannot reach that power either.
