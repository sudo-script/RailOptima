"""
RailOptima Sample Data Generator
Generates realistic railway data for testing and demonstration purposes.
"""

import json
import csv
import random
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TrainData:
    """Train data structure"""
    id: str
    name: str
    route: str
    departure_time: str
    arrival_time: str
    status: str
    priority: int
    capacity: int
    current_station: Optional[str]
    delay_minutes: int
    train_type: str
    operator: str

@dataclass
class StationData:
    """Station data structure"""
    id: str
    name: str
    location: Dict[str, float]
    capacity: int
    current_trains: int
    status: str
    station_type: str
    region: str
    platforms: int

@dataclass
class InfrastructureData:
    """Infrastructure data structure"""
    id: str
    type: str
    status: str
    location: Dict[str, float]
    maintenance_due: Optional[str]
    capacity: Optional[int]
    length_km: Optional[float]
    condition: str

@dataclass
class DisruptionData:
    """Disruption data structure"""
    id: str
    type: str
    severity: str
    affected_trains: List[str]
    affected_stations: List[str]
    start_time: str
    estimated_end_time: Optional[str]
    description: str
    impact_level: str

class RailwayDataGenerator:
    """Generates realistic railway data for testing"""
    
    def __init__(self, output_dir: str = "support/Sample Data Preparation"):
        self.output_dir = output_dir
        self.stations = []
        self.trains = []
        self.infrastructure = []
        self.disruptions = []
        
        # Railway network configuration
        self.station_names = [
            "Central Station", "North Terminal", "South Junction", "East Gate", "West Hub",
            "Metro Center", "Transit Point", "Railway Plaza", "Commuter Hub", "Express Terminal",
            "Regional Station", "Interchange Point", "Main Station", "City Center", "Downtown Terminal"
        ]
        
        self.train_types = ["Express", "Local", "Freight", "High-Speed", "Commuter", "Regional"]
        self.operators = ["RailOptima Express", "Metro Rail", "Regional Transit", "Freight Lines", "City Commuter"]
        self.infrastructure_types = ["track", "signal", "bridge", "tunnel", "platform", "switch", "crossing"]
        self.disruption_types = ["delay", "cancellation", "track_closure", "signal_failure", "weather", "maintenance"]
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_stations(self, count: int = 15) -> List[StationData]:
        """Generate realistic station data"""
        logger.info(f"Generating {count} stations...")
        
        stations = []
        for i in range(count):
            station_id = f"S{i+1:03d}"
            name = random.choice(self.station_names)
            
            # Generate realistic coordinates (simulating a regional network)
            lat = 40.5 + random.uniform(-0.5, 0.5)  # NYC area
            lng = -74.0 + random.uniform(-0.5, 0.5)
            
            station = StationData(
                id=station_id,
                name=name,
                location={"lat": round(lat, 4), "lng": round(lng, 4)},
                capacity=random.randint(5, 20),
                current_trains=random.randint(0, 5),
                status="operational",
                station_type=random.choice(["major", "minor", "junction", "terminal"]),
                region=random.choice(["North", "South", "East", "West", "Central"]),
                platforms=random.randint(2, 8)
            )
            stations.append(station)
        
        self.stations = stations
        return stations
    
    def generate_trains(self, count: int = 25) -> List[TrainData]:
        """Generate realistic train data"""
        logger.info(f"Generating {count} trains...")
        
        trains = []
        base_time = datetime.now() + timedelta(hours=1)
        
        for i in range(count):
            train_id = f"T{i+1:03d}"
            train_type = random.choice(self.train_types)
            operator = random.choice(self.operators)
            
            # Generate realistic train names
            if train_type == "Express":
                name = f"{train_type} {random.choice(['Alpha', 'Beta', 'Gamma', 'Delta'])}"
            elif train_type == "Freight":
                name = f"{train_type} {random.randint(1000, 9999)}"
            else:
                name = f"{train_type} {random.choice(['A', 'B', 'C', 'D'])}"
            
            # Generate route (simplified)
            start_station = random.choice(self.stations)
            end_station = random.choice([s for s in self.stations if s.id != start_station.id])
            route = f"{start_station.name}-{end_station.name}"
            
            # Generate realistic timing
            departure_time = base_time + timedelta(minutes=random.randint(0, 180))
            travel_time = timedelta(minutes=random.randint(30, 180))
            arrival_time = departure_time + travel_time
            
            # Determine priority based on train type
            if train_type == "Express":
                priority = random.randint(1, 2)
            elif train_type == "Freight":
                priority = random.randint(3, 4)
            else:
                priority = random.randint(2, 3)
            
            train = TrainData(
                id=train_id,
                name=name,
                route=route,
                departure_time=departure_time.isoformat(),
                arrival_time=arrival_time.isoformat(),
                status=random.choice(["scheduled", "boarding", "departed", "arrived"]),
                priority=priority,
                capacity=random.randint(50, 300) if train_type != "Freight" else random.randint(20, 100),
                current_station=start_station.id if random.random() < 0.3 else None,
                delay_minutes=random.randint(0, 30) if random.random() < 0.2 else 0,
                train_type=train_type,
                operator=operator
            )
            trains.append(train)
        
        self.trains = trains
        return trains
    
    def generate_infrastructure(self, count: int = 20) -> List[InfrastructureData]:
        """Generate infrastructure data"""
        logger.info(f"Generating {count} infrastructure components...")
        
        infrastructure = []
        for i in range(count):
            infra_id = f"I{i+1:03d}"
            infra_type = random.choice(self.infrastructure_types)
            
            # Generate location near stations
            station = random.choice(self.stations)
            lat = station.location["lat"] + random.uniform(-0.01, 0.01)
            lng = station.location["lng"] + random.uniform(-0.01, 0.01)
            
            # Determine status and maintenance
            status = random.choice(["operational", "maintenance", "out_of_service"])
            maintenance_due = None
            if status == "maintenance" or random.random() < 0.1:
                maintenance_due = (datetime.now() + timedelta(days=random.randint(1, 30))).isoformat()
            
            # Set capacity based on type
            capacity = None
            if infra_type in ["track", "platform"]:
                capacity = random.randint(2, 8)
            
            # Set length for tracks
            length_km = None
            if infra_type == "track":
                length_km = round(random.uniform(1.0, 50.0), 2)
            
            infra = InfrastructureData(
                id=infra_id,
                type=infra_type,
                status=status,
                location={"lat": round(lat, 4), "lng": round(lng, 4)},
                maintenance_due=maintenance_due,
                capacity=capacity,
                length_km=length_km,
                condition=random.choice(["excellent", "good", "fair", "poor"])
            )
            infrastructure.append(infra)
        
        self.infrastructure = infrastructure
        return infrastructure
    
    def generate_disruptions(self, count: int = 5) -> List[DisruptionData]:
        """Generate disruption data"""
        logger.info(f"Generating {count} disruptions...")
        
        disruptions = []
        for i in range(count):
            disruption_id = f"D{i+1:03d}"
            disruption_type = random.choice(self.disruption_types)
            
            # Select affected trains and stations
            affected_trains = random.sample([t.id for t in self.trains], random.randint(1, 3))
            affected_stations = random.sample([s.id for s in self.stations], random.randint(1, 2))
            
            # Generate timing
            start_time = datetime.now() - timedelta(minutes=random.randint(10, 120))
            estimated_end_time = start_time + timedelta(minutes=random.randint(30, 180))
            
            # Determine severity based on type
            if disruption_type in ["track_closure", "signal_failure"]:
                severity = random.choice(["high", "critical"])
                impact_level = "major"
            elif disruption_type == "weather":
                severity = random.choice(["medium", "high"])
                impact_level = "moderate"
            else:
                severity = random.choice(["low", "medium"])
                impact_level = "minor"
            
            # Generate description
            station_name = next(s.name for s in self.stations if s.id in affected_stations)
            descriptions = {
                "delay": f"Mechanical issue causing delays at {station_name}",
                "cancellation": f"Service cancellation due to equipment failure",
                "track_closure": f"Track closure at {station_name} for emergency repairs",
                "signal_failure": f"Signal system failure affecting {station_name}",
                "weather": f"Weather-related delays affecting multiple services",
                "maintenance": f"Scheduled maintenance work at {station_name}"
            }
            
            disruption = DisruptionData(
                id=disruption_id,
                type=disruption_type,
                severity=severity,
                affected_trains=affected_trains,
                affected_stations=affected_stations,
                start_time=start_time.isoformat(),
                estimated_end_time=estimated_end_time.isoformat(),
                description=descriptions[disruption_type],
                impact_level=impact_level
            )
            disruptions.append(disruption)
        
        self.disruptions = disruptions
        return disruptions
    
    def save_to_csv(self, data: List[Any], filename: str) -> None:
        """Save data to CSV file"""
        filepath = os.path.join(self.output_dir, filename)
        
        if not data:
            logger.warning(f"No data to save to {filename}")
            return
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = data[0].__dict__.keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in data:
                # Convert nested dicts to JSON strings for CSV
                row = {}
                for key, value in item.__dict__.items():
                    if isinstance(value, dict):
                        row[key] = json.dumps(value)
                    elif isinstance(value, list):
                        row[key] = json.dumps(value)
                    else:
                        row[key] = value
                writer.writerow(row)
        
        logger.info(f"Saved {len(data)} records to {filename}")
    
    def save_to_json(self, data: List[Any], filename: str) -> None:
        """Save data to JSON file"""
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert dataclass objects to dictionaries
        json_data = [asdict(item) for item in data]
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(json_data, jsonfile, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(data)} records to {filename}")
    
    def generate_all_data(self, 
                         stations_count: int = 15,
                         trains_count: int = 25,
                         infrastructure_count: int = 20,
                         disruptions_count: int = 5) -> Dict[str, List[Any]]:
        """Generate all sample data"""
        logger.info("Starting comprehensive data generation...")
        
        # Generate all data types
        stations = self.generate_stations(stations_count)
        trains = self.generate_trains(trains_count)
        infrastructure = self.generate_infrastructure(infrastructure_count)
        disruptions = self.generate_disruptions(disruptions_count)
        
        # Save to files
        self.save_to_csv(stations, "stations.csv")
        self.save_to_csv(trains, "trains.csv")
        self.save_to_csv(infrastructure, "infrastructure.csv")
        self.save_to_csv(disruptions, "disruptions.csv")
        
        self.save_to_json(stations, "stations.json")
        self.save_to_json(trains, "trains.json")
        self.save_to_json(infrastructure, "infrastructure.json")
        self.save_to_json(disruptions, "disruptions.json")
        
        # Create a combined dataset
        combined_data = {
            "stations": [asdict(s) for s in stations],
            "trains": [asdict(t) for t in trains],
            "infrastructure": [asdict(i) for i in infrastructure],
            "disruptions": [asdict(d) for d in disruptions],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "stations_count": len(stations),
                "trains_count": len(trains),
                "infrastructure_count": len(infrastructure),
                "disruptions_count": len(disruptions),
                "generator_version": "1.0.0"
            }
        }
        
        combined_filepath = os.path.join(self.output_dir, "railway_data.json")
        with open(combined_filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(combined_data, jsonfile, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved combined dataset to railway_data.json")
        
        return {
            "stations": stations,
            "trains": trains,
            "infrastructure": infrastructure,
            "disruptions": disruptions
        }
    
    def create_scenario_data(self, scenario: str) -> Dict[str, List[Any]]:
        """Create data for specific scenarios"""
        logger.info(f"Generating scenario: {scenario}")
        
        if scenario == "rush_hour":
            return self.generate_all_data(
                stations_count=20,
                trains_count=50,
                infrastructure_count=25,
                disruptions_count=8
            )
        elif scenario == "maintenance":
            return self.generate_all_data(
                stations_count=10,
                trains_count=15,
                infrastructure_count=15,
                disruptions_count=12
            )
        elif scenario == "minimal":
            return self.generate_all_data(
                stations_count=5,
                trains_count=8,
                infrastructure_count=10,
                disruptions_count=2
            )
        else:
            return self.generate_all_data()

def main():
    """Main function to generate sample data"""
    print("🚆 RailOptima Sample Data Generator")
    print("=" * 50)
    
    generator = RailwayDataGenerator()
    
    # Generate default dataset
    print("\n📊 Generating default dataset...")
    data = generator.generate_all_data()
    
    print(f"\n✅ Generated:")
    print(f"   📍 Stations: {len(data['stations'])}")
    print(f"   🚂 Trains: {len(data['trains'])}")
    print(f"   🏗️ Infrastructure: {len(data['infrastructure'])}")
    print(f"   ⚠️ Disruptions: {len(data['disruptions'])}")
    
    # Generate scenario datasets
    scenarios = ["rush_hour", "maintenance", "minimal"]
    for scenario in scenarios:
        print(f"\n🎭 Generating {scenario} scenario...")
        scenario_dir = f"support/Sample Data Preparation/scenarios/{scenario}"
        os.makedirs(scenario_dir, exist_ok=True)
        
        scenario_generator = RailwayDataGenerator(output_dir=scenario_dir)
        scenario_data = scenario_generator.create_scenario_data(scenario)
        
        print(f"   📍 Stations: {len(scenario_data['stations'])}")
        print(f"   🚂 Trains: {len(scenario_data['trains'])}")
        print(f"   🏗️ Infrastructure: {len(scenario_data['infrastructure'])}")
        print(f"   ⚠️ Disruptions: {len(scenario_data['disruptions'])}")
    
    print(f"\n🎉 All sample data generated successfully!")
    print(f"📁 Files saved to: {generator.output_dir}")

if __name__ == "__main__":
    main()
