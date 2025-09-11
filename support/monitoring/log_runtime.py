"""
Enhanced Runtime Monitoring Module for RailOptima
Provides comprehensive function execution time measurement, profiling, and performance tracking.
"""

import os
import json
import time
import datetime
import threading
import functools
import traceback
from typing import Any, Callable, TypeVar, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar("T")

class PerformanceLevel(Enum):
    """Performance level classifications"""
    EXCELLENT = "excellent"  # < 100ms
    GOOD = "good"          # < 1s
    ACCEPTABLE = "acceptable"  # < 5s
    SLOW = "slow"          # < 30s
    CRITICAL = "critical"  # > 30s

@dataclass
class RuntimeMeasurement:
    """Structured runtime measurement data"""
    timestamp: str
    function_name: str
    module_name: str
    runtime_seconds: float
    args_count: int
    kwargs_count: int
    success: bool
    error_message: Optional[str] = None
    memory_usage_mb: Optional[float] = None
    thread_id: Optional[str] = None
    call_stack_depth: int = 0

@dataclass
class PerformanceProfile:
    """Performance profile for a function"""
    function_name: str
    module_name: str
    call_count: int
    total_runtime: float
    average_runtime: float
    min_runtime: float
    max_runtime: float
    success_rate: float
    error_count: int
    last_called: str
    performance_level: str

