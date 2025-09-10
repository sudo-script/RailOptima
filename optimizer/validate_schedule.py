# optimizer/validate_schedule.py
import pandas as pd
import os
import json

# Input/output paths
input_path = os.path.join("optimizer", "schedule_output.json")
report_path = os.path.join("optimizer", "reports", "validation_report.txt")

# Load optimized schedule (JSON, not CSV)
try:
    with open(input_path, "r") as f:
        data = json.load(f)
    df = pd.DataFrame(data["schedule"])
except Exception as e:
    print(f"Error reading {input_path}: {e}")
    exit(1)

# Normalize column names
df.columns = [c.strip().lower() for c in df.columns]

results = []

# Check 1: Departures happen after arrivals (if arrival exists)
if "arrival" in df.columns:
    if all(pd.to_datetime(df["optimized_departure"]) >= pd.to_datetime(df["arrival"])):
        results.append("[OK] All departures happen after arrivals.")
    else:
        results.append("[FAIL] Some departures happen before arrivals!")
else:
    results.append("[INFO] No 'arrival' column found, skipping arrival check.")

# Check 2: Overlapping conflicts
conflicts = []
df_sorted = df.sort_values(by="scheduled_departure").reset_index(drop=True)

for i in range(1, len(df_sorted)):
    prev_train = df_sorted.loc[i-1]
    curr_train = df_sorted.loc[i]
    if pd.to_datetime(curr_train["scheduled_departure"]) < pd.to_datetime(prev_train["optimized_departure"]):
        conflicts.append((prev_train["train_id"], curr_train["train_id"]))

if conflicts:
    results.append(f"[FAIL] Overlapping conflicts found: {conflicts}")
else:
    results.append("[OK] No overlapping conflicts.")

# Check 3: No negative delays
if "delay_min" in df.columns and all(df["delay_min"] >= 0):
    results.append("[OK] No negative delays.")
else:
    results.append("[FAIL] Negative delays detected or 'delay_min' missing.")

# Check 4: Priority respected
priority_violations = []
for i in range(1, len(df_sorted)):
    prev, curr = df_sorted.loc[i-1], df_sorted.loc[i]
    if (
        pd.to_datetime(curr["optimized_departure"]) < pd.to_datetime(prev["optimized_departure"])
        and curr["priority"] < prev["priority"]
    ):
        priority_violations.append((prev["train_id"], curr["train_id"]))

if priority_violations:
    results.append(f"[FAIL] Priority violations: {priority_violations}")
else:
    results.append("[OK] Train priorities respected in scheduling.")

# Save validation report
os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(results))

# Print results
print("\n".join(results))
print(f"[OK] Validation complete. Report saved at: {report_path}")
