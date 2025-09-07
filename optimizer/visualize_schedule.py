import pandas as pd
import matplotlib.pyplot as plt
import os

# Load the optimized schedule
df = pd.read_csv("schedule_output.csv")

# Convert times
df["departure"] = pd.to_datetime(df["departure"])
df["optimized_departure"] = pd.to_datetime(df["optimized_departure"])

# Ensure reports folder exists
os.makedirs("reports", exist_ok=True)

# --- Timeline Plot (Scheduled vs Optimized) ---
plt.figure(figsize=(10, 6))
plt.plot(df["train_id"], df["departure"], "o-", label="Scheduled")
plt.plot(df["train_id"], df["optimized_departure"], "s-", label="Optimized", color="orange")
plt.xlabel("Train ID")
plt.ylabel("Departure Time")
plt.title("Scheduled vs Optimized Departure Times")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("reports/timeline.png")
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
    plt.savefig("reports/delays.png")
    plt.close()

print("✅ Visualizations saved in 'reports/' folder.")
