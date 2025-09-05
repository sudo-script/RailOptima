import pandas as pd
from ortools.sat.python import cp_model
import json

# Load dataset (file is in the same folder as this script)
df = pd.read_csv("trains.csv")

# Convert arrival/departure times into minutes
def time_to_minutes(t):
    h, m = map(int, t.split(":"))
    return h * 60 + m

df["arrival_min"] = df["arrival"].apply(time_to_minutes)
df["departure_min"] = df["departure"].apply(time_to_minutes)

# OR-Tools model
model = cp_model.CpModel()

# Create decision variables for train departure times
departure_vars = {}
for idx, row in df.iterrows():
    departure_vars[row["train_id"]] = model.NewIntVar(
        row["arrival_min"], 1440, f"dep_{row['train_id']}"
    )

# Constraints: train cannot depart before its arrival
for idx, row in df.iterrows():
    model.Add(departure_vars[row["train_id"]] >= row["arrival_min"])

# Objective: minimize weighted delays (priority-aware)
objective_terms = []
for idx, row in df.iterrows():
    delay = departure_vars[row["train_id"]] - row["departure_min"]
    weight = 4 - row["priority"]  # higher priority = higher weight
    objective_terms.append(weight * delay)

model.Minimize(sum(objective_terms))

# Solve
solver = cp_model.CpSolver()
status = solver.Solve(model)

print("\n=== Optimized Schedule ===")
results = []
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    for idx, row in df.iterrows():
        train_id = row["train_id"]
        dep_time = solver.Value(departure_vars[train_id])
        h, m = divmod(dep_time, 60)
        dep_str = f"{h:02d}:{m:02d}"

        delay = dep_time - row["departure_min"]

        print(f"{train_id} | Scheduled: {row['departure']} | Optimized: {dep_str} | Delay: {delay} min | Priority: {row['priority']}")

        results.append({
            "train_id": train_id,
            "scheduled_departure": row["departure"],
            "optimized_departure": dep_str,
            "delay_minutes": int(delay),
            "priority": int(row["priority"])
        })
else:
    print("No solution found.")

# Save to JSON
with open("schedule.json", "w") as f:
    json.dump(results, f, indent=4)

# Save also to CSV
pd.DataFrame(results).to_csv("schedule_output.csv", index=False)

print("\n✅ Optimized schedule saved to schedule.json and schedule_output.csv")

