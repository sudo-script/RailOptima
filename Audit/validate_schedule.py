import pandas as pd
from datetime import datetime
import os

# ---------- CONFIG ----------
HUMAN_DECISION_FILE = r"Audit/TestData/human_decision_schedule.csv"
TOLERANCE_MIN       = 5    # widened to ±10 minutes
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

    # Check columns
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

if __name__ == "__main__":
    main()
