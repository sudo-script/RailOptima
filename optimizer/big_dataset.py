import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json

# ======================
# Config
# ======================
num_trains = 100
start_time = datetime.strptime("06:00", "%H:%M")
output_folder = r"Audit/TestData"
os.makedirs(output_folder, exist_ok=True)

optimizer_input_file = os.path.join(output_folder, "optimizer_input_schedule.csv")
optimizer_json_file = os.path.join(output_folder, "optimizer_input_schedule.json")

# ======================
# Generate Train IDs
# ======================
train_ids = [f"T{str(i+1).zfill(3)}" for i in range(num_trains)]

# ======================
# Generate Scheduled Departures
# ======================
scheduled_times = [start_time]
for i in range(1, num_trains):
    gap = np.random.randint(5, 16)  # 5-15 minutes gap
    scheduled_times.append(scheduled_times[-1] + timedelta(minutes=gap))

scheduled_departure = [t.strftime("%H:%M") for t in scheduled_times]

# ======================
# Assign priorities randomly
# ======================
priorities = np.random.choice([1, 2, 3], size=num_trains, p=[0.2, 0.5, 0.3])

# ======================
# Create DataFrame
# ======================
optimizer_input_df = pd.DataFrame({
    "train_id": train_ids,
    "scheduled_departure": scheduled_departure,
    "priority": priorities
})

# ======================
# Save CSV
# ======================
optimizer_input_df.to_csv(optimizer_input_file, index=False)
print(f"[OK] Optimizer input schedule saved at: {optimizer_input_file}")

# ======================
# Convert to JSON
# ======================
optimizer_input_df.to_json(optimizer_json_file, orient="records", indent=4)
print(f"[OK] Optimizer input schedule saved as JSON at: {optimizer_json_file}")
