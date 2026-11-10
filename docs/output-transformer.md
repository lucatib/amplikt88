# Output transformer specification

One transformer per channel (TR2 on `amplikt88.kicad_sch`), two matched ones for stereo. It couples a push-pull pair of KT88 in ultralinear class AB, 450 V B+, fixed bias, to an 8 ohm speaker, inside a feedback loop of about 16 dB.

The figures marked *model* come from `python3 spice/ot_study.py`, which reruns the simulation of the schematic with other transformers. Nothing here has been measured on hardware.

## Order sheet

| | Requirement | Notes |
|---|---|---|
| Type | Push-pull, ultralinear, with centre tap | |
| Primary impedance | 4 kohm anode to anode, +/-5 % | With 8 ohm on the secondary |
| Screen taps | 40 % of the turns of each half, counted from the centre tap | 40 to 43 % is acceptable |
| Secondary | 8 ohm | 4 and 16 ohm taps welcome, not required |
| Turns ratio | 22.4 : 1, whole primary to 8 ohm | 31.6 : 1 to 4 ohm, 15.8 : 1 to 16 ohm |
| Power | 70 W continuous sine at 30 Hz | 529 V rms across the primary, 23.7 V rms on 8 ohm |
| Power at 20 Hz | 30 W or more | Same flux as 70 W at 30 Hz |
| Primary inductance | 30 H or more, 30 to 80 H preferred | Whole primary, 50 Hz, 10 V rms, no DC. Above 100 H the coupling capacitors change, see "Other transformers" |
| DC unbalance | 6 mA between the halves with 25 H or more left | 10 % of the idle current |
| Leakage inductance | 15 mH or less, target 8 mH | Whole primary, secondary shorted, 1 kHz |
| Shunt capacitance | 1 nF or less, target 500 pF | Referred across the whole primary |
| First resonance | Above 40 kHz, target 60 kHz | |
| Frequency response | 20 Hz to 30 kHz within 1 dB at 1 W | Driven from 4.5 kohm anode to anode, 8 ohm load |
| Primary resistance | 60 ohm or less per half, halves within 10 % | |
| Secondary resistance | 0.35 ohm or less (8 ohm winding) | |
| Insertion loss | 0.4 dB or less | |
| Primary current, each half | 60 mA DC idle, 150 mA average and 0.2 A rms at full power, 0.4 A peak | The screen current flows in the part between tap and centre tap |
| Secondary current | 3 A rms continuous | 4.2 A if a 4 ohm tap is fitted |
| Working voltage | 450 V DC on the whole primary (470 V with the valves cold, over 500 V with high mains), plus the signal | Each anode swings from about 30 V to 850 V; 820 V peak between the anodes |
| Test voltage | 3 kV rms, 50 Hz, 1 minute, primary to secondary and core | Secondary to core 500 V. One secondary end is grounded in the amplifier |
| Insulation between halves | For 2 kV peak | An open or reactive load under overdrive raises the swing well above 850 V |
| Temperature | Class B (130 C) or better, 50 C ambient | It sits on the chassis next to four valves |
| Mounting | On the chassis, off the board, leads 300 mm or tags | Core at right angles to the mains transformer and the choke |
| Marking | Every lead identified, start of each winding marked | See the table below |
| Pair matching | Ratio within 1 %, inductance and leakage within 15 % | For the two channels |

Winding: the two halves of the primary symmetrical (same sections, same position relative to the secondary), primary and secondary interleaved in several sections. The screen-tap part of each half is wound within the same sections as the rest of that half, so the 40 % holds at high frequency too. Bifilar halves are not wanted: there are 820 V peak between them.

## Connections

Pin numbers are those of the symbol `amplikt88:OT_PP_UL`.

| Pin | Net | Goes to | Polarity |
|---|---|---|---|
| 1 | `OT_A1` | V3 anode (pin 3) | Start of the primary (dot) |
| 2 | `OT_UL1` | V3 screen through R17 | |
| 3 | `B_PLUS` | Centre tap, B+ | |
| 4 | `OT_UL2` | V4 screen through R18 | |
| 5 | `OT_A2` | V4 anode (pin 3) | End of the primary |
| 6 | `OT_S_HI` | Speaker +, feedback through R9 and C6 | Start of the secondary (dot) |
| 7 | `GND` | Speaker -, ground | |

