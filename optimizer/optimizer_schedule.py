import pandas as pd
import sys
import json
from datetime import datetime, timedelta

# ============================
# Load dataset
# ============================
if len(sys.argv) > 1:
    dataset = sys.argv[1]
else:
    dataset = "trains.csv"  # default file

df = pd.read_csv(dataset)

# ============================
# Convert times to datetime
# ============================
df["arrival"] = pd.to_datetime(df["arrival"], format="%H:%M")
df["departure"] = pd.to_datetime(df["departure"], format="%H:%M")

# Sort by departure, then by priority
df = df.sort_values(by=["departure", "priority"], ascending=[True, True])

# ============================
# Optimize Schedule (simple delay handling)
# ============================
optimized_times = []
last_time = None

for _, row in df.iterrows():
    sched_time = row["departure"]

    if last_time and sched_time <= last_time:
        # Push forward by 5 min if conflict
        sched_time = last_time + timedelta(minutes=5)

    optimized_times.append(sched_time)
    last_time = sched_time

df["optimized_departure"] = optimized_times

# ============================
# Calculate delays
# ============================
df["delay_min"] = (
    (df["optimized_departure"] - df["departure"]).dt.total_seconds() // 60
).astype(int)

# ============================
# Save outputs
# ============================
df_out = df[["train_id", "arrival", "departure", "optimized_departure", "delay_min", "priority"]]

# Save CSV
df_out.to_csv("schedule_output.csv", index=False)

# Save JSON (records style)
df_out.to_json("schedule_output.json", orient="records", indent=4)

# Save API-style JSON
with open("schedule_api.json", "w") as f:
    json.dump({"trains": df_out.to_dict(orient="records")}, f, indent=4, default=str)

# ============================
# Print Summary
# ============================
print("\n=== Optimized Schedule ===")
for _, row in df_out.iterrows():
    print(
        f"{row['train_id']}: Arr {row['arrival'].strftime('%H:%M')}, "
        f"Sched Dep {row['departure'].strftime('%H:%M')} → "
        f"Opt Dep {row['optimized_departure'].strftime('%H:%M')}, "
        f"Delay {row['delay_min']} min, Priority {row['priority']}"
    )

print("\n✅ Optimized schedule saved to schedule_output.csv, schedule_output.json, and schedule_api.json")
