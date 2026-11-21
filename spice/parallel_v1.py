#!/usr/bin/env python3
"""Reproducible parallel-V1 experiment; production schematics are not edited.

Requires ngspice and NumPy. First export the current schematic with KiCad:
  kicad-cli sch export netlist --format spice -o baseline.cir amplikt88.kicad_sch
  python parallel_v1.py --netlist baseline.cir --out results/v1-parallel

Ideal B+=450V and bias=-65V; actual RC driver supplies, existing valve/OT models.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import tempfile
import numpy as np

HERE = Path(__file__).resolve().parent
CASCODE_RBOT = '263.7k'  # solved for V1_A = 89.25 V (baseline); ~47 V upper grid


def replace_part(net, ref, value):
    net, count = re.subn(rf'(?m)^({ref} \S+ \S+ )\S+', rf'\g<1>{value}', net)
    if count != 1:
        raise ValueError(f'Expected exactly one {ref}, got {count}')
    return net


def remove_part(net, ref):
    net, count = re.subn(rf'(?m)^{ref} .*\n?', '', net)
    if count != 1:
        raise ValueError(f'Expected exactly one {ref}, got {count}')
    return net


# Lag (step) compensation at V1_A replacing C15/R26 across the V2 anodes.
# *_lag: bandwidth matched to baseline (~38 kHz); *_lag_damped: 1 uF ringing and
# every phase margin at least as good as baseline, at ~30-32 kHz bandwidth.
LAG = {'baseline_lag': ('15k', '150p'), 'baseline_lag_damped': ('15k', '180p'),
       'follower_lag': ('12k', '180p'), 'follower_lag_damped': ('15k', '220p'),
       # Parallel V1 has half the output resistance: start from half R, double C.
       'parallel_scaled_lag': ('5.6k', '360p'), 'parallel_scaled_lag_damped': ('5.6k', '430p'),
       # CCS tail variants, tuned to the same margins/ringing as baseline_lag_damped.
       'ccs_low_lag': ('15k', '180p'), 'ccs_raised_lag': ('15k', '120p')}


def follower(net):
    """Spare section (pins 6/7/8) as a DC-coupled cathode follower V1 -> V2 grid."""
    net, count = re.subn(r'(?m)^XV1 (\S+) (\S+) (\S+) \S+ \S+ \S+ ECC83$',
                         r'XV1 \1 \2 \3 B_CF CF_G LTP_G1 ECC83', net)
    if count != 1:
        raise ValueError('V1 dual-triode instance not found')
    net, count = re.subn(r'(?m)^R5 V1_A LTP_G1 (\S+)$', r'R5 V1_A CF_G \1', net)
    if count != 1:
        raise ValueError('R5 V1_A LTP_G1 not found')
    # Own dropper from B_DRV (~340 V, ~250 V anode-cathode), ~1 mA in a 91k cathode load.
    return net + '\nRCF B_DRV B_CF 100k\nCCF B_CF GND 22u\nRCFK LTP_G1 GND 91k\n'


def lag_at_v1(net, name):
    rs, cs = LAG[name]
    net = remove_part(remove_part(net, 'C15'), 'R26')
    return net + f'\nRSTEP V1_A NSTEP {rs}\nCSTEP NSTEP GND {cs}\n'


# Spare section as the V2 tail current sink (replaces R8). Grid reference from a
# B_DRV divider (RCCS1 / RCCS2, bypassed); degeneration RCCSK to ground. The bias
# rail is not used: it sags under load (see README, bias supply).
#   ccs_low:    DC levels kept; 1.5 mA tail, R6/R7 150k keep the V2 anodes ~323 V.
#   ccs_raised: V1_A lifted to ~150 V so a full 2.33 mA sink fits; V1 rebiased with
#               the feedback fraction R4/(R4+R9) and time constant R9*C6 kept.
CCS = {
    'ccs_low': {'parts': [('R6', '150k'), ('R7', '150k')], 'rk': '4.7k', 'rref': '15.79k'},
    'ccs_raised': {'parts': [('R3', '362k'), ('R4', '2.65k'), ('R9', '318k'), ('C6', '6.8p')],
                   'rk': '4.7k', 'rref': '24.58k'},
}


def ccs_tail(net, name):
    cfg = CCS[name]
    net, count = re.subn(r'(?m)^XV1 (\S+) (\S+) (\S+) \S+ \S+ \S+ ECC83$',
                         r'XV1 \1 \2 \3 LTP_K CCS_G CCS_K ECC83', net)
    if count != 1:
        raise ValueError('V1 dual-triode instance not found')
    net = remove_part(net, 'R8')
    for ref, val in cfg['parts']:
        net = replace_part(net, ref, val)
    return net + (f'\nRCCSK CCS_K GND {cfg["rk"]}\nRCCS1 B_DRV CCS_G 1meg'
                  f'\nRCCS2 CCS_G GND {cfg["rref"]}\nCCCS CCS_G GND 10u\n')


def variant(net, name):
    if name == 'baseline':
        return net
    if name.startswith('ccs_'):
        base = name.removesuffix('_lag')
        net = ccs_tail(net, base)
        return lag_at_v1(net, name) if name in LAG else net
    if name.startswith('baseline_lag'):
        return lag_at_v1(net, name)
    if name.startswith('follower'):
        net = follower(net)
        return lag_at_v1(net, name) if name in LAG else net
    pattern = r'(?m)^XV1 (\S+) (\S+) (\S+) \S+ \S+ \S+ ECC83$'
    if name in ('cascode', 'cascode_comp'):
        # Active section (pins 1/2/3) at the bottom, spare (6/7/8) stacked on top as
        # common-grid stage; V1_A keeps its DC level for the DC-coupled LTP.
        net, count = re.subn(pattern, r'XV1 V1_MID \2 \3 \1 CAS_G V1_MID ECC83', net)
        if count != 1:
            raise ValueError('V1 dual-triode instance not found')
        for ref, val in [('R4', '680'), ('R9', '82k'), ('C6', '27p')]:
            net = replace_part(net, ref, val)
        net += (f'\nRCAS1 B_DRV CAS_G 2.2meg\nRCAS2 CAS_G GND {CASCODE_RBOT}'
                '\nCCAS CAS_G GND 10u\n')
        if name == 'cascode_comp':
            # Lag step at V1_A: brings HF loop gain and margins back to about baseline.
            net += '\nRSTEP V1_A NSTEP 150k\nCSTEP NSTEP GND 100p\n'
        return net
    net, count = re.subn(pattern, r'XV1 \1 \2 \3 \1 \2 \3 ECC83', net)
    if count != 1:
        raise ValueError('V1 dual-triode instance not found')
    if name.startswith('parallel_scaled'):
        for ref, val in [('R3', '235k'), ('R4', '750'), ('R22', '75k'),
                         ('R9', '90k'), ('C6', '24p'), ('C12', '44u')]:
            net = replace_part(net, ref, val)
        if name in LAG:
            net = lag_at_v1(net, name)
        elif name != 'parallel_scaled':
            raise ValueError(name)
    elif name != 'parallel_direct':
        raise ValueError(name)
    return net


def harmonics(time, voltage, freq, cycles=8):
    """Resample a coherent window, excluding duplicated FFT end point."""
    start = time[-1] - cycles/freq
    if start < time[0] - 1e-10:
        raise ValueError('Insufficient transient window')
    uniform = start + np.arange(cycles*2048)/(freq*2048)
    y = np.interp(uniform, time, voltage)
    spectrum = np.fft.rfft(y-y.mean())*2/len(y)
    h = np.abs(spectrum[cycles*np.arange(1, 11)])
    return {'fundamental_peak_V': float(h[0]),
            'power_W': float(h[0]**2/16),
            'thd_pct': float(np.linalg.norm(h[1:])/h[0]*100)}


class Study:
    def __init__(self, output):
        self.output = output
        self.tmp = tempfile.TemporaryDirectory(prefix='parallel-v1-')
        self.work = Path(self.tmp.name)
        self.counter = 0

    def run(self, net, commands):
        self.counter += 1
        stem = self.work / f'run-{self.counter}'
        dat = stem.with_suffix('.dat')
        cir = stem.with_suffix('.cir')
        cir.write_text(net + '\n.control\nset wr_singlescale\nset numdgt=15\n'
                       + commands.replace('@DATA@', dat.as_posix())
                       + '\nquit\n.endc\n.end\n')
        p = subprocess.run(['ngspice', '-b', str(cir)], capture_output=True,
                           text=True, timeout=300)
        stem.with_suffix('.log').write_text(p.stdout+p.stderr)
        if p.returncode or not dat.exists() or re.search(
                r'(?im)^.*(?:timestep too small|fatal error|simulation interrupted)', p.stdout+p.stderr):
            raise RuntimeError(f'ngspice failed: {cir}\n{p.stdout[-2000:]}\n{p.stderr[-2000:]}')
        a = np.loadtxt(dat, ndmin=2)
        if not np.isfinite(a).all():
            raise RuntimeError(f'Nonfinite data in {dat}')
        return a

    def dc(self, net):
        names = ['B_DRV', 'B_V1', 'V1_A', 'V1_K', 'LTP_K', 'LTP_A1',
                 'LTP_A2', 'V3_K', 'V4_K', 'V3_G1']
        row = self.run(net, 'op\nwrdata @DATA@ '+' '.join(f'v({x})' for x in names))[0]
        return dict(zip(names, map(float, row[1:])))

    def ac(self, net, name):
        data = self.run(net, 'ac dec 100 0.01 10meg\n'
                       'wrdata @DATA@ vdb(OT_S_HI) vp(OT_S_HI)')
        np.savetxt(self.output/f'{name}-ac.csv', data, delimiter=',',
                   header='frequency_Hz,gain_dB,phase_rad', comments='')
        f, g = data[:, 0], data[:, 1]
        ref = float(np.interp(np.log10(1000), np.log10(f), g))
        band = f[g >= ref-3]
        return {'gain_1k_dB': ref, 'gain_1k': 10**(ref/20),
                'low_3dB_Hz': float(band.min()), 'high_3dB_Hz': float(band.max())}

    def loop(self, net, name):
        # Voltage injection between the loaded secondary and the high-Z feedback
        # branch: DC topology retained, VIN AC grounded. Zout << Zfeedback is
        # required; this is not a general two-injection return-ratio method.
        n = net.replace('AC 1 SIN', 'AC 0 SIN')
        n = re.sub(r'(?m)^((?:R9|C6) .*?)OT_S_HI', r'\1FB_IN', n)
        n += '\nVTEST FB_IN OT_S_HI DC 0 AC 1\n'
        data = self.run(n, 'ac dec 140 0.001 10meg\nlet loop=-v(OT_S_HI)/v(FB_IN)\n'
                       'wrdata @DATA@ real(loop) imag(loop)')
        f = data[:, 0]
        z = data[:, 1]+1j*data[:, 2]
        db = 20*np.log10(np.abs(z))
        phase = np.unwrap(np.angle(z))*180/np.pi
        mid = np.argmin(abs(f-1000))
        phase -= 360*round(phase[mid]/360)
        cross = []
        for i in range(len(f)-1):
            if db[i]*db[i+1] <= 0:
                weight = -db[i]/(db[i+1]-db[i])
                fc = math.exp(math.log(f[i])+weight*math.log(f[i+1]/f[i]))
                pc = phase[i]+weight*(phase[i+1]-phase[i])
                cross.append({'frequency_Hz': fc, 'phase_deg': float(pc),
                              'phase_margin_deg': float(180-abs(pc))})
        np.savetxt(self.output/f'{name}-loop.csv', np.column_stack([f, db, phase]),
                   delimiter=',', header='frequency_Hz,loop_dB,phase_deg', comments='')
        return {'loop_1k_dB': float(db[mid]), 'unity_crossings': cross}

    def sine(self, net, freq, vin, duration=.15, points=256):
        end = max(duration, 24/freq)
        end = math.ceil(end*freq)/freq
        step = 1/(freq*points)
        n = re.sub(r'SIN\(0 \{VAMP\} 1k\)', f'SIN(0 {vin:.12g} {freq:g})', net)
        data = self.run(n, f'tran {step:.12g} {end:.12g} {end-10/freq:.12g} {step:.12g}\n'
                        'wrdata @DATA@ v(OT_S_HI) v(V3_G1,V3_K) v(V4_G1,V4_K) v(V1_A)')
        result = harmonics(data[:, 0], data[:, 1], freq)
        result.update(vin_peak_V=vin, freq_Hz=freq, duration_s=end,
                      points_per_cycle=points,
                      grid_peak_V=float(data[:, 2:4].max()),
                      V1_anode_mean_V=float(np.mean(data[:, 4])))
        earlier = data[data[:, 0] <= end-2/freq]
        old = harmonics(earlier[:, 0], earlier[:, 1], freq, cycles=6)
        result['window_thd_delta_pct'] = result['thd_pct']-old['thd_pct']
        return result

    def at_power(self, net, freq, power, gain):
        vin = math.sqrt(16*power)/gain
        result = {}
        for _ in range(5):
            try:
                result = self.sine(net, freq, vin)
            except subprocess.TimeoutExpired:
                result.update(note=f'drive search timed out at vin={vin:.4g} V')
                result.setdefault('power_W', 0.)
                break
            if abs(result['power_W']/power-1) < .002:
                break
            vin *= math.sqrt(power/result['power_W'])
        result['target_W'] = power
        result.update(freq_Hz=freq)
        result['target_reached'] = bool(abs(result['power_W']/power-1) <= .01)
        return result

    def square(self, net, cap):
        n = re.sub(r'SIN\(0 \{VAMP\} 1k\)',
                   'PULSE(-0.02 0.02 20u 0.5u 0.5u 49.5u 100u)', net)
        if cap:
            n += f'\nCLOAD OT_S_HI GND {cap:g}\n'
        a = self.run(n, 'tran 0.1u 2m 1.8m 0.1u\nwrdata @DATA@ v(OT_S_HI)')
        t, v = a[:, 0], a[:, 1]
        top = np.mean(v[(t >= .00194) & (t <= .001965)])
        bottom = np.mean(v[(t >= .00199) & (t <= .001999)])
        peak = max(v[(t >= .00192) & (t <= .00197)])
        return {'cap_F': cap, 'overshoot_pct': float(100*(peak-top)/(top-bottom)),
                'step_V': float(top-bottom)}


def build_net(source, name, bias):
    net = re.sub(r'(?<=\s)/', '', source)
    net = re.sub(r'(?im)^\.include .*$', f'.include "{(HERE/"amplikt88.lib").as_posix()}"', net)
    net = re.sub(r'(?im)^\.end\s*$', '', net)
    net = variant(net, name)
    net = re.sub(r'(POS=)[0-9.]+', rf'\g<1>{bias:.9f}', net)
    for i, node in enumerate(sorted(set(re.findall(r'unconnected-\S+', net)))):
        net += f'\nRFLOAT{i} {node} GND 1e9\n'
    return net + ('\nV_BPLUS B_PLUS GND DC 450\nV_NEG VBIAS_NEG GND DC -65\n'
                  'VIN IN_RAW GND DC 0 AC 1 SIN(0 {VAMP} 1k)\nRL OT_S_HI GND 8\n'
                  '.param VAMP=0\n.options reltol=1e-5 abstol=1e-11 vntol=1e-7 itl1=500 itl4=200\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--netlist', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=HERE/'results/v1-parallel')
    parser.add_argument('--quick', action='store_true', help='DC/AC/loop/square only')
    parser.add_argument('--variants', nargs='+',
                        default=['baseline', 'parallel_direct', 'parallel_scaled'])
    parser.add_argument('--resume', action='store_true', help='Reuse completed results for identical inputs')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if args.netlist.resolve() in [(args.out/f'{n}.cir').resolve() for n in
                                 ['baseline', 'parallel_direct', 'parallel_scaled', 'cascode', 'cascode_comp',
                                  'follower', 'follower_lag', 'follower_lag_damped',
                                  'baseline_lag', 'baseline_lag_damped',
                                  'parallel_scaled_lag', 'parallel_scaled_lag_damped',
                                  'ccs_low', 'ccs_raised', 'ccs_low_lag', 'ccs_raised_lag']]:
        parser.error('Use a distinct source-export.cir; variant benches are generated outputs')
    source = args.netlist.read_text()
    study = Study(args.out)
    results = {'model_sha256': hashlib.sha256((HERE/'amplikt88.lib').read_bytes()).hexdigest(),
               'netlist_sha256': hashlib.sha256(args.netlist.read_bytes()).hexdigest(),
               'ngspice_version': subprocess.check_output(['ngspice','--version'], text=True),
               'variants': {}}
    if args.resume and (args.out/'summary.json').exists():
        previous = json.loads((args.out/'summary.json').read_text())
        if any(previous[key] != results[key] for key in ['model_sha256', 'netlist_sha256']):
            raise ValueError('Resume inputs differ from recorded hashes')
        results = previous

    def save():
        (args.out/'summary.json').write_text(json.dumps(results, indent=2)+'\n')

    for name in args.variants:
        print(name, flush=True)
        item = results['variants'].get(name) if args.resume else None
        if item:
            bias = item['bias_position']
        else:
            lo, hi = 0., .95
            for _ in range(13):
                mid = (lo+hi)/2
                dc = study.dc(build_net(source, name, mid))
                if dc['V3_K'] < .060:
                    lo = mid
                else:
                    hi = mid
            bias = (lo+hi)/2
        net = build_net(source, name, bias)
        # Saved bench is independently runnable after setting VAMP and an analysis.
        portable = net.replace((HERE/'amplikt88.lib').as_posix(), '../../amplikt88.lib')
        (args.out/f'{name}.cir').write_text(portable+'\n.op\n.end\n')
        if item is None:
            item = {'bias_position': bias, 'dc': study.dc(net), 'ac': study.ac(net, name),
                    'loop_voltage_injection': study.loop(net, name),
                    'square_10k': [study.square(net, c) for c in [0, 1e-7, 1e-6]]}
        results['variants'][name] = item
        save()
        print(json.dumps(item), flush=True)
        if not args.quick and name != 'parallel_direct':
            item.setdefault('power_tests', [])
            ac = np.loadtxt(args.out/f'{name}-ac.csv', delimiter=',', skiprows=1)
            for freq, watts in [(20, 10), (100, 37), (1000, 1), (1000, 37), (1000, 60),
                                (10000, 10), (10000, 37), (20000, 1)]:
                if any(t['freq_Hz'] == freq and t['target_W'] == watts for t in item['power_tests']):
                    continue
                gain = 10**(np.interp(np.log10(freq), np.log10(ac[:,0]), ac[:,1])/20)
                test = study.at_power(net, freq, watts, gain)
                item['power_tests'].append(test)
                save()
                print(name, test, flush=True)
            item.setdefault('convergence', [])
            for test in item['power_tests']:
                if (test['freq_Hz'], test['target_W']) in [(1000,37), (1000,60), (10000,10)]:
                    if any(c['freq_Hz'] == test['freq_Hz'] and c['vin_peak_V'] == test['vin_peak_V']
                           for c in item['convergence']):
                        continue
                    check = study.sine(net, test['freq_Hz'], test['vin_peak_V'], duration=1., points=512)
                    item['convergence'].append(check)
                    save()
                    print(name, 'convergence', check, flush=True)
        results['variants'][name] = item
        save()
    print('Completed', args.out, flush=True)


if __name__ == '__main__':
    main()