Pin 6 must be in phase with pin 1: with the dots as drawn the feedback is negative. If the amplifier gains about 16 dB or oscillates when the feedback is connected, the secondary (or the two anode leads) is reversed.

## Where the numbers come from

**Primary impedance and power.** The Genalex data sheet gives, for a pair in ultralinear with 40 % taps and fixed bias at 460 V: 4 kohm anode to anode, 2 x 50 mA idle, 2 x 140 mA at full signal, 70 W at 2 % distortion. This amplifier runs at 450 V and 60 mA, so 4 kohm and 70 W. The same sheet gives 100 W into 4.5 kohm at 560 V, which this supply does not reach.

*Model*, schematic as drawn, 1 kHz into 8 ohm, at the drive where distortion reaches 1 %:

| Primary (ohm) | Turns ratio to 8 ohm | Power at 1 % THD (W) | THD at 37 W (%) | Anode swing (V) | Peak between anodes (V) | Peak cathode current (mA) | Average B+ current (mA) |
|---|---|---|---|---|---|---|---|
| 3300 | 20.3 | 91 | 0.35 | 25 to 846 | 822 | 485 | 340 |
| **4000** | **22.4** | **77** | **0.31** | **24 to 852** | **829** | **407** | **295** |
| 5000 | 25.0 | 64 | 0.26 | 22 to 858 | 837 | 332 | 253 |
| 6600 | 28.7 | 50 | 0.21 | 21 to 863 | 844 | 258 | 213 |

The valve model is more generous than the data sheet (77 W against 70 W), so the transformer is specified for 70 W. At 3.3 kohm the model gives more power, but the supply would have to deliver 340 mA (the mains transformer is rated 300 mA) and the valves work beyond the data sheet's conditions; above 5 kohm power is lost for little gain in distortion.

**Voltages.** At full power each anode swings about 400 V either side of B+, so it reaches 850 V to ground and the two anodes are 820 V apart. If the speaker is disconnected, or is strongly reactive, while the amplifier is overdriven, the load line no longer limits the swing: that is what breaks output transformers, hence the test voltage.

**Leakage inductance and capacitance.** The loop is rolled off inside the amplifier (C15 and R26 across the anodes of the driver pair), so that it crosses unity near 29 kHz, below the transformer's own corner. Leakage and capacitance then decide how much phase margin is left there. *Model*, feedback 120 k / 18 pF:

| Leakage (mH) | Capacitance | Unity loop gain (kHz) | Phase margin (deg) | Gain margin (dB) |
|---|---|---|---|---|
| 5 | 300 pF | 29.2 | 128 | 23 |
| 10 | 300 pF | 29.2 | 124 | 26 |
| 24 | 300 pF | 29.2 | 113 | 31 |
| 40 | 300 pF | 27.1 | 103 | 33 |
| 60 | 300 pF | 24.1 | 93 | 36 |
| 10 | 1 nF | 28.1 | 108 | 33 |
| 24 | 1 nF | 28.1 | 96 | 36 |
| 24 | 2 nF | 25.1 | 79 | 40 |
| 40 | 2 nF | 24.1 | 66 | 40 |

10 kHz square wave, overshoot in %:

| Leakage (mH) | Capacitance | 8 ohm | 8 ohm + 0.1 uF | 8 ohm + 1 uF |
|---|---|---|---|---|
| 5 | 300 pF | 2.7 | 3.4 | 1.5 |
| 10 | 1 nF | 2.3 | 2.1 | 4.3 |
| 24 | 300 pF | 2.3 | 2.2 | 2.0 |
| 40 | 2 nF | 4.6 | 7.0 | 34 |

Inside the limits of the order sheet (15 mH, 1 nF) the phase margin stays above 100 degrees and the square wave is clean with any load. The schematic is simulated with 24 mH and 300 pF, a mediocre transformer; with 40 mH and 2 nF it only misbehaves with 1 uF across the speaker. The transformer also sets the response without feedback at the top, so the resonance above 40 kHz is still worth asking for.

