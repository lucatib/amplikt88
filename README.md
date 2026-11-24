# amplikt88

Mono KT88 push-pull power amplifier, ultralinear, class AB, fixed bias. KiCad 10 project: schematic on two sheets ([PDF](amplikt88.pdf)), two-layer board.

![3D view](docs/pcb-3d-perspective.png)

## Circuit

- **Input:** ECC83 triode, 470k anode load, unbypassed cathode (R4 1.5k) takes the global feedback.
- **Driver:** ECC83 long-tailed pair, direct coupled to the input stage as in the Mullard 5-10/5-20. The tail is the spare V1 triode as a 2.33 mA current sink fed from BIAS_CCS. Lag R29 15k + C17 180p at V1's anode.
- **Output:** 2x KT88, coupled through C7/C8 0.47 µF 630 V, screens on the transformer's 40 % UL taps, 200k grid resistors, bias trimmers RV1/RV2.
- **Feedback:** 180k ∥ 12 pF from the speaker terminal to V1's cathode, about 17 dB.
- **Supply** ([power sheet](docs/schematic/power.svg)): 330 V bridge, C-L-C to 450 V B+, decoupled B_DRV and B_V1, bridge-rectified −65 V bias rail, 6.3 V heaters.

![Amplifier sheet](docs/schematic/amplikt88.svg)

Design studies: [spare-triode comparison](docs/research/amplikt88-innovation/spare-triode-comparison.md), [output transformer](docs/output-transformer.md), [innovation review](docs/amplikt88-innovation-review.md), [design notes](docs/valve-design-notes.md).

## Simulation

`python3 spice/simulate.py` exports the netlist with `kicad-cli` and runs ngspice ([models](spice/amplikt88.lib)); `spice/plot.py` redraws the plots. Ideal 450 V and −65 V sources, 8 Ω load.

| | |
|---|---|
| Idle | 60 mA per KT88 (grid −55.8 V) |
| Loop gain, 1 kHz | 17.3 dB |
| Margins, top / bottom | 102° / 28 dB, 56° / 26 dB |
| Bandwidth (−3 dB) | 2.9 Hz – 33 kHz |
| THD, 37 W | 0.078 % at 1 kHz, 0.51 % at 10 kHz |
| Power at 1 % THD | 60 W |

![Simulation plots](spice/simulation.png)

The valve models are fits to the [datasheets](docs/datasheets/README.md) (5–12 % rms); use the numbers to compare variants, not as measurements.

## Board

218.67 × 98.0 mm, two layers, mounted vertically on an L bracket. Five M4 holes: four corners and H2 on the centre line.

| Top | Bottom |
|---|---|
| ![Top](docs/pcb-3d.png) | ![Bottom](docs/pcb-3d-bottom.png) |

![Routing: F.Cu red, B.Cu blue, vias yellow, milled slots cyan](docs/pcb-routing.png)

- **F.Cu** carries the signal and power nets. **B.Cu** carries the ground star from J4 pin 6, plus short jumpers for blocked or low-voltage nets (VBIAS_NEG, heaters, LTP_A1, G3_IN, G4_IN, V2_G2 to C16). Two vias, 1.6/0.8 mm.
- **Clearance to ground and mounting holes:** 5 mm for HV, 6.3 mm for UL taps and screens, 8 mm for KT88 anodes. HV nets keep 2.5 mm from each other. Rules are in [amplikt88.kicad_dru](amplikt88.kicad_dru).
- **Milled slots (0.8 mm, Edge.Cuts):** three slots lengthen the surface path where high and low voltage sit close: an L at V3 between R17.2 (UL tap) and C7.2 (G3_IN), an L under R12 at V4 (G4_IN), and a straight one in J4 between B_V1 (pin 3) and VBIAS_NEG (pin 4). The `FESSURA_*` rule areas in the DRC rules mark them. Ask the board house for milled slots, not V-score.
- **Heaters:** V1 + V2 go to JH2, V3 to JH3, V4 to JH4. Each pair is wired separately to the 6.3 V winding, so DRC lists 4 unconnected heater items by design.
- **Off-board connections:** TR2 to the output transformer, J4 to the supply, J3 to the speaker, J2 for the input.
- **Back side:** C7, C8 and C16 (film caps, WIMA MKS 4 630 VDC) sit on the back, away from the KT88 glass. C7 and C8 (0.47 µF, MKS4J034706A) are 9 × 19 × 31.5 mm, C16 (1 µF, MKS4J041006B) 11 × 21 × 31.5 mm, all on a 27.5 mm pitch. C16 lies along the bottom edge between JH3 and R10 (its body comes to about 0.3 mm from the edge on the back): /V2_G2 reaches it from R10 on B.Cu, its ground end joins the star at R19.

## Before building

Nothing has been measured on hardware. Check:
- **Transformers:**
  - Output: 4 kΩ plate-to-plate, 40 % UL taps, 8 Ω, 70 W ([spec](docs/output-transformer.md)).
  - Power: toroidal, wound to order (about 200 VA): 230 V 50 Hz primary; HV 330 V rms at full load, 500 mA AC (about 300 mA DC in a winder's capacitor-input rating); heaters 6.3 V / 4.5 A; bias 60 V / 100 mA; electrostatic screen between primary and secondaries; regulation 5 % or better; EN 61558.
  - Inrush: F1 is a slow-blow T2A (high I²t). If it blows at switch-on, add a soft-start (NTC in series with the primary, shorted by a relay after a second or two) rather than a bigger fuse.
  - Choke: 5 H / 300 mA.
- **Secondary phase:** wire the secondary in phase with the input. If it oscillates, swap the leads.
- **Bias:** turn both trimmers to most negative before power-up, then set 60 mA per KT88 (60 mV across the 1 Ω cathode resistors). Stay below 75 mA.
- **Sensitivity:** 0.16 V rms in gives 37 W. Fit a volume control.

- **Capacitor voltages:** C7 and C8 carry about 380 V DC at idle (LTP anode 325 V, KT88 grid −56 V) and up to about 590 V at a cold start with high mains, when V2 does not conduct yet and its anodes sit at the unloaded B+. C16 follows the LTP grid, which also rises towards B_V1 before V1 conducts. Use parts rated 630 VDC or more for all three.

**Danger:** B+ is 450 V and the capacitors hold their charge after power-off. Measure before touching.

## References

- Mullard, [*Circuits for Audio Amplifiers*](https://www.worldradiohistory.com/BOOKSHELF-ARH/Technology/Technology-General/Mullard%20Circuits%20For%20Audio%20Amplifiers.pdf), 1959: the 5-20 and 5-10 driver topology.
- G.E.C., [*An Approach to Audio Frequency Amplifier Design*](https://archive.org/details/An_Approach_to_Audio_Frequency_Amplifier_Design_G.E._Valve-Electronics_Dept._195), 1957: KT88 fixed-bias UL amplifiers.
- Radiotron Designer's Handbook, Valley–Wallman, Williamson, Morgan Jones: local copies and links in [docs/references](docs/references/README.md).
- Valve datasheets: [docs/datasheets](docs/datasheets/README.md).

[License](LICENSE)
