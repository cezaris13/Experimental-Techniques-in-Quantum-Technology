#!/usr/bin/env python3
#!/usr/bin/env python3
"""
Plot a converted PyRPL spectrum-analyzer CSV with matplotlib.

Reproduces the GUI: Magnitude (dB) on top, Phase (deg) below.
Auto-detects columns, so it works whether they are named in1_in1_dB /
cross_phase_deg or the trace_N fallback.

Usage:
    python plot_curve.py ~/pyrpl_user_dir/curve/csv/1.csv
    python plot_curve.py 1.csv out.png      # also save to file
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt

if len(sys.argv) < 2:
    sys.exit("Usage: python plot_curve.py <file.csv> [out.png]")

path = sys.argv[1]
save_to = sys.argv[2] if len(sys.argv) > 2 else None

# '#' lines are the params header written by the converter -> skip them.
df = pd.read_csv(path, comment="#")
xcol = df.columns[0]                       # frequency_Hz
x = df[xcol]

db_cols    = [c for c in df.columns if c.endswith("_dB")]
phase_cols = [c for c in df.columns if c.endswith("_phase_deg")]

have_phase = bool(phase_cols)
fig, axes = plt.subplots(2 if have_phase else 1, 1, figsize=(11, 7),
                         sharex=True, squeeze=False)
ax_mag = axes[0][0]

for c in db_cols:
    ax_mag.plot(x, df[c], lw=0.6, label=c[:-3])
ax_mag.set_ylabel("Magnitude (dB)")
ax_mag.set_title("Spectrum analyzer")
ax_mag.grid(True, alpha=0.3)
if db_cols:
    ax_mag.legend(fontsize=8, loc="upper right")

if have_phase:
    ax_ph = axes[1][0]
    for c in phase_cols:
        ax_ph.plot(x, df[c], lw=0.6, label=c[:-len("_phase_deg")])
    ax_ph.set_ylabel("Phase (deg)")
    ax_ph.set_ylim(-180, 180)
    ax_ph.grid(True, alpha=0.3)
    if len(phase_cols) > 1:
        ax_ph.legend(fontsize=8, loc="upper right")
    bottom = ax_ph
else:
    bottom = ax_mag

bottom.set_xlabel("Frequency (Hz)")
fig.tight_layout()

if save_to:
    fig.savefig(save_to, dpi=150)
    print("saved", save_to)
else:
    plt.show()
