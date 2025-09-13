import pandas as pd
from datetime import datetime
import os

# ---------- CONFIG ----------
HUMAN_DECISION_FILE = r"Audit/TestData/human_decision_schedule.csv"
AUDIT_LOG_FILE      = r"Audit/TestData/audit_log_template.csv"
TOLERANCE_MIN       = 5
SCENARIO_NAME       = "human_decision_schedule"    # scenario tag
RUN_ID              = datetime.now().strftime("%Y%m%d_%H%M%S")
# ----------------------------

def time_diff_minutes(t1, t2):
    """Absolute difference in minutes between two HH:MM strings."""
    fmt = "%H:%M"
    dt1 = datetime.strptime(t1, fmt)
    dt2 = datetime.strptime(t2, fmt)
    return abs((dt1 - dt2).total_seconds() / 60)

def main():
    print("[DEBUG] Loading human decisions:", HUMAN_DECISION_FILE)
    df = pd.read_csv(HUMAN_DECISION_FILE)

    required = {"train_id","scheduled_departure","priority",
                "optimized_departure","human_decision"}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"Missing columns in human decision file: {missing}")

    # Match if within tolerance
    df["match"] = df.apply(
        lambda row: time_diff_minutes(row["human_decision"],
                                      row["optimized_departure"]) <= TOLERANCE_MIN,
        axis=1
    )

    accuracy = df["match"].mean() * 100
    print(f"[RESULT] Agreement within ±{TOLERANCE_MIN} min: {accuracy:.2f}%")

    # ---------- Build log rows for this run ----------
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_rows = []
    for _, row in df.iterrows():
        log_rows.append({
            "Time": now,
            "Scenario": SCENARIO_NAME,
            "System_Recommendation": row["optimized_departure"],
            "Human_Override": row["human_decision"],
            "Reason": "",
            "match": row["match"],
            "Match": "YES" if row["match"] else "NO",
            "Notes": "",
            "Run": RUN_ID
        })

    # ---- Add a dotted separator row AFTER the full batch ----
    log_rows.append({
        "Time": "........................................",  # separator marker
        "Scenario": "",
        "System_Recommendation": "",
        "Human_Override": "",
        "Reason": "",
        "match": "",
        "Match": "",
        "Notes": "",
        "Run": ""
    })

    log_df = pd.DataFrame(log_rows)

    # create file with header if it doesn't exist yet
    if not os.path.isfile(AUDIT_LOG_FILE):
        log_df.to_csv(AUDIT_LOG_FILE, index=False, mode="w")
    else:
        # append without headers so each run's data + separator is one block
        log_df.to_csv(AUDIT_LOG_FILE, index=False, mode="a", header=False)

    print("-" * 60)
    print(f"[INFO] Appended {len(df)} records plus separator to {AUDIT_LOG_FILE}")
    print(f"[INFO] Run ID: {RUN_ID}")
    print("-" * 60)

if __name__ == "__main__":
    main()