**Primary inductance.** With 40 H the output stage rolls off at about 8 Hz before feedback (the valves present about 4.5 kohm anode to anode, in parallel with the 4 kohm load). Inside the loop this pole meets the two coupling networks (C5/R5 and C7, C8 / R11, R12), so more inductance is not automatically better. *Model*:

| Primary inductance (H) | Unity loop gain (Hz) | Phase margin (deg) | Gain margin (dB) |
|---|---|---|---|
| 20 | 2.8 | 74 | 27 |
| 40 | 1.6 | 60 | 22 |
| 80 | 1.0 | 47 | 17 |
| 150 | 0.7 | 36 | 13 |
| 300 | 0.5 | 29 | 10 |

Inductance also changes with level, by a factor of three or more between a few volts and full power, which is why the range matters more than the single figure.

**Power at low frequency.** The core is sized by the voltage it must take at the lowest full-power frequency: 529 V rms at 30 Hz. At 20 Hz the same flux allows 353 V, about 31 W. The model has linear inductors and says nothing about this; the winder's figure is the one that counts.

**DC unbalance.** The bias trimmers set the two idle currents within 1 or 2 mA, but valves drift and age. A core with no gap at all (a toroid, or interleaved laminations) loses inductance and low-frequency power quickly with a few mA of difference.

## Measurements to ask for

Per transformer: primary inductance (50 Hz, 10 V and 230 V rms), leakage inductance whole primary to secondary and half to half (1 kHz), capacitance primary to secondary and across the primary, DC resistance of each section, turns ratio and tap position, frequency of the first resonance, response at 1 W from 4.5 kohm, power at 30 Hz at the onset of saturation, test voltage applied.

## Other transformers

- **5 kohm, 100 W (Hammond 1650R: 5 kohm centre tapped, 40 % taps, 4-8-16 ohm, 318 mA).** Works without changes: about 64 W in the model, less distortion at normal levels, lower peak current. Rated at 100 W it has margin at 30 Hz.
- **4 kohm toroid (Toroidy TTG-KT88PP: 4 kohm, 43 % tap, 12 Hz to 56 kHz, 300 mA according to distributor listings).** The impedance and the tap are right. A toroid typically has several hundred henries of primary inductance and little tolerance for DC unbalance. With 300 to 430 H the model gives 28 degrees of phase margin and 9 to 10 dB of gain margin at the bottom as drawn; C5 2.2 uF with C7 and C8 0.47 uF brings them to about 45 degrees and 19 dB. Keep the idle currents matched within 2 or 3 mA.
- **6.6 kohm.** 50 W in the model. Only worth it for a transformer already on the shelf.
- **A secondary other than 8 ohm for the feedback.** R9 and C6 are sized for the 8 ohm terminal. From a 4 ohm tap R9 becomes about 82 k, from 16 ohm about 170 k, and C6 scales the other way.

Check the tap percentage, leakage and inductance of any ready-made part on its own data sheet before ordering; the figures above for commercial parts are from the manufacturer's page or from distributors.

## With the real transformer on the bench

The compensation (C15 470 pF with R26 10k across the driver anodes, R9 120k with C6 18 pF) is trimmed on the simulated transformer, so repeat the test on the real one: 10 kHz square wave at about 1 W into 8 ohm, then with 0.1 uF and 1 uF across the load. If the edge rings, raise C15 (470 pF to 1 nF) and, if that is not enough, R9 (less feedback); a larger C6 makes it worse. If the edge is clean with all three loads and more bandwidth is wanted (the model gives 23 kHz at -3 dB), lower C15 to 330 or 220 pF and repeat. At the bottom, watch the output with no signal at switch-on and after a deep bass transient: slow breathing at 1 to 3 Hz means too little margin there, cured by a larger C5 and smaller C7 and C8.

## Sources

- [Genalex Gold Lion KT88 data sheet](https://img.audiomania.ru/data/genalex_kt88_gold_lion_matched.pdf): operating conditions, ratings, pinout.
- [Hammond 1650R](https://www.hammfg.com/part/1650R) and the [1650 series listing](https://elcodis.com/parts/895830/1650R.html): 100 W, 5 kohm, 40 % taps.
- [Toroidy TTG-KT88PP at TME](https://www.tme.com/us/en-us/details/ttg-kt88pp/toroidal-transformers/toroidy/): distributor listing.
