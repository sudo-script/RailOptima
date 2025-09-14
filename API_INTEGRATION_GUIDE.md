# RailOptima API Integration Guide

## 🔗 **Files Connected to API for Frontend Data Access**

This guide explains which files from the RailOptima optimizer and audit systems are now connected to the API for frontend data access.

## 📁 **Connected Data Sources**

### **1. Core Optimizer Outputs**
- **`optimizer/schedule_output.json`** → `/optimizer/schedule` endpoint
  - Contains optimized train schedules with departure times, priorities, and delays
  - Used by frontend to display real-time train status and schedules

- **`optimizer/schedule_output.csv`** → Integrated into train data
  - CSV version of optimized schedule for analysis
  - Converted to API format for frontend consumption

- **`optimizer/schedule_api.json`** → Reference format
  - API-compatible format for schedule data

### **2. Audit & Validation Data**
- **`Audit/audit_report.csv`** → `/audit/report` endpoint
  - Audit results and accuracy metrics
  - Used by frontend to display validation results and system accuracy

- **`Audit/audit_report.txt`** → Integrated into audit endpoint
  - Human-readable audit report
  - Provides detailed validation information

- **`Audit/TestData/human_decision_schedule.csv`** → Available for comparison
  - Human decision outputs for validation comparison

### **3. Conflict Detection**
- **`optimizer/trains_conflict.csv`** → `/optimizer/conflicts` endpoint
  - Conflict detection results from validation
  - Used by frontend to display scheduling conflicts and issues

### **4. Visualization & Reports**
- **`optimizer/reports/`** directory → `/visualization/reports` endpoint
  - All visualization outputs (PNG files, reports)
  - Available for frontend to display charts and analysis

- **`optimizer/log_report.py`** → Integrated into status endpoints
  - Execution logs and statistics
  - Provides system performance metrics

## 🚀 **New API Endpoints**

### **Optimizer Data Endpoints**
```
GET /optimizer/schedule          - Get optimized schedule data
GET /optimizer/conflicts         - Get conflict detection results
GET /optimizer/status            - Get optimizer integration status
POST /optimizer/reload           - Reload data from files
```

### **Audit & Validation Endpoints**
```
GET /audit/report                - Get audit report data
```

### **Visualization Endpoints**
```
GET /visualization/reports       - Get available visualization files
```

### **Enhanced Existing Endpoints**
```
GET /trains                      - Now uses real optimizer data when available
GET /info                        - Updated with new endpoint information
```

## 🔄 **Data Flow**

```
Optimizer Files → API Integration → Frontend
     ↓                ↓              ↓
schedule_output.json → /optimizer/schedule → Train Dashboard
audit_report.csv → /audit/report → Validation Display
trains_conflict.csv → /optimizer/conflicts → Conflict Alerts
reports/*.png → /visualization/reports → Charts & Graphs
```

## 🛠 **Integration Features**

### **Automatic Data Loading**
- API automatically loads optimizer data on startup
- Real-time data reload capability via `/optimizer/reload` endpoint
- Fallback to mock data if optimizer files are not available

### **Data Conversion**
- Optimizer JSON/CSV data converted to frontend-compatible format
- Maintains backward compatibility with existing frontend code
- Handles missing or corrupted data gracefully

### **Status Monitoring**
- `/optimizer/status` endpoint provides integration health check
- Shows which data sources are loaded and available
- Provides data counts and last update timestamps

## 🧪 **Testing Integration**

Run the integration test script to verify everything is working:

```bash
python test_api_integration.py
```

This will test:
- ✅ API connectivity
- ✅ Optimizer data loading
- ✅ All new endpoints
- ✅ Data conversion accuracy
- ✅ Error handling

## 📊 **Frontend Usage Examples**

### **Get Real Train Data**
```javascript
// Frontend can now get real optimized train data
const trains = await apiClient.getTrains();
// Returns trains with real delays, priorities, and schedules from optimizer
```

### **Get Audit Results**
```javascript
// Get validation and audit results
const auditData = await fetch('/api/audit/report');
// Returns accuracy metrics and validation results
```

### **Get Conflicts**
```javascript
// Get scheduling conflicts
const conflicts = await fetch('/api/optimizer/conflicts');
// Returns detected conflicts for display in alerts
```

### **Get Visualization Data**
```javascript
// Get available reports and charts
const reports = await fetch('/api/visualization/reports');
// Returns list of available visualization files
```

## 🔧 **Configuration**

### **File Paths**
The API automatically detects and loads data from:
- `optimizer/schedule_output.json`
- `Audit/audit_report.csv`
- `optimizer/trains_conflict.csv`
- `optimizer/reports/` directory

### **Data Refresh**
- Data is loaded on API startup
- Use `/optimizer/reload` endpoint to refresh data
- Frontend can trigger reloads when needed

## 🚨 **Error Handling**

- **Missing Files**: API falls back to mock data
- **Corrupted Data**: Logs errors and continues with available data
- **Network Issues**: Frontend handles API failures gracefully
- **Data Format Issues**: API validates and converts data safely

## 📈 **Performance**

- **Lazy Loading**: Data loaded only when needed
- **Caching**: Data cached in memory for fast access
- **Background Reload**: Data reload doesn't block API responses
- **Efficient Conversion**: Minimal overhead in data transformation

## 🔮 **Future Enhancements**

- Real-time data streaming from optimizer
- WebSocket integration for live updates
- Advanced caching strategies
- Data versioning and history tracking
- Automated data validation and quality checks

---

## 🎯 **Summary**

The RailOptima API now provides a complete bridge between the optimizer/audit systems and the frontend, enabling:

1. **Real-time train data** from optimized schedules
2. **Audit and validation results** for system monitoring
3. **Conflict detection** for operational alerts
4. **Visualization data** for charts and reports
5. **Status monitoring** for system health

All data flows seamlessly from the optimizer files to the frontend dashboard, providing operators with real-time insights into the railway system's performance and optimization results.
