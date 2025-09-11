# optimizer/test_optimizer.py
import os
import json
import pandas as pd
import subprocess

print(">>> Running Optimizer Verification...")

# Step 1: Run optimizer_schedule.py
result = subprocess.run(
    ["python", "optimizer/optimizer_schedule.py"],
    capture_output=True, text=True
)
print(result.stdout)
if result.returncode != 0:
    print("[FAIL] optimizer_schedule.py did not run successfully")
    exit(1)

# Step 2: Check output files
json_file = "optimizer/schedule_output.json"
csv_file = "optimizer/schedule_output.csv"

if not os.path.exists(json_file):
    print("[FAIL] schedule_output.json not found!")
    exit(1)

if not os.path.exists(csv_file):
    print("[FAIL] schedule_output.csv not found!")
    exit(1)

print("[OK] Output files generated")

# Step 3: Validate JSON
with open(json_file, "r") as f:
    data = json.load(f)

if isinstance(data, list) and len(data) > 0:
    print("[OK] JSON contains schedule data")
else:
    print("[FAIL] JSON file is empty or invalid")

# Step 4: Validate CSV
df = pd.read_csv(csv_file)
if "train_id" in df.columns and not df.empty:
    print("[OK] CSV contains train schedule data")
else:
    print("[FAIL] CSV file invalid or missing columns")

print(">>> Optimizer verification complete ✅")
