#!/usr/bin/env python3
"""Plots for the amplikt88 simulation: spice/simulation.png.

Compares the schematic as drawn (ECC83 pair, 120k/18p feedback) with the first
attempt (47k/47p) and an ECC82 pair. Needs matplotlib on top of simulate.py's
requirements.

    python3 spice/plot.py
"""
import cmath, math, os, re, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import simulate as sim

# Reference palette, categorical slots 1-3 (validated all-pairs, light mode)
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
VARIANTS = [
    ("ECC83 pair, 120k / 18p (schematic)", "ecc83", "120k", "18p", "#2a78d6"),
    ("ECC83 pair, 47k / 47p", "ecc83", "47k", "47p", "#eb6834"),
    ("ECC82 pair, 47k / 47p", "ecc82", "47k", "47p", "#1baf7a"),
]


def num(s):
    return float(s.replace("k", "e3").replace("p", "e-12").replace("u", "e-6"))


def closed_loop(net, ltp, pos, rf, cf):
    rows, _ = sim.ngspice(sim.bench(net, ltp, pos, rf, cf), "ac dec 40 10 1meg\nwrdata @DAT@ vdb(OT_S_HI)", "cl")
    ref = min(rows, key=lambda x: abs(x[0] - 1000))[1]
    return [x[0] for x in rows], [x[1] - ref for x in rows]


def loop_gain(net, ltp, pos, rf, cf):
    rows, _ = sim.ngspice(sim.bench(net, ltp, pos, rf, cf, open_loop=True),
                          "ac dec 60 10 5meg\nlet A = v(OT_S_HI)/v(V1_G)\nwrdata @DAT@ real(A) imag(A)", "loop")
    R, C = num(rf), num(cf)
    f, mag, ph = [], [], []
    for x in rows:
        zf = 1 / (1 / R + 1j * 2 * math.pi * x[0] * C)
        t = complex(x[1], x[3]) * 1000 / (1000 + zf)
        f.append(x[0]); mag.append(20 * math.log10(abs(t))); ph.append(math.degrees(cmath.phase(t)))
    for i in range(1, len(ph)):
        while ph[i] - ph[i - 1] > 180: ph[i] -= 360
        while ph[i] - ph[i - 1] < -180: ph[i] += 360
    return f, mag, ph


def square(net, ltp, pos, rf, cf, cload):
    n = sim.bench(net, ltp, pos, rf, cf)
    n = re.sub(r"VIN IN_RAW GND DC 0 AC 1 SIN\([^)]*\)",
               "VIN IN_RAW GND DC 0 AC 1 PULSE(-0.06 0.06 20u 0.5u 0.5u 49.5u 100u)", n) + f"CL OT_S_HI GND {cload}\n"
    rows, _ = sim.ngspice(n, "tran 0.2u 500u 0 0.2u\nwrdata @DAT@ v(OT_S_HI)", "sq")
    seg = [(x[0], x[1]) for x in rows if 400e-6 <= x[0] <= 500e-6]
    hi = [v for t, v in seg if 440e-6 <= t <= 468e-6]
    lo = [v for t, v in seg if 490e-6 <= t <= 499e-6]
    top, bot = sum(hi) / len(hi), sum(lo) / len(lo)
    return [(t - 400e-6) * 1e6 for t, v in seg], [(v - bot) / (top - bot) for t, v in seg]


def style(ax, title, xlabel, ylabel):
    ax.set_facecolor(SURFACE)
    ax.set_title(title, loc="left", fontsize=10.5, color=INK, pad=8)
    ax.set_xlabel(xlabel, fontsize=9, color=INK2)
    ax.set_ylabel(ylabel, fontsize=9, color=INK2)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=8.5, length=0)


def hz(ax):
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v / 1e6:g}M" if v >= 1e6 else f"{v / 1e3:g}k" if v >= 1e3 else f"{v:g}"))


