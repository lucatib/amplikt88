#!/usr/bin/env python3
"""Merge per-variant result folders (results/v1-parallel-<variant>/) into
results/v1-parallel/summary.json so every variant shares one comparison file."""
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
MAIN = HERE/'results/v1-parallel'


def main():
    summary = json.loads((MAIN/'summary.json').read_text())
    for folder in sorted(HERE.glob('results/v1-parallel-*')):
        part = json.loads((folder/'summary.json').read_text())
        for key in ['model_sha256', 'netlist_sha256']:
            if part[key] != summary[key]:
                raise ValueError(f'{folder.name}: {key} differs from main study')
        for name, item in part['variants'].items():
            summary['variants'][name] = item
            print('merged', name)
        for f in folder.iterdir():
            if f.name == 'summary.json':
                continue
            target = MAIN/(f'{folder.name.removeprefix("v1-parallel-")}-{f.name}' if f.name == 'run.log' else f.name)
            shutil.copy2(f, target)
        shutil.rmtree(folder)
    (MAIN/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')


if __name__ == '__main__':
    main()
