# optimizer/log_report.py
import os
import datetime

def write_log(message, log_file="reports/run_log.txt"):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

if __name__ == "__main__":
    print(">>> Running log_report.py ...")
    write_log("Log report script executed successfully ✅")
    print("[OK] Log written to reports/run_log.txt")
