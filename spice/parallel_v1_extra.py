#!/usr/bin/env python3
"""Extra parallel-V1 checks: V1 small-signal/noise budget and THD sweeps that
locate which stage distorts. Run after parallel_v1.py (uses its bias results).

  python3 parallel_v1_extra.py            # writes results/v1-parallel/extra.json
"""
from concurrent.futures import ProcessPoolExecutor
import json
import os
import math
from pathlib import Path
import re
import sys
import numpy as np
from parallel_v1 import Study, build_net, harmonics

HERE = Path(__file__).resolve().parent
OUT = HERE/'results/v1-parallel'
VARIANTS = ['baseline', 'parallel_scaled']
KOREN = dict(MU=112.4, EX=1.1, KG1=813, KP=623, KVB=10670)  # ECC83, amplikt88.lib
K_BOLTZ_T = 1.38e-23*300


def koren_ia(va, vg, p=KOREN):
    e1 = va/p['KP']*math.log1p(math.exp(p['KP']*(1/p['MU']+vg/math.sqrt(p['KVB']+va*va))))
    return 2*e1**p['EX']/p['KG1']


def small_signal(dc, name):
    """Per-section gm/ra from the simulator's own model at the solved operating point."""
    va, vg = dc['V1_A']-dc['V1_K'], -dc['V1_K']
    h = 1e-3
    gm = (koren_ia(va, vg+h)-koren_ia(va, vg-h))/(2*h)
    ra = 2*h/(koren_ia(va+h, vg)-koren_ia(va-h, vg))
    n = 2 if name.startswith('parallel') else 1
    r3, r4 = (235e3, 750.) if name == 'parallel_scaled' else (470e3, 1500.)
    r9 = 90e3 if name == 'parallel_scaled' else 180e3
    gm_t, ra_t, mu = n*gm, ra/n, gm*ra
    rk = r4*r9/(r4+r9)            # cathode sees R4 || R9 (secondary ~0 ohm)
    rout = r3*(ra_t+(mu+1)*rk)/(r3+ra_t+(mu+1)*rk)
    gain = mu*r3/(r3+ra_t+(mu+1)*rk)
    # Grid-referred noise resistance: triode Req ~ 3/gm (shot noise), cathode
    # resistance appears ~directly in series with the grid, plus the 1k stopper R1.
    req_valve = 3/gm_t
    req_total = req_valve+rk+1e3
    vn = math.sqrt(4*K_BOLTZ_T*req_total*20e3)
    return {'ia_per_section_mA': koren_ia(va, vg)*1e3, 'gm_per_section_mA_V': gm*1e3,
            'ra_per_section_k': ra/1e3, 'mu': mu, 'stage_gain_open': gain,
            'rout_k': rout/1e3, 'req_valve_k': req_valve/1e3, 'req_total_k': req_total/1e3,
            'input_noise_uV_20k': vn*1e6,
            # Miller term only; Cgk is largely bootstrapped by the cathode signal.
            'input_miller_pF_est': n*1.7*(1+gain)}


def sweep_point(args):
    name, bias, freq, vin = args
    study = Study(OUT)
    net = build_net((OUT/'source-export.cir').read_text(), name, bias)
    end = math.ceil(max(.15, 24/freq)*freq)/freq
    step = 1/(freq*256)
    n = re.sub(r'SIN\(0 \{VAMP\} 1k\)', f'SIN(0 {vin:.12g} {freq:g})', net)
    data = study.run(n, f'tran {step:.12g} {end:.12g} {end-10/freq:.12g} {step:.12g}\n'
                     'wrdata @DATA@ v(OT_S_HI) v(V1_A) v(LTP_A1,LTP_A2) v(V3_G1,V3_K) '
                     'v(V4_G1,V4_K) v(V1_G,V1_K)')
    t = data[:, 0]
    cols = {'out': 1, 'v1_anode': 2, 'ltp_diff': 3, 'kt88_grid': 4, 'v1_gk': 6}  # wr_singlescale
    row = {'variant': name, 'freq_Hz': freq, 'vin_peak_V': vin}
    for key, c in cols.items():
        hm = harmonics(t, data[:, c], freq)
        row[f'{key}_peak_V'] = hm['fundamental_peak_V']
        row[f'{key}_thd_pct'] = hm['thd_pct']
    row['power_W'] = row['out_peak_V']**2/16
    row['kt88_grid_max_V'] = float(max(data[:, 4].max(), data[:, 5].max()))
    row['v1_anode_min_V'] = float(data[:, 2].min())
    row['v1_anode_max_V'] = float(data[:, 2].max())
    return row


def main():
    summary = json.loads((OUT/'summary.json').read_text())
    variants = sys.argv[1:] or VARIANTS
    out_name = 'extra.json' if variants == VARIANTS else f'extra-{"-".join(variants)}.json'
    result = {'small_signal': {}, 'sweeps': []}
    for name in ['baseline', 'parallel_direct', 'parallel_scaled']:
        if name in variants or variants == VARIANTS:
            result['small_signal'][name] = small_signal(summary['variants'][name]['dc'], name)
    jobs = []
    plan = {1000: [.20, .26, .29, .31, .33, .36],
            10000: [.02, .04, .07, .10, .13, .16, .20],
            20000: [.02, .04, .06, .08]}
    if os.environ.get('EXTRA_PLAN') == 'hf':
        # 10 kHz power-bandwidth sweep: where does V2 run out of drive?
        plan = {10000: [.07, .10, .13, .16, .20, .25, .30, .36]}
        out_name = 'extra-hf.json'
    for name in variants:
        bias = summary['variants'][name]['bias_position']
        for freq, amps in plan.items():
            jobs += [(name, bias, freq, v) for v in amps]
    with ProcessPoolExecutor(max_workers=16) as pool:
        for row in pool.map(sweep_point, jobs):
            result['sweeps'].append(row)
            print(json.dumps(row), flush=True)
    (OUT/out_name).write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result['small_signal'], indent=2))


if __name__ == '__main__':
    main()
