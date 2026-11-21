# amplikt88 circuit research and innovation review

Research date: 2026-11-21. Baseline: main at `2396b10`.

## Recommendation

The most useful first experiment with the unused half of V1 is a **DC-coupled cathode follower between the input amplifier and V2**. It addresses a specific weakness: V1's high output resistance driving V2's input capacitance. It does not directly increase the current available to the KT88 grids. A more ambitious alternative makes the spare triode a cathodyne phase splitter and repurposes both halves of V2 as separate voltage drivers.

Before comparing either variant, qualify the simulation measurements, establish the real output-transformer characteristics, and include the actual power supply. Otherwise a better-looking THD or stability figure may reflect the test method rather than the circuit.

These are established circuit techniques applied to this project, **not claims of a new invention**. Innovation here means a demonstrable improvement in bandwidth, distortion, overload recovery, noise, reliability or serviceability. No schematic, PCB or simulation program was changed for this review. No new SPICE or hardware performance result is claimed.

## 1. Evidence and scope

This report combines current schematic/netlist inspection, existing project studies, selected book passages, manufacturer data and original first-order calculations. It is a circuit-focused research collection, not an exhaustive reading or extraction of every book. Exact page references below distinguish passages inspected from further-reading pointers. The complete Blencowe books and complete *Building Valve Amplifiers* are not available in the repository; their samples cannot support a claim to have read those books.

Evidence labels used here:

- **Verified configuration:** values or connections inspected in the project files.
- **Reported simulation:** an existing project result, not rerun or independently validated here.
- **Estimate:** a calculation with stated simplifying assumptions.
- **Proposal:** a circuit or measurement change still requiring design and testing.

The [output/feedback evidence note](research/amplikt88-innovation/output-feedback.md) records additional source and simulation details. The XML netlist is a local inspection aid and is ignored by Git; the committed schematics remain the portable circuit reference.

## 2. Current circuit baseline

| Block | Verified configuration | Implication |
|---|---|---|
| Input | V1 ECC83, active section pins 1/2/3; R3 470k, R4 1.5k, R2 470k, input stopper R1 1k, C3 100nF | High voltage gain and high anode output resistance; cathode receives global feedback |
| Spare V1 section | Pin 6 anode unconnected; pins 7/8 grid/cathode grounded | Both heater halves are already powered. Using this section adds HT current, but no additional heater current |
| Phase splitter | V2 ECC83 LTP; R6/R7 100k, R8 39k; V1 directly coupled through R5 1k | Common-mode/DC operating point depends on V1's anode voltage |
| Second LTP grid | R10 1.8M supplies DC from the first grid; C16 2.2uF bypasses to ground | DC tracking and AC reference have a long settling time |
| KT88 drive | C7/C8 2.2uF/630V, R11/R12 200k, R13/R14 5k | Driver loading, grid-current onset and coupling-capacitor recovery must be evaluated together |
| Output | Two KT88, fixed bias, 4k plate-to-plate transformer, 40% UL taps, R17/R18 470 ohm screen stoppers | Screen current and actual transformer behaviour matter at high output |
| Bias | Individual 10k pots, R15/R16 27k, R27/R28 220k wiper-return resistors; 1 ohm cathode sense resistors | Wiper-contact protection exists; complete bias-supply-loss protection does not follow from it |
| Feedback | R9 180k parallel C6 12pF, secondary to V1 cathode | Retain this as the baseline, not older settings in narrative history |
| HF compensation | C15 330pF in series with R26 10k across V2 anodes | Values verified in the current schematic |
| HT | 330V/500mA AC winding, bridge, C1/C2 100uF/550V, L1 5H/300mA | Capacitor-input winding current is not equal to DC load current |
| Small-signal rails | R21 3.3k/C11 47uF to B_DRV; R22 150k/C12 22uF to B_V1 | Extra current in V1 has a large effect on rail voltage |
| Heaters | 6.3V/4.5A, R24/R25 100 ohm artificial centre reference to ground | V2 cathodes are well above heater DC potential |

The README reports approximately B+=450V, B_DRV=440V, B_V1=355V, V1 anode=89V, V2 cathodes=91V, V2 current=1.15mA per section, and KT88 cathode current=60mA each. It reports 60W at 1% THD and 0.11% THD at 37.3W. These remain **reported simulations**, with ideal B+ and bias sources.

