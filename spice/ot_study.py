#!/usr/bin/env python3
"""What the amplifier asks of its output transformer: the numbers behind
docs/output-transformer.md.

Swaps the transformer model's parameters in the netlist of the schematic and
reruns the bench of simulate.py: power and valve stress against the primary
impedance, loop margins against leakage inductance, winding capacitance and
primary inductance, and the square-wave test for three transformers.

    python3 spice/ot_study.py

The model has linear inductors, so it says nothing about the core (power at
30 Hz, saturation with unbalanced idle currents).
"""
import math, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import simulate as sim

LTP = "ecc83"


def transformer(net, raa=4000, lp=40, leak_mh=24, cw="300p"):
    """Netlist with another transformer: plate-to-plate ohms into 8 ohm, primary
    henries, leakage in mH seen from the primary, capacitance across the primary."""
    new, n = re.subn(r"OT_PP_UL LH=\S+ RATIO=\S+",
                     f"OT_PP_UL LH={lp / 4:g} RATIO={math.sqrt(raa / 8):.3f} "
                     f"KC={math.sqrt(1 - leak_mh * 1e-3 / lp):.7f} CW={cw}", net)
    assert n == 1, "transformer instance not found in the netlist"
    return new


def drive(net, pos, rf, cf, vin, freq=1000):
    """Steady state with `vin` volts peak at the input."""
    T = 1 / freq
    n = sim.bench(net, LTP, pos, rf, cf).replace("{VAMP}", f"{vin:.4f}")
    rows, _ = sim.ngspice(n, f"tran {T / 500:.3g} {12 * T:.4g} 0 {T / 500:.3g}\n"
                          "wrdata @DAT@ v(OT_S_HI) v(OT_A1) v(V3_K) i(V_BPLUS) v(OT_A1,OT_A2)", "drive")
    t0 = rows[-1][0] - 6 * T
    w = [x for x in rows if x[0] >= t0]

    def harm(k):
        a = sum(x[1] * math.cos(2 * math.pi * k * (x[0] - t0) / T) for x in w) * 2 / len(w)
        b = sum(x[1] * math.sin(2 * math.pi * k * (x[0] - t0) / T) for x in w) * 2 / len(w)
        return math.hypot(a, b)
    h = [harm(k) for k in range(1, 11)]
    return dict(vin=vin, power=h[0] ** 2 / 16, thd=math.sqrt(sum(x * x for x in h[1:])) / h[0] * 100,
                anode_min=min(x[3] for x in w), anode_max=max(x[3] for x in w),       # wrdata repeats time
                cathode_peak_mA=max(x[5] for x in w) * 1000,                          # across the 1 ohm resistor
                supply_avg_mA=-sum(x[7] for x in w) / len(w) * 1000, aa_peak=max(abs(x[9]) for x in w))


def at_thd(net, pos, rf, cf, limit=1.0):
    """The drive that gives `limit` % distortion, by bisection."""
    lo, hi = 0.15, 0.6
    for _ in range(8):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if drive(net, pos, rf, cf, mid)["thd"] < limit else (lo, mid)
    return drive(net, pos, rf, cf, lo)


def ringing(overshoot):
    """Past 100 % the square wave never settles in the window it is measured in."""
    return str(overshoot) if 0 <= overshoot < 100 else "oscillates"


def main():
    net = sim.export_netlist()
    rf = re.search(sim.FEEDBACK % "R9", net).group(2)
    cf = re.search(sim.FEEDBACK % "C6", net).group(2)
    pos = sim.find_bias(net, LTP, rf, cf)
    print(f"Feedback {rf} / {cf}, bias trimmer at {pos}\n")

    print("| Raa (ohm) | Turns ratio to 8 ohm | Power at 1 % THD (W) | THD at 37 W (%) | Anode swing (V) "
          "| Peak a-a (V) | Peak cathode current (mA) | Average B+ current (mA) |\n|---|---|---|---|---|---|---|---|")
    for raa in (3300, 4000, 5000, 6600):
        n = transformer(net, raa=raa)
        clip = at_thd(n, pos, rf, cf)
        low = drive(n, pos, rf, cf, 0.24)
        print(f"| {raa} | {math.sqrt(raa / 8):.1f} | {clip['power']:.0f} | {low['thd']:.2f} | "
              f"{clip['anode_min']:.0f} to {clip['anode_max']:.0f} | {clip['aa_peak']:.0f} | "
              f"{clip['cathode_peak_mA']:.0f} | {clip['supply_avg_mA']:.0f} |", flush=True)

    def margins(**kw):
        return sim.loop_margins(transformer(net, **kw), LTP, pos, rf, cf)

    print("\n| Leakage (mH) | Capacitance | Unity loop gain (kHz) | Phase margin (deg) | Gain margin (dB) |\n|---|---|---|---|---|")
    for leak, cw in ((5, "300p"), (10, "300p"), (24, "300p"), (40, "300p"), (60, "300p"),
                     (10, "1n"), (24, "1n"), (24, "2n"), (40, "2n")):
        m = margins(leak_mh=leak, cw=cw)
        print(f"| {leak} | {cw}F | {m.get('unity_f_kHz')} | {m.get('phase_margin_deg')} | {m.get('gain_margin_dB')} |", flush=True)

    print("\n| Primary inductance (H) | Unity loop gain (Hz) | Phase margin (deg) | Gain margin (dB) |\n|---|---|---|---|")
    for lp in (20, 40, 80, 150, 300):
        m = margins(lp=lp)
        print(f"| {lp} | {m.get('lf_unity_Hz')} | {m.get('lf_phase_margin_deg')} | {m.get('lf_gain_margin_dB')} |", flush=True)

    print("\n| Leakage (mH) | Capacitance | Overshoot, 8 ohm (%) | + 0.1 uF (%) | + 1 uF (%) |\n|---|---|---|---|---|")
    for leak, cw in ((5, "300p"), (10, "1n"), (24, "300p"), (40, "2n")):
        n = transformer(net, leak_mh=leak, cw=cw)
        print(f"| {leak} | {cw}F | " + " | ".join(ringing(sim.overshoot(n, LTP, pos, rf, cf, cl)) for cl in (None, "0.1u", "1u")) + " |",
              flush=True)


if __name__ == "__main__":
    sys.exit(main())
