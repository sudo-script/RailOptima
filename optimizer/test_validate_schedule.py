import os
import pandas as pd
import subprocess

# Paths
BASELINE_FILE = "optimizer/baseline.csv"
SCHEDULE_FILE = "optimizer/schedule_output.csv"
VALIDATOR_SCRIPT = "optimizer/validate_schedule.py"
REPORT_FILE = "optimizer/reports/validation_report.txt"

def run_validator():
    """Run validator.py and capture its output."""
    print(">>> Running validator ...")
    try:
        result = subprocess.run(
            ["python", VALIDATOR_SCRIPT],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Validator failed:", e.stderr)
        return None


def setup_case(case_name, schedule_df, baseline_df):
    """Set up test case by writing schedule & baseline to CSV."""
    print(f"\n[TEST] Setting up case: {case_name}")
    schedule_df.to_csv(SCHEDULE_FILE, index=False)
    baseline_df.to_csv(BASELINE_FILE, index=False)


def run_case(case_name, schedule_df, baseline_df):
    """Run a single test case."""
    setup_case(case_name, schedule_df, baseline_df)
    output = run_validator()
    if output:
        print(f"[RESULT] {case_name} ✅\n")
        print(output)
    else:
        print(f"[RESULT] {case_name} ❌\n")


def main():
    # ---- Perfect Match Case ----
    schedule_pm = pd.DataFrame({
        "train_id": ["T1", "T2"],
        "arrival": ["08:00", "08:30"],
        "optimized_departure": ["08:10", "08:40"],
        "priority": [1, 2],
        "delay_min": [0, 0],
        "conflict_resolved": [0, 0],
    })
    baseline_pm = pd.DataFrame({
        "Train_ID": ["T1", "T2"],
        "Expected_Departure": ["08:10", "08:40"]
    })
    run_case("Perfect Match Case", schedule_pm, baseline_pm)

    # ---- Conflict Case ----
    schedule_conf = schedule_pm.copy()
    schedule_conf.loc[1, "optimized_departure"] = "08:45"  # shifted
    schedule_conf.loc[1, "delay_min"] = 5
    baseline_conf = baseline_pm.copy()
    run_case("Conflict Case", schedule_conf, baseline_conf)

    # ---- Missing Baseline Entry ----
    schedule_missing = schedule_pm.copy()
    schedule_missing.loc[len(schedule_missing)] = ["T3", "09:00", "09:10", 3, 0, 0]
    baseline_missing = baseline_pm.copy()
    run_case("Missing Baseline Entry", schedule_missing, baseline_missing)


if __name__ == "__main__":
    main()
