import pandas as pd
from datetime import datetime

def log_audit(scenario, system_recommendation, human_override, reason, match):
    log_file = "Audit/audit_log_template.csv"

    # Prepare the row
    new_entry = {
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Scenario": scenario,
        "System_Recommendation": system_recommendation,
        "Human_Override": human_override,
        "Reason": reason,
        "Match": match,
    }

    try:
        # Load existing log
        df = pd.read_csv(log_file)
    except FileNotFoundError:
        # If first time, create with columns
        df = pd.DataFrame(columns=["Time", "Scenario", "System_Recommendation",
                                   "Human_Override", "Reason", "Match"])

    # Append new row
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)

    # Save back
    df.to_csv(log_file, index=False)


# Example usage inside validation
# Suppose optimizer says "T101 → dep 08:20", baseline says same
system_out = "T101 dep 08:20"
baseline_out = "T101 dep 08:20"

if system_out == baseline_out:
    log_audit("Day2", system_out, "-", "-", "Yes")
else:
    log_audit("Day2", system_out, baseline_out, "Mismatch found", "No")