class RuntimeProfiler:
    """Enhanced runtime profiler with detailed metrics and analysis"""
    
    def __init__(self, log_file: str = "reports/runtime_log.txt",
                 json_log_file: str = "reports/runtime_profile.json"):
        self.log_file = log_file
        self.json_log_file = json_log_file
        self.measurements: List[RuntimeMeasurement] = []
        self.profiles: Dict[str, PerformanceProfile] = {}
        self.callbacks: List[Callable[[RuntimeMeasurement], None]] = []
        self.thresholds = {
            "warning": 1.0,    # 1 second
            "critical": 5.0,    # 5 seconds
            "timeout": 30.0     # 30 seconds
        }
        self._lock = threading.Lock()
        
        # Ensure directories exist
        for file_path in [self.log_file, self.json_log_file]:
            directory = os.path.dirname(file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
    
    def measure_function(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Measure execution time of a function with enhanced tracking.

        Args:
            func (callable): The function to measure.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            T: The return value of the function.
        """
        start_time = time.time()
        thread_id = threading.current_thread().name
        call_stack_depth = len(traceback.extract_stack()) - 1
        
        # Get memory usage if psutil is available
        memory_start = self._get_memory_usage()
        
        try:
            result: T = func(*args, **kwargs)
            success = True
            error_message = None
        except Exception as e:
            success = False
            error_message = str(e)
            result = None
            raise
        finally:
            end_time = time.time()
            runtime = round(end_time - start_time, 3)
            memory_end = self._get_memory_usage()
            memory_usage = memory_end - memory_start if memory_end and memory_start else None
            
            measurement = RuntimeMeasurement(
                timestamp=datetime.datetime.now().isoformat(),
                function_name=func.__name__,
                module_name=func.__module__ or "unknown",
                runtime_seconds=runtime,
                args_count=len(args),
                kwargs_count=len(kwargs),
                success=success,
                error_message=error_message,
                memory_usage_mb=memory_usage,
                thread_id=thread_id,
                call_stack_depth=call_stack_depth
            )
            
            with self._lock:
                self.measurements.append(measurement)
                self._update_profile(measurement)
                self._log_measurement(measurement)
                self._check_thresholds(measurement)
                self._trigger_callbacks(measurement)
        
        return result
    
    def _get_memory_usage(self) -> Optional[float]:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except ImportError:
            return None
    
    def _update_profile(self, measurement: RuntimeMeasurement) -> None:
        """Update performance profile for the function"""
        key = f"{measurement.module_name}.{measurement.function_name}"
        
        if key not in self.profiles:
            self.profiles[key] = PerformanceProfile(
                function_name=measurement.function_name,
                module_name=measurement.module_name,
                call_count=0,
                total_runtime=0.0,
                average_runtime=0.0,
                min_runtime=float('inf'),
                max_runtime=0.0,
                success_rate=0.0,
                error_count=0,
                last_called=measurement.timestamp,
                performance_level="unknown"
            )
        
        profile = self.profiles[key]
        profile.call_count += 1
        profile.total_runtime += measurement.runtime_seconds
        profile.average_runtime = profile.total_runtime / profile.call_count
        profile.min_runtime = min(profile.min_runtime, measurement.runtime_seconds)
        profile.max_runtime = max(profile.max_runtime, measurement.runtime_seconds)
        profile.last_called = measurement.timestamp
        
        if not measurement.success:
            profile.error_count += 1
        
        profile.success_rate = (profile.call_count - profile.error_count) / profile.call_count * 100
        
        # Determine performance level
        if profile.average_runtime < 0.1:
            profile.performance_level = PerformanceLevel.EXCELLENT.value
        elif profile.average_runtime < 1.0:
            profile.performance_level = PerformanceLevel.GOOD.value
        elif profile.average_runtime < 5.0:
            profile.performance_level = PerformanceLevel.ACCEPTABLE.value
        elif profile.average_runtime < 30.0:
            profile.performance_level = PerformanceLevel.SLOW.value
        else:
            profile.performance_level = PerformanceLevel.CRITICAL.value
    
    def _log_measurement(self, measurement: RuntimeMeasurement) -> None:
        """Log measurement to files"""
        # Text log
        try:
            log_line = f"[{measurement.timestamp}] {measurement.module_name}.{measurement.function_name} executed in {measurement.runtime_seconds}s"
            if not measurement.success:
                log_line += f" (ERROR: {measurement.error_message})"
            if measurement.memory_usage_mb:
                log_line += f" (Memory: {measurement.memory_usage_mb:.2f}MB)"
            
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")
        except Exception as e:
            logger.error(f"Failed to write runtime log: {e}")
        
        # JSON log
        try:
            with open(self.json_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(measurement)) + "\n")
        except Exception as e:
            logger.error(f"Failed to write JSON runtime log: {e}")
    
    def _check_thresholds(self, measurement: RuntimeMeasurement) -> None:
        """Check if measurement exceeds thresholds"""
        if measurement.runtime_seconds > self.thresholds["critical"]:
            self._trigger_alert(measurement, "Critical Performance")
        elif measurement.runtime_seconds > self.thresholds["warning"]:
            self._trigger_alert(measurement, "Slow Performance")
    
    def _trigger_alert(self, measurement: RuntimeMeasurement, alert_type: str) -> None:
        """Trigger performance alerts"""
        print(f"⚠️ {alert_type}: {measurement.module_name}.{measurement.function_name} took {measurement.runtime_seconds}s")
    
    def _trigger_callbacks(self, measurement: RuntimeMeasurement) -> None:
        """Trigger registered callbacks"""
        for callback in self.callbacks:
            try:
                callback(measurement)
            except Exception as e:
                logger.error(f"Runtime callback failed: {e}")
    
    def add_callback(self, callback: Callable[[RuntimeMeasurement], None]) -> None:
        """Add a callback function for runtime measurements"""
        self.callbacks.append(callback)
    
    def get_profile(self, function_name: str, module_name: Optional[str] = None) -> Optional[PerformanceProfile]:
        """Get performance profile for a specific function"""
        if module_name:
            key = f"{module_name}.{function_name}"
        else:
            # Find by function name only
            matching_keys = [k for k in self.profiles.keys() if k.endswith(f".{function_name}")]
            if not matching_keys:
                return None
            key = matching_keys[0]  # Take first match
        
        return self.profiles.get(key)
    
    def get_all_profiles(self) -> Dict[str, PerformanceProfile]:
        """Get all performance profiles"""
        return self.profiles.copy()
    
    def get_slowest_functions(self, limit: int = 10) -> List[PerformanceProfile]:
        """Get the slowest functions by average runtime"""
        profiles = list(self.profiles.values())
        profiles.sort(key=lambda p: p.average_runtime, reverse=True)
        return profiles[:limit]
    
    def get_most_called_functions(self, limit: int = 10) -> List[PerformanceProfile]:
        """Get the most frequently called functions"""
        profiles = list(self.profiles.values())
        profiles.sort(key=lambda p: p.call_count, reverse=True)
        return profiles[:limit]
    
    def get_functions_by_performance_level(self, level: PerformanceLevel) -> List[PerformanceProfile]:
        """Get functions by performance level"""
        return [p for p in self.profiles.values() if p.performance_level == level.value]
    
    def get_runtime_statistics(self) -> Dict[str, Any]:
        """Get overall runtime statistics"""
        if not self.measurements:
            return {"message": "No measurements available"}
        
        runtimes = [m.runtime_seconds for m in self.measurements if m.success]
        errors = [m for m in self.measurements if not m.success]
        
        stats = {
            "total_measurements": len(self.measurements),
            "successful_calls": len(runtimes),
            "failed_calls": len(errors),
            "success_rate": len(runtimes) / len(self.measurements) * 100 if self.measurements else 0,
            "unique_functions": len(self.profiles),
            "total_runtime": sum(runtimes) if runtimes else 0
        }
        
        if runtimes:
            stats.update({
                "average_runtime": sum(runtimes) / len(runtimes),
                "min_runtime": min(runtimes),
                "max_runtime": max(runtimes),
                "median_runtime": sorted(runtimes)[len(runtimes) // 2]
            })
        
        return stats
    
    def export_profiles(self, output_file: str) -> bool:
        """Export performance profiles to JSON file"""
        try:
            directory = os.path.dirname(output_file)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            profiles_data = {k: asdict(v) for k, v in self.profiles.items()}
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(profiles_data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to export profiles: {e}")
            return False
    
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
        logger.info(f"Cleared {cleared_count} old runtime measurements")
        return cleared_count

# Global runtime profiler instance
runtime_profiler = RuntimeProfiler()

def log_runtime(func: Callable[..., T], *args: Any, log_file: str = "reports/runtime_log.txt", **kwargs: Any) -> T:
    """
    Legacy function for backward compatibility.
    """
    return runtime_profiler.measure_function(func, *args, **kwargs)

def runtime_monitor(log_file: str = "reports/runtime_log.txt"):
    """
    Decorator for automatic runtime monitoring of functions.
    
    Usage:
        @runtime_monitor()
        def my_function():
            # function code
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            return runtime_profiler.measure_function(func, *args, **kwargs)
        return wrapper
    return decorator

def performance_monitor(threshold_seconds: float = 1.0):
    """
    Decorator that only logs functions exceeding a performance threshold.
    
    Usage:
        @performance_monitor(threshold_seconds=2.0)
        def slow_function():
            # function code
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                runtime = time.time() - start_time
                if runtime > threshold_seconds:
                    measurement = RuntimeMeasurement(
                        timestamp=datetime.datetime.now().isoformat(),
                        function_name=func.__name__,
                        module_name=func.__module__ or "unknown",
                        runtime_seconds=runtime,
                        args_count=len(args),
                        kwargs_count=len(kwargs),
                        success=True,
                        thread_id=threading.current_thread().name
                    )
                    runtime_profiler._log_measurement(measurement)
                    print(f"⚠️ Slow function: {func.__name__} took {runtime:.3f}s (threshold: {threshold_seconds}s)")
        return wrapper
    return decorator

def get_runtime_summary() -> Dict[str, Any]:
    """Get a summary of runtime performance"""
    stats = runtime_profiler.get_runtime_statistics()
    profiles = runtime_profiler.get_all_profiles()
    
    # Count functions by performance level
    level_counts = {}
    for profile in profiles.values():
        level_counts[profile.performance_level] = level_counts.get(profile.performance_level, 0) + 1
    
    # Find slowest functions
    slowest = runtime_profiler.get_slowest_functions(5)
    most_called = runtime_profiler.get_most_called_functions(5)
    
    return {
        "statistics": stats,
        "performance_levels": level_counts,
        "slowest_functions": [asdict(p) for p in slowest],
        "most_called_functions": [asdict(p) for p in most_called],
        "total_profiles": len(profiles)
    }

# Example callback for real-time monitoring
def performance_callback(measurement: RuntimeMeasurement) -> None:
    """Example callback for performance monitoring"""
    if measurement.runtime_seconds > 5.0:
        print(f"🐌 Slow execution: {measurement.function_name} took {measurement.runtime_seconds}s")
    if not measurement.success:
        print(f"❌ Function failed: {measurement.function_name} - {measurement.error_message}")

# Add example callback
runtime_profiler.add_callback(performance_callback)

# --- Example usage ---
if __name__ == "__main__":
    print(">>> Running enhanced runtime monitoring...")
    
    # Test with decorator
    @runtime_monitor()
    def dummy_optimizer(x: int, y: int) -> int:
        time.sleep(1.2)  # simulate heavy computation
        return x + y
    
    @performance_monitor(threshold_seconds=0.5)
    def quick_function() -> str:
        time.sleep(0.1)  # This won't be logged
        return "quick"
    
    @performance_monitor(threshold_seconds=0.5)
    def slow_function() -> str:
        time.sleep(1.0)  # This will be logged
        return "slow"
    
    # Test functions
    print("\n--- Testing functions ---")
    result1 = dummy_optimizer(5, 7)
    print(f"Optimizer result: {result1}")
    
    result2 = quick_function()
    print(f"Quick function result: {result2}")
    
    result3 = slow_function()
    print(f"Slow function result: {result3}")
    
    # Test error handling
    @runtime_monitor()
    def error_function() -> None:
        raise ValueError("Test error")
    
    try:
        error_function()
    except ValueError:
        print("Caught expected error")
    
    print("\n--- Runtime Summary ---")
    summary = get_runtime_summary()
    print(f"Total measurements: {summary['statistics']['total_measurements']}")
    print(f"Success rate: {summary['statistics']['success_rate']:.1f}%")
    print(f"Average runtime: {summary['statistics'].get('average_runtime', 'N/A')}s")
    print(f"Total unique functions: {summary['total_profiles']}")
    
    print("\n--- Performance Levels ---")
    for level, count in summary['performance_levels'].items():
        print(f"{level}: {count}")
    
    print("\n--- Slowest Functions ---")
    for func in summary['slowest_functions']:
        print(f"{func['function_name']}: {func['average_runtime']:.3f}s avg ({func['call_count']} calls)")
    
    print("\n--- Most Called Functions ---")
    for func in summary['most_called_functions']:
        print(f"{func['function_name']}: {func['call_count']} calls ({func['average_runtime']:.3f}s avg)")
    
    print("\n--- Export Test ---")
    success = runtime_profiler.export_profiles("reports/runtime_profiles.json")
    print(f"Profile export: {'✅ Success' if success else '❌ Failed'}")
