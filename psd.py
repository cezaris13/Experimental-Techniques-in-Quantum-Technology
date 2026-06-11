import pickle
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch

# =========================
# File name
# =========================
filename = "1.dat"   # change this if your file has another name

# =========================
# Load PyRPL .dat file
# =========================
with open(filename, "rb") as f:
    saved_data = pickle.load(f)

settings = saved_data[1]
trace = np.array(saved_data[2])

# PyRPL stores trace as:
# trace[0] = time axis
# trace[1] = voltage axis
time = trace[0]
voltage = trace[1]

# =========================
# Sampling information
# =========================
dt = np.mean(np.diff(time))
fs = 1 / dt

print(f"Duration: {settings['duration']:.6f} s")
print(f"Number of samples: {len(voltage)}")
print(f"Sampling frequency: {fs:.2f} Hz")

# =========================
# Remove DC offset
# =========================
voltage_ac = voltage - np.mean(voltage)

# =========================
# Plot time-domain signal
# =========================
plt.figure(figsize=(8, 5))
plt.plot(time, voltage)
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.title("Red Pitaya Time-Domain Voltage Trace")
plt.grid(True)
plt.tight_layout()
plt.savefig("time_domain_voltage.png", dpi=300, bbox_inches="tight")
plt.show()

# =========================
# Calculate PSD
# =========================
frequencies, psd = welch(
    voltage_ac,
    fs=fs,
    nperseg=4096,
    scaling="density"
)

# =========================
# Plot PSD
# =========================
plt.figure(figsize=(8, 5))
plt.semilogy(frequencies, psd)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Voltage PSD (V²/Hz)")
plt.title("Voltage Power Spectral Density")
plt.grid(True)
plt.tight_layout()
plt.savefig("voltage_psd.png", dpi=300, bbox_inches="tight")
plt.show()

# =========================
# Optional: Integrated noise power
# =========================
noise_power = np.trapz(psd, frequencies)
rms_voltage = np.sqrt(noise_power)

print(f"Integrated voltage noise power: {noise_power:.3e} V²")
print(f"RMS voltage noise: {rms_voltage:.3e} V")