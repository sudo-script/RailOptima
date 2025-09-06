import pandas as pd

# Load the optimized schedule
df = pd.read_csv("schedule_output.csv")

print("\n=== Validation Report ===")

# Check for duplicate departure times
duplicates = df[df.duplicated("optimized_departure", keep=False)]

if duplicates.empty:
    print("✅ No conflicts: all trains have unique departure times.")
else:
    print("⚠️ Conflict detected! Trains with same optimized departure:")
    print(duplicates)
