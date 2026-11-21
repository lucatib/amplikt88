# Output stage, transformer and global feedback: evidence note

## 1. What circuit and results are actually established?

### Takeaway
The current circuit is a conventional fixed-bias ultralinear KT88 pair with secondary-to-input-cathode feedback. File inspection validates its topology and values; no hardware performance or fresh simulation result is validated here. Research performed 2026-11-21 in the main checkout; no simulation was rerun. The local XML netlist used below is a generated, Git-ignored inspection aid; use the committed schematic when reading this note from a fresh checkout. See the [consolidated review](../../amplikt88-innovation-review.md) for V1 spare-triode options and the complete recommendation.

### Cited Findings
- The schematic and XML netlist agree: V3/V4 anodes connect to TR2 pins 1/5; screens connect through R17/R18, 470 ohm, to UL pins 2/4; pin 3 is B_PLUS. Pin 6 feeds J3+ and R9/C6; pin 7 and J3− are grounded. R9=180k and C6=12p return to V1_K, with R4=1.5k to ground. C15=330p in series with R26=10k bridges the LTP anodes. [Schematic](../../../amplikt88.kicad_sch), [netlist](../../../amplikt88.net.xml).
- V2 ECC83 drives the KT88s through C7/C8=2.2uF, R11/R12=200k bias returns and R13/R14=5k grid stoppers. V1 is directly coupled through R5=1k to V2 grid 1; R10=1.8M supplies grid 2 DC, C16=2.2uF grounds it for AC, and R8=39k is the shared tail. R19/R20=1 ohm measure **cathode**, not solely anode, current. R27/R28=220k return bias wipers to the negative rail if contact is lost. [Netlist](../../../amplikt88.net.xml).
- Transformer model: LH=10H per half, ratio 22.4, KC=.9997, 60 ohm per primary half, 0.3 ohm secondary, 300p across the primary. It has linear inductors, no saturation/hysteresis or excitation-dependent permeability, and no distributed winding-capacitance model. KT88 model comments explicitly acknowledge underestimated screen current at low anode voltage and no grid current below zero. [Model](../../../spice/amplikt88.lib).
- README figures—60W at 1% THD, 0.11% at 37.3W, 17.4dB loop gain, 95°/82° HF/LF margins, 0.56-ohm output impedance—are **historical reported simulations**, not measurements or independently reproduced results. Historical 680p/4.7k and 120k/18p recommendations conflict with current values. Transformer alternatives also conflict internally: 5k gives 54W in its table but 64W in prose; 6.6k gives 43W versus 50W. [README](../../../README.md), [transformer document](../../output-transformer.md).

### Inferences
Original calculations from the cited circuit values:
- Whole-primary inductance is approximately 4LH=40H; the model's stated leakage approximation gives 40(1−.9997²)=24.0mH. This exceeds the order-sheet maximum of 15mH: simulated baseline and procurement target differ.
- 70W/8 ohm requires 23.66Vrms secondary and approximately 530Vrms whole-primary, 750V peak differential. Constant-flux scaling gives 70(20/30)²=31.1W at 20Hz, not 70W. This is a sizing relation, not saturation verification.
- R10C16=3.96s, corner 0.040Hz. C7/R11 gives a simplified 0.44s, 0.362Hz corner, excluding driver and bias-source impedance. Large capacitors aid LF separation but can prolong overload recovery.
- R9C6=2.16us, corner 73.7kHz; R26C15=3.30us, 48.2kHz. The latter is the series-branch transition, **not** the amplifier's dominant pole. Differential loading and driver impedance must be included.

### Gaps
Actual transformer characteristics, screen dissipation, overload recovery and operating-point drift remain unmeasured. The 60mV bias target includes screen current; it does not independently establish anode dissipation.

## 2. What do the books support?

### Takeaway
The books support measured transformer/loop co-design and balanced drive. They do not validate a performance uplift for this amplifier.

### Cited Findings
Page numbers below are **one-based PDF pages**, checked directly in each local PDF's page text; printed page numbers are separately stated. `pdftotext` failed to launch and bundled `fitz` was absent; bundled PDFium provided extraction. Source PDFs were unchanged; extracted text was confined to temporary storage.

