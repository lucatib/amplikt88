#!/usr/bin/env python3
"""DC sensitivity of each spare-triode variant to ECC83 emission spread.

V2 is DC-coupled to V1, so whatever V1's output level does, the LTP follows.
Both V1 sections are scaled together (same envelope), KG1 x0.8 = ~+25 % current,
KG1 x1.25 = ~-20 % current.   python3 parallel_v1_spread.py  -> results/v1-parallel/spread.json
"""
import json
from pathlib import Path
import re
from parallel_v1 import Study, build_net

HERE = Path(__file__).resolve().parent
OUT = HERE/'results/v1-parallel'
SPREAD = [(0.8, 'strong'), (1.0, 'nominal'), (1.25, 'weak')]
NODES = {'baseline': [], 'parallel_scaled': [], 'cascode': ['V1_MID', 'CAS_G'],
         'follower': ['B_CF', 'CF_G']}
COMMON = ['V1_A', 'V1_K', 'LTP_G1', 'LTP_K', 'LTP_A1']


def with_emission(net, k):
    net = re.sub(r'(?m)^(XV1 .*) ECC83$', r'\1 ECC83X', net)
    section = 'TRIODE MU=112.4 EX=1.1 KG1={:g} KP=623 KVB=10670 CGK=1.6p CGP=1.7p CPK=0.46p'.format(813*k)
    return net + (f'\n.subckt ECC83X A1 G1 K1 A2 G2 K2\nX1 A1 G1 K1 {section}\n'
                  f'X2 A2 G2 K2 {section}\n.ends\n')


def main():
    source = (OUT/'source-export.cir').read_text()
    summary = json.loads((OUT/'summary.json').read_text())
    study = Study(OUT)
    result = {}
    for name, extra in NODES.items():
        net = build_net(source, name, summary['variants'][name]['bias_position'])
        names = COMMON+extra
        result[name] = {}
        for k, label in SPREAD:
            row = study.run(with_emission(net, k), 'op\nwrdata @DATA@ '+' '.join(f'v({x})' for x in names))[0]
            d = dict(zip(names, map(float, row[1:])))
            if name == 'cascode':
                d.update(lower_Vak=d['V1_MID']-d['V1_K'], upper_Vak=d['V1_A']-d['V1_MID'],
                         upper_Vgk=d['CAS_G']-d['V1_MID'])
            if name == 'follower':
                d.update(cf_Vak=d['B_CF']-d['LTP_G1'], cf_Vgk=d['CF_G']-d['LTP_G1'])
            result[name][label] = d
            print(name, label, {a: round(b, 2) for a, b in d.items()}, flush=True)
    (OUT/'spread.json').write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()
