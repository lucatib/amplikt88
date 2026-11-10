#!/usr/bin/env python3
"""Simulate amplikt88 in ngspice.

KiCad exports the netlist from amplikt88.kicad_sch (the Sim.* fields on the
symbols point at amplikt88.lib); this script adds a bench around it (ideal
B+ and bias rails, 1 kHz source, 8 ohm load) and runs the analyses.

    python3 spice/simulate.py                  # the schematic as drawn
    python3 spice/simulate.py --ltp ecc82      # ECC82 in the long-tailed pair
    python3 spice/simulate.py --rf 82k --cf 27p

The power supply sheet is not simulated; B+, the driver rail drop and the
negative bias rail are modelled as ideal sources. Valve models are Koren fits
(the KT88 is fitted to one operating point only), the output transformer is a
coupled-inductor model with assumed leakage. Use it to compare variants, not
to certify the design.
"""
import argparse, cmath, math, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCH = os.path.join(ROOT, "amplikt88.kicad_sch")
WORK = tempfile.mkdtemp(prefix="amplikt88-sim-")


def export_netlist():
    out = os.path.join(WORK, "amp.cir")
    subprocess.run(["kicad-cli", "sch", "export", "netlist", "--format", "spice", "-o", out, SCH],
                   check=True, capture_output=True)
    # ngspice reads a leading / in an expression as division
    return re.sub(r"(?<=\s)/", "", open(out).read())


def bench(net, ltp, pos, rf, cf, open_loop=False):
    n = net.replace(".end\n", "")
    n = re.sub(r"(XRV[12] .*POS=)[0-9.]+", rf"\g<1>{pos}", n)
    n = re.sub(r"(R9 OT_S_HI V1_K )\S+", rf"\g<1>{rf}", n)
    n = re.sub(r"(C6 OT_S_HI V1_K )\S+", rf"\g<1>{cf}", n)
    if ltp == "ecc82":
        n = re.sub(r"(XV2 .*) ECC83", r"\1 ECC82", n)
        for old, new in (("R6 B_DRV LTP_A1 82k", "R6 B_DRV LTP_A1 22k"), ("R7 B_DRV LTP_A2 82k", "R7 B_DRV LTP_A2 22k"),
                         ("R8 LTP_K VBIAS_NEG 33k", "R8 LTP_K VBIAS_NEG 12k"), ("R21 B_PLUS B_DRV 33k", "R21 B_PLUS B_DRV 18k")):
            assert old in n, old
            n = n.replace(old, new)
    if open_loop:   # feedback network kept as a load, its output end grounded
        n = re.sub(r"(R9 )OT_S_HI", r"\1GND", n)
        n = re.sub(r"(C6 )OT_S_HI", r"\1GND", n)
    for i, node in enumerate(sorted(set(re.findall(r"unconnected-\S+", n)))):
        n += f"RFLOAT{i} {node} GND 1e9\n"
    return n + ("V_BPLUS B_PLUS GND DC 450\nV_NEG VBIAS_NEG GND DC -65\n"
                "VIN IN_RAW GND DC 0 AC 1 SIN(0 {VAMP} 1k)\nRL OT_S_HI GND 8\n"
                ".options reltol=0.003 gmin=1e-12 itl1=500 itl4=200\n.param VAMP=1\n")


def ngspice(net, control, tag):
    cir = os.path.join(WORK, tag + ".cir")
    dat = os.path.join(WORK, tag + ".dat")
    open(cir, "w").write(net + "\n.control\n" + control.replace("@DAT@", dat) + "\n.endc\n.end\n")
    p = subprocess.run(["ngspice", "-b", cir], capture_output=True, text=True, timeout=900)
    rows = []
    if os.path.exists(dat):
        for line in open(dat):
            try:
                rows.append([float(x) for x in line.split()])
            except ValueError:
                pass
    return rows, p.stdout + p.stderr


def idle_current(net, ltp, pos, rf, cf):
    _, log = ngspice(bench(net, ltp, pos, rf, cf), "op\nprint v(V3_K) v(V4_K) v(V3_G1)", "op")
    v = {m.group(1).lower(): float(m.group(2)) for m in re.finditer(r"v\((\w+)\)\s*=\s*(\S+)", log)}
    return v["v3_k"] * 1000, v["v3_g1"]


def find_bias(net, ltp, rf, cf, target_ma=60.0):
    lo, hi = 0.3, 0.95
    for _ in range(9):
        mid = (lo + hi) / 2
        ia, _ = idle_current(net, ltp, mid, rf, cf)
        lo, hi = (mid, hi) if ia < target_ma else (lo, mid)
    return round((lo + hi) / 2, 3)


