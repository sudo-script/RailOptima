import pandas as pd
import json
import os

print("[DEBUG] Script started")

# --- Paths ---
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_file = os.path.join(base_dir, "optimizer", "schedule.json")   # ✅ Fixed path
output_json = os.path.join(base_dir, "optimizer", "schedule_output.json")
output_csv = os.path.join(base_dir, "optimizer", "schedule_output.csv")

print("[DEBUG] Paths set")

# --- Load JSON input ---
with open(input_file, "r") as f:
    data = json.load(f)

print("[DEBUG] JSON loaded successfully")

# --- Ensure schedule key exists ---
if isinstance(data, dict) and "schedule" in data:
    schedule = data["schedule"]
elif isinstance(data, list):  # if JSON is a list of train dicts
    schedule = data
else:
    raise KeyError("The JSON must contain either a list of trains or a 'schedule' key.")

# --- Create DataFrame ---
df = pd.DataFrame(schedule)
print(f"[DEBUG] DataFrame created with columns: {df.columns.tolist()}")

# --- Standardize column names ---
df = df.rename(columns={
    "delay_minutes": "delay_min"
})

# --- Convert times ---
for col in ["scheduled_departure", "optimized_departure"]:
    if col in df.columns:
        df[col] = pd.to_datetime("1900-01-01 " + df[col].astype(str), errors="coerce")

print("[DEBUG] Time conversion complete")

# --- Conflict Resolution (simple placeholder) ---
conflict_count = 0
for i in range(1, len(df)):
    if df.loc[i, "optimized_departure"] <= df.loc[i-1, "optimized_departure"]:
        df.loc[i, "optimized_departure"] = df.loc[i-1, "optimized_departure"] + pd.Timedelta(minutes=5)
        df.loc[i, "delay_min"] = (df.loc[i, "optimized_departure"] - df.loc[i, "scheduled_departure"]).seconds // 60
        conflict_count += 1
        print(f"[DEBUG] Conflict resolved for {df.loc[i, 'train_id']}")

print(f"[DEBUG] Conflict resolution complete. Resolved {conflict_count} conflicts.")

# --- Save outputs ---

# Convert datetime columns back to strings for JSON serialization
for col in ["scheduled_departure", "optimized_departure"]:
    if col in df.columns:
        df[col] = df[col].dt.strftime("%H:%M")

with open(output_json, "w") as f:
    json.dump(df.to_dict(orient="records"), f, indent=4)
print(f"[OK] Optimized schedule saved at: {output_json}")

df.to_csv(output_csv, index=False)
print(f"[OK] CSV export saved at: {output_csv}")

print("[DEBUG] Script finished successfully")

