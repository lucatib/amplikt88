#!/usr/bin/env python3
"""Source-impedance and capacitive-load checks after parallel_v1.py."""
import json
import sys
from pathlib import Path
from parallel_v1 import Study, build_net

HERE = Path(__file__).resolve().parent
OUT = HERE/'results/v1-parallel'


def main():
    source = (OUT/'source-export.cir').read_text()
    main_results = json.loads((OUT/'summary.json').read_text())
    study = Study(OUT)
    result = {}
    names = sys.argv[1:] or ['baseline', 'parallel_scaled']
    for name in names:
        bias = main_results['variants'][name]['bias_position']
        net = build_net(source, name, bias)
        rows = {}
        for rs in [10000, 47000]:
            n = net.replace('VIN IN_RAW', 'VIN SOURCE')+f'\nRSOURCE SOURCE IN_RAW {rs}\n'
            rows[f'source_{rs}_ohm'] = study.ac(n, f'{name}-source-{rs}')
        for cap in [1e-7, 1e-6]:
            n = net+f'\nCLOAD OT_S_HI GND {cap:g}\n'
            rows[f'loop_load_{cap:g}_F'] = study.loop(n, f'{name}-load-{cap:g}')
        result[name] = rows
        print(name, rows, flush=True)
    if sys.argv[1:]:
        (OUT/'checks-variants.json').write_text(json.dumps(result, indent=2)+'\n')
        return
    name = 'parallel_direct'
    prior = main_results['variants'][name]
    net = build_net(source, name, prior['bias_position'])
    result[name] = {'power_tests': [study.at_power(net, 1000, watts, prior['ac']['gain_1k'])
                                   for watts in [37, 60]]}
    print(name, result[name], flush=True)
    (OUT/'checks.json').write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()
