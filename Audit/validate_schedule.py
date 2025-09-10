import pandas as pd
from datetime import datetime

def log_audit(scenario, system_recommendation, human_override, reason, match, notes=""):
    log_file = "Audit/audit_log_template.csv"

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
optimizer_df = pd.read_csv("schedule_output.csv")   # <-- Input from Member 2
baseline_df = pd.read_csv("test_scenarios_day3_manual.csv")  # <-- Your manual baseline

# ======================
# STEP 2: Compare row by row
# ======================
for idx, row in optimizer_df.iterrows():
    train_id = row["train_id"]
    system_out = f"{train_id} dep {row['optimized_departure']}"

    # Find matching train in baseline
    baseline_row = baseline_df[baseline_df["Train_ID"] == train_id]

    if not baseline_row.empty:
        baseline_out = f"{train_id} dep {baseline_row['Expected_Departure'].values[0]}"

        if row["optimized_departure"] == baseline_row["Expected_Departure"].values[0]:
            log_audit("Day3", system_out, "-", "-", "Yes", "Matches baseline")
        else:
            log_audit("Day3", system_out, baseline_out, "Mismatch found", "No",
                      "System gave different time than manual baseline")
    else:
        log_audit("Day3", system_out, "-", "-", "No", "Train not found in baseline")
