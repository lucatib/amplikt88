#!/usr/bin/env python3
"""Half-wave (as drawn: D5) vs full bridge on the 60 V bias winding.

Same model as bias_supply_study.py: winding as a sine with the calibrated 28.3 ohm
series resistance, C13 100u, R23 2.7k, C14 100u. Loads: 3.53 mA on VBIAS_NEG (the
trimmer strings) and, for the tail sink, 2.4 mA more drawn from the raw node (C13)
through R34 2.2k / C19 100u as on the power sheet. Reports the KT88 bias rail,
BIAS_CCS, ripple at each node, the raw node's source resistance, and the winding's
rms and DC current (a half-wave puts DC through the winding).

  python3 bias_bridge_study.py   -> results/v1-parallel/bias_bridge.json
On Windows it calls ngspice through WSL without opening console windows.
"""
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
OUT = HERE/'results/v1-parallel'
RS = 28.3          # ohm, calibrated in bias_supply_study.py
NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)


def circuit(kind, vac, i_bias, i_ccs):
    pk = vac*math.sqrt(2)
    if kind == 'half':      # as drawn: one end of the winding at ground, D5 to the raw node
        rect = 'VS a 0 SIN(0 {:.3f} 50)\nRS a a1 {}\nVT a1 a2 0\nD5 raw a2 DR\n'.format(pk, RS)
    else:                   # floating winding into a bridge: + to ground, - to the raw node
        rect = ('VS a b SIN(0 {:.3f} 50)\nRS a a1 {}\nVT a1 a2 0\nRB b 0 1meg\n'
                'D1 a2 0 DR\nD2 b 0 DR\nD3 raw a2 DR\nD4 raw b DR\n').format(pk, RS)
    return f"""* bias supply, {kind}
{rect}C13 raw 0 100u IC=-80
R23 raw neg 2.7k
C14 neg 0 100u IC=-70
IBIAS 0 neg {i_bias}
R34 raw ccs 2.2k
C19 ccs 0 100u IC=-75
ICCS 0 ccs {i_ccs}
.model DR D(IS=7.0e-9 N=1.8 RS=0.042 BV=1000 CJO=10p)
.options method=gear reltol=1e-4
.control
tran 50u 5 0 50u uic
meas tran vneg AVG v(neg) from=4 to=5
meas tran ppneg PP v(neg) from=4 to=5
meas tran vccs AVG v(ccs) from=4 to=5
meas tran ppccs PP v(ccs) from=4 to=5
meas tran vraw AVG v(raw) from=4 to=5
meas tran ppraw PP v(raw) from=4 to=5
meas tran irms RMS i(VT) from=4 to=5
meas tran idc AVG i(VT) from=4 to=5
.endc
.end
"""


def ngspice(cir_text, work):
    f = Path(work)/'b.cir'
    f.write_text(cir_text)
    if os.name == 'nt':
        wsl_path = '/mnt/' + str(f).replace(':', '').replace('\\', '/')
        wsl_path = wsl_path[:5] + wsl_path[5].lower() + wsl_path[6:]
        cmd = ['wsl.exe', '-e', 'ngspice', '-b', wsl_path]
    else:
        cmd = ['ngspice', '-b', str(f)]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=300, creationflags=NO_WINDOW).stdout
    r = {}
    for line in out.splitlines():
        k, _, v = line.partition('=')
        if k.strip() in ('vneg', 'ppneg', 'vccs', 'ppccs', 'vraw', 'ppraw', 'irms', 'idc'):
            r[k.strip()] = float(v.split()[0])
    return r


def main():
    work = tempfile.mkdtemp(prefix='bias-bridge-', dir=OUT)
    res = {}
    for kind in ['half', 'bridge']:
        res[kind] = {}
        for vac in [54., 60., 66.]:
            a = ngspice(circuit(kind, vac, 3.53e-3, 2.4e-3), work)
            b = ngspice(circuit(kind, vac, 3.53e-3, 4.4e-3), work)   # +2 mA on the raw node
            a['raw_source_ohm'] = (b['vraw']-a['vraw'])/2e-3
            res[kind][f'{vac:.0f}'] = a
    for f in Path(work).iterdir():
        f.unlink()
    os.rmdir(work)
    (OUT/'bias_bridge.json').write_text(json.dumps(res, indent=2)+'\n')
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