### Baseline discrepancies to resolve

1. Older paragraphs recommend 680pF/4.7k compensation and 120k/18pF feedback; these are not the present schematic.
2. The transformer document gives conflicting power figures for alternative primary impedances. Do not combine those tables and paragraphs into one performance specification.
3. Its 4/16-ohm feedback-resistor suggestions also need recalculation for the current 180k baseline. For an unchanged output stage and equal output power, tap voltage scales with the square root of load impedance; preserving feedback requires approximately 127k/255k rather than treating old values as current. Exact values require the loaded loop calculation, and C6 must be reconsidered too.
4. The model's nominal whole-primary inductance is about 40H and its stated leakage approximation gives 24mH; the transformer purchase target specifies no more than 15mH. This is a model-versus-procurement difference, not a measured transformer defect.
5. Existing notes call V1's capacitive-load pole far above audio. The estimate below shows why that statement is too strong.

## 3. Using the unused V1 triode

> **Simulation results (2026-11-21):** [spare-triode-comparison.md](research/amplikt88-innovation/spare-triode-comparison.md) compares parallel, cascode and cathode follower against the baseline.
> - The parallel option is neutral.
> - The cascode gives the best THD, but is unstable as built and its DC point drifts badly with the DC-coupled V2.
> - The follower is safe but buys little.
> - As a V2 tail current sink returned to the bias supply's raw node, it is the one use that measurably helps: LTP balance improves 30× and low-level THD halves, with V1 and V2 unchanged.
>
> The 10 kHz power limit (~17 W) comes from C15/R26 loading V2's anodes. Moving that lag to V1's anode fixes it without the spare triode.

The pin numbers above identify the spare section unambiguously; do not rely on A/B unit names in imported netlists. The following diagrams are original topology sketches, not copied book figures or complete build circuits.

### Option A — cathode follower before the existing LTP

```text
Input -> V1 active triode -> V1 spare cathode follower -> V2 LTP -> KT88 pair -> OT
           ^                                                         |
           +---------------- existing global feedback ----------------+
```

**Why it is worth testing.** Using Philips' approximate low-current parameters, mu=100 and ra=80k, the present input stage has:

```text
Rout(V1) ~ 470k || [80k + 101 * 1.5k] = 155k ohm
LTP effective anode load ~ 100k || 200k = 66.7k ohm
LTP single-output gain ~ 100 * 66.7k / [2 * (62.5k + 66.7k)] = 25.8
Estimated LTP input capacitance ~ 1.6pF + 1.6pF * (1 + 25.8) = 44.5pF
Local pole ~ 1 / (2*pi*155k*44.5pF) = 23kHz
```

This simplified estimate neglects finite-tail effects, cathode bootstrapping of grid-cathode capacitance, stray capacitance, frequency-dependent gain and the global loop. It identifies a plausible bottleneck, **not the closed-loop -3dB frequency**. The deliberate C15/R26 network may remain the dominant limitation even after buffering.

An ECC83 follower at roughly 1mA, with ra around 62.5k and mu around 100, driven by the existing high-impedance stage, has an estimated low-frequency output resistance:

```text
Rout(follower) ~ (ra + source resistance)/(mu + 1) || cathode load
              ~ (62.5k + 155k)/101 || cathode load
              ~ 2.1k ohm for a large cathode load
```

Using only `1/gm` would understate output resistance because V1 does not provide a zero-impedance source. The follower also presents much less Miller loading to V1. These are reasons to test it, not a promise of lower amplifier THD or increased output power.

**Required design changes:**

- Bias the follower to deliver approximately the DC level V2 needs, then solve all stages together. A cathode voltage near 90–92V at 1mA suggests a cathode resistance near 90k as a starting estimate, not a final part value. Follower grid-to-cathode offset changes V2's tail current and anode headroom.
- Give the follower a suitable decoupled supply. Adding 1mA behind R22=150k would require another 150V drop at the old operating point; B_V1 cannot simply remain 355V. A new supply branch or redesigned dropper is necessary.
- Do not simply connect its anode to B_DRV=440V: with a 91V cathode this implies about 349V anode-to-cathode, above the inspected Philips ECC83 300V operating limit. A lower rail must also have startup and mains headroom.
- Reconnect R10 so both V2 grids receive the intended common DC reference. Account for C16's charge-up and discharge paths.
- Check cold start, unequal warm-up, hot restart and loss of either triode's emission. With direct coupling, a cold upstream stage can force a downstream grid far above its normal voltage.
- Retain suitable grid/output isolation at the sockets and check follower parasitic oscillation. Redesign the HF compensation after changing the plant.

