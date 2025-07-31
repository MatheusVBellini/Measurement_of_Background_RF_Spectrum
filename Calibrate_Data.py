import json
import numpy as np

offset_dB = 0
filepath = "data/measurements/"
filename = "3b07.jsonl"
input_file = filepath + filename
output_file = input_file.replace(".jsonl", "_calibrated.jsonl")

# Progress estimation logic
def count_lines(file):
    with open(file, "rb") as f:
        return sum(1 for _ in f)
total = count_lines(input_file)
processed = 0
progress_0 = 0
progress_1 = 0

# Update cycle
print("Starting data calibration...")
with open(input_file, "r", encoding="utf-8") as fin, \
     open(output_file, "w", encoding="utf-8") as fout:
    for line in fin:
        # add fixed offset to every power sample
        entry = json.loads(line)
        p = np.array(entry["Relative Power (dB)"], dtype=float)
        entry["Relative Power (dB)"] = (p + offset_dB).tolist()
        fout.write(json.dumps(entry) + "\n")

        # Update statistics
        processed += 1
        progress_1 = 100 * processed / total
        if (progress_1 - progress_0 >= 5) or (progress_1 == 100):
            print(f"{processed} measurements processed ({progress_1:.0f}%)")
            progress_0 = progress_1

print(f"Written calibrated data to: {output_file}")
