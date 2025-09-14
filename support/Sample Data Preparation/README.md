# RailOptima Sample Data Preparation System

A comprehensive data generation and management system for creating realistic railway data for testing and demonstration purposes.

## 🚀 Features

### Core Components

- **Data Generator** (`sample_data_generator.py`): Creates realistic railway data with configurable scenarios
- **Data Loader** (`data_loader.py`): Loads and converts data for API consumption
- **Multiple Formats**: Supports both CSV and JSON output formats
- **Scenario Management**: Pre-configured scenarios for different testing needs
- **API Integration**: Seamless integration with the RailOptima API stub

### Key Capabilities

- ✅ **Realistic Data Generation**: Creates authentic railway network data
- ✅ **Multiple Scenarios**: Rush hour, maintenance, minimal, and default scenarios
- ✅ **Flexible Output**: CSV and JSON formats for different use cases
- ✅ **API Integration**: Direct loading into the API stub
- ✅ **Data Validation**: Consistency checks and error handling
- ✅ **Extensible Design**: Easy to add new data types and scenarios

## 📁 Project Structure

```
Sample Data Preparation/
├── sample_data_generator.py    # Main data generator
├── data_loader.py              # Data loading and conversion
├── README.md                   # This documentation
├── railway_data.json           # Combined dataset (default)
├── stations.csv                # Station data (CSV)
├── stations.json               # Station data (JSON)
├── trains.csv                  # Train data (CSV)
├── trains.json                 # Train data (JSON)
├── infrastructure.csv          # Infrastructure data (CSV)
├── infrastructure.json         # Infrastructure data (JSON)
├── disruptions.csv             # Disruption data (CSV)
├── disruptions.json            # Disruption data (JSON)
└── scenarios/                  # Scenario-specific data
    ├── rush_hour/              # High-traffic scenario
    ├── maintenance/             # Maintenance-heavy scenario
    └── minimal/                 # Minimal data scenario
```

## 🛠️ Installation & Setup

1. **Ensure Dependencies**:
   ```bash
   pip install pandas numpy
   ```

2. **Generate Sample Data**:
   ```bash
   python sample_data_generator.py
   ```

3. **Verify Data Generation**:
   ```bash
   python data_loader.py
   ```

## 🚀 Usage Examples

### Basic Data Generation

```python
from sample_data_generator import RailwayDataGenerator

# Create generator
generator = RailwayDataGenerator()

# Generate default dataset
data = generator.generate_all_data(
    stations_count=15,
    trains_count=25,
    infrastructure_count=20,
    disruptions_count=5
)

# Generate specific scenario
rush_hour_data = generator.create_scenario_data("rush_hour")
```

### Loading Data for API

```python
from data_loader import load_sample_data, get_available_scenarios

# Load default data
default_data = load_sample_data()

# Load scenario data
scenarios = get_available_scenarios()
maintenance_data = load_sample_data("maintenance")

# Check data counts
print(f"Stations: {len(default_data['stations'])}")
print(f"Trains: {len(default_data['trains'])}")
```

### API Integration

```python
# The API stub automatically loads data on startup
# You can also reload data dynamically:

import requests

# Check current scenario
response = requests.get("http://localhost:8000/scenarios")
scenarios = response.json()["available_scenarios"]

# Load a different scenario
response = requests.post(f"http://localhost:8000/scenarios/{scenarios[0]}/load")

# Reload current data
response = requests.post("http://localhost:8000/reload")
```

## 📊 Data Structure

### Train Data
```json
{
  "id": "T001",
  "name": "Express Alpha",
  "route": "Central Station-North Terminal",
  "departure_time": "2024-01-15T10:00:00",
  "arrival_time": "2024-01-15T11:30:00",
  "status": "scheduled",
  "priority": 1,
  "capacity": 200,
  "current_station": "S001",
  "delay_minutes": 0,
  "train_type": "Express",
  "operator": "RailOptima Express"
}
```

### Station Data
```json
{
  "id": "S001",
  "name": "Central Station",
  "location": {"lat": 40.7128, "lng": -74.0060},
  "capacity": 15,
  "current_trains": 4,
  "status": "operational",
  "station_type": "major",
  "region": "Central",
  "platforms": 6
}
```

