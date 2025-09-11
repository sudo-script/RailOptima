"""
Enhanced Log Reporting Module for RailOptima
Provides comprehensive logging capabilities with levels, filtering, and structured output.
"""

import os
import json
import datetime
import logging
import threading
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogLevel(Enum):
    """Log levels following standard logging conventions"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class LogEntry:
    """Structured log entry data"""
    timestamp: str
    level: str
    message: str
    module: Optional[str] = None
    function: Optional[str] = None
    line_number: Optional[int] = None
    extra_data: Optional[Dict[str, Any]] = None
    thread_id: Optional[str] = None

class LogFilter:
    """Log filtering capabilities"""
    
    def __init__(self):
        self.level_threshold = LogLevel.INFO
        self.module_filters: List[str] = []
        self.message_patterns: List[str] = []
        self.exclude_patterns: List[str] = []
    
    def set_level_threshold(self, level: LogLevel) -> None:
        """Set minimum log level to include"""
        self.level_threshold = level
    
    def add_module_filter(self, module_pattern: str) -> None:
        """Add module name pattern to include"""
        self.module_filters.append(module_pattern)
    
    def add_message_pattern(self, pattern: str) -> None:
        """Add message pattern to include"""
        self.message_patterns.append(pattern)
    
    def add_exclude_pattern(self, pattern: str) -> None:
        """Add pattern to exclude"""
        self.exclude_patterns.append(pattern)
    
    def matches(self, log_entry: LogEntry) -> bool:
        """Check if log entry matches filter criteria"""
        # Check level threshold
        if LogLevel(log_entry.level).value < self.level_threshold.value:
            return False
        
        # Check module filters
        if self.module_filters and log_entry.module:
            if not any(re.search(pattern, log_entry.module, re.IGNORECASE) 
                      for pattern in self.module_filters):
                return False
        
        # Check message patterns
        if self.message_patterns:
            if not any(re.search(pattern, log_entry.message, re.IGNORECASE) 
                      for pattern in self.message_patterns):
                return False
        
        # Check exclude patterns
        if self.exclude_patterns:
            if any(re.search(pattern, log_entry.message, re.IGNORECASE) 
                   for pattern in self.exclude_patterns):
                return False
        
        return True

class LogReporter:
    """Enhanced log reporter with structured logging and filtering"""
    
    def __init__(self, log_file: str = "reports/run_log.txt",
                 json_log_file: str = "reports/structured_log.json"):
        self.log_file = log_file
        self.json_log_file = json_log_file
        self.log_entries: List[LogEntry] = []
        self.filters: List[LogFilter] = []
        self.callbacks: List[Callable[[LogEntry], None]] = []
        self._lock = threading.Lock()
        
        # Ensure directories exist
        for file_path in [self.log_file, self.json_log_file]:
            directory = os.path.dirname(file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
    
    def write_log(self, message: str, level: LogLevel = LogLevel.INFO,
                 module: Optional[str] = None, function: Optional[str] = None,
                 line_number: Optional[int] = None, extra_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Write a structured log entry.

        Args:
            message (str): The message to log.
            level (LogLevel): Log level.
            module (str, optional): Module name.
            function (str, optional): Function name.
            line_number (int, optional): Line number.
            extra_data (dict, optional): Additional data to include.
        """
        timestamp = datetime.datetime.now().isoformat()
        thread_id = threading.current_thread().name
        
        log_entry = LogEntry(
            timestamp=timestamp,
            level=level.value,
            message=message,
            module=module,
            function=function,
            line_number=line_number,
            extra_data=extra_data,
            thread_id=thread_id
        )
        
        with self._lock:
            self.log_entries.append(log_entry)
            self._write_to_files(log_entry)
            self._trigger_callbacks(log_entry)
    
    def _write_to_files(self, log_entry: LogEntry) -> None:
        """Write log entry to both text and JSON files"""
        # Write to text file
        try:
            log_line = f"[{log_entry.timestamp}] [{log_entry.level}] {log_entry.message}"
            if log_entry.module:
                log_line += f" (module: {log_entry.module})"
            if log_entry.function:
                log_line += f" (function: {log_entry.function})"
            if log_entry.extra_data:
                log_line += f" (data: {log_entry.extra_data})"
            
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")
        except Exception as e:
            print(f"[ERROR] Could not write to log file {self.log_file}: {e}")
        
        # Write to JSON file
        try:
            with open(self.json_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(log_entry)) + "\n")
        except Exception as e:
            print(f"[ERROR] Could not write to JSON log file {self.json_log_file}: {e}")
    
    def _trigger_callbacks(self, log_entry: LogEntry) -> None:
        """Trigger registered callbacks"""
        for callback in self.callbacks:
            try:
                callback(log_entry)
            except Exception as e:
                print(f"[ERROR] Log callback failed: {e}")
    
    def add_callback(self, callback: Callable[[LogEntry], None]) -> None:
        """Add a callback function for log entries"""
        self.callbacks.append(callback)
    
    def add_filter(self, log_filter: LogFilter) -> None:
        """Add a log filter"""
        self.filters.append(log_filter)
    
    def read_logs(self, apply_filters: bool = True) -> List[LogEntry]:
        """
        Read and return log entries, optionally applying filters.

        Args:
            apply_filters (bool): Whether to apply registered filters.

        Returns:
            List[LogEntry]: List of log entries.
        """
        if apply_filters and self.filters:
            filtered_entries = []
            for entry in self.log_entries:
                if all(filter_obj.matches(entry) for filter_obj in self.filters):
                    filtered_entries.append(entry)
            return filtered_entries
        return self.log_entries.copy()
    
    def read_logs_from_file(self, log_file: Optional[str] = None) -> List[str]:
        """
        Read raw log lines from file.

        Args:
            log_file (str, optional): Path to log file. Uses default if None.

        Returns:
            List[str]: List of raw log lines.
        """
        file_path = log_file or self.log_file
        if not os.path.exists(file_path):
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.readlines()
        except Exception:
            return []
    
    def get_logs_by_level(self, level: LogLevel) -> List[LogEntry]:
        """Get logs filtered by level"""
        return [entry for entry in self.log_entries if LogLevel(entry.level) == level]
    
    def get_logs_by_module(self, module_pattern: str) -> List[LogEntry]:
        """Get logs filtered by module pattern"""
        pattern = re.compile(module_pattern, re.IGNORECASE)
        return [entry for entry in self.log_entries 
                if entry.module and pattern.search(entry.module)]
    
    def get_logs_by_time_range(self, start_time: datetime.datetime, 
                              end_time: datetime.datetime) -> List[LogEntry]:
        """Get logs within time range"""
        return [entry for entry in self.log_entries
                if start_time <= datetime.datetime.fromisoformat(entry.timestamp) <= end_time]
    
    def get_recent_logs(self, hours: int = 24) -> List[LogEntry]:
        """Get logs from the last N hours"""
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=hours)
        return [entry for entry in self.log_entries
                if datetime.datetime.fromisoformat(entry.timestamp) >= cutoff_time]
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get statistics about logged entries"""
        if not self.log_entries:
            return {"message": "No log entries available"}
        
        # Count by level
        level_counts = {}
        for entry in self.log_entries:
            level_counts[entry.level] = level_counts.get(entry.level, 0) + 1
        
        # Count by module
        module_counts = {}
        for entry in self.log_entries:
            if entry.module:
                module_counts[entry.module] = module_counts.get(entry.module, 0) + 1
        
        # Time range
        timestamps = [datetime.datetime.fromisoformat(entry.timestamp) for entry in self.log_entries]
        time_range = {
            "earliest": min(timestamps).isoformat() if timestamps else None,
            "latest": max(timestamps).isoformat() if timestamps else None,
            "total_entries": len(self.log_entries)
        }
        
        return {
            "level_counts": level_counts,
            "module_counts": module_counts,
            "time_range": time_range,
            "total_entries": len(self.log_entries)
        }
    
    def export_logs(self, output_file: str, format: str = "json") -> bool:
        """
        Export logs to file in specified format.

        Args:
            output_file (str): Output file path.
            format (str): Export format ("json", "csv", "txt").

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            directory = os.path.dirname(output_file)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            if format.lower() == "json":
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump([asdict(entry) for entry in self.log_entries], f, indent=2)
            
            elif format.lower() == "csv":
                import csv
                with open(output_file, "w", newline="", encoding="utf-8") as f:
                    if self.log_entries:
                        writer = csv.DictWriter(f, fieldnames=asdict(self.log_entries[0]).keys())
                        writer.writeheader()
                        writer.writerows([asdict(entry) for entry in self.log_entries])
            
            elif format.lower() == "txt":
                with open(output_file, "w", encoding="utf-8") as f:
                    for entry in self.log_entries:
                        f.write(f"[{entry.timestamp}] [{entry.level}] {entry.message}\n")
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            return True
        except Exception as e:
            print(f"[ERROR] Could not export logs: {e}")
            return False
    
    def clear_old_logs(self, days: int = 7) -> int:
        """Clear logs older than N days"""
        cutoff_time = datetime.datetime.now() - datetime.timedelta(days=days)
        original_count = len(self.log_entries)
        
        with self._lock:
            self.log_entries = [
                entry for entry in self.log_entries
                if datetime.datetime.fromisoformat(entry.timestamp) >= cutoff_time
            ]
        
        cleared_count = original_count - len(self.log_entries)
        logger.info(f"Cleared {cleared_count} old log entries")
        return cleared_count

