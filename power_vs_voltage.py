import matplotlib.pyplot as plt
import numpy as np

# Data
optical_power_plus = np.array([
    9.999, 20.01, 29.75, 39.41, 50.32, 59.99,
    70.96, 79.99, 90.80, 100.4, 110.4, 120.3
])

output_plus = np.array([
    76.5, 157.4, 235.7, 313.3, 403.3, 481.6,
    569.6, 643.7, 730.2, 809.0, 889.2, 969.5
])

optical_power_minus = np.array([
    10.06, 19.78, 29.83, 39.36, 49.72, 60.16,
    70.15, 80.48, 90.80, 100.8, 110.3, 121.1
])

output_minus = -np.array([
    66.5, 143.8, 224.1, 304.9, 383.8, 471.5,
    552.8, 636.0, 720.1, 800.5, 877.2, 962.0
])

# Linear fits
slope_plus, intercept_plus = np.polyfit(
    optical_power_plus, output_plus, 1
)
slope_minus, intercept_minus = np.polyfit(
    optical_power_minus, output_minus, 1
)

fit_plus = slope_plus * optical_power_plus + intercept_plus
fit_minus = slope_minus * optical_power_minus + intercept_minus

print(f"Slope (+): {slope_plus:.3f} mV/µW")
print(f"Slope (-): {slope_minus:.3f} mV/µW")

# Plot
plt.figure(figsize=(8, 6))

plt.scatter(
    optical_power_plus,
    output_plus,
    label="Output + Data"
)

plt.plot(
    optical_power_plus,
    fit_plus,
    label=f"Output + Fit (slope = {slope_plus:.3f} mV/µW)"
)

plt.scatter(
    optical_power_minus,
    output_minus,
    label="Output - Data"
)

plt.plot(
    optical_power_minus,
    fit_minus,
    '--',
    label=f"Output - Fit (slope = {slope_minus:.3f} mV/µW)"
)

plt.axhline(0, linewidth=1)

plt.xlabel("Optical Power (µW)")
plt.ylabel("Output Voltage (mV)")
plt.title("Output Voltage vs Optical Power")
plt.grid(True)
plt.legend()
plt.tight_layout()

# Save figure
plt.savefig(
    "output_voltage_vs_optical_power.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()