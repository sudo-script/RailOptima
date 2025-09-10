# optimizer/visualize_schedule.py
import pandas as pd
import matplotlib.pyplot as plt
import os
import json

# Load the optimized schedule
with open("optimizer/schedule_output.json", "r") as f:
    data = json.load(f)

df = pd.DataFrame(data["schedule"])

# Convert times
df["scheduled_departure"] = pd.to_datetime(df["scheduled_departure"])
df["optimized_departure"] = pd.to_datetime(df["optimized_departure"])

# Ensure reports folder exists
os.makedirs("optimizer/reports", exist_ok=True)

# --- Timeline Plot (Scheduled vs Optimized) ---
plt.figure(figsize=(10, 6))
plt.plot(df["train_id"], df["scheduled_departure"], "o-", label="Scheduled")
plt.plot(df["train_id"], df["optimized_departure"], "s-", label="Optimized", color="orange")
plt.xlabel("Train ID")
plt.ylabel("Departure Time")
plt.title("Scheduled vs Optimized Departure Times")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("optimizer/reports/timeline.png")
plt.close()

# --- Delay Bar Chart ---
if "delay_min" in df.columns:
    plt.figure(figsize=(10, 6))
    plt.bar(df["train_id"], df["delay_min"], color="red")
    plt.xlabel("Train ID")
    plt.ylabel("Delay (minutes)")
    plt.title("Delays per Train")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("optimizer/reports/delays.png")
    plt.close()

print("Visualizations saved in 'optimizer/reports/' folder.")
