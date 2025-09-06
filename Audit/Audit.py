import pandas as pd

# === Load Optimizer Output (schedule.csv) ===
df = pd.read_csv("C:/Users/Lenovo/OneDrive/Documents/RailOptima/Audit/output1.csv")

# === Rule Check Functions ===
def check_priority(row):
    """Express (priority 1) should not have more delay than lower priority trains."""
    if row["priority"] == 1 and row["delay_minutes"] > 0:
        return "❌ Fail"
    return "✅ Pass"

def check_headway(df):
    """Ensure at least 5 minutes gap between consecutive departures."""
    results = []
    dep_times = sorted(zip(df["train_id"], df["optimized_departure"]))
    
    # Convert HH:MM → minutes
    def time_to_minutes(t):
        h, m = map(int, t.split(":"))
        return h * 60 + m

    dep_times = [(tid, time_to_minutes(dep)) for tid, dep in dep_times]
    
    for i in range(len(dep_times)):
        if i == 0:
            results.append("✅ Pass")
        else:
            gap = dep_times[i][1] - dep_times[i-1][1]
            if gap < 5:
                results.append("⚠️ Needs Check")
            else:
                results.append("✅ Pass")
    return results

# === Apply Checks ===
df["Priority Rule"] = df.apply(check_priority, axis=1)

# Headway Rule (train order matters)
df = df.sort_values("optimized_departure").reset_index(drop=True)
df["Headway Rule"] = check_headway(df)

# === Add Notes Column ===
df["Notes"] = ""

# === Save Audit File ===
df.to_excel("audit_report.xlsx", index=False)
df.to_csv("audit_report.csv", index=False)

print("✅ Audit file generated: audit_report.xlsx & audit_report.csv")
