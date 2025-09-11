
import pandas as pd
from datetime import datetime
import os

# ======================
# Setup audit log
# ======================
LOG_FILE = r"Audit/audit_log_template.csv"

def log_audit(run_name, scenario, system_recommendation, human_override, reason, match, notes=""):
    """Append a row to the audit log."""
    new_entry = {
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Run": run_name,
        "Scenario": scenario,
        "System_Recommendation": system_recommendation,
        "Human_Override": human_override,
        "Reason": reason,
        "Match": match,
        "Notes": notes
    }

    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
    else:
        df = pd.DataFrame(columns=new_entry.keys())

    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(LOG_FILE, index=False)

def start_audit_run(run_name):
    """Add a separator row at the start of a new audit run."""
    sep_row = {
        "Time": "",
        "Run": run_name,
        "Scenario": f"===== START {run_name.upper()} =====",
        "System_Recommendation": "",
        "Human_Override": "",
        "Reason": "",
        "Match": "",
        "Notes": ""
    }
    blank_row = {col: "" for col in sep_row.keys()}

    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
    else:
        df = pd.DataFrame(columns=sep_row.keys())

    df = pd.concat([df, pd.DataFrame([sep_row, blank_row])], ignore_index=True)
    df.to_csv(LOG_FILE, index=False)

# ======================
# Generic audit function
# ======================
def run_audit(optimizer_path, baseline_path, run_name=None):
    """Compare optimizer output with baseline and append generic log messages."""
    optimizer_df = pd.read_csv(optimizer_path)
    baseline_df = pd.read_csv(baseline_path)

    # Auto-generate run_name from baseline filename if not provided
    if run_name is None:
        run_name = os.path.splitext(os.path.basename(baseline_path))[0]

    # Start a new audit run with separator
    start_audit_run(run_name)

    # Compare optimizer vs baseline
    for idx, row in optimizer_df.iterrows():
        train_id = row["train_id"]
        opt_time = pd.to_datetime(row["optimized_departure"]).strftime("%H:%M")
        system_out = f"{train_id} dep {opt_time}"

        baseline_row = baseline_df[baseline_df["Train_ID"] == train_id]

        if baseline_row.empty:
            log_audit(run_name, "Train Not Found", system_out, "-", "Train missing in baseline", "No")
        else:
            baseline_time = pd.to_datetime(baseline_row["Expected_Departure"].values[0]).strftime("%H:%M")
            baseline_out = f"{train_id} dep {baseline_time}"

            if opt_time == baseline_time:
                log_audit(run_name, "Departure Match", system_out, "-", "Times match", "Yes", "System matches baseline")
            else:
                log_audit(run_name, "Departure Mismatch", system_out, baseline_out,
                          "Times differ", "No", "System time differs from baseline")

    print(f" Audit run '{run_name}' complete. Check {LOG_FILE} for results.")

# ======================
# Example usage
# ======================
if __name__ == "__main__":
    optimizer_path = r"Audit/schedule_output.csv"
    baseline_path = r"Audit/test_scenarios_day2.csv"

    run_audit(optimizer_path, baseline_path)
