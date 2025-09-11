import os
import time
import datetime
from typing import Any, Callable, TypeVar


T = TypeVar("T")


def log_runtime(func: Callable[..., T], *args: Any, log_file: str = "reports/runtime_log.txt", **kwargs: Any) -> T:
    """
    Measure execution time of a function and log it.

    Args:
        func (callable): The function to measure.
        *args: Positional arguments for the function.
        log_file (str): Path to the log file (default: reports/runtime_log.txt).
        **kwargs: Keyword arguments for the function.

    Returns:
        result: The return value of the function.
    """
    directory = os.path.dirname(log_file)
    if directory:
        os.makedirs(directory, exist_ok=True)

    start_time = time.time()
    try:
        result: T = func(*args, **kwargs)
        return result
    finally:
        end_time = time.time()
        runtime = round(end_time - start_time, 3)  # seconds
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] Function '{func.__name__}' executed in {runtime} sec\n")
        except Exception:
            pass
        print(f"[OK] {func.__name__} executed in {runtime} sec (logged in {log_file})")


# --- Example usage ---
if __name__ == "__main__":
    print(">>> Running log_runtime.py ...")

    # Dummy example function
    def dummy_optimizer(x: int, y: int) -> int:
        time.sleep(1.2)  # simulate heavy computation
        return x + y

    # Log its runtime
    result = log_runtime(dummy_optimizer, 5, 7)
    print("Result:", result)
