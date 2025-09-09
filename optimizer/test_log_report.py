# optimizer/test_log_report.py
import os

print(">>> Running Log Report Verification...")

exit_code = os.system("python optimizer/log_report.py")

if exit_code != 0:
    print("[FAIL] log_report.py did not run successfully")
else:
    if os.path.exists("reports/run_log.txt"):
        print("[OK] run_log.txt found ✅")
        with open("reports/run_log.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            print(f"[INFO] Last log entry:\n{lines[-1] if lines else 'Empty log file'}")
    else:
        print("[FAIL] run_log.txt not found ❌")
