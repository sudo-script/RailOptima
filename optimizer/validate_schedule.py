import os
import json
import pandas as pd
from datetime import datetime

# === Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
optimized_file = os.path.join(BASE_DIR, "schedule_output.json")
baseline_file = os.path.join(BASE_DIR, "baseline.csv")

print("[DEBUG] Validator started")

# === Load files ===
try:
    with open(optimized_file, "r") as f:
        optimized_data = json.load(f)
    print("[DEBUG] Optimized schedule loaded")
except FileNotFoundError:
    raise FileNotFoundError(f"Optimized file not found: {optimized_file}")

try:
    baseline_df = pd.read_csv(baseline_file)
    print("[DEBUG] Baseline loaded")
except FileNotFoundError:
    raise FileNotFoundError(f"Baseline file not found: {baseline_file}")

# === Convert to DataFrames ===
opt_df = pd.DataFrame(optimized_data)
opt_df.columns = opt_df.columns.str.lower()
baseline_df.columns = baseline_df.columns.str.lower()

# === Standardize time columns ===
for df in [opt_df, baseline_df]:
    if "scheduled_departure" in df.columns:
        df["scheduled_departure"] = pd.to_datetime(df["scheduled_departure"], errors="coerce").dt.strftime("%H:%M")
    if "optimized_departure" in df.columns:
        df["optimized_departure"] = pd.to_datetime(df["optimized_departure"], errors="coerce").dt.strftime("%H:%M")
    if "expected_departure" in df.columns:
        df["expected_departure"] = pd.to_datetime(df["expected_departure"], errors="coerce").dt.strftime("%H:%M")

# === Validation ===
logs = []
for _, row in opt_df.iterrows():
    baseline_row = baseline_df[baseline_df["train_id"] == row["train_id"]]

    if not baseline_row.empty:
        opt_time = row["optimized_departure"]
        baseline_time = baseline_row["expected_departure"].values[0]

        if opt_time == baseline_time:
            logs.append(f"Train {row['train_id']}: Departure Match ({opt_time})")
        else:
            reason = "conflict adjustment" if int(row.get("delay_min", 0)) > 0 else "manual override"
            logs.append(f"Train {row['train_id']}: Departure Mismatch ({opt_time} vs {baseline_time}) - Reason: {reason}")
    else:
        logs.append(f"Train {row['train_id']}: No baseline found")

# === Save log ===
log_file = os.path.join(BASE_DIR, f"validation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
with open(log_file, "w") as f:
    f.write("\n".join(logs))

print(f"[OK] Validation log saved at: {log_file}")