### Infrastructure Data
```json
{
  "id": "I001",
  "type": "track",
  "status": "operational",
  "location": {"lat": 40.7128, "lng": -74.0060},
  "maintenance_due": "2024-02-15T00:00:00",
  "capacity": 4,
  "length_km": 25.5,
  "condition": "good"
}
```

### Disruption Data
```json
{
  "id": "D001",
  "type": "signal_failure",
  "severity": "high",
  "affected_trains": ["T001", "T002"],
  "affected_stations": ["S001"],
  "start_time": "2024-01-15T09:30:00",
  "estimated_end_time": "2024-01-15T11:00:00",
  "description": "Signal failure at Central Station causing delays",
  "impact_level": "major"
}
```

## 🎭 Available Scenarios

### Default Scenario
- **Stations**: 15
- **Trains**: 25
- **Infrastructure**: 20
- **Disruptions**: 5
- **Use Case**: General testing and development

### Rush Hour Scenario
- **Stations**: 20
- **Trains**: 50
- **Infrastructure**: 25
- **Disruptions**: 8
- **Use Case**: High-traffic testing, performance evaluation

### Maintenance Scenario
- **Stations**: 10
- **Trains**: 15
- **Infrastructure**: 15
- **Disruptions**: 12
- **Use Case**: Maintenance-heavy testing, disruption handling

### Minimal Scenario
- **Stations**: 5
- **Trains**: 8
- **Infrastructure**: 10
- **Disruptions**: 2
- **Use Case**: Quick testing, minimal resource usage

## 🔧 Configuration

### Customizing Data Generation

```python
# Modify the generator configuration
generator = RailwayDataGenerator()

# Custom station names
generator.station_names = ["Custom Station 1", "Custom Station 2"]

# Custom train types
generator.train_types = ["Express", "Local", "Custom Type"]

# Custom operators
generator.operators = ["Custom Rail", "Test Operator"]
```

### Adding New Scenarios

```python
def create_custom_scenario(self, scenario_name: str) -> Dict[str, List[Any]]:
    """Create a custom scenario"""
    if scenario_name == "custom":
        return self.generate_all_data(
            stations_count=30,
            trains_count=100,
            infrastructure_count=50,
            disruptions_count=20
        )
    else:
        return self.generate_all_data()
```

## 📈 API Endpoints

The API stub provides several endpoints for data management:

### Data Management
- `GET /scenarios` - List available scenarios
- `POST /scenarios/{scenario_name}/load` - Load specific scenario
- `POST /reload` - Reload current data
- `GET /data/summary` - Get data summary

### Data Access
- `GET /trains` - Get all trains
- `GET /stations` - Get all stations
- `GET /infrastructure` - Get all infrastructure
- `GET /disruptions` - Get all disruptions

### System Information
- `GET /` - API information and available scenarios
- `GET /health` - Health check
- `GET /metrics` - System metrics

## 🧪 Testing

### Run Data Generator Test
```bash
python sample_data_generator.py
```

### Run Data Loader Test
```bash
python data_loader.py
```

### Run API Integration Test
```bash
# Start API server
python ../api_support/api_stub.py

# In another terminal, run test
python test_api_integration.py
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **File Not Found**: Check that data files exist in the correct directory
3. **API Connection**: Verify the API server is running on port 8000
4. **Data Format**: Ensure JSON files are valid and properly formatted

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Data Validation

Check data integrity:
```python
from data_loader import DataLoader

loader = DataLoader()
data = loader.load_combined_data()

# Validate data structure
assert len(data["stations"]) > 0, "No stations loaded"
assert len(data["trains"]) > 0, "No trains loaded"
assert len(data["infrastructure"]) > 0, "No infrastructure loaded"
```

## 📝 Data Formats

### CSV Format
- Human-readable format
- Suitable for Excel/Google Sheets
- Contains JSON strings for complex fields
- Headers included

### JSON Format
- Machine-readable format
- Suitable for API consumption
- Structured data types
- Metadata included

### Combined Format
- Single file with all data types
- Includes generation metadata
- Optimized for API loading
- Version information included

## 🤝 Contributing

1. Follow the existing data structure patterns
2. Add comprehensive docstrings
3. Include example usage
4. Update this README for new features
5. Test with the provided examples

## 📝 License

This sample data preparation system is part of the RailOptima project and follows the same licensing terms.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the example code
3. Check the generated data files
4. Enable debug logging for detailed information

---

**RailOptima Sample Data Preparation** - Realistic railway data for testing and development 🚆