# Global log reporter instance
log_reporter = LogReporter()

def write_log(message: str, level: LogLevel = LogLevel.INFO,
             module: Optional[str] = None, function: Optional[str] = None,
             line_number: Optional[int] = None, extra_data: Optional[Dict[str, Any]] = None) -> None:
    """
    Convenience function to write logs using the global reporter.
    """
    log_reporter.write_log(message, level, module, function, line_number, extra_data)

def read_logs(log_file: Optional[str] = None) -> List[str]:
    """
    Convenience function to read raw log lines.
    """
    return log_reporter.read_logs_from_file(log_file)

def get_log_summary() -> Dict[str, Any]:
    """Get a summary of recent logs"""
    stats = log_reporter.get_log_statistics()
    recent_logs = log_reporter.get_recent_logs(24)
    
    # Count recent errors and warnings
    recent_errors = len([log for log in recent_logs if log.level == "ERROR"])
    recent_warnings = len([log for log in recent_logs if log.level == "WARNING"])
    
    return {
        "summary": stats,
        "recent_logs_count": len(recent_logs),
        "recent_errors": recent_errors,
        "recent_warnings": recent_warnings,
        "most_common_level": max(stats["level_counts"].items(), key=lambda x: x[1])[0] if stats["level_counts"] else None,
        "most_active_module": max(stats["module_counts"].items(), key=lambda x: x[1])[0] if stats["module_counts"] else None
    }

