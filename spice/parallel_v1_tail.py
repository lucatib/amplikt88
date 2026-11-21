#!/usr/bin/env python3
"""Tail checks: LTP output balance and DC spread, comparing the
R8 resistor tail with the spare-triode current sink.

  python3 parallel_v1_tail.py   -> results/v1-parallel/tail.json
"""
import json
from pathlib import Path
import numpy as np
from parallel_v1 import Study, build_net
from parallel_v1_spread import with_emission

HERE = Path(__file__).resolve().parent
OUT = HERE/'results/v1-parallel'
VARIANTS = ['baseline_lag_damped', 'ccs_low_lag', 'ccs_raised_lag', 'ccs_neg_lag']
FREQS = [100, 1000, 10000, 20000]


def balance(study, net):
    """Closed-loop AC: imbalance = |A1 + A2| / |A1 - A2| at the LTP anodes."""
    data = study.run(net, 'ac dec 50 10 100k\nwrdata @DATA@ real(v(LTP_A1)) imag(v(LTP_A1)) '
                     'real(v(LTP_A2)) imag(v(LTP_A2))')
    f = data[:, 0]
    a1, a2 = data[:, 1]+1j*data[:, 2], data[:, 3]+1j*data[:, 4]
    out = {}
    for fr in FREQS:
        i = int(np.argmin(abs(f-fr)))
        out[f'{fr}_Hz_pct'] = float(abs(a1[i]+a2[i])/abs(a1[i]-a2[i])*100)
    return out


def main():
    source = (OUT/'source-export.cir').read_text()
    summary = json.loads((OUT/'summary.json').read_text())
    study = Study(OUT)
    result = {}
    for name in VARIANTS:
        net = build_net(source, name, summary['variants'][name]['bias_position'])
        item = {'balance': balance(study, net), 'spread': {}}
        nodes = ['V1_A', 'LTP_K', 'LTP_A1'] + (['CCS_K', 'CCS_G'] if name.startswith('ccs') else [])
        nodes += ['B_CCS', 'VBIAS_NEG'] if name.startswith('ccs_neg') else []
        for k, label in [(0.8, 'strong'), (1.0, 'nominal'), (1.25, 'weak')]:
            # V1 (input + spare/CCS) emission scaled; V2 nominal.
            row = study.run(with_emission(net, k), 'op\nwrdata @DATA@ '+' '.join(f'v({x})' for x in nodes))[0]
            d = dict(zip(nodes, map(float, row[1:])))
            if 'B_CCS' in d:
                d['tail_mA'] = (d['CCS_K']-d['B_CCS'])/13
                d['ccs_Vgk'] = d['CCS_G']-d['CCS_K']
            elif 'CCS_K' in d:
                d['tail_mA'] = d['CCS_K']/4.7
                d['ccs_Vgk'] = d['CCS_G']-d['CCS_K']
            else:
                d['tail_mA'] = d['LTP_K']/39
            item['spread'][label] = d
        result[name] = item
        print(name, json.dumps(item), flush=True)
    (OUT/'tail.json').write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()
