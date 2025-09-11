"""
Monitoring Configuration and Orchestrator for RailOptima
Central configuration and coordination of all monitoring components.
"""

import os
import json
import time
import datetime
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Import monitoring modules
from monitoring.failure import FailureMonitor, FailureSeverity, FailureType
from monitoring.latency import LatencyMonitor, LatencyThreshold
from monitoring.log_report import LogReporter, LogLevel, LogFilter
from monitoring.log_runtime import RuntimeProfiler, PerformanceLevel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitoringMode(Enum):
    """Monitoring operation modes"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"
    MAINTENANCE = "maintenance"

@dataclass
class MonitoringConfig:
    """Configuration for monitoring system"""
    mode: str = MonitoringMode.DEVELOPMENT.value
    enabled_modules: List[str] = None
    api_endpoints: List[str] = None
    check_interval: int = 60  # seconds
    log_retention_days: int = 7
    alert_thresholds: Dict[str, Any] = None
    output_directory: str = "reports"
    
    def __post_init__(self):
        if self.enabled_modules is None:
            self.enabled_modules = ["failure", "latency", "log_report", "log_runtime"]
        if self.api_endpoints is None:
            self.api_endpoints = [
                "http://localhost:8000/trains",
                "http://localhost:8000/stations",
                "http://localhost:8000/infrastructure",
                "http://localhost:8000/disruptions",
                "http://localhost:8000/optimize",
                "http://localhost:8000/health",
                "http://localhost:8000/metrics"
            ]
        if self.alert_thresholds is None:
            self.alert_thresholds = {
                "latency_warning": 1000,  # ms
                "latency_critical": 3000,  # ms
                "failure_rate": 10,  # failures per hour
                "runtime_warning": 5.0,  # seconds
                "runtime_critical": 30.0  # seconds
            }

class MonitoringOrchestrator:
    """Main orchestrator for all monitoring components"""
    
    def __init__(self, config: Optional[MonitoringConfig] = None):
        self.config = config or MonitoringConfig()
        self.monitors = {}
        self.is_running = False
        self.monitoring_thread = None
        self.callbacks: List[Callable[[str, Dict[str, Any]], None]] = []
        
        # Initialize monitoring modules
        self._initialize_monitors()
        
        # Ensure output directory exists
        os.makedirs(self.config.output_directory, exist_ok=True)
    
    def _initialize_monitors(self) -> None:
        """Initialize all monitoring modules"""
        if "failure" in self.config.enabled_modules:
            self.monitors["failure"] = FailureMonitor(
                log_file=f"{self.config.output_directory}/failures_log.txt",
                metrics_file=f"{self.config.output_directory}/failure_metrics.json"
            )
        
        if "latency" in self.config.enabled_modules:
            self.monitors["latency"] = LatencyMonitor(
                log_file=f"{self.config.output_directory}/api_latency_log.txt",
                metrics_file=f"{self.config.output_directory}/latency_metrics.json"
            )
        
        if "log_report" in self.config.enabled_modules:
            self.monitors["log_report"] = LogReporter(
                log_file=f"{self.config.output_directory}/run_log.txt",
                json_log_file=f"{self.config.output_directory}/structured_log.json"
            )
        
        if "log_runtime" in self.config.enabled_modules:
            self.monitors["log_runtime"] = RuntimeProfiler(
                log_file=f"{self.config.output_directory}/runtime_log.txt",
                json_log_file=f"{self.config.output_directory}/runtime_profile.json"
            )
    
    def add_callback(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """Add a callback for monitoring events"""
        self.callbacks.append(callback)
    
    def _trigger_callbacks(self, event_type: str, data: Dict[str, Any]) -> None:
        """Trigger all registered callbacks"""
        for callback in self.callbacks:
            try:
                callback(event_type, data)
            except Exception as e:
                logger.error(f"Monitoring callback failed: {e}")
    
    def start_monitoring(self) -> None:
        """Start continuous monitoring"""
        if self.is_running:
            logger.warning("Monitoring is already running")
            return
        
        self.is_running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("Monitoring started")
        self._log_event("monitoring_started", {"timestamp": datetime.datetime.now().isoformat()})
    
    def stop_monitoring(self) -> None:
        """Stop continuous monitoring"""
        if not self.is_running:
            logger.warning("Monitoring is not running")
            return
        
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("Monitoring stopped")
        self._log_event("monitoring_stopped", {"timestamp": datetime.datetime.now().isoformat()})
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.is_running:
            try:
                self._run_monitoring_cycle()
                time.sleep(self.config.check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)  # Short delay before retry
    
    def _run_monitoring_cycle(self) -> None:
        """Run a single monitoring cycle"""
        cycle_start = datetime.datetime.now()
        
        # Check API endpoints
        if "latency" in self.monitors:
            self._check_api_endpoints()
        
        # Check system health
        self._check_system_health()
        
        # Generate summary
        summary = self.get_monitoring_summary()
        
        # Log cycle completion
        cycle_duration = (datetime.datetime.now() - cycle_start).total_seconds()
        self._log_event("monitoring_cycle", {
            "duration": cycle_duration,
            "timestamp": cycle_start.isoformat(),
            "summary": summary
        })
    
    def _check_api_endpoints(self) -> None:
        """Check all configured API endpoints"""
        latency_monitor = self.monitors.get("latency")
        if not latency_monitor:
            return
        
        for endpoint in self.config.api_endpoints:
            try:
                measurement = latency_monitor.measure_latency(endpoint, timeout=10)
                if measurement and measurement.error_message:
                    self._log_event("api_error", {
                        "endpoint": endpoint,
                        "error": measurement.error_message,
                        "timestamp": measurement.timestamp
                    })
            except Exception as e:
                logger.error(f"Error checking endpoint {endpoint}: {e}")
    
    def _check_system_health(self) -> None:
        """Check overall system health"""
        health_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "monitors_active": len(self.monitors),
            "config_mode": self.config.mode
        }
        
        # Check each monitor's health
        for name, monitor in self.monitors.items():
            try:
                if hasattr(monitor, 'get_metrics'):
                    metrics = monitor.get_metrics()
                    health_data[f"{name}_metrics"] = metrics
            except Exception as e:
                logger.error(f"Error getting metrics from {name}: {e}")
                health_data[f"{name}_error"] = str(e)
        
        self._log_event("system_health", health_data)
    
    def _log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log a monitoring event"""
        if "log_report" in self.monitors:
            log_reporter = self.monitors["log_report"]
            log_reporter.write_log(
                f"Monitoring event: {event_type}",
                LogLevel.INFO,
                "monitoring_orchestrator",
                "_log_event",
                extra_data=data
            )
        
        self._trigger_callbacks(event_type, data)
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get comprehensive monitoring summary"""
        summary = {
            "timestamp": datetime.datetime.now().isoformat(),
            "config": asdict(self.config),
            "monitors": {},
            "overall_health": "unknown"
        }
        
        # Collect data from each monitor
        for name, monitor in self.monitors.items():
            try:
                if name == "failure":
                    summary["monitors"]["failure"] = monitor.get_metrics()
                elif name == "latency":
                    summary["monitors"]["latency"] = monitor.get_overall_stats(24)
                elif name == "log_report":
                    summary["monitors"]["log_report"] = monitor.get_log_statistics()
                elif name == "log_runtime":
                    summary["monitors"]["log_runtime"] = monitor.get_runtime_statistics()
            except Exception as e:
                logger.error(f"Error getting summary from {name}: {e}")
                summary["monitors"][name] = {"error": str(e)}
        
        # Determine overall health
        summary["overall_health"] = self._assess_overall_health(summary["monitors"])
        
        return summary
    
    def _assess_overall_health(self, monitors_data: Dict[str, Any]) -> str:
        """Assess overall system health based on monitor data"""
        health_score = 100
        
        # Check failure metrics
        if "failure" in monitors_data:
            failure_data = monitors_data["failure"]
            if failure_data.get("failure_rate", 0) > self.config.alert_thresholds["failure_rate"]:
                health_score -= 30
        
        # Check latency metrics
        if "latency" in monitors_data:
            latency_data = monitors_data["latency"]
            if "overall" in latency_data:
                overall = latency_data["overall"]
                if overall.get("overall_mean_ms", 0) > self.config.alert_thresholds["latency_critical"]:
                    health_score -= 40
                elif overall.get("overall_mean_ms", 0) > self.config.alert_thresholds["latency_warning"]:
                    health_score -= 20
        
        # Check runtime metrics
        if "log_runtime" in monitors_data:
            runtime_data = monitors_data["log_runtime"]
            if runtime_data.get("average_runtime", 0) > self.config.alert_thresholds["runtime_critical"]:
                health_score -= 30
            elif runtime_data.get("average_runtime", 0) > self.config.alert_thresholds["runtime_warning"]:
                health_score -= 15
        
        # Determine health level
        if health_score >= 90:
            return "excellent"
        elif health_score >= 70:
            return "good"
        elif health_score >= 50:
            return "fair"
        elif health_score >= 30:
            return "poor"
        else:
            return "critical"
    
    def export_monitoring_data(self, output_file: str) -> bool:
        """Export all monitoring data to a single file"""
        try:
            summary = self.get_monitoring_summary()
            
            directory = os.path.dirname(output_file)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Failed to export monitoring data: {e}")
            return False
    
    def cleanup_old_data(self) -> int:
        """Clean up old monitoring data"""
        total_cleared = 0
        
        for name, monitor in self.monitors.items():
            try:
                if hasattr(monitor, 'clear_old_measurements'):
                    cleared = monitor.clear_old_measurements(self.config.log_retention_days)
                    total_cleared += cleared
                elif hasattr(monitor, 'clear_old_logs'):
                    cleared = monitor.clear_old_logs(self.config.log_retention_days)
                    total_cleared += cleared
            except Exception as e:
                logger.error(f"Error cleaning up {name}: {e}")
        
        logger.info(f"Cleaned up {total_cleared} old monitoring records")
        return total_cleared
    
    def update_config(self, new_config: MonitoringConfig) -> None:
        """Update monitoring configuration"""
        self.config = new_config
        self._initialize_monitors()
        logger.info("Monitoring configuration updated")
    
    def get_config(self) -> MonitoringConfig:
        """Get current monitoring configuration"""
        return self.config

# Global monitoring orchestrator instance
monitoring_orchestrator = MonitoringOrchestrator()

def start_monitoring(config: Optional[MonitoringConfig] = None) -> None:
    """Start monitoring with optional configuration"""
    if config:
        monitoring_orchestrator.update_config(config)
    monitoring_orchestrator.start_monitoring()

def stop_monitoring() -> None:
    """Stop monitoring"""
    monitoring_orchestrator.stop_monitoring()

def get_monitoring_summary() -> Dict[str, Any]:
    """Get current monitoring summary"""
    return monitoring_orchestrator.get_monitoring_summary()

def export_monitoring_data(output_file: str = "reports/monitoring_summary.json") -> bool:
    """Export monitoring data"""
    return monitoring_orchestrator.export_monitoring_data(output_file)

# Example callback for monitoring events
def monitoring_event_callback(event_type: str, data: Dict[str, Any]) -> None:
    """Example callback for monitoring events"""
    if event_type in ["api_error", "system_health"]:
        print(f"📊 Monitoring Event: {event_type}")
        if event_type == "api_error":
            print(f"   Endpoint: {data.get('endpoint', 'Unknown')}")
            print(f"   Error: {data.get('error', 'Unknown')}")
        elif event_type == "system_health":
            print(f"   Health: {data.get('overall_health', 'Unknown')}")

# Add example callback
monitoring_orchestrator.add_callback(monitoring_event_callback)

# --- Example usage ---
if __name__ == "__main__":
    print(">>> Running monitoring orchestrator...")
    
    # Create custom configuration
    config = MonitoringConfig(
        mode=MonitoringMode.DEVELOPMENT.value,
        enabled_modules=["failure", "latency", "log_report", "log_runtime"],
        check_interval=30,  # Check every 30 seconds
        log_retention_days=3,
        alert_thresholds={
            "latency_warning": 500,
            "latency_critical": 2000,
            "failure_rate": 5,
            "runtime_warning": 2.0,
            "runtime_critical": 10.0
        }
    )
    
    # Start monitoring
    start_monitoring(config)
    
    print("Monitoring started. Press Ctrl+C to stop...")
    
    try:
        # Run for a short time to demonstrate
        time.sleep(60)  # Run for 1 minute
        
        # Get summary
        print("\n--- Monitoring Summary ---")
        summary = get_monitoring_summary()
        print(f"Overall Health: {summary['overall_health']}")
        print(f"Active Monitors: {len(summary['monitors'])}")
        
        # Export data
        success = export_monitoring_data("reports/monitoring_demo.json")
        print(f"Data export: {'✅ Success' if success else '❌ Failed'}")
        
    except KeyboardInterrupt:
        print("\nStopping monitoring...")
    finally:
        stop_monitoring()
        print("Monitoring stopped.")
