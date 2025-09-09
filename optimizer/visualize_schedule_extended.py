# optimizer/visualize_schedule_extended.py
import pandas as pd
import matplotlib.pyplot as plt
import os

# Paths
input_path = os.path.join("optimizer", "schedule_output.csv")
reports_dir = os.path.join("optimizer", "reports")
os.makedirs(reports_dir, exist_ok=True)

# Load optimized schedule
try:
    df = pd.read_csv(input_path)
except FileNotFoundError:
    print(f"[ERROR] Could not find {input_path}. Please run optimizer_schedule.py first.")
    exit(1)

# Normalize column names
df.columns = [c.strip().lower() for c in df.columns]

# Convert times
for col in ["arrival", "scheduled_departure", "optimized_departure"]:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

# --- Gantt-style Timeline ---
plt.figure(figsize=(12, 6))
for i, row in df.iterrows():
    plt.plot(
        [row["arrival"], row["optimized_departure"]],
        [row["train_id"], row["train_id"]],
        marker="o",
        linewidth=2,
        label=row["train_id"] if i == 0 else ""
    )

plt.xlabel("Time")
plt.ylabel("Train ID")
plt.title("Train Schedule Timeline (Arrival → Optimized Departure)")
plt.xticks(rotation=45)
plt.legend(loc="upper left")
plt.tight_layout()
plt.savefig(os.path.join(reports_dir, "gantt_timeline.png"))
plt.close()

# --- Delay Summary Bar Chart ---
if "delay_min" in df.columns:
    plt.figure(figsize=(10, 6))
    plt.bar(df["train_id"], df["delay_min"], color="tomato")
    plt.xlabel("Train ID")
    plt.ylabel("Delay (minutes)")
    plt.title("Delays per Train (Optimized vs Scheduled)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, "delay_summary.png"))
    plt.close()

# --- Summary Report ---
summary_path = os.path.join(reports_dir, "visualization_summary.txt")
with open(summary_path, "w", encoding="utf-8") as f:
    if "delay_min" in df.columns:
        avg_delay = df["delay_min"].mean()
        max_delay = df["delay_min"].max()
        delayed_trains = (df["delay_min"] > 0).sum()

        f.write("Visualization Summary Report\n")
        f.write("=" * 40 + "\n")
        f.write(f"Total trains: {len(df)}\n")
        f.write(f"Delayed trains: {delayed_trains}\n")
        f.write(f"Average delay: {avg_delay:.2f} minutes\n")
        f.write(f"Maximum delay: {max_delay} minutes\n")
    else:
        f.write("No delay data available in schedule.\n")

print("[OK] Visualizations saved in 'optimizer/reports/' folder.")
print(f"[OK] Summary report saved at: {summary_path}")
