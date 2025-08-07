import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# -------------------- File Paths ----------------------- #
files = [
    'data/measurements/Passive Gains - 2.4GHz.csv',
    'data/measurements/Active Gains - 2.4GHz.csv'
]

# -----------------------  Plot -------------------------- #
for fp in files:
    df = pd.read_csv(fp)
    df = df.replace(',', '.', regex=True)
    df = df.dropna(subset=['Vin (mV)', 'Detection Gain (V/V)']).astype({'Vin (mV)': float, 'Detection Gain (V/V)': float})

    mask_zero      = df['Detection Gain (V/V)'] == 0
    mask_between   = (df['Detection Gain (V/V)'] > 0) & (df['Detection Gain (V/V)'] <= 1)
    mask_above_one = df['Detection Gain (V/V)'] > 1

    # create a new figure for this file
    plt.figure(figsize=(10, 6))

    if mask_zero.any():
        plt.plot(df.loc[mask_zero, 'Vin (mV)'], df.loc[mask_zero, 'Detection Gain (V/V)'],
                 '--', color='gray', label='gain = 0')
    if mask_between.any():
        plt.plot(df.loc[mask_between, 'Vin (mV)'], df.loc[mask_between, 'Detection Gain (V/V)'],
                 '-',  linewidth=2, color='red',  label='0 < gain ≤ 1')
    if mask_above_one.any():
        plt.plot(df.loc[mask_above_one, 'Vin (mV)'], df.loc[mask_above_one, 'Detection Gain (V/V)'],
                 '-',  linewidth=2, color='blue', label='gain > 1')

    plt.xlabel('Vin (mV)')
    plt.ylabel('Detection Gain (V/V)')
    plt.title(f'Gain vs. Vin • {Path(fp).stem}')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(Path(fp).with_suffix('.png'), dpi=300)

    plt.show()
