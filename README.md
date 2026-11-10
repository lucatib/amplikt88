# amplikt88

Mono power amplifier, schematic in KiCad 10, two sheets (PDF of both in `amplikt88.pdf`):

- `amplikt88.kicad_sch`: the amplifier (input, driver, output stage, bias trimmers).
- `power.kicad_sch`: the power supply (mains, rectifier and filter, driver rail, negative bias supply, heater centre tap).

The nets that cross between the sheets are global labels: `B_PLUS`, `B_DRV`, `B_V1`, `VBIAS_NEG`, `HEATER_A`, `HEATER_B`.

- **Output stage:** 2x KT88, push-pull, class AB, ultralinear (screens on the output transformer taps), adjustable fixed bias.
- **Driver:** ECC83 long-tailed pair, tail returned to the negative bias rail. One grid takes the signal, the other takes the global feedback from the speaker terminal.
- **Input stage:** ECC83 section (the second section is grounded).
- **Supply:** 330 V winding, bridge, C-L-C filter to about 450 V B+, separate decoupled rail for the driver, 6.3 V heaters with an artificial centre tap, about -65 V bias supply.

## Assumptions to confirm before building

All values are a first pass, not simulated or measured.

- Output transformer 4 kohm plate-to-plate with ultralinear taps and an 8 ohm secondary. The real transformer sets the operating point.
- Power transformer 230 V, 330 V / 300 mA HV, 6.3 V / 4.5 A, 50 V bias winding.
- Driver swing: the ECC83 pair must give about +/-45 V per grid. Check by simulation; if short, use an ECC82 for the pair.
- Feedback (22k / 1k, about -27 dB) needs the secondary phased so the speaker terminal is in phase with the anode of the valve driven by `LTP_A1`. Swap the secondary leads if it oscillates or the gain rises.
- Bias trimmers: set both fully to the most negative end before first power-up, then raise the bias to about 60 mA per valve, measured across the 1 ohm cathode resistors (60 mV).

## Safety

B+ is about 450 V and the reservoir capacitors hold charge after power-off. The 100k bleeder takes minutes to bring them down, so measure before touching.

## Notes on the schematic

- ECC83, KT88 and both transformers are single-unit symbols in `amplikt88.kicad_sym`, with the real pin numbers (KiCad's own ECC83 is split into three units). KT88 pins 1 and 6 are not connected.
- Short nets within a stage are drawn as wires (routed with `route_nets`, `max_length` 110 mm). The ones that cross the sheet, such as B+, the heater lines and the negative bias rail, stay as net labels.
- Resistor and capacitor footprints are not assigned yet.