- Crowhurst/Cooper: PDF 39 (printed 38) discusses deliberate HF shaping; PDF 64 (63) addresses tolerances and DC imbalance. PDF 108 (107) emphasizes load-dependent stability; PDF 110–111 (109–110), figs. 518–519, discuss short loops and tertiary-winding feedback, including insufficient secondary feedback voltage and primary-divider loading. PDF 113 (112) connects unequal drive to lost power and transformer polarization. These are historical design arguments, not universal guarantees. [Crowhurst/Cooper](../../references/crowhurst-cooper-high-fidelity-circuit-design-1956.pdf).
- Linsley Hood: PDF 80–81 (printed 67–68) explains level-dependent inductance, saturation and the interleaving/capacitance compromise. PDF 88 (75) addresses reactive-load stability margins. PDF 112–113 (99–100) describes UL tradeoffs and Quad cathode feedback. PDF 128 (115) favors feedback from the loaded speaker winding and reactive-load square-wave checks. [Linsley Hood](../../references/linsley-hood-valve-and-transistor-audio-amplifiers.pdf).

### Inferences
These sources favor retaining speaker-terminal sensing while improving the characterized plant. Tertiary feedback senses a different winding; its coupling to the loaded secondary must be demonstrated, not assumed.

### Gaps
Further targeted coverage: Crowhurst/Cooper chapter 3, PDF 57–64, stability criteria; chapter 6, beginning around PDF 112–113, phase splitting. Hood chapter 2, PDF 41–42, transformer equivalent circuits; chapter 5, PDF 87–88, feedback stability; chapter 6, PDF 111–113 and 128, distributed loading and conclusions. Spot checks are not a whole-book review.

## 3. Which improvements deserve priority, and what must be tested?

### Takeaway
Rank measurement credibility and transformer-specific compensation ahead of adding circuitry. All proposals below are **recommendations**, not validated improvements.

### Cited Findings
- `power_test(freq)` leaves the source at `SIN(...1k)` and uses fixed `tran 2u 12m`; changing `freq` changes harmonic interpretation, not excitation. Harmonics use equal-weight sums over potentially adaptive transient samples without explicit uniform resampling or time-weighted integration. `ot_study.drive(freq)` similarly leaves excitation at 1k. Its nominal “THD at 37W” column instead uses fixed 0.24V input across variants. [simulate.py](../../../spice/simulate.py), [ot_study.py](../../../spice/ot_study.py).
- `loop_response` multiplies grid-to-output gain by R4/(R4+Zf). Cathode injection has finite, frequency-dependent loading and differs from grid drive; this is an approximation, not a verified return-ratio measurement. The PSU study is separate and uses average-current loads; amplifier B+ and bias are ideal sources. [simulate.py](../../../spice/simulate.py), [PSU study](../../../spice/psu_study.py).

### Inferences
1. **First: qualify evaluation methods.** Require coherent, settled, frequency-correct excitation; uniform sampling or time-weighted harmonic analysis; timestep convergence; fixed-output-power comparisons; and a loading-preserving return-ratio method. Reconcile claimed margins and output impedance before claiming innovation.
2. **Transformer-specific compensation:** measure inductance versus level and DC imbalance, leakage, DCR, tap ratios and resonances. Then assess C15/R26 and R9/C6 jointly. Tradeoff: bandwidth versus robust margins; more C6 is not automatically safer. Test resistive and reactive loads, variable-frequency square waves, LF bursts and clipping recovery, with tube/mains/tolerance variation.
3. **Balanced, lower-impedance drive:** evaluate LTP balance and headroom under actual grid loading before considering a buffer or revised driver. Tradeoff: heater/power cost, extra parasitics and startup behavior. Measure both grid-to-cathode waveforms, screen current and post-clipping bias recovery.
4. **Exploratory tertiary/cathode feedback:** custom windings may support local correction, but increase transformer complexity and drive demand. Illustratively, a cathode winding at 10% of each half-primary would move about 37.5V peak at 70W; this adds substantially to required ground-referenced grid swing. No existing spare winding implements this. Require a new model, drive budget, polarity/coupling verification and complete stability/overload tests.

### Gaps
No measured benefit, optimized component values, safe maximum continuous power, or improved THD figure can yet be assigned to these proposals. All circuit/code changes are deferred.
