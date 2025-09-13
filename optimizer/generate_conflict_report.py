import pandas as pd
import random
from datetime import datetime, timedelta

def to_time_str(minutes):
    return f"{minutes//60:02d}:{minutes%60:02d}"

def to_minutes(t):
    h, m = map(int, t.split(":"))
    return h * 60 + m

def generate_conflict_dataset(input_file, output_file):
    df = pd.read_csv(input_file)

    # Convert to minutes for manipulation
    df["scheduled_minutes"] = df["scheduled_departure"].apply(to_minutes)

    optimized_times = []
    for t in df["scheduled_minutes"]:
        # introduce random delays (0 to 10 mins) to simulate optimizer
        delay = random.choice([0, 2, 3, 5, 7, 10])  
        optimized_times.append(t + delay)

    df["optimized_minutes"] = optimized_times
    df["optimized_departure"] = df["optimized_minutes"].apply(to_time_str)

    # Delay column
    df["delay_minutes"] = df["optimized_minutes"] - df["scheduled_minutes"]

    # Conflict detection (if optimized departure within 5 min of another train)
    conflicts = []
    for i in range(len(df)):
        for j in range(i+1, len(df)):
            if abs(df.loc[i, "optimized_minutes"] - df.loc[j, "optimized_minutes"]) < 5:
                conflicts.append((df.loc[i, "train_id"], df.loc[j, "train_id"]))

    print("Summary:")
    print(" Total trains:", len(df))
    print(" Avg delay:", df["delay_minutes"].mean())
    print(" Conflicts found:", len(conflicts))
    print(" Trains delayed >5min:", (df["delay_minutes"] >= 5).sum())

    # Save enriched dataset
    df.to_csv(output_file, index=False)

if __name__ == "__main__":
    generate_conflict_dataset("optimizer/optimizer_input_schedule.csv", "optimizer/conflict_report.csv")
