# RailOptima Monitoring System

A comprehensive monitoring solution for the RailOptima railway traffic management system, providing real-time monitoring, performance tracking, and alerting capabilities.

## 🚀 Features

### Core Monitoring Components

- **API Stub** (`api_support/api_stub.py`): Complete FastAPI mock server with railway management endpoints
- **Failure Monitoring** (`monitoring/failure.py`): Advanced error detection, classification, and alerting
- **Latency Monitoring** (`monitoring/latency.py`): API performance measurement with statistical analysis
- **Log Reporting** (`monitoring/log_report.py`): Structured logging with filtering and export capabilities
- **Runtime Profiling** (`monitoring/log_runtime.py`): Function execution time tracking with decorators
- **Monitoring Orchestrator** (`monitoring_config.py`): Central coordination and configuration management

### Key Capabilities

- ✅ **Real-time Monitoring**: Continuous health checks and performance tracking
- ✅ **Structured Logging**: JSON-formatted logs with multiple output formats
- ✅ **Performance Profiling**: Function-level execution time analysis
- ✅ **Failure Classification**: Categorized error tracking with severity levels
- ✅ **Statistical Analysis**: Comprehensive metrics and trend analysis
- ✅ **Alerting System**: Configurable thresholds and callback notifications
- ✅ **Data Export**: Multiple format support (JSON, CSV, TXT)
- ✅ **Thread Safety**: Concurrent monitoring with proper synchronization

## 📁 Project Structure

```
monitoring/
├── api_support/
│   └── api_stub.py              # FastAPI mock server
├── monitoring/
│   ├── failure.py               # Failure detection and alerting
│   ├── latency.py               # API latency measurement
│   ├── log_report.py            # Structured logging system
│   └── log_runtime.py           # Runtime profiling
├── monitoring_config.py         # Central orchestrator
└── README.md                    # This file
```

## 🛠️ Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify Installation**:
   ```bash
   python -c "import fastapi, requests, psutil; print('Dependencies installed successfully')"
   ```

## 🚀 Quick Start

### 1. Start the API Server

```bash
# Start the mock API server
python monitoring/api_support/api_stub.py
```

The API will be available at `http://localhost:8000` with the following endpoints:
- `/trains` - Train management
- `/stations` - Station information
- `/infrastructure` - Infrastructure components
- `/disruptions` - Disruption tracking
- `/optimize` - Schedule optimization
- `/health` - Health check
- `/metrics` - System metrics

### 2. Run Individual Monitoring Components

```bash
# Test failure monitoring
python monitoring/monitoring/failure.py

# Test latency monitoring
python monitoring/monitoring/latency.py

# Test log reporting
python monitoring/monitoring/log_report.py

# Test runtime profiling
python monitoring/monitoring/log_runtime.py
```

### 3. Start Comprehensive Monitoring

```bash
# Start the monitoring orchestrator
python monitoring/monitoring_config.py
```

## 📊 Usage Examples

### Basic Monitoring Setup

```python
from monitoring.monitoring_config import start_monitoring, MonitoringConfig, MonitoringMode

# Configure monitoring
config = MonitoringConfig(
    mode=MonitoringMode.PRODUCTION.value,
    check_interval=60,  # Check every minute
    api_endpoints=[
        "http://localhost:8000/trains",
        "http://localhost:8000/health"
    ]
)

# Start monitoring
start_monitoring(config)
```

### Using Decorators for Runtime Monitoring

```python
from monitoring.log_runtime import runtime_monitor, performance_monitor

@runtime_monitor()
def optimize_schedule(trains_data):
    # Your optimization logic here
    return optimized_schedule

@performance_monitor(threshold_seconds=2.0)
def slow_function():
    # Only logs if execution takes > 2 seconds
    pass
```

### Structured Logging

```python
from monitoring.log_report import write_log, LogLevel

# Log with different levels
write_log("System started", LogLevel.INFO, "system", "startup")
write_log("High memory usage", LogLevel.WARNING, "monitor", "check_memory", 
         extra_data={"usage": "85%"})
write_log("Critical error", LogLevel.ERROR, "api", "connect",
         extra_data={"url": "http://api.example.com"})
```

### API Health Checking