def main():
    net = sim.export_netlist()
    data, table = [], []
    for label, ltp, rf, cf, color in VARIANTS:
        pos = sim.find_bias(net, ltp, rf, cf)
        data.append((label, color, closed_loop(net, ltp, pos, rf, cf), loop_gain(net, ltp, pos, rf, cf),
                     square(net, ltp, pos, rf, cf, "1u")))
        m = sim.loop_margins(net, ltp, pos, rf, cf)
        p = sim.power_test(net, ltp, pos, rf, cf)
        table.append((label, m["loop_gain_1k_dB"], m.get("phase_margin_deg"), m.get("gain_margin_dB"),
                      f'{p["P_8ohm_W"]} W: {p["THD_pct"]} %', f'{sim.overshoot(net, ltp, pos, rf, cf, "0.1u")} / {sim.overshoot(net, ltp, pos, rf, cf, "1u")} %'))

    fig, axs = plt.subplots(2, 2, figsize=(11.5, 8.6), facecolor=SURFACE)
    fig.subplots_adjust(left=0.07, right=0.97, top=0.92, bottom=0.27, hspace=0.38, wspace=0.22)
    ax = axs[0, 0]; style(ax, "Closed-loop response", "Frequency (Hz)", "Gain relative to 1 kHz (dB)"); hz(ax)
    for label, c, cl, lg, sq in data:
        ax.plot(*cl, color=c, linewidth=1.6, solid_capstyle="round", label=label)
    ax.axhline(-3, color=INK2, linewidth=0.8, linestyle=(0, (1, 3)))
    ax.set_xlim(10, 1e6); ax.set_ylim(-40, 3)
    ax.text(12, -2.4, "-3 dB", fontsize=8, color=INK2, va="bottom")
    ax = axs[0, 1]; style(ax, "Loop gain", "Frequency (Hz)", "Loop gain (dB)"); hz(ax)
    for label, c, cl, lg, sq in data:
        ax.plot(lg[0], lg[1], color=c, linewidth=1.6, solid_capstyle="round")
    ax.axhline(0, color=INK2, linewidth=0.8); ax.set_xlim(1e3, 2e6); ax.set_ylim(-60, 30)
    ax.text(1.2e3, 0.8, "0 dB", fontsize=8, color=INK2)
    ax = axs[1, 0]; style(ax, "Loop phase (stable while above -180)", "Frequency (Hz)", "Phase (degrees)"); hz(ax)
    for label, c, cl, lg, sq in data:
        k = [i for i, f in enumerate(lg[0]) if f >= 1e3]
        ax.plot([lg[0][i] for i in k], [lg[2][i] for i in k], color=c, linewidth=1.6, solid_capstyle="round")
    ax.axhline(-180, color=INK2, linewidth=0.8); ax.set_xlim(1e3, 2e6); ax.set_ylim(-320, 20)
    ax.text(1.2e3, -176, "-180 deg", fontsize=8, color=INK2, va="bottom")
    ax = axs[1, 1]; style(ax, "10 kHz square wave into 8 ohm + 1 uF", "Time (us)", "Output, normalised to the flat top")
    for label, c, cl, lg, sq in data:
        ax.plot(sq[0], sq[1], color=c, linewidth=1.6, solid_capstyle="round")
    ax.axhline(1, color=GRID, linewidth=0.8); ax.set_xlim(15, 100)
    handles = [plt.Line2D([0], [0], color=c, linewidth=2.2) for _, c, *_ in data]
    fig.legend(handles, [d[0] for d in data], loc="upper center", ncol=3, frameon=False, fontsize=9.5,
               bbox_to_anchor=(0.5, 0.995), labelcolor=INK)
    cols = ["Variant", "Loop gain\nat 1 kHz", "Phase\nmargin", "Gain\nmargin", "Power and THD\nat 1 kHz", "Overshoot, 0.1 / 1 uF\n(10 kHz square)"]
    cell = [[t[0], f"{t[1]} dB", f"{t[2]} deg", f"{t[3]} dB", t[4], t[5]] for t in table]
    tab = fig.add_axes([0.07, 0.03, 0.90, 0.16]); tab.axis("off")
    tb = tab.table(cellText=cell, colLabels=cols, loc="center", cellLoc="left", colWidths=[0.30, 0.10, 0.10, 0.10, 0.17, 0.23])
    tb.auto_set_font_size(False); tb.set_fontsize(8.8); tb.scale(1, 1.75)
    for (r, c_), cl in tb.get_celld().items():
        cl.set_edgecolor(GRID); cl.set_facecolor(SURFACE)
        cl.get_text().set_color(INK if r else INK2)
        if r == 0: cl.set_height(cl.get_height() * 1.35)
    fig.canvas.draw()
    for i, (_, c, *_) in enumerate(data, start=1):   # colored key beside the name
        cell = tb[(i, 0)]
        tab.add_patch(plt.Rectangle((cell.get_x() + 0.012, cell.get_y() + cell.get_height() / 2 - 0.045), 0.012, 0.09,
                                    transform=tab.transAxes, facecolor=c, edgecolor="none", clip_on=False))
        cell.get_text().set_text("      " + data[i - 1][0])
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "simulation.png")
    fig.savefig(out, dpi=150, facecolor=SURFACE)
    print(out)


if __name__ == "__main__":
    main()
