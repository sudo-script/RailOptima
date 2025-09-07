import pandas as pd
import matplotlib.pyplot as plt
import os

# Ensure reports folder exists
os.makedirs("reports", exist_ok=True)

# Load optimized schedule
df = pd.read_csv("schedule_output.csv")

# Convert times to datetime
df["scheduled_departure"] = pd.to_datetime(df["scheduled_departure"], format="%H:%M")
df["optimized_departure"] = pd.to_datetime(df["optimized_departure"], format="%H:%M")

# Compute delay in minutes if not present
if "delay_min" not in df.columns:
    df["delay_min"] = (df["optimized_departure"] - df["scheduled_departure"]).dt.total_seconds() / 60
    df["delay_min"] = df["delay_min"].astype(int)

# === 1. Scheduled vs Optimized ===
plt.figure(figsize=(10, 6))
plt.plot(df["train_id"], df["scheduled_departure"].dt.strftime("%H:%M"),
         marker="o", label="Scheduled", color="blue")
plt.plot(df["train_id"], df["optimized_departure"].dt.strftime("%H:%M"),
         marker="x", label="Optimized", color="green")
plt.xlabel("Train ID")
plt.ylabel("Departure Time (HH:MM)")
plt.title("Scheduled vs Optimized Departures")
plt.legend()
plt.savefig("reports/scheduled_vs_optimized.png")
plt.close()

# === 2. Delay per Train ===
plt.figure(figsize=(8, 5))
plt.bar(df["train_id"], df["delay_min"], color="orange")
plt.xlabel("Train ID")
plt.ylabel("Delay (minutes)")
plt.title("Delay per Train")
plt.savefig("reports/delay_per_train.png")
plt.close()

# === 3. Priority vs Delay ===
plt.figure(figsize=(8, 5))
plt.scatter(df["priority"], df["delay_min"], color="red")
plt.xlabel("Priority")
plt.ylabel("Delay (minutes)")
plt.title("Impact of Priority on Delay")
plt.savefig("reports/priority_vs_delay.png")
plt.close()

print("✅ Reports saved in 'reports/' folder.")
