
import pandas as pd
from datetime import datetime

def log_audit(scenario, system_recommendation, human_override, reason, match, notes=""):
    log_file = r"C:/Users/Lenovo/OneDrive/Documents/RailOptima/Audit/audit_log_template.csv"

    new_entry = {
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Scenario": scenario,
        "System_Recommendation": system_recommendation,
        "Human_Override": human_override,
        "Reason": reason,
        "Match": match,
        "Notes": notes
    }

    try:
        df = pd.read_csv(log_file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Time", "Scenario", "System_Recommendation",
                                   "Human_Override", "Reason", "Match", "Notes"])

    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(log_file, index=False)

# ======================
# STEP 1: Load optimizer output
# ======================
optimizer_df = pd.read_csv(r"C:/Users/Lenovo/OneDrive/Documents/RailOptima/Audit/schedule_output copy.csv")
baseline_df = pd.read_csv(r"C:/Users/Lenovo/OneDrive/Documents/RailOptima/Audit/test_scenarios_day3_manual.csv")

# ======================
# STEP 2: Normalize column names
# ======================
# Standardize both DataFrames to 'train_id' and 'departure'
optimizer_df.rename(columns={
    "Train_ID": "train_id",
    "Train": "train_id",
    "Departure": "optimized_departure",
    "Dep Time": "optimized_departure"
}, inplace=True)

baseline_df.rename(columns={
    "Train_ID": "train_id",
    "Train": "train_id",
    "Dep Time": "expected_departure",
    "Departure": "expected_departure"
}, inplace=True)

# ======================
# STEP 3: Compare row by row
# ======================
for idx, row in optimizer_df.iterrows():
    train_id = row.get("train_id")
    optimized_departure = str(row.get("optimized_departure")).strip()

    if train_id is None or optimized_departure is None:
        log_audit("Day3", "-", "-", "Missing train_id or departure", "No", "Data missing in optimizer output")
        continue

    system_out = f"{train_id} dep {optimized_departure}"

    # Find matching train in baseline
    baseline_row = baseline_df[baseline_df["train_id"] == train_id]

    if not baseline_row.empty:
        expected_departure = str(baseline_row["expected_departure"].values[0]).strip()
        baseline_out = f"{train_id} dep {expected_departure}"

        if optimized_departure == expected_departure:
            log_audit("Day3", system_out, "-", "-", "Yes", "Matches baseline")
        else:
            log_audit("Day3", system_out, baseline_out, "Mismatch found", "No",
                      "System gave different time than manual baseline")
    else:
        log_audit("Day3", system_out, "-", "-", "No", "Train not found in baseline")