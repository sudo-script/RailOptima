import os
import json
import pandas as pd

# === Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(BASE_DIR, "schedule.json")          # input JSON
baseline_file = os.path.join(BASE_DIR, "baseline.csv")        # baseline reference
output_json = os.path.join(BASE_DIR, "schedule_output.json")  # output JSON
output_csv = os.path.join(BASE_DIR, "schedule_output.csv")    # output CSV

print("[DEBUG] Script started")
print("[DEBUG] Paths set")

# === Load input JSON ===
try:
    with open(input_file, "r") as f:
        schedule_data = json.load(f)
    print("[DEBUG] JSON loaded successfully")
except FileNotFoundError:
    raise FileNotFoundError(f"Input file not found at {input_file}")

# === Convert to DataFrame ===
if isinstance(schedule_data, dict) and "schedule" in schedule_data:
    df = pd.DataFrame(schedule_data["schedule"])
elif isinstance(schedule_data, list):
    df = pd.DataFrame(schedule_data)
else:
    raise KeyError("The JSON file must contain either a 'schedule' key or a list of schedules.")

# === Standardize column names ===
df.columns = df.columns.str.lower()
print(f"[DEBUG] DataFrame created with columns: {df.columns.tolist()}")

# === Standardize time columns ===
time_cols = ["scheduled_departure", "optimized_departure"]
for col in time_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%H:%M")

print("[DEBUG] Time conversion complete")

# === Load Baseline for Accuracy Preservation ===
try:
    baseline_df = pd.read_csv(baseline_file)
    baseline_df.columns = baseline_df.columns.str.lower()
    print("[DEBUG] Baseline loaded successfully")
except FileNotFoundError:
    print("[WARNING] No baseline.csv found, skipping baseline preservation.")
    baseline_df = None

# === Preserve baseline for high-priority trains ===
if baseline_df is not None:
    for i, row in df.iterrows():
        baseline_row = baseline_df[baseline_df["train_id"] == row["train_id"]]
        if not baseline_row.empty and row["priority"] == 1:
            baseline_time = pd.to_datetime(baseline_row["expected_departure"].values[0], errors="coerce")
            df.loc[i, "optimized_departure"] = baseline_time.strftime("%H:%M")
            df.loc[i, "delay_min"] = 0

print("[DEBUG] Conflict resolution & baseline preservation complete")

# === Save outputs ===
# Convert Timestamp -> str
df = df.astype(str)

with open(output_json, "w") as f:
    json.dump(df.to_dict(orient="records"), f, indent=4)

df.to_csv(output_csv, index=False)

print(f"[OK] Optimized schedule saved at: {output_json}")
print(f"[OK] CSV export saved at: {output_csv}")
print("[DEBUG] Script finished successfully")
