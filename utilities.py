import matplotlib.pyplot as plt
from scipy import fft
import numpy as np

# https://www.tutorialspoint.com/saving-all-the-open-matplotlib-figures-in-one-file-at-once
from matplotlib.backends.backend_pdf import PdfPages

cm = 1/2.54  # centimeters in inches


def plot_spectrums(gain_vec,data_psd_mat_avg,freq_vec,plot_filename):
    """
    A function that plots the spectrums of the data
    """
    # Prepare legend
    legend_prefix = "Gain = "
    legend_suffix = "dB"
    legend_vec = [legend_prefix+str(gain_vec[n_gain])+legend_suffix for n_gain in range(len(gain_vec))]


    # Compute subplot layout (based on https://stackoverflow.com/a/24829741)
    # limit plot to 5 columns
    columns = 5
    quotient, remainder = divmod(len(gain_vec), columns)
    rows = quotient
    if remainder:
        rows = rows + 1
    

    # Create one figure with multiple subplots containing the individual PSDs
    fig, axes = plt.subplots(figsize=(29.7*cm, 21*cm),nrows=rows, ncols=columns, sharex=True, sharey=True)
    axes_flat = axes.flat
    for n_gain in range(len(gain_vec)):
        axes_flat[n_gain].semilogy(fft.fftshift(freq_vec)/1e6, fft.fftshift(data_psd_mat_avg[:,n_gain]),label=legend_vec[n_gain])
        axes_flat[n_gain].grid()
        axes_flat[n_gain].legend()

    # Set axis titles
    # Operate on just the bottom row of axes:
    for ax in axes[-1, :]:
        ax.set_xlabel("Frequency [MHz]")

    # Operate on just the first column of axes:
    for ax in axes[:, 0]:
        ax.set_ylabel("PSD [V**2/Hz]")


    plt.figure(figsize=(29.7*cm, 21*cm))
    plt.semilogy(fft.fftshift(freq_vec)/1e6, fft.fftshift(data_psd_mat_avg, axes=0))
    # plt.ylim([1e-7, 1e2])
    plt.grid()
    plt.xlabel("frequency [MHz]")
    plt.ylabel("PSD [V**2/Hz]")
    plt.legend(legend_vec,ncol=3)

    save_multi_image(plot_filename)

    plt.show()

# https://www.tutorialspoint.com/saving-all-the-open-matplotlib-figures-in-one-file-at-once
def save_multi_image(filename):
    pp = PdfPages(filename)
    fig_nums = plt.get_fignums()
    figs = [plt.figure(n) for n in fig_nums]
    for fig in figs:
        fig.savefig(pp, format='pdf')
    
    pp.close()



def compute_SNR(data_psd_mat_avg, Fsig_offset, BW, sample_rate):
    """
    docstring
    """
    # Compute the signal bin
    Fsig_bin = np.fix(Fsig_offset/sample_rate*len(data_psd_mat_avg))
    # compute the signal bins with blackman window
    Fsig_bin_vec = np.arange(-2,3)+Fsig_bin
    # Compute the signal power
    Psig_vec = np.sum(data_psd_mat_avg[Fsig_bin_vec.astype(int),:],axis=0)
    # Compute the noise power
    Pnoise_vec = np.sum(data_psd_mat_avg,axis=0)-Psig_vec
    # Compute the SNR
    SNR_vec = Psig_vec/Pnoise_vec

    return SNR_vec

def sig_power(data_psd_mat_avg, Fsig_offset, sample_rate):
    """
    docstring
    """
    # Compute the signal bin
    Fsig_bin = np.fix(Fsig_offset/sample_rate*len(data_psd_mat_avg))
    # compute the signal bins with blackman window
    Fsig_bin_vec = np.arange(-2,3)+Fsig_bin
    # Compute the signal power
    Psig_vec = np.sum(data_psd_mat_avg[Fsig_bin_vec.astype(int),:],axis=0)

    return Psig_vec