def loop_margins(net, ltp, pos, rf, cf):
    rows, _ = ngspice(bench(net, ltp, pos, rf, cf, open_loop=True),
                      "ac dec 60 10 5meg\nlet A = v(OT_S_HI)/v(V1_G)\nwrdata @DAT@ real(A) imag(A)", "loop")
    R = float(re.sub("k", "e3", rf)); C = float(re.sub("p", "e-12", cf))
    f, mag, ph = [], [], []
    for x in rows:
        zf = 1 / (1 / R + 1j * 2 * math.pi * x[0] * C)          # Rf in parallel with Cf
        t = complex(x[1], x[3]) * 1000 / (1000 + zf)             # beta = Rk / (Rk + Zf), Rk = 1k
        f.append(x[0]); mag.append(20 * math.log10(abs(t))); ph.append(math.degrees(cmath.phase(t)))
    for i in range(1, len(ph)):
        while ph[i] - ph[i - 1] > 180: ph[i] -= 360
        while ph[i] - ph[i - 1] < -180: ph[i] += 360
    out = {"loop_gain_1k_dB": round(mag[min(range(len(f)), key=lambda i: abs(f[i] - 1000))], 1)}
    for i in range(1, len(f)):
        if "unity_f_kHz" not in out and mag[i - 1] > 0 >= mag[i]:
            out.update(unity_f_kHz=round(f[i] / 1e3, 1), phase_margin_deg=round(180 + ph[i], 1))
        if "f_180_kHz" not in out and ph[i - 1] > -180 >= ph[i]:
            out.update(f_180_kHz=round(f[i] / 1e3, 1), gain_margin_dB=round(-mag[i], 1))
    return out


def power_test(net, ltp, pos, rf, cf, vout_pk=24.4, freq=1000):
    rows, _ = ngspice(bench(net, ltp, pos, rf, cf), "ac dec 10 1k 1k\nwrdata @DAT@ vdb(OT_S_HI)", "gain")
    gain = 10 ** (rows[0][1] / 20)
    n = bench(net, ltp, pos, rf, cf).replace("{VAMP}", f"{vout_pk / gain:.4f}")
    rows, _ = ngspice(n, "tran 2u 12m 0 2u\nwrdata @DAT@ v(OT_S_HI) v(V3_G1) v(V4_G1)", "tran")
    T = 1 / freq
    t0 = rows[-1][0] - 6 * T
    w = [x for x in rows if x[0] >= t0]
    vo = [x[1] for x in w]
    def harm(k):
        a = sum(v * math.cos(2 * math.pi * k * (x[0] - t0) / T) for v, x in zip(vo, w)) * 2 / len(w)
        b = sum(v * math.sin(2 * math.pi * k * (x[0] - t0) / T) for v, x in zip(vo, w)) * 2 / len(w)
        return math.hypot(a, b)
    h = [harm(k) for k in range(1, 11)]
    return dict(closed_loop_gain=round(gain, 1), vin_peak_V=round(vout_pk / gain, 3),
                P_8ohm_W=round(h[0] ** 2 / 16, 1), THD_pct=round(math.sqrt(sum(x * x for x in h[1:])) / h[0] * 100, 3),
                grid_V3_V=(round(min(x[3] for x in w), 1), round(max(x[3] for x in w), 1)),   # wrdata repeats time
                grid_V4_V=(round(min(x[5] for x in w), 1), round(max(x[5] for x in w), 1)))


def overshoot(net, ltp, pos, rf, cf, cload):
    n = bench(net, ltp, pos, rf, cf)
    n = re.sub(r"VIN IN_RAW GND DC 0 AC 1 SIN\([^)]*\)",
               "VIN IN_RAW GND DC 0 AC 1 PULSE(-0.06 0.06 20u 0.5u 0.5u 49.5u 100u)", n)
    if cload:
        n += f"CL OT_S_HI GND {cload}\n"
    rows, _ = ngspice(n, "tran 0.2u 500u 0 0.2u\nwrdata @DAT@ v(OT_S_HI)", "square")
    seg = [(x[0], x[1]) for x in rows if 400e-6 <= x[0] <= 500e-6]
    top = sum(v for t, v in seg if 440e-6 <= t <= 468e-6) / sum(1 for t, v in seg if 440e-6 <= t <= 468e-6)
    bot = sum(v for t, v in seg if 490e-6 <= t <= 499e-6) / sum(1 for t, v in seg if 490e-6 <= t <= 499e-6)
    peak = max(v for t, v in seg if 420e-6 <= t <= 470e-6)
    return round((peak - top) / (top - bot) * 100, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ltp", choices=("ecc83", "ecc82"), default="ecc83", help="valve in the long-tailed pair")
    ap.add_argument("--rf", help="feedback resistor R9 (default: from the schematic)")
    ap.add_argument("--cf", help="lead capacitor C6 across it (default: from the schematic)")
    a = ap.parse_args()
    net = export_netlist()
    rf = a.rf or re.search(r"R9 OT_S_HI V1_K (\S+)", net).group(1)
    cf = a.cf or re.search(r"C6 OT_S_HI V1_K (\S+)", net).group(1)
    pos = find_bias(net, a.ltp, rf, cf)
    ia, vg = idle_current(net, a.ltp, pos, rf, cf)
    print(f"LTP {a.ltp.upper()}, Rf {rf}, Cf {cf}")
    print(f"bias: trimmer at {pos} of its travel -> {ia:.0f} mA per KT88, grid {vg:.1f} V")
    print("loop:", loop_margins(net, a.ltp, pos, rf, cf))
    print("35 W, 1 kHz, 8 ohm:", power_test(net, a.ltp, pos, rf, cf))
    for cl in (None, "0.1u", "1u"):
        print(f"10 kHz square, 8 ohm{' + ' + cl + 'F' if cl else ''}: overshoot {overshoot(net, a.ltp, pos, rf, cf, cl)} %")


if __name__ == "__main__":
    sys.exit(main())
