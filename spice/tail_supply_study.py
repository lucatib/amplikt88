#!/usr/bin/env python3
"""Tail current sink vs real supplies: mains range and single faults.

Both CCS layouts and the R8 reference run with the realistic bias network
(parallel_v1.bias_network: half-wave raw node, C13, R23 2.7k, C14). B+ scales
with mains like the bias winding (0.9 / 1.0 / 1.1).

1. Mains: retrim each KT88 to 60 mA; report the trimmer position needed (must
   stay inside the 0..1 travel), bias rail, tail current and V2 levels.
2. Faults at nominal mains with the nominal trim left in place: KT88 cathode
   current when the sink valve shorts anode-cathode, its cathode shorts to the
   heater (~0 V via the 100 ohm heater references) or it stops conducting.

  python3 tail_supply_study.py   -> results/v1-parallel/tail_supply.json
"""
import json
from pathlib import Path
import re
import parallel_v1 as p

HERE = Path(__file__).resolve().parent
OUT = HERE/'results/v1-parallel'
VARIANTS = ['baseline_lag_damped', 'ccs_raised_lag', 'ccs_neg_lag']
NODES = ['VBIAS_NEG', 'BIAS_RAW', 'V3_K', 'V4_K', 'V1_A', 'LTP_K', 'LTP_A1', 'BIAS_A']


def op(study, net, extra=()):
    names = NODES + list(extra)
    row = study.run(net, 'op\nwrdata @DATA@ '+' '.join(f'v({x})' for x in names))[0]
    return dict(zip(names, map(float, row[1:])))


def tail_ma(name, d):
    if name.startswith('ccs_neg'):
        return (d['CCS_K']-d['BIAS_CCS'])/13
    if name.startswith('ccs'):
        return d['CCS_K']/4.7
    return d['LTP_K']/39


def extra_nodes(name):
    if name.startswith('ccs_neg'):
        return ['CCS_K', 'CCS_G', 'BIAS_CCS']
    return ['CCS_K', 'CCS_G'] if name.startswith('ccs') else []


def trim(study, source, name):
    lo, hi = 0., 1.
    for _ in range(16):
        mid = (lo+hi)/2
        d = op(study, p.build_net(source, name, mid, real_bias=True))
        if d['V3_K'] < .060:
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2


def faults(name):
    if not name.startswith('ccs'):
        return {'open (R8 open)': lambda n: p.replace_part(n, 'R8', '1e9')}
    return {
        'anode-cathode short': lambda n: n+'\nRFAULT LTP_K CCS_K 10\n',
        'cathode-heater short': lambda n: n+'\nRFAULT CCS_K GND 100\n',
        'no emission': lambda n: re.sub(r'(?m)^(XV1 \S+ \S+ \S+) LTP_K ', r'\1 NC_A ', n)+'\nRNC NC_A GND 1e9\n',
    }


def main():
    source = (OUT/'source-export.cir').read_text()
    study = p.Study(OUT)
    result = {}
    for name in VARIANTS:
        item = {'mains': {}, 'faults': {}}
        for mains in [0.9, 1.0, 1.1]:
            p.MAINS = mains
            pos = trim(study, source, name)
            d = op(study, p.build_net(source, name, pos, real_bias=True), extra_nodes(name))
            d.update(trim_position=pos, tail_mA=tail_ma(name, d), KT88_mA=d['V3_K']*1e3)
            item['mains'][f'{mains:.1f}'] = d
            print(name, mains, {k: round(v, 3) for k, v in d.items()}, flush=True)
        p.MAINS = 1.0
        pos = item['mains']['1.0']['trim_position']
        for label, apply in faults(name).items():
            d = op(study, apply(p.build_net(source, name, pos, real_bias=True)), extra_nodes(name))
            d.update(KT88_mA=d['V3_K']*1e3, KT88_W_est=d['V3_K']*(450-d['V3_K']))
            if label != 'no emission' and 'CCS_K' in d:
                d['tail_mA'] = tail_ma(name, d) if label != 'cathode-heater short' else None
            item['faults'][label] = d
            print(name, label, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in d.items()}, flush=True)
        result[name] = item
    (OUT/'tail_supply.json').write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()
