"""
Enhanced Failure Monitoring Module for RailOptima
Provides comprehensive failure detection, logging, and alerting capabilities.
"""

import os
import json
import logging
import datetime
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from requests import exceptions as req_exc
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FailureSeverity(Enum):
    """Failure severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class FailureType(Enum):
    """Types of failures that can occur"""
    API_ERROR = "api_error"
    CONNECTION_ERROR = "connection_error"
    TIMEOUT_ERROR = "timeout_error"
    VALIDATION_ERROR = "validation_error"
    SYSTEM_ERROR = "system_error"
    DATA_ERROR = "data_error"

@dataclass
class FailureEvent:
    """Structured failure event data"""
    timestamp: str
    failure_type: str
    severity: str
    message: str
    url: Optional[str] = None
    status_code: Optional[int] = None
    error_details: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    resolved: bool = False

class FailureMonitor:
    """Enhanced failure monitoring with metrics and alerting"""
    
    def __init__(self, log_file: str = "reports/failures_log.txt", 
                 metrics_file: str = "reports/failure_metrics.json"):
        self.log_file = log_file
        self.metrics_file = metrics_file
        self.failure_history: List[FailureEvent] = []
        self.alert_callbacks: List[Callable[[FailureEvent], None]] = []
        self.metrics = {
            "total_failures": 0,
            "failures_by_type": {},
            "failures_by_severity": {},
            "failures_by_hour": {},
            "last_failure": None,
            "consecutive_failures": 0,
            "failure_rate": 0.0
        }
        self._lock = threading.Lock()
        
        # Ensure directories exist
        for file_path in [self.log_file, self.metrics_file]:
            directory = os.path.dirname(file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
    
    def log_failure(self, message: str, failure_type: FailureType = FailureType.SYSTEM_ERROR,
                   severity: FailureSeverity = FailureSeverity.MEDIUM, 
                   url: Optional[str] = None, status_code: Optional[int] = None,
                   error_details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a failure event with structured data and metrics tracking.

        Args:
            message (str): Description of the failure.
            failure_type (FailureType): Type of failure.
            severity (FailureSeverity): Severity level.
            url (str, optional): URL that failed.
            status_code (int, optional): HTTP status code.
            error_details (dict, optional): Additional error information.
        """
        with self._lock:
            timestamp = datetime.datetime.now().isoformat()
            
            # Create failure event
            failure_event = FailureEvent(
                timestamp=timestamp,
                failure_type=failure_type.value,
                severity=severity.value,
                message=message,
                url=url,
                status_code=status_code,
                error_details=error_details
            )
            
            # Add to history
            self.failure_history.append(failure_event)
            
            # Update metrics
            self._update_metrics(failure_event)
            
            # Log to file
            self._write_failure_log(failure_event)
            
            # Trigger alerts if needed
            self._check_alerts(failure_event)
            
            # Print to console
            log_line = f"[{timestamp}] FAILURE [{severity.value.upper()}] {failure_type.value}: {message}"
            if url:
                log_line += f" (URL: {url})"
            if status_code:
                log_line += f" (Status: {status_code})"
            
            print(log_line)
            logger.error(log_line)
    
    def _update_metrics(self, failure_event: FailureEvent) -> None:
        """Update failure metrics"""
        self.metrics["total_failures"] += 1
        self.metrics["last_failure"] = failure_event.timestamp
        
        # Count by type
        failure_type = failure_event.failure_type
        self.metrics["failures_by_type"][failure_type] = \
            self.metrics["failures_by_type"].get(failure_type, 0) + 1
        
        # Count by severity
        severity = failure_event.severity
        self.metrics["failures_by_severity"][severity] = \
            self.metrics["failures_by_severity"].get(severity, 0) + 1
        
        # Count by hour
        hour = datetime.datetime.fromisoformat(failure_event.timestamp).hour
        self.metrics["failures_by_hour"][str(hour)] = \
            self.metrics["failures_by_hour"].get(str(hour), 0) + 1
        
        # Check for consecutive failures
        if len(self.failure_history) >= 2:
            last_two = self.failure_history[-2:]
            if (last_two[0].url == last_two[1].url and 
                datetime.datetime.fromisoformat(last_two[1].timestamp) - 
                datetime.datetime.fromisoformat(last_two[0].timestamp) < 
                datetime.timedelta(minutes=5)):
                self.metrics["consecutive_failures"] += 1
            else:
                self.metrics["consecutive_failures"] = 1
        else:
            self.metrics["consecutive_failures"] = 1
        
        # Calculate failure rate (failures per hour)
        if len(self.failure_history) > 1:
            first_failure = datetime.datetime.fromisoformat(self.failure_history[0].timestamp)
            last_failure = datetime.datetime.fromisoformat(failure_event.timestamp)
            hours_elapsed = (last_failure - first_failure).total_seconds() / 3600
            if hours_elapsed > 0:
                self.metrics["failure_rate"] = len(self.failure_history) / hours_elapsed
        
        # Save metrics to file
        self._save_metrics()
    
    def _write_failure_log(self, failure_event: FailureEvent) -> None:
        """Write structured failure log to file"""
        try:
            log_entry = {
                "timestamp": failure_event.timestamp,
                "failure_type": failure_event.failure_type,
                "severity": failure_event.severity,
                "message": failure_event.message,
                "url": failure_event.url,
                "status_code": failure_event.status_code,
                "error_details": failure_event.error_details,
                "retry_count": failure_event.retry_count
            }
            
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to write failure log: {e}")
    
    def _save_metrics(self) -> None:
        """Save metrics to JSON file"""
        try:
            with open(self.metrics_file, "w", encoding="utf-8") as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def _check_alerts(self, failure_event: FailureEvent) -> None:
        """Check if alerts should be triggered"""
        # Alert on critical failures
        if failure_event.severity == FailureSeverity.CRITICAL.value:
            self._trigger_alert(failure_event, "Critical failure detected")
        
        # Alert on consecutive failures
        if self.metrics["consecutive_failures"] >= 3:
            self._trigger_alert(failure_event, f"Consecutive failures: {self.metrics['consecutive_failures']}")
        
        # Alert on high failure rate
        if self.metrics["failure_rate"] > 10:  # More than 10 failures per hour
            self._trigger_alert(failure_event, f"High failure rate: {self.metrics['failure_rate']:.2f}/hour")
    
    def _trigger_alert(self, failure_event: FailureEvent, alert_message: str) -> None:
        """Trigger alert callbacks"""
        for callback in self.alert_callbacks:
            try:
                callback(failure_event)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
    
    def add_alert_callback(self, callback: Callable[[FailureEvent], None]) -> None:
        """Add an alert callback function"""
        self.alert_callbacks.append(callback)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current failure metrics"""
        with self._lock:
            return self.metrics.copy()
    
    def get_recent_failures(self, hours: int = 24) -> List[FailureEvent]:
        """Get failures from the last N hours"""
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=hours)
        return [
            f for f in self.failure_history 
            if datetime.datetime.fromisoformat(f.timestamp) >= cutoff_time
        ]
    
    def resolve_failure(self, failure_id: str) -> bool:
        """Mark a failure as resolved"""
        # This would need failure IDs to be implemented
        # For now, just log the resolution
        logger.info(f"Failure {failure_id} marked as resolved")
        return True

# Global failure monitor instance
failure_monitor = FailureMonitor()

def log_failure(message: str, failure_type: FailureType = FailureType.SYSTEM_ERROR,
               severity: FailureSeverity = FailureSeverity.MEDIUM, 
               url: Optional[str] = None, status_code: Optional[int] = None,
               error_details: Optional[Dict[str, Any]] = None) -> None:
    """
    Convenience function to log failures using the global monitor.
    """
    failure_monitor.log_failure(message, failure_type, severity, url, status_code, error_details)

def check_api(url: str, timeout: int = 10, retries: int = 3) -> Optional[int]:
    """
    Enhanced API health check with retry logic and detailed failure tracking.

    Args:
        url (str): API endpoint to check.
        timeout (int): Timeout in seconds.
        retries (int): Number of retry attempts.

    Returns:
        Optional[int]: HTTP status code if successful, else None.
    """
    last_exception = None
    
    for attempt in range(retries + 1):
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout)
            response_time = time.time() - start_time
            
            if response.status_code != 200:
                failure_monitor.log_failure(
                    f"{url} returned status {response.status_code}",
                    FailureType.API_ERROR,
                    FailureSeverity.MEDIUM if response.status_code < 500 else FailureSeverity.HIGH,
                    url=url,
                    status_code=response.status_code,
                    error_details={"response_time": response_time, "attempt": attempt + 1}
                )
            
            return response.status_code
            
        except req_exc.Timeout as e:
            last_exception = e
            failure_monitor.log_failure(
                f"Timeout contacting {url}",
                FailureType.TIMEOUT_ERROR,
                FailureSeverity.HIGH,
                url=url,
                error_details={"timeout": timeout, "attempt": attempt + 1}
            )
            
        except req_exc.ConnectionError as e:
            last_exception = e
            failure_monitor.log_failure(
                f"Connection error contacting {url}",
                FailureType.CONNECTION_ERROR,
                FailureSeverity.HIGH,
                url=url,
                error_details={"attempt": attempt + 1}
            )
            
        except Exception as e:
            last_exception = e
            failure_monitor.log_failure(
                f"Unexpected error contacting {url}: {e}",
                FailureType.SYSTEM_ERROR,
                FailureSeverity.CRITICAL,
                url=url,
                error_details={"error_type": type(e).__name__, "attempt": attempt + 1}
            )
        
        # Wait before retry (exponential backoff)
        if attempt < retries:
            wait_time = min(2 ** attempt, 10)  # Max 10 seconds
            time.sleep(wait_time)
    
    # All retries failed
    failure_monitor.log_failure(
        f"All {retries + 1} attempts failed for {url}",
        FailureType.CONNECTION_ERROR,
        FailureSeverity.CRITICAL,
        url=url,
        error_details={"total_attempts": retries + 1, "last_error": str(last_exception)}
    )
    
    return None

def check_multiple_apis(urls: List[str], timeout: int = 10) -> Dict[str, Optional[int]]:
    """
    Check multiple API endpoints concurrently.
    
    Args:
        urls (List[str]): List of URLs to check.
        timeout (int): Timeout for each request.
    
    Returns:
        Dict[str, Optional[int]]: Mapping of URL to status code or None.
    """
    results = {}
    
    def check_single_api(url: str) -> None:
        results[url] = check_api(url, timeout)
    
    threads = []
    for url in urls:
        thread = threading.Thread(target=check_single_api, args=(url,))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    return results

def get_failure_summary() -> Dict[str, Any]:
    """Get a summary of recent failures"""
    metrics = failure_monitor.get_metrics()
    recent_failures = failure_monitor.get_recent_failures(24)
    
    return {
        "summary": metrics,
        "recent_failures_count": len(recent_failures),
        "critical_failures": len([f for f in recent_failures if f.severity == "critical"]),
        "high_failures": len([f for f in recent_failures if f.severity == "high"]),
        "most_common_type": max(metrics["failures_by_type"].items(), key=lambda x: x[1])[0] if metrics["failures_by_type"] else None,
        "most_common_severity": max(metrics["failures_by_severity"].items(), key=lambda x: x[1])[0] if metrics["failures_by_severity"] else None
    }

# Example alert callback
def email_alert_callback(failure_event: FailureEvent) -> None:
    """Example alert callback for email notifications"""
    print(f"🚨 ALERT: {failure_event.severity.upper()} failure detected!")
    print(f"   Type: {failure_event.failure_type}")
    print(f"   Message: {failure_event.message}")
    print(f"   Time: {failure_event.timestamp}")
    if failure_event.url:
        print(f"   URL: {failure_event.url}")

# Add example alert callback
failure_monitor.add_alert_callback(email_alert_callback)

# --- Example usage ---
if __name__ == "__main__":
    print(">>> Running enhanced failure monitoring...")
    
    # Example endpoints
    endpoints = [
        "http://localhost:8000/trains",
        "http://localhost:8000/stations",
        "http://localhost:8000/infrastructure",
        "http://localhost:8000/disruptions",
        "http://localhost:8000/optimize",
        "http://localhost:8000/health",
        "http://localhost:8000/fake_endpoint"  # This will trigger failure
    ]
    
    print("\n--- Checking individual endpoints ---")
    for url in endpoints:
        status = check_api(url)
        if status:
            print(f"✅ {url}: {status}")
        else:
            print(f"❌ {url}: Failed")
    
    print("\n--- Checking multiple endpoints concurrently ---")
    results = check_multiple_apis(endpoints)
    for url, status in results.items():
        if status:
            print(f"✅ {url}: {status}")
        else:
            print(f"❌ {url}: Failed")
    
    print("\n--- Failure Summary ---")
    summary = get_failure_summary()
    print(f"Total failures: {summary['summary']['total_failures']}")
    print(f"Recent failures (24h): {summary['recent_failures_count']}")
    print(f"Critical failures: {summary['critical_failures']}")
    print(f"High failures: {summary['high_failures']}")
    print(f"Most common type: {summary['most_common_type']}")
    print(f"Most common severity: {summary['most_common_severity']}")
    print(f"Failure rate: {summary['summary']['failure_rate']:.2f}/hour")
