import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# --------------------  Parse File ----------------------- #
path = "data/measurements/"
filename = "measurements_20250725_165539.jsonl"
filename = path + filename
with open(filename, 'r') as file:
    measurements = json.load(file)
freqs = np.array(measurements['Frequencies (Hz)'])
power = np.array(measurements['Relative Power (dB)'])

# -----------------------  Plot -------------------------- #
plt.figure(figsize=(12, 6))
plt.plot(freqs / 1e9, power)  # Convert to GHz
plt.title(f"Spectrum Measurement\n{measurements['Timestamp']}")
plt.xlabel('Frequency (GHz)')
plt.ylabel('Relative Power (dB)')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# -------------------------------------------------------- #
