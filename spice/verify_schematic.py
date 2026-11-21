#!/usr/bin/env python3
"""Verify the schematic as drawn (lag at V1_A + V2 tail sink) against the study.

Export the netlist first (Windows or Linux):
  kicad-cli sch export netlist --format spice -o results/v1-parallel/schematic-export.cir ../amplikt88.kicad_sch
  python3 verify_schematic.py --netlist results/v1-parallel/schematic-export.cir

The netlist is used unchanged (variant 'baseline'). The bench adds the realistic
bias supply (raw node, C13, R23, C14) and the power-sheet R34 2.2k / C19 100u that
feed B_CCS, so the tail sink sees the same supply as in ccs_neg_lag.
"""
import argparse
import json
import math
from pathlib import Path
import numpy as np
import parallel_v1 as p
from parallel_v1_tail import balance

HERE = Path(__file__).resolve().parent
OUT = HERE/'results/v1-parallel'
B_CCS_FEED = '\nRB34 BIAS_RAW B_CCS 2.2k\nCB19 B_CCS GND 100u\n'


def bench(source, pos):
    return p.build_net(source, 'baseline', pos, real_bias=True) + B_CCS_FEED


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--netlist', type=Path, default=OUT/'schematic-export.cir')
    args = ap.parse_args()
    source = args.netlist.read_text()
    for part in ['R29', 'C17', 'R31', 'R32', 'R33', 'C18']:
        assert f'\n{part} ' in '\n'+source, f'{part} missing: export the edited schematic'
    for part in ['R8', 'C15', 'R26']:
        assert f'\n{part} ' not in '\n'+source, f'{part} still present'
    study = p.Study(OUT)
    lo, hi = 0., 1.
    for _ in range(14):
        mid = (lo+hi)/2
        d = study.dc(bench(source, mid))
        lo, hi = (mid, hi) if d['V3_K'] < .060 else (lo, mid)
    pos = (lo+hi)/2
    net = bench(source, pos)
    names = ['VBIAS_NEG', 'B_CCS', 'CCS_G', 'CCS_K', 'LTP_K', 'LTP_A1', 'LTP_A2', 'V1_A', 'V3_K', 'V4_K']
    row = study.run(net, 'op\nwrdata @DATA@ '+' '.join(f'v({x})' for x in names))[0]
    dc = dict(zip(names, map(float, row[1:])))
    dc.update(tail_mA=(dc['CCS_K']-dc['B_CCS'])/13, ccs_Vak=dc['LTP_K']-dc['CCS_K'],
              ccs_Vgk=dc['CCS_G']-dc['CCS_K'], trim_position=pos)
    res = {'dc': dc, 'ac': study.ac(net, 'schematic'), 'loop': study.loop(net, 'schematic'),
           'loop_100n': study.loop(net+'\nCLOAD OT_S_HI GND 1e-7\n', 'schematic-100n'),
           'loop_1u': study.loop(net+'\nCLOAD OT_S_HI GND 1e-6\n', 'schematic-1u'),
           'square_10k': [study.square(net, c) for c in [0, 1e-7, 1e-6]],
           'balance': balance(study, net), 'power_tests': []}
    print(json.dumps({k: res[k] for k in ['dc', 'ac', 'balance']}, indent=1), flush=True)
    ac = np.loadtxt(OUT/'schematic-ac.csv', delimiter=',', skiprows=1)
    for freq, watts in [(1000, 1), (1000, 37), (1000, 60), (10000, 10), (10000, 37), (20000, 1)]:
        gain = 10**(np.interp(math.log10(freq), np.log10(ac[:, 0]), ac[:, 1])/20)
        t = study.at_power(net, freq, watts, gain)
        res['power_tests'].append(t)
        print(freq, watts, round(t['power_W'], 2), round(t['thd_pct'], 4), flush=True)
    (OUT/'schematic-verify.json').write_text(json.dumps(res, indent=2)+'\n')


if __name__ == '__main__':
    main()
