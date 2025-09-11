"""
RailOptima Sample Data System Demo
Demonstrates the complete sample data preparation and API integration system.
"""

import requests
import time
import json
import sys
import os

# Add the support directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__)))
try:
    from Sample_Data_Preparation.data_loader import load_sample_data, get_available_scenarios
    from Sample_Data_Preparation.sample_data_generator import RailwayDataGenerator
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'Sample Data Preparation'))
    from data_loader import load_sample_data, get_available_scenarios
    from sample_data_generator import RailwayDataGenerator

def demo_data_generation():
    """Demonstrate data generation capabilities"""
    print("🚆 RailOptima Sample Data System Demo")
    print("=" * 60)
    
    print("\n📊 1. Data Generation Demo")
    print("-" * 30)
    
    # Create a small demo dataset
    generator = RailwayDataGenerator(output_dir="support/Sample Data Preparation/demo")
    demo_data = generator.generate_all_data(
        stations_count=5,
        trains_count=8,
        infrastructure_count=6,
        disruptions_count=3
    )
    
    print(f"✅ Generated demo dataset:")
    print(f"   📍 Stations: {len(demo_data['stations'])}")
    print(f"   🚂 Trains: {len(demo_data['trains'])}")
    print(f"   🏗️ Infrastructure: {len(demo_data['infrastructure'])}")
    print(f"   ⚠️ Disruptions: {len(demo_data['disruptions'])}")
    
    # Show sample data
    if demo_data['trains']:
        sample_train = demo_data['trains'][0]
        print(f"\n🚂 Sample Train: {sample_train.name}")
        print(f"   Route: {sample_train.route}")
        print(f"   Type: {sample_train.train_type}")
        print(f"   Operator: {sample_train.operator}")
    
    if demo_data['stations']:
        sample_station = demo_data['stations'][0]
        print(f"\n📍 Sample Station: {sample_station.name}")
        print(f"   Location: {sample_station.location}")
        print(f"   Capacity: {sample_station.capacity}")
        print(f"   Type: {sample_station.station_type}")

def demo_data_loading():
    """Demonstrate data loading capabilities"""
    print("\n📥 2. Data Loading Demo")
    print("-" * 30)
    
    # Load default data
    print("🔍 Loading default data...")
    default_data = load_sample_data()
    print(f"✅ Default data loaded:")
    print(f"   📍 Stations: {len(default_data['stations'])}")
    print(f"   🚂 Trains: {len(default_data['trains'])}")
    print(f"   🏗️ Infrastructure: {len(default_data['infrastructure'])}")
    print(f"   ⚠️ Disruptions: {len(default_data['disruptions'])}")
    
    # Show available scenarios
    scenarios = get_available_scenarios()
    print(f"\n🎭 Available scenarios: {scenarios}")
    
    # Load each scenario
    for scenario in scenarios:
        print(f"\n📋 Loading {scenario} scenario...")
        scenario_data = load_sample_data(scenario)
        print(f"   📍 Stations: {len(scenario_data['stations'])}")
        print(f"   🚂 Trains: {len(scenario_data['trains'])}")
        print(f"   🏗️ Infrastructure: {len(scenario_data['infrastructure'])}")
        print(f"   ⚠️ Disruptions: {len(scenario_data['disruptions'])}")

