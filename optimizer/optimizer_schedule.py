import os
import json
import pandas as pd

# =========================
# File paths
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
input_file  = os.path.join(BASE_DIR, "schedule.json")
output_json = os.path.join(BASE_DIR, "schedule_output.json")
output_csv  = os.path.join(BASE_DIR, "schedule_output.csv")

print("[DEBUG] Optimizer started")

# =========================
# Load input JSON
# =========================
with open(input_file, "r") as f:
    schedule_data = json.load(f)

if isinstance(schedule_data, dict) and "schedule" in schedule_data:
    df = pd.DataFrame(schedule_data["schedule"])
elif isinstance(schedule_data, list):
    df = pd.DataFrame(schedule_data)
else:
    raise KeyError("JSON must contain 'schedule' key or be a list of schedules")

df.columns = df.columns.str.lower()

# Convert times to datetime
df["scheduled_departure"] = pd.to_datetime(df["scheduled_departure"], format="%H:%M", errors="coerce")
df["optimized_departure"] = df["scheduled_departure"].copy()
df["delay_min"] = 0

BASE_BUFFER = 3
PRIORITY_BUFFER_EXTRA = 2
MAX_DELAY = 30

df = df.sort_values("scheduled_departure").reset_index(drop=True)

# Conflict resolution
for i in range(1, len(df)):
    prev_time = df.loc[i-1, "optimized_departure"]
    curr_time = df.loc[i, "optimized_departure"]
    priority_gap = max(0, df.loc[i-1, "priority"] - df.loc[i, "priority"])
    dynamic_buffer = BASE_BUFFER + PRIORITY_BUFFER_EXTRA * priority_gap

    if curr_time <= prev_time + pd.Timedelta(minutes=dynamic_buffer):
        if df.loc[i, "priority"] < df.loc[i-1, "priority"]:
            new_time = prev_time + pd.Timedelta(minutes=dynamic_buffer)
            delay = (new_time - df.loc[i, "scheduled_departure"]).total_seconds() / 60
            if delay <= MAX_DELAY:
                df.loc[i, "optimized_departure"] = new_time
                df.loc[i, "delay_min"] = max(0, int(round(delay)))
            else:
                shift_prev = curr_time - pd.Timedelta(minutes=dynamic_buffer)
                df.loc[i-1, "optimized_departure"] = shift_prev
        else:
            for j in range(i-1, -1, -1):
                if df.loc[j, "priority"] < df.loc[i, "priority"]:
                    new_prev = curr_time - pd.Timedelta(minutes=dynamic_buffer)
                    df.loc[j, "optimized_departure"] = new_prev
                    delay = (new_prev - df.loc[j, "scheduled_departure"]).total_seconds() / 60
                    df.loc[j, "delay_min"] = max(0, int(round(delay)))
                    break
            else:
                new_time = prev_time + pd.Timedelta(minutes=dynamic_buffer)
                delay = (new_time - df.loc[i, "scheduled_departure"]).total_seconds() / 60
                df.loc[i, "optimized_departure"] = new_time
                df.loc[i, "delay_min"] = max(0, int(round(delay)))

df["scheduled_departure"] = df["scheduled_departure"].dt.strftime("%H:%M")
df["optimized_departure"] = df["optimized_departure"].dt.strftime("%H:%M")

with open(output_json, "w") as f:
    json.dump({"schedule": df.to_dict(orient="records")}, f, indent=4)

df.to_csv(output_csv, index=False)

print(f"[OK] Optimized schedule saved at: {output_json}")
print(f"[OK] CSV export saved at: {output_csv}")
print("[DEBUG] Optimizer finished successfully")