```python
from monitoring.failure import check_api, check_multiple_apis

# Check single endpoint
status = check_api("http://localhost:8000/health")

# Check multiple endpoints concurrently
results = check_multiple_apis([
    "http://localhost:8000/trains",
    "http://localhost:8000/stations"
])
```

### Latency Measurement

```python
from monitoring.latency import log_api_latency, measure_multiple_apis

# Measure single endpoint
latency = log_api_latency("http://localhost:8000/optimize")

# Measure multiple endpoints
measurements = measure_multiple_apis([
    "http://localhost:8000/trains",
    "http://localhost:8000/disruptions"
])
```

## 📈 Monitoring Dashboard

### Key Metrics Tracked

1. **API Performance**:
   - Response times (mean, median, P95, P99)
   - Success rates
   - Error counts by type

2. **System Health**:
   - Function execution times
   - Memory usage
   - Error rates
   - Overall health score

3. **Failure Analysis**:
   - Failure types and severity
   - Consecutive failure tracking
   - Failure rate trends

### Performance Levels

- **Excellent**: < 100ms average latency
- **Good**: < 1s average latency
- **Acceptable**: < 5s average latency
- **Slow**: < 30s average latency
- **Critical**: > 30s average latency

## 🔧 Configuration

### Monitoring Modes

- **Development**: Verbose logging, frequent checks
- **Testing**: Moderate logging, standard intervals
- **Production**: Minimal logging, optimized performance
- **Maintenance**: Focused monitoring, reduced overhead

### Alert Thresholds

```python
alert_thresholds = {
    "latency_warning": 1000,    # 1 second
    "latency_critical": 3000,   # 3 seconds
    "failure_rate": 10,         # failures per hour
    "runtime_warning": 5.0,     # 5 seconds
    "runtime_critical": 30.0    # 30 seconds
}
```

## 📋 API Reference

### Core Classes

- `MonitoringOrchestrator`: Main monitoring coordinator
- `FailureMonitor`: Error detection and classification
- `LatencyMonitor`: API performance measurement
- `LogReporter`: Structured logging system
- `RuntimeProfiler`: Function execution profiling

### Key Functions

- `start_monitoring()`: Begin continuous monitoring
- `stop_monitoring()`: Stop monitoring
- `get_monitoring_summary()`: Get comprehensive status
- `export_monitoring_data()`: Export data to file

## 🚨 Alerting

The monitoring system supports multiple alerting mechanisms:

1. **Console Alerts**: Real-time console notifications
2. **Callback Functions**: Custom alert handlers
3. **Log Files**: Persistent alert logging
4. **Metrics Export**: Data export for external systems

### Example Alert Callback

```python
def custom_alert_callback(event_type, data):
    if event_type == "api_error":
        # Send email, Slack notification, etc.
        send_notification(f"API Error: {data['error']}")
    
    elif event_type == "system_health":
        if data['overall_health'] == 'critical':
            trigger_emergency_procedures()
```

## 📊 Data Export

### Supported Formats

- **JSON**: Structured data export
- **CSV**: Tabular data for analysis
- **TXT**: Human-readable logs

### Export Examples

```python
# Export monitoring summary
export_monitoring_data("reports/monitoring_summary.json")

# Export runtime profiles
runtime_profiler.export_profiles("reports/performance_profiles.json")

# Export logs
log_reporter.export_logs("reports/logs.csv", format="csv")
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Permission Errors**: Check file write permissions in reports directory
3. **API Connection Issues**: Verify API endpoints are accessible
4. **Memory Usage**: Monitor memory consumption with large datasets

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Check

```python
from monitoring.monitoring_config import get_monitoring_summary

summary = get_monitoring_summary()
print(f"System Health: {summary['overall_health']}")
```

## 🤝 Contributing

1. Follow the existing code structure
2. Add comprehensive docstrings
3. Include example usage
4. Update this README for new features
5. Test with the provided examples

## 📝 License

This monitoring system is part of the RailOptima project and follows the same licensing terms.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the example code
3. Check the generated log files in the `reports/` directory
4. Enable debug logging for detailed information

---

**RailOptima Monitoring System** - Comprehensive monitoring for railway traffic management 🚆
