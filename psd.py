import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch

# =========================
# SETTINGS
# =========================

number_of_files = 12   # change to total number of .dat files
nperseg_default = 4096

# If True, pair 1 is used as the zero-power electronic noise floor
subtract_electronic_noise = True

# =========================
# LOAD PyRPL .dat FILE
# =========================

def load_pyrpl_dat(filename):
    with open(filename, "rb") as f:
        saved_data = pickle.load(f)

    trace = np.array(saved_data[2])

    time = trace[0]
    voltage = trace[1]

    return time, voltage

# =========================
# CALCULATE RF NOISE POWER
# =========================

def calculate_rf_noise_power(time, voltage):
    dt = np.mean(np.diff(time))
    fs = 1 / dt

    # Remove DC offset before PSD
    voltage_ac = voltage - np.mean(voltage)

    nperseg = min(nperseg_default, len(voltage_ac))

    frequencies, psd = welch(
        voltage_ac,
        fs=fs,
        nperseg=nperseg,
        scaling="spectrum"
    )
    print(frequencies.shape)
    exit()
    plt.semilogy(frequencies, psd)
    
    # Integrated noise power in V²
    noise_power = np.trapz(psd, frequencies)

    # RMS noise voltage in V
    rms_noise_voltage = np.sqrt(noise_power)

    return noise_power, rms_noise_voltage, frequencies, psd

# =========================
# PROCESS FILE PAIRS
# =========================

pair_numbers = []
monitor_avg_voltage = []
rf_noise_power_total = []
rf_rms_voltage_total = []

for pair_start in range(1, number_of_files + 1, 2):
    rf_file = f"{pair_start}.dat"
    monitor_file = f"{pair_start + 1}.dat"

    if not os.path.exists(rf_file) or not os.path.exists(monitor_file):
        print(f"Skipping missing pair: {rf_file}, {monitor_file}")
        continue

    # Load files
    time_rf, voltage_rf = load_pyrpl_dat(rf_file)
    time_monitor, voltage_monitor = load_pyrpl_dat(monitor_file)

    # Average monitor voltage = proxy for optical power
    avg_monitor = np.mean(voltage_monitor)

    # RF noise power
    noise_power, rms_noise, frequencies, psd = calculate_rf_noise_power(
        time_rf,
        voltage_rf
    )

    pair_number = (pair_start + 1) // 2

    pair_numbers.append(pair_number)
    monitor_avg_voltage.append(avg_monitor)
    rf_noise_power_total.append(noise_power)
    rf_rms_voltage_total.append(rms_noise)

    print(f"Pair {pair_number}: {rf_file} + {monitor_file}")
    print(f"  Average monitor voltage: {avg_monitor:.6e} V")
    print(f"  Total RF noise power: {noise_power:.6e} V²")
    print(f"  Total RF RMS noise voltage: {rms_noise:.6e} V")
    print()

# Convert to arrays
pair_numbers = np.array(pair_numbers)
monitor_avg_voltage = np.array(monitor_avg_voltage)
rf_noise_power_total = np.array(rf_noise_power_total)
rf_rms_voltage_total = np.array(rf_rms_voltage_total)

# =========================
# SUBTRACT ELECTRONIC NOISE FLOOR
# =========================

if subtract_electronic_noise:
    electronic_noise_floor = rf_noise_power_total[0]

    rf_noise_power_corrected = rf_noise_power_total - electronic_noise_floor

    # Prevent tiny negative values from numerical noise
    rf_noise_power_corrected[rf_noise_power_corrected < 0] = 0

    rf_rms_voltage_corrected = np.sqrt(rf_noise_power_corrected)

    print("Electronic noise subtraction enabled")
    print(f"Electronic noise floor from Pair 1: {electronic_noise_floor:.6e} V²")
    print()
else:
    electronic_noise_floor = 0
    rf_noise_power_corrected = rf_noise_power_total
    rf_rms_voltage_corrected = rf_rms_voltage_total

# =========================
# SORT BY MONITOR VOLTAGE
# =========================

sort_index = np.argsort(monitor_avg_voltage)

monitor_avg_voltage = monitor_avg_voltage[sort_index]
rf_noise_power_total = rf_noise_power_total[sort_index]
rf_noise_power_corrected = rf_noise_power_corrected[sort_index]
rf_rms_voltage_total = rf_rms_voltage_total[sort_index]
rf_rms_voltage_corrected = rf_rms_voltage_corrected[sort_index]

# =========================
# PLOT 1: TOTAL RF NOISE POWER
# =========================

plt.figure(figsize=(8, 5))
plt.plot(
    monitor_avg_voltage,
    rf_noise_power_total,
    "o-",
    label="Total RF noise power"
)

plt.xlabel("Average Monitor Voltage (V)")
plt.ylabel("Integrated RF Noise Power (V²)")
plt.title("Total RF Noise Power vs Monitor Voltage")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("total_rf_noise_power_vs_monitor_voltage.png", dpi=300, bbox_inches="tight")
plt.show()

# =========================
# PLOT 2: ELECTRONIC-NOISE-SUBTRACTED RF NOISE POWER
# =========================

plt.figure(figsize=(8, 5))
plt.plot(
    monitor_avg_voltage,
    rf_noise_power_corrected,
    "o-",
    label="RF noise power - electronic noise floor"
)

plt.xlabel("Average Monitor Voltage (V)")
plt.ylabel("Corrected RF Noise Power (V²)")
plt.title("Corrected RF Noise Power vs Monitor Voltage")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("corrected_rf_noise_power_vs_monitor_voltage.png", dpi=300, bbox_inches="tight")
plt.show()

# =========================
# PLOT 3: CORRECTED RMS NOISE VOLTAGE
# =========================

plt.figure(figsize=(8, 5))
plt.plot(
    monitor_avg_voltage,
    rf_rms_voltage_corrected,
    "s-",
    label="Corrected RF RMS noise voltage"
)

plt.xlabel("Average Monitor Voltage (V)")
plt.ylabel("Corrected RF RMS Noise Voltage (V)")
plt.title("Corrected RF RMS Noise Voltage vs Monitor Voltage")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("corrected_rf_rms_noise_voltage_vs_monitor_voltage.png", dpi=300, bbox_inches="tight")
plt.show()