# Example callback for real-time monitoring
def console_callback(log_entry: LogEntry) -> None:
    """Example callback that prints critical logs to console"""
    if log_entry.level in ["ERROR", "CRITICAL"]:
        print(f"🚨 {log_entry.level}: {log_entry.message}")
        if log_entry.module:
            print(f"   Module: {log_entry.module}")
        if log_entry.extra_data:
            print(f"   Data: {log_entry.extra_data}")

# Add example callback
log_reporter.add_callback(console_callback)

# --- Example usage ---
if __name__ == "__main__":
    print(">>> Running enhanced log reporting...")
    
    # Test different log levels
    write_log("System startup initiated", LogLevel.INFO, "system", "startup")
    write_log("Configuration loaded successfully", LogLevel.INFO, "config", "load_config")
    write_log("Database connection established", LogLevel.INFO, "database", "connect")
    
    write_log("High memory usage detected", LogLevel.WARNING, "monitor", "check_memory", 
             extra_data={"memory_usage": "85%", "threshold": "80%"})
    
    write_log("Failed to connect to external API", LogLevel.ERROR, "api", "connect",
             extra_data={"url": "http://external-api.com", "retry_count": 3})
    
    write_log("Critical system failure", LogLevel.CRITICAL, "system", "emergency_shutdown",
             extra_data={"error_code": "SYS001", "affected_services": ["api", "database"]})
    
    print("\n--- Log Summary ---")
    summary = get_log_summary()
    print(f"Total entries: {summary['summary']['total_entries']}")
    print(f"Recent logs (24h): {summary['recent_logs_count']}")
    print(f"Recent errors: {summary['recent_errors']}")
    print(f"Recent warnings: {summary['recent_warnings']}")
    print(f"Most common level: {summary['most_common_level']}")
    print(f"Most active module: {summary['most_active_module']}")
    
    print("\n--- Level Distribution ---")
    for level, count in summary['summary']['level_counts'].items():
        print(f"{level}: {count}")
    
    print("\n--- Module Distribution ---")
    for module, count in summary['summary']['module_counts'].items():
        print(f"{module}: {count}")
    
    print("\n--- Recent Logs ---")
    recent_logs = log_reporter.get_recent_logs(1)  # Last hour
    for log_entry in recent_logs[-5:]:  # Show last 5
        print(f"[{log_entry.timestamp}] [{log_entry.level}] {log_entry.message}")
    
    print("\n--- Export Test ---")
    success = log_reporter.export_logs("reports/log_export.json", "json")
    print(f"JSON export: {'✅ Success' if success else '❌ Failed'}")
    
    success = log_reporter.export_logs("reports/log_export.txt", "txt")
    print(f"TXT export: {'✅ Success' if success else '❌ Failed'}")