**Expected scope of benefit:** reduced interstage loading and possibly better HF balance/linearity. It does not buffer C7/C8 from KT88 grid current, since V2 still directly drives them.

**Acceptance:** at matched output power, bandwidth and feedback, demonstrate improved HF distortion or response without worse LF/HF stability, startup stress, noise or clipping recovery.

### Option B — parallel the two V1 triodes

```text
Input -> V1 sections in parallel -> existing V2 LTP -> KT88 pair
```

At unchanged per-section operating point, effective ra halves and gm doubles. An approximate scaling is to halve the common anode resistor and cathode resistor, and revise the supply dropper for twice the current. With comparable stage gain, output resistance can approach half the original value.

The costs are doubled input capacitance, more HT current, possible extra source/potentiometer loading, and changed feedback injection. Halving R4 while retaining R9 approximately halves the resistive feedback fraction: this is not a drop-in modification. Two independent, equal valve-noise sources could yield up to about 3dB less equivalent input voltage noise under ideal conditions; resistor noise, hum, correlated noise and source impedance can erase that benefit.

**Ranking:** a simpler alternative if measured input-stage noise or loading is the problem. Test against Option A rather than assuming two triodes must sound better. Do not tie sections together while retaining all existing bias values.

### Option C — cathodyne plus dedicated push-pull drivers

```text
Input -> V1 active gain stage -> V1 spare cathodyne --+-> V2 section 1 -> KT88 1
                                                   +-> V2 section 2 -> KT88 2
```

This uses all four small-signal triodes. V1's spare section produces opposite-phase signals; V2's sections become separate common-cathode voltage drivers, with independent bias arrangements rather than the existing LTP tail. It separates phase splitting from large-signal voltage drive.

It is the strongest architectural candidate if **loaded KT88 drive** is the actual bottleneck. However, retaining ECC83 sections at similar currents does not automatically provide a low-impedance power-valve driver. Evaluate a properly biased ECC81 or ECC82 in V2 as a separate variant, with its own voltage, dissipation, heater-cathode and supply checks; it is not just a tube substitution. Lower mu changes the available loop gain.

The cathodyne must see balanced loads. Additional coupling networks or direct-coupling level shifts change LF stability and startup behaviour. Polarity through the added inverting driver stage must be verified before closing feedback. This option requires a new signal-path design and likely PCB rerouting.

**Ranking:** second-stage investigation after the baseline establishes whether drive swing, drive impedance or first-stage loading dominates. Do not infer AB2 capability merely from adding drivers.

### Other uses and exclusions

- **V1 spare as a constant-current tail for V2:** possible as an all-valve experiment, but a bare triode is not an ideal current sink. At approximately 2.3mA total LTP current and only about 91V available, its load line, degeneration and bias-reference headroom need solving. Its heater is shared with the near-ground input stage. A suitably rated semiconductor CCS is usually more practical if hybrid circuitry is acceptable.
- **Extra common-cathode gain stage:** low priority. The existing amplifier already has very high sensitivity; extra gain and inversion add compensation work without addressing a demonstrated shortage.
- **Input buffer ahead of V1:** useful only if the actual source impedance/input-capacitance problem dominates. It leaves the V1-to-V2 high-impedance interface intact.
- **One follower for both KT88 grids:** not possible as two independent opposite-phase outputs. Two buffer paths are needed. A White cathode follower or SRPP also needs more than the single unused section if the existing gain stage is retained.
- **Leave it unused:** keep as the control case. Using every section is not itself a performance metric.

## 4. Other improvements, ranked by evidence and cost

