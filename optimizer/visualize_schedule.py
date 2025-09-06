import pandas as pd
import matplotlib.pyplot as plt

# Load optimized schedule
df = pd.read_csv("schedule_output.csv")

# Convert times explicitly (avoids warnings)
df["optimized_departure"] = pd.to_datetime(df["optimized_departure"], format="%H:%M")
df["scheduled_departure"] = pd.to_datetime(df["scheduled_departure"], format="%H:%M")

# Plot Scheduled vs Optimized
plt.figure(figsize=(10, 6))

# Plot scheduled times (blue)
plt.scatter(df["scheduled_departure"], df["train_id"], color="blue", label="Scheduled")

# Plot optimized times (green)
plt.scatter(df["optimized_departure"], df["train_id"], color="green", label="Optimized")

# Draw delay lines (red dashed)
for _, row in df.iterrows():
    if row["delay_minutes"] > 0:
        plt.plot(
            [row["scheduled_departure"], row["optimized_departure"]],
            [row["train_id"], row["train_id"]],
            color="red",
            linestyle="--",
            label="Delay" if "Delay" not in plt.gca().get_legend_handles_labels()[1] else ""
        )
        # Add delay label
        plt.text(
            row["optimized_departure"],
            row["train_id"],
            f"+{row['delay_minutes']} min",
            color="red",
            fontsize=9,
            va="bottom",
            ha="left"
        )

# Labels & formatting
plt.title("Train Schedule Optimization (Scheduled vs Optimized)")
plt.xlabel("Time")
plt.ylabel("Trains")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()

# Save and show
plt.savefig("schedule_plot.png")
plt.show()
