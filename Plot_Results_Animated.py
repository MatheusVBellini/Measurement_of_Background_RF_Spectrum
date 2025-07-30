import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from datetime import datetime

# --------------------  Aux Functions ----------------------- #
path = "data/measurements/"
filename = path + "measurements_20250728_164416.jsonl"

def stream_data(filepath):
    with open(filepath, "rb") as f:
        for line in f:
            entry = json.loads(line)
            ts = datetime.fromisoformat(entry["Timestamp"])
            freqs = np.array(entry["Frequencies (Hz)"])
            pows  = np.array(entry["Relative Power (dB)"])
            yield ts, freqs, pows

# -----------------------  Plot -------------------------- #
data_stream = stream_data(filename)

# grab first two frames (and keep both freq arrays in case they ever change)
t0, f0, p0 = next(data_stream)
t1, f1, p1 = next(data_stream)

fig, ax = plt.subplots(figsize=(16, 8))

# the spectrum line
line, = ax.plot(f0, p0, linewidth=1.5, antialiased=True)

# axis labels
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("Relative Power (dB)")

# fixed axes limits
ax.set_xlim(f0.min(), f0.max())
ymin = min(p0.min(), p1.min())
ymax = max(p0.max(), p1.max())
m = 0.1*(ymax - ymin)
ax.set_ylim(ymin - m, ymax + m)

# prepare container for annotation artists
annotations = []

# precompute the bin edges at 0.5 GHz steps
bin_edges = np.arange(0.5e9, f0.max() + 0.5e9, 0.5e9)

frame_interp = 1
step = 0

def update(_):
    global t0, t1, f0, f1, p0, p1, step, annotations

    # update spectrum
    line.set_ydata(p1)
    # update title to show current time
    ax.set_title(f"Time: {t1.strftime('%Y-%m-%d %H:%M:%S')}")

    # remove old annotations
    for art in annotations:
        art.remove()
    annotations.clear()

    # for each 0.5 GHz bin, find and mark the peak
    for lo, hi in zip(bin_edges[:-1], bin_edges[1:]):
        mask = (f1 >= lo) & (f1 < hi)
        if not np.any(mask):
            continue
        # index of peak within this bin
        local_idx = np.argmax(p1[mask])
        # get actual frequency & power
        freq_peak = f1[mask][local_idx]
        pow_peak  = p1[mask][local_idx]

        # plot a little marker
        mk, = ax.plot(freq_peak, pow_peak, marker='o', markersize=5)
        # and a text label just above it
        txt = ax.text(
            freq_peak,
            pow_peak,
            f"{freq_peak/1e9:.2f} GHz\n{pow_peak:.1f} dB",
            fontsize=8, ha='center', va='bottom'
        )
        annotations.extend([mk, txt])

    # advance the two-frame buffer
    step += 1
    if step >= frame_interp:
        try:
            t0, p0 = t1, p1
            t1, f1, p1 = next(data_stream)
            step = 0
        except StopIteration:
            # no more data → stop updating
            return [line] + annotations

    # return all artists that changed
    return [line] + annotations

ani = FuncAnimation(fig, update, interval=20, blit=False)
plt.show()
