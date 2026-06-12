import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch

# =========================
# SETTINGS
# =========================

number_of_files = 12
nperseg_default = 4096

# =========================
# LOAD PyRPL FILE
# =========================

def load_pyrpl_dat(filename):
    with open(filename, "rb") as f:
        saved_data = pickle.load(f)

    trace = np.array(saved_data[2])

    time = trace[0]
    voltage = trace[1]

    return time, voltage

# =========================
# CALCULATE PSD
# =========================

def calculate_psd(time, voltage):

    dt = np.mean(np.diff(time))
    fs = 1 / dt

    voltage = voltage - np.mean(voltage)

    nperseg = min(nperseg_default, len(voltage))
    frequencies, psd = welch(
        voltage,
        fs=fs,
        window="hamming",
        noverlap=0,
        nfft=2**12,
        scaling="spectrum"
    )

    return frequencies, psd

# =========================
# FIND LOWEST AND HIGHEST
# MONITOR VOLTAGES
# =========================

measurements = []

for pair_start in range(1, number_of_files + 1, 2):

    rf_file = f"{pair_start}.dat"
    monitor_file = f"{pair_start+1}.dat"

    if not os.path.exists(rf_file):
        continue

    if not os.path.exists(monitor_file):
        continue

    time_mon, voltage_mon = load_pyrpl_dat(monitor_file)

    avg_monitor_voltage = np.mean(voltage_mon)

    measurements.append({
        "rf_file": rf_file,
        "monitor_file": monitor_file,
        "avg_voltage": avg_monitor_voltage
    })

# Lowest monitor voltage
lowest = min(measurements, key=lambda x: x["avg_voltage"])

# Highest monitor voltage
highest = max(measurements, key=lambda x: x["avg_voltage"])

print("Lowest monitor voltage:")
print(lowest)

print()

print("Highest monitor voltage:")
print(highest)

# =========================
# CALCULATE PSDs
# =========================

time_low, voltage_low = load_pyrpl_dat(lowest["rf_file"])
time_high, voltage_high = load_pyrpl_dat(highest["rf_file"])

freq_low, psd_low = calculate_psd(time_low, voltage_low)
freq_high, psd_high = calculate_psd(time_high, voltage_high)

# =========================
# PLOT PSD COMPARISON
# =========================

plt.figure(figsize=(8,5))

plt.semilogy(
    freq_low,
    psd_low,
    label=f"Lowest monitor voltage ({lowest['avg_voltage']:.3e} V)"
)

plt.semilogy(
    freq_high,
    psd_high,
    label=f"Highest monitor voltage ({highest['avg_voltage']:.3e} V)"
)

plt.xlabel("Frequency (Hz)")
plt.ylabel("Voltage PSD (V²/Hz)")
plt.title("PSD Comparison")
plt.grid(True, which="both")
plt.legend()
plt.tight_layout()

plt.savefig(
    "psd_highest_vs_lowest_voltage.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()