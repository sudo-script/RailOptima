import pandas as pd

# Load dataset
df = pd.read_csv("trains.csv")

print("=== Raw Train Schedule Dataset ===")
print(df)

# Convert HH:MM to minutes for optimization
def time_to_minutes(t):
    h, m = map(int, t.split(":"))
    return h * 60 + m

df["arrival_min"] = df["arrival"].apply(time_to_minutes)
df["departure_min"] = df["departure"].apply(time_to_minutes)

print("\n=== Converted Schedule (Minutes) ===")
print(df)
