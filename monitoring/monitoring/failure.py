import os
import datetime
from typing import Optional

import requests
from requests import exceptions as req_exc


def log_failure(message: str, log_file: str = "reports/failures_log.txt") -> None:
    """
    Append a failure message with timestamp to the log file.

    Args:
        message (str): Description of the failure.
        log_file (str): Path to the log file (default: reports/failures_log.txt).
    """
    directory = os.path.dirname(log_file)
    if directory:
        os.makedirs(directory, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] FAILURE: {message}"

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
    except Exception:
        pass

    print(log_line)


def check_api(url: str, log_file: str = "reports/failures_log.txt", timeout: int = 10) -> Optional[int]:
    """
    Check if an API endpoint is working. Log failures if request fails or returns error code.

    Args:
        url (str): API endpoint (e.g., http://localhost:8000/recommendations).
        log_file (str): Log file path.
        timeout (int): Timeout in seconds.

    Returns:
        Optional[int]: HTTP status code if reachable, else None.
    """
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code != 200:
            log_failure(f"{url} returned status {response.status_code}", log_file)
        return response.status_code
    except (req_exc.Timeout, req_exc.ConnectionError) as e:
        log_failure(f"Error contacting {url}: {type(e).__name__}: {e}", log_file)
        return None
    except Exception as e:
        log_failure(f"Unexpected error contacting {url}: {e}", log_file)
        return None


# --- Example usage ---
if __name__ == "__main__":
    print(">>> Running log_failures.py ...")

    # Example endpoints (from api_stub.py)
    endpoints = [
        "http://localhost:8000/trains",
        "http://localhost:8000/infrastructure",
        "http://localhost:8000/disruptions",
        "http://localhost:8000/recommendations",
        "http://localhost:8000/fake_endpoint"  # <- This will trigger failure
    ]

    for url in endpoints:
        check_api(url)