def demo_api_integration():
    """Demonstrate API integration"""
    print("\n🌐 3. API Integration Demo")
    print("-" * 30)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test API connectivity
        print("🔗 Testing API connectivity...")
        response = requests.get(f"{base_url}/", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {data['status']}")
            print(f"📊 Current Scenario: {data['current_scenario']}")
            print(f"🎭 Available Scenarios: {data['available_scenarios']}")
            
            # Test data endpoints
            print(f"\n📊 Testing data endpoints...")
            
            # Trains
            response = requests.get(f"{base_url}/trains")
            if response.status_code == 200:
                trains = response.json()
                print(f"✅ Trains: {len(trains)} loaded")
                if trains:
                    print(f"   Sample: {trains[0]['name']} ({trains[0]['id']})")
            
            # Stations
            response = requests.get(f"{base_url}/stations")
            if response.status_code == 200:
                stations = response.json()
                print(f"✅ Stations: {len(stations)} loaded")
                if stations:
                    print(f"   Sample: {stations[0]['name']} ({stations[0]['id']})")
            
            # Test scenario switching
            scenarios = data['available_scenarios']
            if scenarios:
                print(f"\n🔄 Testing scenario switching...")
                scenario = scenarios[0]
                response = requests.post(f"{base_url}/scenarios/{scenario}/load")
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Switched to '{scenario}' scenario")
                    print(f"   📊 Data counts: {result['data_counts']}")
            
            # Test metrics
            print(f"\n📈 Testing metrics endpoint...")
            response = requests.get(f"{base_url}/metrics")
            if response.status_code == 200:
                metrics = response.json()
                print(f"✅ Metrics retrieved:")
                print(f"   🚂 Trains: {metrics['trains']['total']} total, {metrics['trains']['delayed']} delayed")
                print(f"   📍 Stations: {metrics['stations']['total']} total, {metrics['stations']['operational']} operational")
                print(f"   ⚠️ Disruptions: {metrics['disruptions']['active']} active")
            
        else:
            print(f"❌ API not responding: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running:")
        print("   python support/api_support/api_stub.py")
    except Exception as e:
        print(f"❌ API test failed: {e}")

def demo_scenario_comparison():
    """Demonstrate scenario differences"""
    print("\n📊 4. Scenario Comparison Demo")
    print("-" * 30)
    
    scenarios = get_available_scenarios()
    scenario_data = {}
    
    # Load all scenarios
    for scenario in scenarios:
        scenario_data[scenario] = load_sample_data(scenario)
    
    # Compare scenarios
    print("📋 Scenario Comparison:")
    print(f"{'Scenario':<12} {'Stations':<8} {'Trains':<8} {'Infrastructure':<12} {'Disruptions':<10}")
    print("-" * 60)
    
    # Default scenario
    default_data = load_sample_data()
    print(f"{'default':<12} {len(default_data['stations']):<8} {len(default_data['trains']):<8} {len(default_data['infrastructure']):<12} {len(default_data['disruptions']):<10}")
    
    # Other scenarios
    for scenario, data in scenario_data.items():
        print(f"{scenario:<12} {len(data['stations']):<8} {len(data['trains']):<8} {len(data['infrastructure']):<12} {len(data['disruptions']):<10}")
    
    # Analyze train types
    print(f"\n🚂 Train Type Analysis:")
    for scenario, data in scenario_data.items():
        train_types = {}
        for train in data['trains']:
            train_type = train.get('train_type', 'Unknown')
            train_types[train_type] = train_types.get(train_type, 0) + 1
        
        print(f"\n{scenario.title()} Scenario:")
        for train_type, count in train_types.items():
            print(f"   {train_type}: {count}")

def demo_data_export():
    """Demonstrate data export capabilities"""
    print("\n📤 5. Data Export Demo")
    print("-" * 30)
    
    # Load data
    data = load_sample_data()
    
    # Create sample export
    export_data = {
        "export_info": {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "scenario": "default",
            "total_records": len(data['stations']) + len(data['trains']) + len(data['infrastructure']) + len(data['disruptions'])
        },
        "summary": {
            "stations": len(data['stations']),
            "trains": len(data['trains']),
            "infrastructure": len(data['infrastructure']),
            "disruptions": len(data['disruptions'])
        },
        "sample_data": {
            "sample_train": data['trains'][0] if data['trains'] else None,
            "sample_station": data['stations'][0] if data['stations'] else None
        }
    }
    
    # Save export
    export_file = "support/Sample Data Preparation/demo_export.json"
    with open(export_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, default=str)
    
    print(f"✅ Data export created: {export_file}")
    print(f"   📊 Total records: {export_data['export_info']['total_records']}")
    print(f"   📍 Stations: {export_data['summary']['stations']}")
    print(f"   🚂 Trains: {export_data['summary']['trains']}")
    print(f"   🏗️ Infrastructure: {export_data['summary']['infrastructure']}")
    print(f"   ⚠️ Disruptions: {export_data['summary']['disruptions']}")

def main():
    """Run the complete demo"""
    print("🎬 Starting RailOptima Sample Data System Demo...")
    
    # Run all demos
    demo_data_generation()
    demo_data_loading()
    demo_api_integration()
    demo_scenario_comparison()
    demo_data_export()
    
    print("\n🎉 Demo completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Start the API server: python support/api_support/api_stub.py")
    print("2. Test the API endpoints in your browser: http://localhost:8000")
    print("3. Try different scenarios: http://localhost:8000/scenarios")
    print("4. View the generated data files in: support/Sample Data Preparation/")
    
    print("\n🔗 Useful Endpoints:")
    print("   • http://localhost:8000/ - API information")
    print("   • http://localhost:8000/trains - All trains")
    print("   • http://localhost:8000/stations - All stations")
    print("   • http://localhost:8000/scenarios - Available scenarios")
    print("   • http://localhost:8000/metrics - System metrics")

if __name__ == "__main__":
    main()
