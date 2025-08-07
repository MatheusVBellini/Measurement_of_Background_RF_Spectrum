import json
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# --------------------  Parse Command Line ----------------------- #
if len(sys.argv) != 2:
    print(f"Usage: python {os.path.basename(__file__)} <path_to_jsonl_file>")
    sys.exit(1)

filename = sys.argv[1]

# --------------------  Parse File ----------------------- #
with open(filename, 'r') as file:
    measurements = json.loads(file.readline())
freqs = np.array(measurements['Frequencies (Hz)'])
power = np.array(measurements['Relative Power (dB)'])

# -----------------------  Plot -------------------------- #
plt.figure(figsize=(12, 6))
plt.plot(freqs / 1e9, power)  # Convert to GHz
plt.title(f"Spectrum Measurement\n{measurements['Timestamp']}")
plt.xlabel('Frequency (GHz)')
plt.ylabel('Power (dBm)')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# -------------------------------------------------------- #
