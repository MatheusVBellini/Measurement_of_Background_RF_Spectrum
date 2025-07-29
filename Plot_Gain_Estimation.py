##
## Plot_Gain_Estimation.py
##
## This script plots the gain estimation for interpolated measured gain points.
##

import time
import adi
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

# --------------------  Parameters  ----------------------- #
# Frequency parameters
BW          = 25e6                                              # Signal bandwidth
f_start     = 500e6                                             # Start frequency
f_stop      = 4.8e9                                             # Stop frequency
f_step      = BW*(2/3)                                          # Frequency step
orig_f_step = 100e6                                             # Original frequency step
orig_freqs  = np.arange(f_start, f_stop + orig_f_step, orig_f_step)
freqs = np.arange(f_start, f_stop + f_step, f_step)

# Sampling parameters
Fs                = int(2.3*BW)                                 # Baseband sampling frequency
samples_per_frame = 2**13                                       # Samples per capture

# Gain parameters
calibration_offset = 0.0                                                                # Calibration offset for gain
orig_antenna_gains = np.loadtxt('data/measurements/Antenna_Gains.csv', delimiter=',')   # Vector to store gains

# Time parameters
Tc = 5                                                          # Capture period in minutes
Tc_secs = Tc * 60                                               # Capture period in seconds

# -------------------- Hardware Init ----------------------- #
sdr = adi.ad9361(uri="ip:137.194.172.35")
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

freq_segments = []
gain_segments  = []
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

    # Save data
    freq_segments.append(f_rf)
    gain_segments.append(antenna_gains)

# Concatenate frequency and power segments
concat_freqs = np.concatenate(freq_segments)
concat_gains = np.concatenate(gain_segments)
order = np.argsort(concat_freqs)
concat_freqs = (concat_freqs[order]).tolist()
concat_gains = (concat_gains[order]).tolist()

# -----------------------  Plot -------------------------- #
plt.figure(figsize=(12, 6))
plt.plot(orig_freqs / 1e9, orig_antenna_gains, 'ro', label='Real Gain Measurements')
plt.plot(np.array(concat_freqs) / 1e9, concat_gains, '-', color='blue', label='Interpolated Gain')
plt.title("Antenna Gain")
plt.xlabel('Frequency (GHz)')
plt.ylabel('Gain (dB)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# --------------------------------------------------------- #
