#!/usr/bin/env python3
"""Negative bias supply on its own: 60 V winding, D5 half-wave, C13 100 uF,
R23, C14 100 uF, DC load. Used to judge whether the V2 tail current sink can
return to VBIAS_NEG (it also biases the KT88s).

  python3 bias_supply_study.py   -> results/v1-parallel/bias_supply.json

The winding series resistance is calibrated to the README's documented point
(-67 V at 5.3 mA with a 60 V winding and R23 2.7k); 54/66 V model low/high mains.
For each mains level and R23 a Thevenin equivalent (Vth, Rth) is fitted from two
loads, for use in the amplifier bench.
"""
import json
import math
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
OUT = HERE/'results/v1-parallel'
W = Path(tempfile.mkdtemp(prefix='amplikt88-bias-'))


def supply(i_load, vac=60., rs=20., r23=2.7e3, tag='b'):
    cir = f"""* bias supply
VS a 0 SIN(0 {vac*math.sqrt(2):.3f} 50)
RS a a1 {rs}
D5 raw a1 D1N4007
C13 raw 0 100u IC=-80
R23 raw neg {r23}
C14 neg 0 100u IC=-65
IL 0 neg {i_load}
.model D1N4007 D(IS=7.0e-9 N=1.8 RS=0.042 BV=1000 CJO=10p)
.options method=gear reltol=1e-4
.control
tran 50u 4 0 50u uic
meas tran vneg AVG v(neg) from=3 to=4
meas tran vpp PP v(neg) from=3 to=4
.endc
.end
"""
    f = W/f'{tag}.cir'
    f.write_text(cir)
    out = subprocess.run(['ngspice', '-b', str(f)], capture_output=True, text=True, timeout=300).stdout
    r = {}
    for line in out.splitlines():
        k, _, v = line.partition('=')
        if k.strip() in ('vneg', 'vpp'):
            r[k.strip()] = float(v.split()[0])
    return r['vneg'], r['vpp']


def calibrate():
    lo, hi = 0., 400.
    for _ in range(16):
        mid = (lo+hi)/2
        v, _ = supply(5.3e-3, rs=mid, tag='cal')
        if v < -67:   # still too negative -> more series resistance
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2


def main():
    rs = calibrate()
    print(f'winding series resistance {rs:.1f} ohm', flush=True)
    result = {'rs_ohm': rs, 'cases': []}
    for r23 in [2.7e3, 1.8e3, 1.5e3]:
        for vac in [54., 60., 66.]:
            rows = {}
            for i in [3.53e-3, 5.3e-3, 6.0e-3, 7.9e-3]:
                rows[f'{i*1e3:.2f}'] = supply(i, vac, rs, r23, tag=f'{r23:.0f}-{vac:.0f}-{i*1e4:.0f}')
            # Negative rail rises towards 0 with load: rail = vth + rth * i_load.
            (v1, _), (v2, _) = rows['3.53'], rows['6.00']
            rth = (v2-v1)/(6.0e-3-3.53e-3)
            case = {'r23': r23, 'vac': vac, 'rail': {k: v for k, (v, _) in rows.items()},
                    'ripple_pp': {k: pp for k, (_, pp) in rows.items()},
                    'vth': v1 - rth*3.53e-3, 'rth': rth}
            result['cases'].append(case)
            print(json.dumps(case), flush=True)
    (OUT/'bias_supply.json').write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()
