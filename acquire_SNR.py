# This python script is used to acquire the SNR of the PlutoSDR
# It is based on the example from the Analog Devices examples
# https://raw.githubusercontent.com/analogdevicesinc/pyadi-iio/master/examples/pluto.py

# Feb 2025: Germain PHAM: 
# - experiment with a single tone signal generator has shown that the local
#   oscillator is not accurate enough to get exactly the tone in the desired bin
# - the code is modified so that user checks the bin of the signal and adjusts
#   the bin center if needed before SNR computation

import time

import adi
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy import fft
import math
import sys

import utilities

# Ask user the distance for file exports
distance = input("Please enter the distance in meters: ")

# RF parameters
Fc                = 2.5e9       # Central frequency of the band
BW                = 20e6        # Considered bandwidth of the system
Fsig_offset       = 1.00125e6   # APPROXIMATE Offset of the signal from the center frequency
Fs                = 30.72e6     # Baseband sampling frequency

# Create radio
sdr = adi.Pluto("usb:1.8.5")

# Number of acquisitions
N_acq = 15
# Samples per capture
samples_per_frame = 2**13

# Signal bin
bin_sig = math.floor(Fsig_offset/Fs*samples_per_frame)
# This will be refined later by the user at runtime

# Configure properties
sdr.rx_rf_bandwidth           = int(BW)
sdr.sample_rate               = int(Fs)
sdr.rx_lo                     = int(Fc)
sdr.rx_enabled_channels       = [0]
sdr.gain_control_mode_chan0   = "manual"
sdr.rx_buffer_size            = samples_per_frame

# Read properties
print("RX LO %s" % (sdr.rx_lo))

# Define a vector of gains to try
gain_start    = -20.
gain_stop     = 45.
gain_step     = 5.
gain_vec      = np.arange(gain_start, gain_stop, gain_step)

# Define a matrix to store the captured data
data_mat = np.zeros((samples_per_frame, len(gain_vec), N_acq), dtype=np.complex64)

# Collect data
for n_gain in range(len(gain_vec)):
    print("Acquiring data for gain = "+str(gain_vec[n_gain])+"dB")
    print("["+str(n_gain+1)+"/"+str(len(gain_vec))+"]")
    sdr.rx_hardwaregain_chan0   = gain_vec[n_gain]
    for n_acq in range(N_acq):
        print('.', end='', flush=True)
        data_mat[:,n_gain,n_acq] = sdr.rx()
        time.sleep(0.2)

# Compute the PSD for each capture
print("Compute the PSD for each capture")
data_psd_mat = np.zeros((samples_per_frame, len(gain_vec), N_acq), dtype=np.float64)
for n_gain in range(len(gain_vec)):
    for n_acq in range(N_acq):
        f, data_psd_mat[:,n_gain,n_acq] = signal.periodogram(data_mat[:,n_gain,n_acq],BW,window='blackman',return_onesided=False)

# Compute the average PSD for each gain value
print("Compute the average PSD for each gain value")
data_psd_mat_avg = np.mean(data_psd_mat, axis=2)

# The expected bin center of the signal is
print("The expected bin center of the signal is: "+str(bin_sig))

# Print message to user
print("Please check the spectrum in the plots and take note of the signal bin")
print("Please close the plot windows to continue")

# Plot the raw psd data around BIN_SIG validation and adjustment, highlight the signal bin and the 3 bins around it
plt.figure()
plt.semilogy(data_psd_mat_avg)
plt.xlabel("frequency bin index")
plt.ylabel("PSD [V**2/Hz]")
plt.xlim(bin_sig+np.array([-10, +10]))
plt.grid()
plt.title("Raw PSD data around BIN_SIG validation and adjustment")
plt.axvline(x=bin_sig, color='r', linestyle='--')
plt.axvline(x=bin_sig+3, color='k', linestyle=':')
plt.axvline(x=bin_sig-3, color='k', linestyle=':')
plt.show()

refine_bin=True
while refine_bin:

    # Ask user to adjust the signal bin
    bin_sig = input("Please enter the signal bin: ")
    # If the anwser contains "+", then compute the sum
    if "+" in bin_sig:
        bin_sig = bin_sig.split("+")
        bin_sig = int(bin_sig[0])+int(bin_sig[1])
    # If the anwser contains "-", then compute the difference
    elif "-" in bin_sig:
        bin_sig = bin_sig.split("-")
        bin_sig = int(bin_sig[0])-int(bin_sig[1])
    # Otherwise, convert the string to an integer
    else:
        bin_sig = int(bin_sig)
    print("The signal bin to be use for the power computation is now: "+str(bin_sig))
    print("Please close the plot windows to continue")

    plt.figure()
    plt.semilogy(data_psd_mat_avg)
    plt.xlabel("frequency bin index")
    plt.ylabel("PSD [V**2/Hz]")
    plt.xlim(bin_sig+np.array([-10, +10]))
    plt.grid()
    plt.title("Raw PSD data around BIN_SIG validation and adjustment")
    plt.axvline(x=bin_sig, color='r', linestyle='--')
    plt.axvline(x=bin_sig+3, color='k', linestyle=':')
    plt.axvline(x=bin_sig-3, color='k', linestyle=':')
    plt.show()
    

    # Ask user if the signal bin is correct
    refine_bin = input("Is the signal bin correct? (y/n): ")
    if refine_bin == 'y':
        refine_bin = False
    else:
        refine_bin = True


# Compute sig_power
sig_power_vec = utilities.sig_power(data_psd_mat_avg, Fsig_offset, sdr.sample_rate)
sig_power_vec_dB = 10*np.log10(sig_power_vec)
# print(str(10*np.log10(sig_power)))

#################################################
# Plotting section and file exports
#################################################

# # Debug
# plt.clf()
# plt.semilogy(f, data_psd_mat_avg[:,0])
# # plt.ylim([1e-7, 1e2])
# plt.xlabel("frequency [Hz]")
# plt.ylabel("PSD [V**2/Hz]")
# plt.draw()
# plt.show()

plot_filename = "distance_"+str(distance)+"m_spectrums.pdf"
utilities.plot_spectrums(gain_vec, data_psd_mat_avg, f, plot_filename)

# Repack data for CSV export
data_csv=np.column_stack((gain_vec, sig_power_vec_dB))

# Export signal power to a CSV file
csv_filename = "distance_"+str(distance)+"m_sig_pows.csv"
# https://stackoverflow.com/questions/36210977/python-numpy-savetxt-header-has-extra-character
np.savetxt(csv_filename, data_csv, delimiter=",", header="Gain [dB], Signal Power [dB]", comments="")

# Export average PSDs to a CSV file
csv_filename = "distance_"+str(distance)+"m_psds.csv"
np.savetxt(csv_filename, data_psd_mat_avg, delimiter=",", header="PSD [V**2/Hz]", comments="")
