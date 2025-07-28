##
## Measure_with_Pluto.py
##
## This script measures the --relative-- power of a signal across a range of frequencies using an ADALM-PLUTO SDR.
## It captures data indefinetly, processes it to calculate power, and exports the results to a JSONL file.
##

import time
import adi
import numpy as np
from scipy import signal
import json
from datetime import datetime

# --------------------  Parameters  ----------------------- #
# Frequency parameters
BW          = 25e6                                              # Signal bandwidth
f_start     = 500e6                                             # Start frequency
f_stop      = 4.8e9                                             # Stop frequency
f_step      = BW*(2/3)                                                # Frequency step
orig_f_step = 100e6                                             # Original frequency step
orig_freqs  = np.arange(f_start, f_stop + orig_f_step, orig_f_step)
freqs = np.arange(f_start, f_stop + f_step, f_step)

# Sampling parameters
Fs                = int(2.3*BW)                                 # Baseband sampling frequency
samples_per_frame = 2**13                                       # Samples per capture

# Gain parameters
calibration_offset = 0.0                                              # Calibration offset for gain
orig_antenna_gains = np.loadtxt('Antenna_Gains.csv', delimiter=',')   # Vector to store gains

# Time parameters
Tc = 5                                                          # Capture period in minutes
Tc_secs = Tc * 60                                               # Capture period in seconds

# File export parameters
filename = "measurements" + datetime.now().strftime("_%Y%m%d_%H%M%S") + ".jsonl"
with open(filename, 'w') as f:
    pass
def add_data_to_file(time, frequency, power):
    data = {"Timestamp": time, "Frequencies (Hz)": frequency, "Relative Power (dB)": power}
    with open(filename, 'a') as f:
        f.write(json.dumps(data) + "\n")

# -------------------- Hardware Init ----------------------- #
sdr = adi.Pluto("usb:0.1.5")
sdr.rx_rf_bandwidth           = int(BW)
sdr.sample_rate               = int(Fs)
sdr.rx_enabled_channels       = [0]
sdr.gain_control_mode_chan0   = "manual"
sdr.rx_buffer_size            = samples_per_frame
sdr.rx_hardwaregain_chan0     = 35
time.sleep(1)  # Allow time for the SDR to adjust

# -------------------- Capture Loop ----------------------- #
# constant values
w = signal.windows.blackman(samples_per_frame)
coherent_gain_dB = -20 * np.log10(np.sum(w) / samples_per_frame)

while (True):
    freq_segments = []
    pow_segments  = []
    for n_freq, LO in enumerate(freqs):
        print(f"Acquiring data at frequency {LO / 1e6:.2f} MHz")
        sdr.rx_lo = int(LO)                              # Set the LO frequency
        time.sleep(0.1)                                    # Allow time for the SDR to adjust

        # Collect data
        data = sdr.rx()
        x = data - np.mean(data)
        X = np.fft.fftshift(np.fft.fft(x * w, n=samples_per_frame)) / samples_per_frame
        f_bb = np.fft.fftshift(np.fft.fftfreq(samples_per_frame, d=1/Fs))

        # Eliminate negative frequencies
        pos = (f_bb >= 0) & (f_bb <= f_step)
        f_bb = f_bb[pos]
        X = X[pos]

        # Calculate power spectrum
        mag_dB = 20 * np.log10(np.abs(X))
        f_rf = f_bb + LO
        antenna_gains = np.interp(f_rf, orig_freqs, orig_antenna_gains)
        mag_dB += coherent_gain_dB #- antenna_gains

        # Save data
        freq_segments.append(f_rf)
        pow_segments.append(mag_dB)

    # Concatenate frequency and power segments
    concat_freqs = np.concatenate(freq_segments)
    concat_pows = np.concatenate(pow_segments)
    order = np.argsort(concat_freqs)
    concat_freqs = (concat_freqs[order]).tolist()
    concat_pows = (concat_pows[order]).tolist()

    # Add data to file
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    add_data_to_file(current_time, concat_freqs, concat_pows)
    time.sleep(Tc_secs)  # Wait for the next capture period

# --------------------------------------------------------- #
