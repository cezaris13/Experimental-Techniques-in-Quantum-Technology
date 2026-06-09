#!/usr/bin/env python3
#!/usr/bin/env python3
"""
Plot PyRPL spectrum-analyzer CSV(s) with matplotlib.
Magnitude (dB) on top, Phase (deg) below, like the GUI.

PyRPL saves ONE channel per .dat/CSV, so the GUI's three traces
(in1 / in2 / cross) are three separate files. This script:

  * plots a single CSV that has several traces (each trace -> its own line), AND
  * overlays several CSVs (or a whole folder) so you get the 3-trace GUI view.

Colours: in1/ch1 -> blue, in2/ch2 -> green, cross -> magenta (else cycled).
Legend label per file comes from its '# name:' header.

Usage:
    python plot_curve.py file.csv
    python plot_curve.py 1.csv 2.csv 3.csv            # overlay the 3 channels
    python plot_curve.py ~/pyrpl_user_dir/curve/csv   # overlay a whole folder
    python plot_curve.py 1.csv 2.csv 3.csv out.png    # trailing image -> save
    python plot_curve.py 1.csv 2.csv 3.csv --combine combined.csv   # also merge
"""

import os
import re
import sys
import glob
from itertools import cycle

import pandas as pd
import matplotlib.pyplot as plt

SUFFIXES = ["_phase_deg", "_mag_dB", "_Vpk2", "_dB", "_re", "_im"]


def base_of(col):
    for s in SUFFIXES:
        if col.endswith(s):
            return col[: -len(s)]
    return col


def color_for(name):
    n = name.lower()
    if "cross" in n:
        return "magenta"
    if "ch1" in n or "in1" in n:
        return "blue"
    if "ch2" in n or "in2" in n:
        return "green"
    return None


def short_name(name):
    n = name.lower()
    if "cross" in n:
        return "cross"
    if "ch1" in n or "in1" in n:
        return "in1"
    if "ch2" in n or "in2" in n:
        return "in2"
    return re.sub(r"\W+", "_", name).strip("_") or "trace"


def read_header(path):
    meta = {}
    with open(path) as f:
        for line in f:
            if not line.startswith("#"):
                break
            k, _, v = line[1:].strip().partition(":")
            meta[k.strip()] = v.strip()
    return meta


def load(path):
    meta = read_header(path)
    df = pd.read_csv(path, comment="#")
    label = meta.get("name") or meta.get("curve_name") or os.path.basename(path)
    return label, df


def expand_inputs(args):
    paths = []
    for a in args:
        if os.path.isdir(a):
            paths += sorted(glob.glob(os.path.join(a, "*.csv")),
                            key=lambda p: (len(os.path.basename(p)), p))
        else:
            paths.append(a)
    return paths


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit("Usage: python plot_curve.py <file.csv> [more.csv ...] "
                 "[out.png] [--combine merged.csv]")

    combine_to = None
    if "--combine" in args:
        i = args.index("--combine")
        combine_to = args[i + 1]
        del args[i:i + 2]

    save_to = None
    if args and args[-1].lower().endswith((".png", ".pdf", ".svg")):
        save_to = args.pop()

    paths = expand_inputs(args)
    if not paths:
        sys.exit("No CSV files found.")

    files = [load(p) for p in paths]

    # ---- collect (label, base, color, columns-dict) per trace ----------
    fallback = cycle(plt.rcParams["axes.prop_cycle"].by_key()["color"])
    traces = []          # (legend, color, df, base)
    single_file = len(files) == 1

    for label, df in files:
        bases = []
        for col in df.columns[1:]:
            b = base_of(col)
            if b not in bases:
                bases.append(b)
        for b in bases:
            # legend: file name (multi-file) or trace base (single multi-trace)
            legend = label if not single_file else (b if len(bases) > 1 else label)
            col_name = legend if not single_file else b
            color = color_for(b if single_file else label) or None
            traces.append((legend, color, df, b))

    # assign cycle colours where none matched
    for k, (legend, color, df, b) in enumerate(traces):
        if color is None:
            traces[k] = (legend, next(fallback), df, b)

    any_phase = any(f"{b}_phase_deg" in df.columns for _, _, df, b in traces)

    fig, axes = plt.subplots(2 if any_phase else 1, 1, figsize=(12, 7),
                             sharex=True, squeeze=False)
    ax_mag = axes[0][0]
    ax_ph = axes[1][0] if any_phase else None

    for legend, color, df, b in traces:
        x = df[df.columns[0]]
        mag = f"{b}_mag_dB" if f"{b}_mag_dB" in df.columns else (
            f"{b}_dB" if f"{b}_dB" in df.columns else None)
        if mag:
            ax_mag.plot(x, df[mag], lw=0.6, color=color, label=legend)
        if ax_ph is not None and f"{b}_phase_deg" in df.columns:
            ax_ph.plot(x, df[f"{b}_phase_deg"], lw=0.6, color=color, label=legend)

    ax_mag.set_ylabel("Magnitude (dB)")
    ax_mag.set_title("Spectrum analyzer")
    ax_mag.grid(True, alpha=0.3)
    ax_mag.legend(fontsize=8, loc="upper right")
    if ax_ph is not None:
        ax_ph.set_ylabel("Phase (deg)")
        ax_ph.set_ylim(-180, 180)
        ax_ph.grid(True, alpha=0.3)
        ax_ph.legend(fontsize=8, loc="upper right")
        bottom = ax_ph
    else:
        bottom = ax_mag
    bottom.set_xlabel("Frequency (Hz)")
    fig.tight_layout()

    # ---- optional: merge the inputs into ONE wide CSV ------------------
    if combine_to:
        merged = None
        for label, df in files:
            sn = short_name(label)
            x = df.columns[0]
            ren = {c: (c if c == x else f"{sn}_{c}") for c in df.columns}
            d = df.rename(columns=ren)
            merged = d if merged is None else merged.merge(d, on=x, how="outer")
        merged = merged.sort_values(merged.columns[0])
        merged.to_csv(combine_to, index=False)
        print("merged ->", combine_to, "(cols:", ", ".join(merged.columns), ")")

    if save_to:
        fig.savefig(save_to, dpi=150)
        print("saved", save_to)
    else:
        plt.show()


if __name__ == "__main__":
    main()