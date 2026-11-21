#!/usr/bin/env python3
"""Verify the schematic as drawn (lag at V1_A + V2 tail sink) against the study.

Export the netlist first (Windows or Linux):
  kicad-cli sch export netlist --format spice -o results/v1-parallel/schematic-export.cir ../amplikt88.kicad_sch
  python3 verify_schematic.py --netlist results/v1-parallel/schematic-export.cir

The netlist is used unchanged (variant 'baseline'). The bench adds the realistic
bias supply (raw node, C13, R23, C14) and the power-sheet R34 2.2k / C19 100u that
feed BIAS_CCS, so the tail sink sees the same supply as in ccs_neg_lag.
"""
import argparse
import re
import json
import math
from pathlib import Path
import numpy as np
import parallel_v1 as p
from parallel_v1_tail import balance

HERE = Path(__file__).resolve().parent
OUT = HERE/'results/v1-parallel'
B_CCS_FEED = '\nRB34 BIAS_RAW BIAS_CCS 2.2k\nCB19 BIAS_CCS GND 100u\n'


def bench(source, pos):
    return p.build_net(source, 'baseline', pos, real_bias=True) + B_CCS_FEED


def sink_nodes(net):
    """Anode, grid and cathode nodes of V1's spare section (pins 6/7/8), read from
    the XV1 line so the check survives label changes (e.g. an auto-named
    Net-_V1A-K_ once the CCS_K label is replaced by a wire)."""
    fields = re.search(r'(?m)^XV1 (.*) ECC83$', net).group(1).split()
    return dict(zip(['anode', 'grid', 'cathode'], [f.lstrip('/') for f in fields[3:6]]))


def part_value(net, ref):
    """Resistance of a part in ohms, from its netlist line (e.g. R31 ... 13k)."""
    value = re.search(rf'(?m)^{ref} \S+ \S+ (\S+)', net).group(1)
    m = re.fullmatch(r'([0-9.]+)(meg|[kmMG]?)', value)
    return float(m.group(1))*{'': 1, 'k': 1e3, 'meg': 1e6, 'M': 1e6, 'G': 1e9, 'm': 1e-3}[m.group(2)]


def polarised_cap_warnings(net, nodes, dc):
    """C18 is an electrolytic on the sink's grid (about -46 V): its pin 1 (+) must
    be the more positive node. SPICE does not care, the real part does."""
    m = re.search(r'(?m)^C18 (\S+) (\S+) ', net)
    plus, minus = (x.lstrip('/') for x in m.groups())
    vp, vm = (0.0 if x == 'GND' else dc[x] for x in (plus, minus))
    return [] if vp >= vm else [f'C18 reverse-biased: + on {plus} ({vp:.1f} V), - on {minus} ({vm:.1f} V)']


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
    nodes = sink_nodes(net)
    names = ['VBIAS_NEG', 'BIAS_CCS', 'LTP_K', 'LTP_A1', 'LTP_A2', 'V1_A', 'V3_K', 'V4_K']
    names += [n for n in (nodes['grid'], nodes['cathode']) if n not in names]
    row = study.run(net, 'op\nwrdata @DATA@ '+' '.join(f'v({x})' for x in names))[0]
    dc = dict(zip(names, map(float, row[1:])))
    k, g = dc[nodes['cathode']], dc[nodes['grid']]
    dc.update(sink_nodes=nodes, tail_mA=(k-dc['BIAS_CCS'])/part_value(net, 'R31')*1e3,
              ccs_Vak=dc[nodes['anode']]-k, ccs_Vgk=g-k, trim_position=pos)
    warnings = polarised_cap_warnings(net, nodes, dc)
    for w in warnings:
        print('WARNING:', w, flush=True)
    res = {'dc': dc, 'warnings': warnings, 'ac': study.ac(net, 'schematic'), 'loop': study.loop(net, 'schematic'),
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
