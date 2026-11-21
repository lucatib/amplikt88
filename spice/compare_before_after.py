#!/usr/bin/env python3
"""Before/after check of the schematic: the same bench on two exported netlists.

  kicad-cli sch export netlist --format spice -o results/v1-parallel/schematic-export.cir ../amplikt88.kicad_sch
  python3 compare_before_after.py                      # table + results/v1-parallel/before-after.json
  python3 compare_before_after.py --check              # exit 1 if 'after' is worse on a checked figure

'before' defaults to results/v1-parallel/schematic-before.cir, the export of the
schematic before the lag move and the tail sink (R8 39k, C15 330p + R26 10k).
Bench as in simulate.py: ideal B+ 450 V, bias -65 V and, when the netlist has the
tail sink, BIAS_CCS -75.7 V (the bias-supply model's value); KT88s trimmed to 60 mA;
8 ohm load. Checked: THD at every test point, phase margin into 100 nF and 1 uF,
1 uF square-wave overshoot. Bandwidth is reported, not checked: the lag fix
narrows it on purpose (38 -> 32 kHz) for better capacitive-load margins.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import math
from pathlib import Path
import sys
import numpy as np
import parallel_v1 as p
from parallel_v1_tail import balance

HERE = Path(__file__).resolve().parent
OUT = HERE/'results/v1-parallel'
POWER = [(1000, 1), (1000, 37), (1000, 60), (10000, 10), (10000, 37), (20000, 1)]
TOL_THD = 1.03      # 3 % relative: simulation noise between two netlists
TOL_PM = 1.0        # degrees
TOL_OVERSHOOT = 1.0  # percentage points


def bench(source, pos):
    net = p.build_net(source, 'baseline', pos)
    if ' BIAS_CCS' in net:
        net += '\nV_CCS BIAS_CCS GND DC -75.7\n'
    return net


def hf_pm(loop):
    hf = [c for c in loop['unity_crossings'] if c['frequency_Hz'] > 100]
    return hf[0]['phase_margin_deg'] if hf else float('nan')


def measure(args):
    tag, path = args
    source = Path(path).read_text()
    study = p.Study(OUT)
    lo, hi = 0., 1.
    for _ in range(14):
        mid = (lo+hi)/2
        lo, hi = (mid, hi) if study.dc(bench(source, mid))['V3_K'] < .060 else (lo, mid)
    net = bench(source, (lo+hi)/2)
    r = {'dc': study.dc(net), 'ac': study.ac(net, f'cmp-{tag}'),
         'pm_resistive': hf_pm(study.loop(net, f'cmp-{tag}')),
         'pm_100n': hf_pm(study.loop(net+'\nCLOAD OT_S_HI GND 1e-7\n', f'cmp-{tag}-100n')),
         'pm_1u': hf_pm(study.loop(net+'\nCLOAD OT_S_HI GND 1e-6\n', f'cmp-{tag}-1u')),
         'overshoot': [study.square(net, c)['overshoot_pct'] for c in [0, 1e-7, 1e-6]],
         'imbalance_1k_pct': balance(study, net)['1000_Hz_pct'], 'thd': {}}
    ac = np.loadtxt(OUT/f'cmp-{tag}-ac.csv', delimiter=',', skiprows=1)
    for freq, watts in POWER:
        gain = 10**(np.interp(math.log10(freq), np.log10(ac[:, 0]), ac[:, 1])/20)
        t = study.at_power(net, freq, watts, gain)
        r['thd'][f'{freq} Hz {watts} W'] = {'power_W': t.get('power_W'), 'thd_pct': t.get('thd_pct'),
                                            'reached': t['target_reached']}
    return tag, r


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--before', default=OUT/'schematic-before.cir')
    ap.add_argument('--after', default=OUT/'schematic-export.cir')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    with ProcessPoolExecutor(2) as ex:
        res = dict(ex.map(measure, [('before', str(a.before)), ('after', str(a.after))]))
    (OUT/'before-after.json').write_text(json.dumps(res, indent=2)+'\n')
    b, n = res['before'], res['after']
    rows = [('V1 anode / V2 cathodes (V)', f"{b['dc']['V1_A']:.1f} / {b['dc']['LTP_K']:.1f}",
             f"{n['dc']['V1_A']:.1f} / {n['dc']['LTP_K']:.1f}"),
            ('-3 dB bandwidth (kHz)', f"{b['ac']['high_3dB_Hz']/1e3:.1f}", f"{n['ac']['high_3dB_Hz']/1e3:.1f}"),
            ('PM resistive / 100 nF / 1 uF (deg)', f"{b['pm_resistive']:.0f} / {b['pm_100n']:.0f} / {b['pm_1u']:.0f}",
             f"{n['pm_resistive']:.0f} / {n['pm_100n']:.0f} / {n['pm_1u']:.0f}"),
            ('10 kHz square overshoot 8 ohm / 100 nF / 1 uF (%)', ' / '.join(f'{x:.1f}' for x in b['overshoot']),
             ' / '.join(f'{x:.1f}' for x in n['overshoot'])),
            ('V2 output imbalance @1 kHz (%)', f"{b['imbalance_1k_pct']:.3f}", f"{n['imbalance_1k_pct']:.3f}")]
    for k in b['thd']:
        f = lambda t: (f"{t['thd_pct']:.3f} %" if t['reached'] else
                       f"clips: {t['power_W']:.1f} W at {t['thd_pct']:.1f} %" if t['power_W'] else 'clips')
        rows.append((f'THD {k}', f(b['thd'][k]), f(n['thd'][k])))
    print(f"{'':52} {'before':>26} {'after':>26}")
    for r in rows:
        print(f'{r[0]:52} {r[1]:>26} {r[2]:>26}')
    worse = []
    for k, t in n['thd'].items():
        tb = b['thd'][k]
        if not t['reached'] or (tb['reached'] and t['thd_pct'] > tb['thd_pct']*TOL_THD):
            worse.append(f'THD {k}')
    for k in ['pm_100n', 'pm_1u']:
        if n[k] < b[k] - TOL_PM:
            worse.append(k)
    if n['overshoot'][2] > b['overshoot'][2] + TOL_OVERSHOOT:
        worse.append('1 uF overshoot')
    print('\nworse than before:', ', '.join(worse) if worse else 'nothing')
    if a.check and worse:
        sys.exit(1)


if __name__ == '__main__':
    main()
