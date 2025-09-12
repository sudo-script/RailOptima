import os
import pandas as pd
from datetime import datetime, timedelta

# ==========================================================
# Configuration
# ==========================================================
OPTIMIZER_OUTPUT = r"Audit/schedule_output_big_data.csv"   # <-- change if your file is elsewhere
OUTPUT_FILE      = r"Audit/TestData/human_decision_schedule.csv"
# ==========================================================

# Scheduling constants (must match the agreed rules)
BASE_BUFFER = 3                # minutes
PRIORITY_BUFFER_EXTRA = 2       # extra minutes per priority gap
MAX_DELAY = 30                 # maximum allowed delay in minutes
# ==========================================================

def recompute_human_decision(df: pd.DataFrame) -> pd.Series:
    """
    Independently compute the 'human decision' optimized departure times
    from the optimizer output, using the same rules.
    Returns a pandas Series of HH:MM strings.
    """
    # work on a copy of the key columns
    tmp = df[["train_id", "scheduled_departure", "priority"]].copy()
    tmp["scheduled_departure"] = pd.to_datetime(tmp["scheduled_departure"], format="%H:%M", errors="coerce")
    tmp = tmp.sort_values("scheduled_departure").reset_index(drop=True)

    tmp["human_time"] = tmp["scheduled_departure"].copy()

    for i in range(1, len(tmp)):
        prev_time = tmp.loc[i-1, "human_time"]
        curr_time = tmp.loc[i, "human_time"]
        priority_gap = max(0, tmp.loc[i-1, "priority"] - tmp.loc[i, "priority"])
        dynamic_buffer = BASE_BUFFER + PRIORITY_BUFFER_EXTRA * priority_gap

        if curr_time <= prev_time + pd.Timedelta(minutes=dynamic_buffer):
            if tmp.loc[i, "priority"] < tmp.loc[i-1, "priority"]:
                new_time = prev_time + pd.Timedelta(minutes=dynamic_buffer)
                delay = (new_time - tmp.loc[i, "scheduled_departure"]).total_seconds() / 60
                if delay <= MAX_DELAY:
                    tmp.loc[i, "human_time"] = new_time
                else:
                    shift_prev = curr_time - pd.Timedelta(minutes=dynamic_buffer)
                    tmp.loc[i-1, "human_time"] = shift_prev
            else:
                for j in range(i-1, -1, -1):
                    if tmp.loc[j, "priority"] < tmp.loc[i, "priority"]:
                        new_prev = curr_time - pd.Timedelta(minutes=dynamic_buffer)
                        tmp.loc[j, "human_time"] = new_prev
                        break
                else:
                    new_time = prev_time + pd.Timedelta(minutes=dynamic_buffer)
                    tmp.loc[i, "human_time"] = new_time

    tmp["human_time"] = tmp["human_time"].dt.strftime("%H:%M")

    # map back to the original order of the optimizer output
    human_map = tmp.set_index("train_id")["human_time"]
    return df["train_id"].map(human_map)

def main():
    print("[DEBUG] Loading optimizer output:", OPTIMIZER_OUTPUT)
    df = pd.read_csv(OPTIMIZER_OUTPUT)

    required = {"train_id","scheduled_departure","priority","optimized_departure","delay_min"}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"Missing columns in optimizer output: {missing}")

    print("[DEBUG] Recomputing human decisions based on rules")
    df["human_decision"] = recompute_human_decision(df)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"[OK] Human decision file saved at: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
