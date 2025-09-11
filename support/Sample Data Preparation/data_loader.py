"""
RailOptima Data Loader
Loads sample data from files and provides it to the API stub.
"""

import json
import csv
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    """Loads railway data from various file formats"""
    
    def __init__(self, data_dir: str = "support/Sample Data Preparation"):
        self.data_dir = data_dir
        self.scenarios_dir = os.path.join(data_dir, "scenarios")
        
    def load_from_json(self, filename: str, scenario: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load data from JSON file"""
        if scenario:
            filepath = os.path.join(self.scenarios_dir, scenario, filename)
        else:
            filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data)} records from {filename}")
            return data
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return []
    
    def load_from_csv(self, filename: str, scenario: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load data from CSV file"""
        if scenario:
            filepath = os.path.join(self.scenarios_dir, scenario, filename)
        else:
            filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            return []
        
        try:
            data = []
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Parse JSON strings in CSV
                    for key, value in row.items():
                        if value.startswith('{') or value.startswith('['):
                            try:
                                row[key] = json.loads(value)
                            except json.JSONDecodeError:
                                pass  # Keep as string if not valid JSON
                    data.append(row)
            logger.info(f"Loaded {len(data)} records from {filename}")
            return data
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return []
    
    def load_combined_data(self, scenario: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Load all data from the combined railway_data.json file"""
        filename = "railway_data.json"
        if scenario:
            filepath = os.path.join(self.scenarios_dir, scenario, filename)
        else:
            filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            logger.error(f"Combined data file not found: {filepath}")
            return {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract the data sections
            result = {
                "stations": data.get("stations", []),
                "trains": data.get("trains", []),
                "infrastructure": data.get("infrastructure", []),
                "disruptions": data.get("disruptions", []),
                "metadata": data.get("metadata", {})
            }
            
            logger.info(f"Loaded combined data: {len(result['stations'])} stations, "
                       f"{len(result['trains'])} trains, {len(result['infrastructure'])} infrastructure, "
                       f"{len(result['disruptions'])} disruptions")
            return result
        except Exception as e:
            logger.error(f"Error loading combined data: {e}")
            return {}
    
    def get_available_scenarios(self) -> List[str]:
        """Get list of available scenarios"""
        if not os.path.exists(self.scenarios_dir):
            return []
        
        scenarios = []
        for item in os.listdir(self.scenarios_dir):
            item_path = os.path.join(self.scenarios_dir, item)
            if os.path.isdir(item_path):
                scenarios.append(item)
        
        return scenarios
    
    def load_scenario_data(self, scenario: str) -> Dict[str, List[Dict[str, Any]]]:
        """Load data for a specific scenario"""
        if scenario not in self.get_available_scenarios():
            logger.error(f"Scenario '{scenario}' not found")
            return {}
        
        return self.load_combined_data(scenario)
    
    def convert_to_api_models(self, data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Any]]:
        """Convert loaded data to API model format"""
        converted = {}
        
        # Convert stations
        converted["stations"] = []
        for station_data in data.get("stations", []):
            station = {
                "id": station_data["id"],
                "name": station_data["name"],
                "location": station_data["location"],
                "capacity": station_data["capacity"],
                "current_trains": station_data["current_trains"],
                "status": station_data["status"]
            }
            converted["stations"].append(station)
        
        # Convert trains
        converted["trains"] = []
        for train_data in data.get("trains", []):
            train = {
                "id": train_data["id"],
                "name": train_data["name"],
                "route": train_data["route"],
                "departure_time": datetime.fromisoformat(train_data["departure_time"]),
                "arrival_time": datetime.fromisoformat(train_data["arrival_time"]),
                "status": train_data["status"],
                "priority": train_data["priority"],
                "capacity": train_data["capacity"],
                "current_station": train_data.get("current_station"),
                "delay_minutes": train_data["delay_minutes"]
            }
            converted["trains"].append(train)
        
        # Convert infrastructure
        converted["infrastructure"] = []
        for infra_data in data.get("infrastructure", []):
            infra = {
                "id": infra_data["id"],
                "type": infra_data["type"],
                "status": infra_data["status"],
                "location": infra_data["location"],
                "maintenance_due": datetime.fromisoformat(infra_data["maintenance_due"]) if infra_data.get("maintenance_due") else None,
                "capacity": infra_data.get("capacity")
            }
            converted["infrastructure"].append(infra)
        
        # Convert disruptions
        converted["disruptions"] = []
        for disruption_data in data.get("disruptions", []):
            disruption = {
                "id": disruption_data["id"],
                "type": disruption_data["type"],
                "severity": disruption_data["severity"],
                "affected_trains": disruption_data["affected_trains"],
                "affected_stations": disruption_data["affected_stations"],
                "start_time": datetime.fromisoformat(disruption_data["start_time"]),
                "estimated_end_time": datetime.fromisoformat(disruption_data["estimated_end_time"]) if disruption_data.get("estimated_end_time") else None,
                "description": disruption_data["description"]
            }
            converted["disruptions"].append(disruption)
        
        return converted

# Global data loader instance
data_loader = DataLoader()

def load_sample_data(scenario: Optional[str] = None) -> Dict[str, List[Any]]:
    """Load sample data for the API"""
    logger.info(f"Loading sample data{' for scenario: ' + scenario if scenario else ''}")
    
    # Load combined data
    raw_data = data_loader.load_combined_data(scenario)
    if not raw_data:
        logger.warning("No data loaded, using empty datasets")
        return {
            "stations": [],
            "trains": [],
            "infrastructure": [],
            "disruptions": []
        }
    
    # Convert to API model format
    converted_data = data_loader.convert_to_api_models(raw_data)
    
    logger.info(f"Successfully loaded and converted data for scenario: {scenario or 'default'}")
    return converted_data

def get_available_scenarios() -> List[str]:
    """Get list of available scenarios"""
    return data_loader.get_available_scenarios()

def reload_data(scenario: Optional[str] = None) -> Dict[str, List[Any]]:
    """Reload data from files"""
    logger.info(f"Reloading data{' for scenario: ' + scenario if scenario else ''}")
    return load_sample_data(scenario)

# --- Example usage ---
if __name__ == "__main__":
    print("📊 RailOptima Data Loader Test")
    print("=" * 40)
    
    # Test loading default data
    print("\n🔍 Loading default data...")
    default_data = load_sample_data()
    print(f"   Stations: {len(default_data['stations'])}")
    print(f"   Trains: {len(default_data['trains'])}")
    print(f"   Infrastructure: {len(default_data['infrastructure'])}")
    print(f"   Disruptions: {len(default_data['disruptions'])}")
    
    # Test loading scenario data
    scenarios = get_available_scenarios()
    print(f"\n🎭 Available scenarios: {scenarios}")
    
    for scenario in scenarios:
        print(f"\n📋 Loading {scenario} scenario...")
        scenario_data = load_sample_data(scenario)
        print(f"   Stations: {len(scenario_data['stations'])}")
        print(f"   Trains: {len(scenario_data['trains'])}")
        print(f"   Infrastructure: {len(scenario_data['infrastructure'])}")
        print(f"   Disruptions: {len(scenario_data['disruptions'])}")
    
    print("\n✅ Data loading test completed!")
