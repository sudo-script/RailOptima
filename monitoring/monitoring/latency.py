import os
import time
import datetime
from typing import Optional

import requests
from requests import exceptions as req_exc


def log_api_latency(url: str, log_file: str = "reports/api_latency_log.txt", timeout: int = 10) -> Optional[float]:
    """
    Measure API latency for a given endpoint and log it.

    Args:
        url (str): The API endpoint to test (e.g., http://localhost:8000/trains).
        log_file (str): Path to log file (default: reports/api_latency_log.txt).
        timeout (int): Max time (seconds) before request fails.

    Returns:
        Optional[float]: Latency in milliseconds if successful, else None.
    """
    directory = os.path.dirname(log_file)
    if directory:
        os.makedirs(directory, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        start = time.time()
        response = requests.get(url, timeout=timeout)
        latency_ms = round((time.time() - start) * 1000, 2)  # ms
        status = response.status_code

        log_line = f"[{timestamp}] {url} responded in {latency_ms} ms (status={status})"
        result: Optional[float] = latency_ms

    except (req_exc.Timeout, req_exc.ConnectionError) as e:
        result = None
        log_line = f"[{timestamp}] ERROR contacting {url}: {type(e).__name__}: {e}"
    except Exception as e:  # fallback safeguard
        result = None
        log_line = f"[{timestamp}] UNEXPECTED ERROR contacting {url}: {e}"

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
    except Exception:
        # Last-resort: still print to console if file logging fails
        pass

    print(log_line)
    return result


# --- Example usage ---
if __name__ == "__main__":
    print(">>> Running log_api_latency.py ...")

    # Example endpoints (from Member 4's api_stub.py)
    endpoints = [
        "http://localhost:8000/trains",
        "http://localhost:8000/infrastructure",
        "http://localhost:8000/disruptions",
        "http://localhost:8000/recommendations"
    ]

    for url in endpoints:
        log_api_latency(url)