| Priority | Proposal | Circuit-specific benefit to investigate | Main cost or failure mode |
|---|---|---|---|
| P0 | Qualify simulator measurements and reconcile documentation | Makes A/B conclusions credible | Engineering effort before any new performance claim |
| P0 | Measure OT and optimize compensation for it | Less unnecessary roll-off while retaining reactive-load margin | Winding resonances and core nonlinearity cannot be inferred from a simple model |
| P1 | Bias-loss/overcurrent supervision using R19/R20 | Detect supply loss, drift and dangerous imbalance; improve serviceability | Monitor failure must not cause loss of negative bias; shutdown must deal with stored HT energy |
| P0 | Move HF lag from C15/R26 (V2 anodes) to 15k + 180pF at V1 anode ([simulated](research/amplikt88-innovation/spare-triode-comparison.md)) | 10 kHz power at 1 % THD ~6 W → ~46 W; margins ≥ baseline | Bandwidth 38 → 32 kHz; must be re-verified with the real OT |
| P1 | Evaluate V1 follower with an appropriate rail ([simulated](research/amplikt88-innovation/spare-triode-comparison.md): safe, small gain once the lag is moved) | Lower V1-to-V2 loading | Supply, startup and loop redesign |
| P1 | Heater elevation and measured grounding improvements | Reduce heater-cathode stress and measured hum | Shared-heater limits, leakage and startup reference behaviour |
| P2 | Constant-current LTP tail, near present 2.3mA total ([simulated](research/amplikt88-innovation/spare-triode-comparison.md#spare-triode-as-v2-tail-current-sink) with the spare ECC83 returned to the bias supply's raw node: LTP imbalance 1.5 % → 0.05 %, low-level THD halved, V1/V2 unchanged, single faults move the KT88 bias ≤ 10 %) | Improve balance and rejection of common disturbances | More gain/bandwidth can reduce margins; HV device parasitics and compliance |
| P2 | Optimize C7/C8 against overload recovery | Shorter bias displacement after clipping | Smaller capacitors can compromise LF gain/phase separation |
| P2 | Dedicated regulated/filtered small-signal rail | Reduce DC drift and supply-mediated interaction | Pass-device voltage/SOA, dissipation, startup and regulator stability |
| P2 | Slow automatic idle-current/balance servo | Compensate ageing and maintain transformer DC balance | Must not follow class-AB signal current; faults, wind-up and LF interaction |
| P3 | Cathodyne with dedicated V2 drivers | More freedom in loaded driver design | Large topology and board change; more poles or difficult DC coupling |
| P3 | Custom cathode/tertiary feedback winding | Local output-stage correction | New transformer, extra drive requirement, coupling and polarity risk |

### Output stage, overload and dissipation

The 1 ohm resistors measure **cathode current**, including screen current. Thus 60mV means 60mA cathode current, not 60mA anode current. `450V * 60mA = 27W` is an approximate upper estimate for idle anode dissipation before subtracting screen current and voltage drops. The KT88 model explicitly understates screen-current growth at low anode voltage, so it cannot certify screen dissipation during clipping.

Check the complete DC grid-return resistance, including the 5k stopper and the bias network's Thevenin resistance. With an ideal bias rail, the normal worst-case pot resistance is approximately `(10k || 27k) || 220k = 7.06k`, making the nominal total about **212k**, not 200k. This is close to the 220k fixed-bias limit listed for the lower-dissipation condition in the local KT88 sheets. Tolerances, dissipation conditions and the actual fitted valve's sheet matter; a 5% 200k part consumes much of the margin. The wiper-failure path is a different circuit state and must be tested for cutoff, not assumed to retain the same resistance limit.

`R11*C7 = 0.44s` and `R10*C16 = 3.96s` are useful simplified recovery scales, not complete time-domain predictions. Compare clipping bursts and recovery as well as steady sine THD. Lower grid-return resistances would increase driver loading; this connects directly to Option C or dual output buffers.

### Bias protection before automatic bias

Use the existing sense resistors for independent current monitoring. A useful first development is a fault-latched system that inhibits HT until the negative bias is valid and responds to bias loss or sustained overcurrent. Thresholds and timing must allow normal signal peaks and warm-up. Opening an HT feed does not instantly remove charge from C1/C2; retain bias and evaluate stored-energy decay. Do not use a speaker-disconnect relay as the only response, leaving an actively driven valve output transformer unloaded.

A later slow servo could control idle current and DC balance, but averaging music-driven cathode current and calling it idle current is incorrect in class AB. Specify signal qualification, startup inhibit, correction limits, sensor-failure behaviour, and an independent overcurrent limit. A firmware crash must not command maximum conduction. This is a proposal, not an implemented protection circuit.

### Heaters, grounding, supply and temperature

The inspected Philips ECC83 sheet gives 300V operating anode voltage, 1W anode dissipation and 180V cathode-to-heater limit (PDF p.5); check the fitted brand and polarity conventions too. With cathodes near 0.84V and 91V, a shared heater reference around **+40 to +60V** is a plausible experiment to reduce the largest normal voltage difference. It needs a filtered, defined DC reference and checks at both ends of the heater AC swing, during start/stop and under faults. Its benefit to hum must be measured, not presumed. Include the data sheet's heater-cathode circuit-resistance condition when changing the return network.

The heater load is approximately `2*1.6A + 2*0.3A = 3.8A`, plus the 100-ohm balancing pair's approximately 31.5mA. Activating the spare V1 section does not change this. Rectifying the existing winding for DC heaters is not automatically within the same RMS-current/voltage budget.

Keep the bridge/reservoir charging-current loop local to the supply. The amplifier board's star-shaped ground does not prove the off-board return paths are quiet. Trace speaker return, KT88 cathode return, bias sensing and input/feedback reference separately; use Kelvin sense returns for millivolt measurements. Maintain the protective-earth chassis bond independently of signal-ground experiments. The PCB clearance rules and DRC results are design checks, not an electrical safety certification.

With the PSU study's 346Vrms no-load winding assumption, the unloaded peak is approximately 489V nominal and **538V at +10% mains**, before diode drops. That is more informative than assuming a fixed 470V cold rail. The 550V reservoir and 500V small-signal capacitors require actual part/surge specifications and startup waveforms. R3 sees roughly 266V at the reported idle point: specify its voltage rating, not merely its footprint or wattage.

The PSU study reports roughly 525mA and 542mA winding RMS at its 60W and 70W load cases, against a 500mA rating. Do not call that a verified continuous-sine capability just because average music demand is lower. Incorporate realistic source impedance, B+ sag, rectifier pulses, choke behaviour and dynamic amplifier current in the comparison. A different rectifier or a larger reservoir is not a free improvement: both can change charging peaks and interference.

For the existing horizontal KT88 arrangement, verify mounting permissions of the actual valves and hot component temperatures. Moving film capacitors behind the board reduces direct exposure but does not establish their operating temperature or the insulation to the bracket.

## 5. Validation plan before selecting a design

### Correct the comparison method

Inspection of `spice/simulate.py` shows `power_test(freq)` leaves the source at 1kHz while changing the harmonic-analysis frequency. It also uses a fixed 12ms transient window and equal-weight harmonic sums over samples without explicit uniform resampling. `ot_study.py` has related frequency and fixed-input-versus-fixed-output comparison issues. These need correction and convergence checks before extending the published tables.

`loop_response()` uses a grid-to-output open-loop response multiplied by a passive divider approximation. Cathode injection and its loading are not equivalent to that simple divider in all conditions. Use a loading-preserving return-ratio measurement and compare it with closed-loop response and transient behaviour. Do not claim the documented phase margins have been disproved; they have not been independently established here.

### Run controlled variants

1. **A0:** current schematic and actual supply/OT parameters, as the control.
2. **A1:** V1 spare follower, revised rail and DC operating points; initially retain baseline compensation to expose the change, then retune for a fair comparison.
3. **A2:** parallel V1 sections with scaled bias/supply/feedback networks.
4. **A3:** semiconductor CCS replacing the LTP tail, near the original total current.
5. **B1:** cathodyne plus independent drivers, only after identifying A0's loaded drive limitation.

Compare variants at both equal closed-loop bandwidth/feedback and each variant's achievable robust optimum. Record sensitivity, noise and power consumption as well as distortion. Use actual source impedance and identical output power; a lower-gain circuit should not appear better merely because it is driven less hard.

### Required observations

| Test | What it resolves |
|---|---|
| DC points and dissipation at mains/tube/tolerance corners | Whether nominal bias survives real spread |
| 20Hz, 100Hz, 1kHz, 10kHz, 20kHz at feasible equal output powers | Whether an improvement is only mid-band; do not demand full 70W at 20Hz from this OT specification |
| Grid-to-cathode waveforms of V2 and both KT88s; screen currents | Which stage actually runs out of headroom |
| HF and LF return ratio; all unity crossings | Whether compensation remains robust |
| Resistive and documented RLC speaker loads; 0.1uF/1uF shunts as stress cases | Reactive-load sensitivity, not just the 8-ohm resistor case |
| Low-level square waves and controlled LF/HF clipping bursts | Ringing, saturation and recovery |
| Cold start, hot restart, shutdown, bias loss and sense-path faults | Reliability and DC-coupling interactions |
| Input shorted/terminated noise spectrum and source-impedance sweep | Whether hum, valve noise or capacitive loading is dominant |
| Thermal soak, winding RMS current and capacitor ripple current | Continuous operating capability |

Provisional engineering goals, not measured achievements: at least 60 degrees phase margin and 10dB gain margin across the agreed model corners, no sustained oscillation, and no component-limit violation. Avoid sacrificing overload recovery for a small nominal THD improvement. Thresholds and test loads must be defined before final optimization. Destructive open-load fault testing is not an ordinary listening/bench test.

## 6. Source map

PDF page numbers are one-based. For Jones, inspected printed pages correspond to PDF page = printed page + 15. Source descriptions are deliberately brief; the proposed modifications and calculations above are our application analysis.

| Source | Inspected location / status | Use in this review |
|---|---|---|
| [Jones, Valve Amplifiers, 3rd ed.](references/morgan-jones-valve-amplifiers-3rd-edition.pdf) | Printed 100–102 / PDF 115–117; 127–128 / PDF 142–143; 396–398 / PDF 411–413; 408–409 / PDF 423–424; 458 / PDF 473, visually checked | Follower impedance, differential pair, separate drive, loading and stability |
| [Crowhurst and Cooper](references/crowhurst-cooper-high-fidelity-circuit-design-1956.pdf) | PDF 39, 64, 108, 110–111, 113; recorded in evidence note | Compensation, tolerance, balance and alternative feedback windings |
| [Linsley Hood](references/linsley-hood-valve-and-transistor-audio-amplifiers.pdf) | PDF 80–81, 88, 112–113, 128; recorded in evidence note | Transformer limitations, reactive loads and output-stage feedback |
| [Blencowe grounding chapter](references/blencowe-tube-preamps-grounding-chapter.pdf) | PDF 2 and 8–10 inspected; use the local file's page numbers, not an assumed book edition | Chassis arrangement, earth bond and charging-current return paths |
| [Blencowe PSU sample](references/blencowe-power-supplies-sample.pdf) | PDF 4 (printed 88), PDF 8 (printed 239) inspected; sample only | Stage decoupling and heater interference |
| [Philips ECC83](datasheets/ecc83-philips.pdf) | PDF 2, 4, 5 visually checked | Capacitance, typical operating points, example phase splitting and ratings |
| [Genalex KT88](datasheets/kt88-genalex-gold-lion.pdf), [JJ KT88](datasheets/kt88-jj.pdf) | Genalex PDF 2–3; JJ PDF 1 inspected | Dissipation/current definitions and grid-return limits |
| [Blencowe direct-coupled follower](https://www.valvewizard.co.uk/dccf.html), [AC follower](https://www.valvewizard.co.uk/accf.html) | Author's pages consulted | Poorly biased followers can draw grid current; output resistance and stability need checking |
| [Blencowe heaters](https://www.valvewizard.co.uk/heater.html) | Author's page consulted | Defined heater reference and shared winding/current considerations |

Further reading already indexed in [references/README.md](references/README.md), **not newly read end-to-end in this review**: Mullard chapters 3/5/6 for the direct-coupled LTP precedent; GEC chapters 4/5 for KT88 amplifiers with separate drivers; Radiotron chapters 5/7/12–14/21/30–31 for transformer, stage, feedback and supply theory; Valley–Wallman chapters 9/10 for loop stability; Williamson for driver/transformer co-design. Jones' contents also point to power supplies at printed p.292 onward. The local *Building Valve Amplifiers* file is only a 19-page preview and is not used as evidence for a complete construction method.

## 7. Proposed decision

Keep the present circuit as the reference. First establish reliable comparison measurements; then prototype **Option A, the V1 spare follower with its own correctly designed supply branch**, alongside the simpler parallel-V1 alternative. Add current monitoring and examine heater elevation independently so their effects can be measured separately. Pursue cathodyne/dedicated drivers only if the loaded driver tests justify the larger redesign.

This sequence uses the spare triode for a measurable purpose, preserves a control circuit, and avoids conflating more stages or more feedback with better performance.
