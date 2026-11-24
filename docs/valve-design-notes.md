# Valve design notes

These earlier notes are written for this amplifier from standard valve theory, not extracted from a book. The third edition of Morgan Jones's *Valve Amplifiers* is now in `docs/references`. See the [circuit research and innovation review](amplikt88-innovation-review.md) for verified source locations, current configuration, limitations of earlier calculations and uses for V1's spare triode.

The operating points come from the simulation in the [README](../README.md#simulation). Nothing has been measured on hardware yet.

## 1. Triode gain stage (V1)

A triode with anode load Ra and an unbypassed cathode resistor Rk has a gain of

    A = mu * Ra / (ra + Ra + (mu + 1) * Rk)

where mu is the amplification factor and ra the anode resistance at the operating point. With no bypass, Rk adds (mu + 1) * Rk to the source resistance seen from the anode. This local feedback lowers the gain and the distortion and raises the output impedance.

V1 is half an ECC83 at about 0.6 mA, so mu is about 100 and ra about 70k. With Ra = 470k and Rk = R4 = 1.5k:

    A = 100 * 470k / (70k + 470k + 101 * 1.5k) = about 68

That is before the global feedback, which also arrives at R4. The pair's grid presents almost no load, because V1 is direct coupled to it.

Points that matter in practice:

- **The load line is set by R3 and B_V1 (355 V).** The anode sits at about 89 V and the cathode at 0.84 V. That leaves plenty of swing for the few volts the pair needs, but the stage runs well below the middle of its load line, because the anode voltage sets the bias of the pair (see section 2).
- **Output impedance** is about ra + (mu + 1) * Rk in parallel with Ra, roughly 160k. It drives the pair's grid and Miller capacitance through R5 (1k). A first-order estimate in the innovation review puts this local pole near 23 kHz, so it cannot be assumed far above audio. This is not the complete amplifier's closed-loop bandwidth.
- **Noise and hum.** The input stage has the most gain after it, so its heater wiring, grid stopper and layout matter most (sections 6 and 7).

## 2. Long-tailed pair phase splitter (V2)

Both triodes share a cathode resistor, the tail. The signal goes into one grid and the other grid is held at AC ground (here by C16), so the two anodes swing in antiphase.

**Balance.** The tail is finite, so the second triode gets slightly less signal than the first. As a rough guide, the second anode's signal falls short by a factor of about

    (mu + 1) * Rt / ((mu + 1) * Rt + ra + Ra)

With a plain resistor tail (the earlier R8, 39k), ra about 65k and Ra = 100k, this gives about 0.96, so the imbalance is a few percent. Designs usually correct it in one of two ways: a slightly larger anode load on the second triode, or a constant-current tail. This amplifier now uses the second: the spare V1 triode is a 2.33 mA current sink in the tail, and the simulated anode signals match within 0.1 %. At high frequencies, stray and Miller capacitance on the second grid unbalance the pair further. That is why C16 was added: see the README's simulation notes.

**Headroom.** Each anode has to swing the peak drive the KT88 grids need, about 57 V for 70 W. With 100k loads into an AC load of about 67k (R11 and R12, 200k, in parallel with the anode loads), the pair has about 233 V from anode to cathode at 1.15 mA. That headroom is what lets it reach the drive without a separate driver stage.

**Grid current.** At rest the grid of the pair sits at about -1.8 V. A real ECC83 starts drawing grid current near -1 V. The README's table shows the most positive grid reaching -0.55 V at 70 W. Above about 50 W, the driver is therefore what limits the power.

**Direct coupling.** The first grid is tied to V1's anode, so the tail can go to ground and still be long, and one coupling capacitor is removed from the loop. The cost: the pair's operating point now depends on V1's anode voltage, and therefore on V1's ageing and on B_V1. Re-check the bias of the pair whenever V1 is replaced.

## 3. Push-pull ultralinear output stage (V3, V4)

**Class AB.** Each KT88 conducts for more than half the cycle but less than all of it. The idle current (60 mA here) sets where crossover happens:

- Too little idle current and the hand-over between the valves shows as crossover distortion.
- Too much and the anode dissipation at idle eats into the margin.

**Dissipation at idle.** About 450 V times 60 mA, which is roughly 27 W per valve, minus the small drops in the transformer and cathode resistor. Compare that with the anode rating in the data sheet for the valve you actually fit. Genalex and JJ do not rate it the same way. The README explains why 75 mA is the ceiling with 200k grid resistors.

**Power estimate.** In push-pull, the load between the anodes is Raa = 4k. Each anode can swing from B+ down to roughly the knee of the curve, about 370 V from 450 V. The peak voltage across the whole primary is then about 2 x 370 V, and the peak power is

    P = (2 * 370)^2 / (2 * 4000) = about 68 W

This agrees with the simulation's 60 W at 1 % and 75 W at 5 %.

**Ultralinear.** The screens go to taps at 40 % of each half-primary. The valve then behaves between a tetrode and a triode. Ideally the tap contributes 40 % of the corresponding anode's AC swing relative to the centre tap, on top of the HT voltage; screen-resistor drops and winding parasitics alter the actual screen voltage. The screen tracks have the 6.3 mm clearance class.

**Fixed bias.** The grids are held at a negative voltage from the bias supply through R11 and R12. Fixed bias gives more power and better regulation than cathode bias, but it needs two things:

- per-valve adjustment, done here with RV1 and RV2 and the 1 ohm sense resistors;
- a fail-safe, here R27 and R28, so a broken trimmer wiper cannot let a valve run away.

The grid resistor limit in the data sheet exists because of reverse grid current. As a valve warms, gas and grid emission push a small current out of the grid. Through a large grid resistor, that current lifts the bias, which raises the anode current, which heats the valve further.

**Grid and screen stoppers.** A small resistor right at each grid pin and at each screen damps parasitic oscillation at VHF. For it to work, it has to be at the socket, not at the other end of a track.

## 4. Global negative feedback

With open-loop gain A and feedback fraction beta, the loop gain is A * beta. The feedback divides distortion, gain errors and output impedance by roughly (1 + A * beta), but only where the loop gain is high. That is in mid-band, and less at the ends.

**Stability.** Every coupling network and every reactance in the output transformer adds phase shift. At the top of the band the culprits are leakage inductance, winding capacitance and Miller capacitance. At the bottom they are the coupling capacitors and the primary inductance. Where the loop gain falls to 1, the total phase shift has to stay well short of 180 degrees.

The usual rule is that one network should set the roll-off, well before the others do. Here that network is:

- the lag R29 15k with C17 180 pF from V1's anode to ground, at the top of the band (it replaced C15 and R26 across the anodes of the pair);
- at the bottom, the coupling networks C7, C8 (0.47 µF) with R11, R12 (200k), 0.094 s, and the second grid of the pair, R10 C16 (1.8M, 1 µF), 1.8 s. With 0.47 µF the low-frequency phase margin is about 56 degrees; larger coupling capacitors raise it (82 degrees with 2.2 µF) but make the bias recover more slowly after the grids are overdriven (about 1.4 s against 0.5 s to settle within 0.2 V).

The feedback capacitor C6 (12 pF across R9) adds phase lead near the top of the loop's band.

**Output transformer phasing.** The secondary must be wired so that the feedback is negative. Wired the wrong way round, it becomes positive feedback and the amplifier oscillates.

**How much feedback.** This design uses about 17 dB, against Mullard's 26 to 30 dB. More feedback lowers distortion and output impedance, but it shrinks the margins and makes the amplifier more sensitive to the transformer and to capacitive loads. The square-wave tests in the README check this trade-off.

## 5. HT supply

**Capacitor input.** A rectifier feeding a reservoir capacitor charges it in short pulses near the top of each half-cycle. The winding's rms current is therefore much higher than the DC load: roughly twice it here, according to `spice/psu_study.py`. Rate the winding for the rms current, not the DC current.

**C-L-C filter.** A choke between two capacitors attenuates the ripple by about

    1 / ((2 * pi * f)^2 * L * C) at f = 100 Hz

With 5 H and the second capacitor, that is a large ratio. Separate RC-decoupled rails for the driver and the input stage add further filtering. They also stop signal currents in the output stage from coupling back into the early stages through a shared supply.

**Switch-on.** Before the valves warm up, nothing draws current and the HT rises towards the peak of the winding. That is about 470 V here, and more with high mains. Every capacitor and resistor on B+ needs a rating above this cold value, not the running one.

**Bleeding.** The bleeder discharges the reservoir after power-off, but slowly. Measure the HT before touching anything.

**Bias supply.** A bridge rectifier on a floating winding (it was a half-wave with one diode) with a light, constant load. The bridge halves the ripple period, puts no DC through the winding, and survives one diode failing open, which with a single diode would lose the KT88 bias. It does not need to be stiff, but it must come up before or together with the HT. If it does not, the KT88s conduct at zero bias. Here the bias winding is on the same transformer and the KT88 heaters take seconds to warm up, so the bias supply comes up first.

## 6. Heaters

**AC heaters with an artificial centre tap.** Two resistors across the 6.3 V winding, with their junction grounded (or lifted on a DC voltage), cancel most of the hum the heater induces in the cathode. Twist the heater pair and route it away from grids. Here the heater wiring is off the board, which helps.

**Heater-to-cathode voltage.** The pair's cathodes sit at about 91 V above ground, while the heater is near ground. That is within the ECC83's heater-to-cathode rating, but it is the figure to check whenever the driver's bias changes. Lifting the heater centre tap to a positive DC voltage reduces both this stress and the hum coupled through heater-cathode leakage.

## 7. Layout and grounding

- **Star ground:** one point where the reservoir capacitor, the signal ground and the chassis meet. Here that is J4 pin 7 on the B.Cu star. The high-current charging pulses of the reservoir must not flow through the signal ground.
- **Grid stoppers at the socket.** Keep the input track short, and keep it away from anodes and from the output transformer leads.
- **Heat.** Electrolytic and film capacitors age quickly near a KT88 bulb. That is why C7, C8 and C16 moved to the back of the board.
- **Clearance and creepage** scale with working voltage, including the peaks on the anodes and the UL taps at full power. The net classes in `amplikt88.kicad_pro` already encode this.

## 8. Components

- **Resistor voltage rating, not just power.** Small axial resistors usually have a maximum working voltage of 250 to 350 V, whatever their wattage. Check each resistor against the largest DC voltage across it, plus the signal swing. On this board:
  - **R3 (470k, DIN0207)** has about 266 V across it at idle, from B_V1 at 355 V to V1's anode at 89 V. While V1 warms up, that drops to almost nothing, but at idle it is over the 250 V limit of a typical 0207 part. Either specify a 350 V part (or a higher-voltage type), or use a larger body.
  - The others on DIN0207 see about 120 V or less: R6, R7, R22, R10, R11, R12.
- **Coupling capacitors** (C7, C8) carry the full B_DRV DC on one side and the bias voltage on the other, and up to about 550 V at switch-on. Use film parts rated 630 V. Leakage through them shifts the KT88 bias, so avoid electrolytics and old paper capacitors here.
- **Electrolytics on the HT** are often series pairs with balancing resistors to reach 550 V. Their ripple current rating matters as much as their capacitance.
- **Trimmers in the bias path** are a known failure point, which is why the wiper fail-safe resistors are there (section 3).

## See also

- [README](../README.md): operating points, simulation results and the reasoning behind each value.
- [docs/output-transformer.md](output-transformer.md): transformer specification and sensitivity.
- [docs/references](references/README.md): Mullard, G.E.C., Radiotron, Valley-Wallman and Williamson. Each covers one or more of the topics above, as listed in the README's references.
