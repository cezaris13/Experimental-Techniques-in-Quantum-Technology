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

    nperseg = min(1024, len(voltage))

    # Safety check: noverlap must be less than nperseg
    noverlap = max(0, nperseg // 2)
    if noverlap >= nperseg:
        noverlap = nperseg - 1

    nfft = max(4096, nperseg)

    print(f"len={len(voltage)}, nperseg={nperseg}, noverlap={noverlap}, nfft={nfft}")

    frequencies, psd = welch(
        voltage,
        fs=fs,
        window="hamming",
        nperseg=nperseg,
        noverlap=noverlap,
        nfft=nfft,
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


'''
# =========================
# SELECT LOWEST, MIDDLE, HIGHEST
# =========================

measurements = sorted(measurements, key=lambda x: x["avg_voltage"])

lowest = measurements[0]
middle = measurements[len(measurements)//2]
highest = measurements[-1]

selected = [
    ("Lowest", lowest),
    ("Middle", middle),
    ("Highest", highest)
]

print("Selected measurements:")
for name, m in selected:
    print(f"{name}: {m}")

# =========================
# NOISE FLOOR
# =========================

# Use the lowest monitor voltage as the electronic noise floor
time_noise, voltage_noise = load_pyrpl_dat(lowest["rf_file"])
freq_noise, psd_noise = calculate_psd(time_noise, voltage_noise)

# =========================
# PLOT 1: RAW PSD
# =========================

plt.figure(figsize=(8,5))

for name, m in selected:
    time_rf, voltage_rf = load_pyrpl_dat(m["rf_file"])
    frequencies, psd = calculate_psd(time_rf, voltage_rf)

    plt.semilogy(
        frequencies,
        psd,
        linewidth=2,
        label=f"{name}: Vmon={m['avg_voltage']:.3e} V"
    )

plt.xscale("log")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Voltage PSD (V²)")
plt.title("PSD Comparison: Lowest, Middle, Highest")
plt.grid(True, which="both")
plt.legend()
plt.tight_layout()

plt.savefig(
    "psd_lowest_middle_highest.png",
    dpi=600,
    bbox_inches="tight"
)

plt.show()

# =========================
# PLOT 2: NOISE CLEARANCE
# =========================
# =========================
# PLOT 2: NOISE CLEARANCE IN dB
# =========================

plt.figure(figsize=(8,5))
plt.xlim(1e3, 1e7)
for name, m in selected:
    if name == "Lowest":
        continue

    time_rf, voltage_rf = load_pyrpl_dat(m["rf_file"])
    frequencies, psd = calculate_psd(time_rf, voltage_rf)

    # Noise clearance in dB above electronic noise floor
    clearance_db = 10 * np.log10(psd / psd_noise)

    plt.semilogx(
        frequencies,
        clearance_db,
        linewidth=2,
        label=f"{name}: Vmon={m['avg_voltage']:.3e} V"
    )

plt.axhline(0, linestyle="--", linewidth=1)

plt.xlabel("Frequency (Hz)")
plt.ylabel("Noise Clearance (dB)")
plt.title("Noise Clearance Above Electronic Noise Floor")
plt.grid(True, which="both")
plt.legend()
plt.tight_layout()

plt.savefig(
    "noise_clearance_db_lowest_middle_highest.png",
    dpi=600,
    bbox_inches="tight"
)

plt.show()

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
plt.xscale('log')
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
'''
# =========================
# PLOT PSD CLEARANCE
# =========================

plt.figure(figsize=(10,6))
# Noise floor = lowest monitor voltage
time_noise, voltage_noise = load_pyrpl_dat(lowest["rf_file"])
freq_noise, psd_noise = calculate_psd(time_noise, voltage_noise)
for m in measurements:

    time_rf, voltage_rf = load_pyrpl_dat(m["rf_file"])
    frequencies, psd = calculate_psd(time_rf, voltage_rf)

    # PSD clearance above noise floor
    clearance_psd = psd - psd_noise

    # avoid negative values on log scale
    clearance_psd[clearance_psd <= 0] = np.nan

    plt.semilogy(
        frequencies,
        clearance_psd,
        linewidth=1.5,
        label=f"{m['avg_voltage']:.3e} V"
    )

plt.xscale("log")
plt.xlim(1e3, 1e7)
plt.xlabel("Frequency (Hz)")
plt.ylabel("PSD Clearance (V²)")
plt.title("PSD Clearance Above Electronic Noise Floor")

plt.grid(True, which="both")

plt.legend(
    title="Monitor Voltage",
    fontsize=8,
    bbox_to_anchor=(1.05, 1),
    loc="upper left"
)

plt.tight_layout()

plt.savefig(
    "all_psd_clearance_curves.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# =========================
# SORT BY MONITOR VOLTAGE
# =========================

measurements = sorted(measurements, key=lambda x: x["avg_voltage"])

print("Measurements found:")

for m in measurements:
    print(
        f"{m['rf_file']} | "
        f"Monitor voltage = {m['avg_voltage']:.3e} V"
    )

# =========================
# PLOT ALL PSD CURVES
# =========================

plt.figure(figsize=(10,6))

for m in measurements:

    time_rf, voltage_rf = load_pyrpl_dat(m["rf_file"])

    frequencies, psd = calculate_psd(
        time_rf,
        voltage_rf
    )

    plt.semilogy(
        frequencies,
        psd,
        linewidth=1.5,
        label=f"{m['avg_voltage']:.3e} V"
    )

plt.xscale("log")

plt.xlabel("Frequency (Hz)")
plt.ylabel("Voltage PSD (V²)")
plt.title("RF Output PSD for All Measurements")

plt.grid(True, which="both")

plt.legend(
    title="Monitor Voltage",
    fontsize=8,
    bbox_to_anchor=(1.05, 1),
    loc="upper left"
)

plt.tight_layout()

plt.savefig(
    "all_psd_curves.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
