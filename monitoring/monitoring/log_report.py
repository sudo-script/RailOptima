import os
import datetime
from typing import List


def write_log(message: str, log_file: str = "reports/run_log.txt") -> None:
    """
    Append a log entry with timestamp to the specified log file.

    Args:
        message (str): The message to log.
        log_file (str): Path to the log file. Default = 'reports/run_log.txt'.
    """
    # Ensure log directory exists
    directory = os.path.dirname(log_file)
    if directory:
        os.makedirs(directory, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"[ERROR] Could not write to log file {log_file}: {e}")


def read_logs(log_file: str = "reports/run_log.txt") -> List[str]:
    """
    Read and return all log entries from the log file.

    Args:
        log_file (str): Path to the log file.

    Returns:
        list[str]: List of log lines (or empty if no file found).
    """
    if not os.path.exists(log_file):
        return []
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            return f.readlines()
    except Exception:
        return []


if __name__ == "__main__":
    print(">>> Running log_report.py ...")
    write_log("Log report script executed successfully ✅")
    print("[OK] Log written to reports/run_log.txt")

    # Optional: show last 3 logs for quick check
    logs = read_logs()
    if logs:
        print("Recent logs:")
        for line in logs[-3:]:
            print("   ", line.strip())
