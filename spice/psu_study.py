"""HV supply on its own: power transformer, bridge, C1, L1, C2.

    python3 spice/psu_study.py

simulate.py feeds the amplifier from an ideal 450 V B+. This bench models the
supply that feeds it: the HV winding as a sine source with its no-load voltage,
a series resistance and 20 mH of leakage; the bridge; C1 100 uF; L1 5 H with
80 ohm DCR; C2 100 uF; the 100k bleeder. The load is the amplifier's average B+
current (driver rails included) at idle and with a continuous sine at 40, 60
and 70 W, from simulate.py's bench. It reports B+, ripple, the DC current in L1
and the rms current in the HV winding, which is what heats the transformer.

Assumptions: a winding is rated at full load, so the no-load voltage is about
7 % higher (300 mA AC winding) or 5 % higher (500 mA), with the series
resistance that drops the difference at the rated current. The choke does not
saturate in the model; its rating is a separate check.
"""
import math, os, subprocess, tempfile

W = tempfile.mkdtemp(prefix="amplikt88-psu-")
LOADS = (("idle", 0.125), ("40 W sine", 0.226), ("60 W sine", 0.260), ("70 W sine", 0.270))
CASES = (("330 V / 300 mA AC winding (before)", dict(vac=353, rs=75)),
         ("330 V / 500 mA AC winding (as drawn)", dict(vac=346, rs=33)))


def run(i_load, vac, rs, lleak=0.02, c1=100e-6, l1=5, dcr=80, c2=100e-6, tag="psu"):
    cir = f"""* HV supply
VS a b SIN(0 {vac * math.sqrt(2):.2f} 50)
RS a a1 {rs}
LS a1 a3 {lleak}
VT a3 a2 0
D1 a2 p DB
D2 b p DB
D3 n a2 DB
D4 n b DB
VN n 0 0
RREF b 0 10meg
C1 p 0 {c1} IC=0
VI p p1 0
L1 p1 p2 {l1}
RL1 p2 bp {dcr}
C2 bp 0 {c2} IC=0
RB bp 0 100k
IL bp 0 {i_load}
.model DB D(IS=1e-9 N=1.8 RS=0.05 BV=1000)
.options method=gear reltol=1e-3 itl4=100
.control
tran 50u 6 0 50u uic
meas tran vbp AVG v(bp) from=5 to=6
meas tran vpp PP v(bp) from=5 to=6
meas tran il1 AVG i(VI) from=5 to=6
meas tran irms RMS i(VT) from=5 to=6
.endc
.end
"""
    f = os.path.join(W, tag + ".cir")
    open(f, "w").write(cir)
    out = subprocess.run(["ngspice", "-b", f], capture_output=True, text=True, timeout=600).stdout
    r = {}
    for line in out.splitlines():
        k, _, v = line.partition("=")
        if k.strip() in ("vbp", "vpp", "il1", "irms"):
            r[k.strip()] = float(v.split()[0])
    return r


def main():
    for name, kw in CASES:
        print(f"\n{name}\n\n| Load | B+ (V) | Ripple pp (V) | L1 DC (mA) | HV winding rms (mA) |\n|---|---|---|---|---|")
        for i, (load, amps) in enumerate(LOADS):
            r = run(amps, tag=f"psu{i}", **kw)
            print(f"| {load} | {r['vbp']:.0f} | {r['vpp']:.2f} | {r['il1'] * 1000:.0f} | {r['irms'] * 1000:.0f} |", flush=True)


if __name__ == "__main__":
    main()
