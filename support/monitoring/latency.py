"""
Enhanced Latency Monitoring Module for RailOptima
Provides comprehensive API latency measurement, performance metrics, and statistical analysis.
"""

import os
import json
import time
import datetime
import statistics
import threading
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from requests import exceptions as req_exc
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LatencyThreshold(Enum):
    """Latency threshold levels"""
    EXCELLENT = 100  # < 100ms
    GOOD = 300      # < 300ms
    ACCEPTABLE = 1000  # < 1s
    SLOW = 3000     # < 3s
    CRITICAL = 10000  # > 10s

@dataclass
class LatencyMeasurement:
    """Structured latency measurement data"""
    timestamp: str
    url: str
    latency_ms: float
    status_code: int
    response_size: Optional[int] = None
    error_message: Optional[str] = None
    retry_count: int = 0

@dataclass
class LatencyStats:
    """Statistical analysis of latency measurements"""
    count: int
    min_ms: float
    max_ms: float
    mean_ms: float
    median_ms: float
    p95_ms: float
    p99_ms: float
    std_dev_ms: float
    success_rate: float
    error_count: int

class LatencyMonitor:
    """Enhanced latency monitoring with performance metrics and alerting"""
    
    def __init__(self, log_file: str = "reports/api_latency_log.txt",
                 metrics_file: str = "reports/latency_metrics.json"):
        self.log_file = log_file
        self.metrics_file = metrics_file
        self.measurements: List[LatencyMeasurement] = []
        self.alert_callbacks: List[Callable[[LatencyMeasurement], None]] = []
        self.thresholds = {
            "warning": 1000,  # 1 second
            "critical": 3000,  # 3 seconds
            "timeout": 10000   # 10 seconds
        }
        self._lock = threading.Lock()
        
        # Ensure directories exist
        for file_path in [self.log_file, self.metrics_file]:
            directory = os.path.dirname(file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
    
    def measure_latency(self, url: str, timeout: int = 10, retries: int = 1) -> Optional[LatencyMeasurement]:
        """
        Measure API latency with enhanced error handling and retry logic.

        Args:
            url (str): The API endpoint to test.
            timeout (int): Max time (seconds) before request fails.
            retries (int): Number of retry attempts.

        Returns:
            Optional[LatencyMeasurement]: Measurement data if successful, else None.
        """
        last_exception = None
        
        for attempt in range(retries + 1):
            try:
                start_time = time.time()
                response = requests.get(url, timeout=timeout)
                end_time = time.time()
                
                latency_ms = round((end_time - start_time) * 1000, 2)
                response_size = len(response.content) if response.content else 0
                
                measurement = LatencyMeasurement(
                    timestamp=datetime.datetime.now().isoformat(),
                    url=url,
                    latency_ms=latency_ms,
                    status_code=response.status_code,
                    response_size=response_size,
                    retry_count=attempt
                )
                
                # Store measurement
                with self._lock:
                    self.measurements.append(measurement)
                    self._log_measurement(measurement)
                    self._check_thresholds(measurement)
                
                return measurement
                
            except req_exc.Timeout as e:
                last_exception = e
                if attempt == retries:  # Last attempt
                    measurement = LatencyMeasurement(
                        timestamp=datetime.datetime.now().isoformat(),
                        url=url,
                        latency_ms=timeout * 1000,  # Record timeout as latency
                        status_code=0,
                        error_message=f"Timeout after {timeout}s",
                        retry_count=attempt
                    )
                    with self._lock:
                        self.measurements.append(measurement)
                        self._log_measurement(measurement)
                        self._check_thresholds(measurement)
                    return measurement
                    
            except req_exc.ConnectionError as e:
                last_exception = e
                if attempt == retries:  # Last attempt
                    measurement = LatencyMeasurement(
                        timestamp=datetime.datetime.now().isoformat(),
                        url=url,
                        latency_ms=0,
                        status_code=0,
                        error_message=f"Connection error: {e}",
                        retry_count=attempt
                    )
                    with self._lock:
                        self.measurements.append(measurement)
                        self._log_measurement(measurement)
                        self._check_thresholds(measurement)
                    return measurement
                    
            except Exception as e:
                last_exception = e
                if attempt == retries:  # Last attempt
                    measurement = LatencyMeasurement(
                        timestamp=datetime.datetime.now().isoformat(),
                        url=url,
                        latency_ms=0,
                        status_code=0,
                        error_message=f"Unexpected error: {e}",
                        retry_count=attempt
                    )
                    with self._lock:
                        self.measurements.append(measurement)
                        self._log_measurement(measurement)
                        self._check_thresholds(measurement)
                    return measurement
            
            # Wait before retry
            if attempt < retries:
                time.sleep(min(2 ** attempt, 5))  # Exponential backoff, max 5s
        
        return None
    
    def _log_measurement(self, measurement: LatencyMeasurement) -> None:
        """Log measurement to file"""
        try:
            log_entry = asdict(measurement)
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to log measurement: {e}")
    
    def _check_thresholds(self, measurement: LatencyMeasurement) -> None:
        """Check if measurement exceeds thresholds and trigger alerts"""
        if measurement.error_message:
            # Error occurred
            self._trigger_alert(measurement, "API Error")
        elif measurement.latency_ms > self.thresholds["critical"]:
            self._trigger_alert(measurement, "Critical Latency")
        elif measurement.latency_ms > self.thresholds["warning"]:
            self._trigger_alert(measurement, "High Latency")
    
    def _trigger_alert(self, measurement: LatencyMeasurement, alert_type: str) -> None:
        """Trigger alert callbacks"""
        for callback in self.alert_callbacks:
            try:
                callback(measurement)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
    
    def add_alert_callback(self, callback: Callable[[LatencyMeasurement], None]) -> None:
        """Add an alert callback function"""
        self.alert_callbacks.append(callback)
    
    def get_stats_for_url(self, url: str, hours: int = 24) -> Optional[LatencyStats]:
        """Get statistical analysis for a specific URL"""
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=hours)
        url_measurements = [
            m for m in self.measurements 
            if m.url == url and datetime.datetime.fromisoformat(m.timestamp) >= cutoff_time
        ]
        
        if not url_measurements:
            return None
        
        latencies = [m.latency_ms for m in url_measurements if m.error_message is None]
        errors = [m for m in url_measurements if m.error_message is not None]
        
        if not latencies:
            return LatencyStats(
                count=len(url_measurements),
                min_ms=0, max_ms=0, mean_ms=0, median_ms=0,
                p95_ms=0, p99_ms=0, std_dev_ms=0,
                success_rate=0.0,
                error_count=len(errors)
            )
        
        return LatencyStats(
            count=len(url_measurements),
            min_ms=min(latencies),
            max_ms=max(latencies),
            mean_ms=statistics.mean(latencies),
            median_ms=statistics.median(latencies),
            p95_ms=self._percentile(latencies, 95),
            p99_ms=self._percentile(latencies, 99),
            std_dev_ms=statistics.stdev(latencies) if len(latencies) > 1 else 0,
            success_rate=len(latencies) / len(url_measurements) * 100,
            error_count=len(errors)
        )
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def get_overall_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get overall statistics for all measurements"""
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=hours)
        recent_measurements = [
            m for m in self.measurements 
            if datetime.datetime.fromisoformat(m.timestamp) >= cutoff_time
        ]
        
        if not recent_measurements:
            return {"message": "No measurements available"}
        
        # Group by URL
        url_stats = {}
        for measurement in recent_measurements:
            url = measurement.url
            if url not in url_stats:
                url_stats[url] = []
            url_stats[url].append(measurement)
        
        # Calculate stats for each URL
        url_analyses = {}
        for url, measurements in url_stats.items():
            stats = self.get_stats_for_url(url, hours)
            if stats:
                url_analyses[url] = asdict(stats)
        
        # Overall metrics
        all_latencies = [m.latency_ms for m in recent_measurements if m.error_message is None]
        total_errors = len([m for m in recent_measurements if m.error_message is not None])
        
        overall_stats = {
            "total_measurements": len(recent_measurements),
            "total_errors": total_errors,
            "success_rate": (len(recent_measurements) - total_errors) / len(recent_measurements) * 100 if recent_measurements else 0,
            "url_count": len(url_stats)
        }
        
        if all_latencies:
            overall_stats.update({
                "overall_min_ms": min(all_latencies),
                "overall_max_ms": max(all_latencies),
                "overall_mean_ms": statistics.mean(all_latencies),
                "overall_median_ms": statistics.median(all_latencies),
                "overall_p95_ms": self._percentile(all_latencies, 95),
                "overall_p99_ms": self._percentile(all_latencies, 99)
            })
        
        return {
            "overall": overall_stats,
            "by_url": url_analyses,
            "thresholds": self.thresholds
        }
    
    def set_thresholds(self, warning: int = 1000, critical: int = 3000, timeout: int = 10000) -> None:
        """Set latency thresholds"""
        self.thresholds = {
            "warning": warning,
            "critical": critical,
            "timeout": timeout
        }
    
    def get_recent_measurements(self, hours: int = 24) -> List[LatencyMeasurement]:
        """Get measurements from the last N hours"""
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=hours)
        return [
            m for m in self.measurements 
            if datetime.datetime.fromisoformat(m.timestamp) >= cutoff_time
        ]
    
    def clear_old_measurements(self, days: int = 7) -> int:
        """Clear measurements older than N days"""
        cutoff_time = datetime.datetime.now() - datetime.timedelta(days=days)
        original_count = len(self.measurements)
        
        with self._lock:
            self.measurements = [
                m for m in self.measurements 
                if datetime.datetime.fromisoformat(m.timestamp) >= cutoff_time
            ]
        
        cleared_count = original_count - len(self.measurements)
        logger.info(f"Cleared {cleared_count} old measurements")
        return cleared_count

# Global latency monitor instance
latency_monitor = LatencyMonitor()

def log_api_latency(url: str, timeout: int = 10, retries: int = 1) -> Optional[float]:
    """
    Convenience function to measure latency using the global monitor.
    
    Returns:
        Optional[float]: Latency in milliseconds if successful, else None.
    """
    measurement = latency_monitor.measure_latency(url, timeout, retries)
    return measurement.latency_ms if measurement else None

def measure_multiple_apis(urls: List[str], timeout: int = 10) -> Dict[str, Optional[LatencyMeasurement]]:
    """
    Measure latency for multiple API endpoints concurrently.
    
    Args:
        urls (List[str]): List of URLs to measure.
        timeout (int): Timeout for each request.
    
    Returns:
        Dict[str, Optional[LatencyMeasurement]]: Mapping of URL to measurement.
    """
    results = {}
    
    def measure_single_api(url: str) -> None:
        results[url] = latency_monitor.measure_latency(url, timeout)
    
    threads = []
    for url in urls:
        thread = threading.Thread(target=measure_single_api, args=(url,))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    return results

def get_latency_summary() -> Dict[str, Any]:
    """Get a summary of recent latency measurements"""
    stats = latency_monitor.get_overall_stats(24)
    recent_measurements = latency_monitor.get_recent_measurements(24)
    
    # Calculate performance grade
    if stats.get("overall", {}).get("overall_mean_ms"):
        mean_latency = stats["overall"]["overall_mean_ms"]
        if mean_latency < LatencyThreshold.EXCELLENT.value:
            grade = "A+ (Excellent)"
        elif mean_latency < LatencyThreshold.GOOD.value:
            grade = "A (Good)"
        elif mean_latency < LatencyThreshold.ACCEPTABLE.value:
            grade = "B (Acceptable)"
        elif mean_latency < LatencyThreshold.SLOW.value:
            grade = "C (Slow)"
        else:
            grade = "D (Critical)"
    else:
        grade = "N/A"
    
    return {
        "performance_grade": grade,
        "stats": stats,
        "recent_measurements_count": len(recent_measurements),
        "thresholds": latency_monitor.thresholds
    }

# Example alert callback
def latency_alert_callback(measurement: LatencyMeasurement) -> None:
    """Example alert callback for latency notifications"""
    if measurement.error_message:
        print(f"🚨 LATENCY ALERT: API Error!")
        print(f"   URL: {measurement.url}")
        print(f"   Error: {measurement.error_message}")
        print(f"   Time: {measurement.timestamp}")
    else:
        print(f"⚠️ LATENCY ALERT: High Latency!")
        print(f"   URL: {measurement.url}")
        print(f"   Latency: {measurement.latency_ms} ms")
        print(f"   Status: {measurement.status_code}")
        print(f"   Time: {measurement.timestamp}")

# Add example alert callback
latency_monitor.add_alert_callback(latency_alert_callback)

# --- Example usage ---
if __name__ == "__main__":
    print(">>> Running enhanced latency monitoring...")
    
    # Example endpoints
    endpoints = [
        "http://localhost:8000/trains",
        "http://localhost:8000/stations",
        "http://localhost:8000/infrastructure",
        "http://localhost:8000/disruptions",
        "http://localhost:8000/optimize",
        "http://localhost:8000/health",
        "http://localhost:8000/metrics"
    ]
    
    print("\n--- Measuring individual endpoints ---")
    for url in endpoints:
        latency = log_api_latency(url)
        if latency is not None:
            print(f"✅ {url}: {latency} ms")
        else:
            print(f"❌ {url}: Failed")
    
    print("\n--- Measuring multiple endpoints concurrently ---")
    results = measure_multiple_apis(endpoints)
    for url, measurement in results.items():
        if measurement and measurement.error_message is None:
            print(f"✅ {url}: {measurement.latency_ms} ms (status: {measurement.status_code})")
        else:
            print(f"❌ {url}: Failed")
    
    print("\n--- Latency Summary ---")
    summary = get_latency_summary()
    print(f"Performance Grade: {summary['performance_grade']}")
    print(f"Total measurements: {summary['stats']['overall']['total_measurements']}")
    print(f"Success rate: {summary['stats']['overall']['success_rate']:.1f}%")
    print(f"Overall mean latency: {summary['stats']['overall'].get('overall_mean_ms', 'N/A')} ms")
    print(f"Overall P95 latency: {summary['stats']['overall'].get('overall_p95_ms', 'N/A')} ms")
    
    print("\n--- URL-specific Statistics ---")
    for url, stats in summary['stats']['by_url'].items():
        print(f"\n{url}:")
        print(f"  Mean: {stats['mean_ms']:.1f} ms")
        print(f"  P95: {stats['p95_ms']:.1f} ms")
        print(f"  Success rate: {stats['success_rate']:.1f}%")
        print(f"  Error count: {stats['error_count']}")
