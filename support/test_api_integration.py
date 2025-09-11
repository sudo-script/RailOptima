"""
Test script to verify API integration with sample data
"""

import requests
import json
import time
import sys
import os

# Add the support directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__)))
try:
    from Sample_Data_Preparation.data_loader import load_sample_data, get_available_scenarios
except ImportError:
    # Fallback for different path structures
    sys.path.append(os.path.join(os.path.dirname(__file__), 'Sample Data Preparation'))
    from data_loader import load_sample_data, get_available_scenarios

def test_api_endpoints():
    """Test the API endpoints with sample data"""
    base_url = "http://localhost:8000"
    
    print("🚆 Testing RailOptima API with Sample Data")
    print("=" * 50)
    
    # Wait for API to start
    print("⏳ Waiting for API to start...")
    time.sleep(3)
    
    try:
        # Test root endpoint
        print("\n📋 Testing root endpoint...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {data['status']}")
            print(f"📊 Current Scenario: {data['current_scenario']}")
            print(f"🎭 Available Scenarios: {data['available_scenarios']}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return
        
        # Test scenarios endpoint
        print("\n🎭 Testing scenarios endpoint...")
        response = requests.get(f"{base_url}/scenarios")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Available scenarios: {data['available_scenarios']}")
            print(f"📊 Current scenario: {data['current_scenario']}")
        else:
            print(f"❌ Scenarios endpoint failed: {response.status_code}")
        
        # Test data summary
        print("\n📊 Testing data summary...")
        response = requests.get(f"{base_url}/data/summary")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Data Summary:")
            print(f"   📍 Stations: {data['data_counts']['stations']}")
            print(f"   🚂 Trains: {data['data_counts']['trains']}")
            print(f"   🏗️ Infrastructure: {data['data_counts']['infrastructure']}")
            print(f"   ⚠️ Disruptions: {data['data_counts']['disruptions']}")
        else:
            print(f"❌ Data summary failed: {response.status_code}")
        
        # Test trains endpoint
        print("\n🚂 Testing trains endpoint...")
        response = requests.get(f"{base_url}/trains")
        if response.status_code == 200:
            trains = response.json()
            print(f"✅ Loaded {len(trains)} trains")
            if trains:
                print(f"   Sample train: {trains[0]['name']} ({trains[0]['id']})")
        else:
            print(f"❌ Trains endpoint failed: {response.status_code}")
        
        # Test stations endpoint
        print("\n📍 Testing stations endpoint...")
        response = requests.get(f"{base_url}/stations")
        if response.status_code == 200:
            stations = response.json()
            print(f"✅ Loaded {len(stations)} stations")
            if stations:
                print(f"   Sample station: {stations[0]['name']} ({stations[0]['id']})")
        else:
            print(f"❌ Stations endpoint failed: {response.status_code}")
        
        # Test infrastructure endpoint
        print("\n🏗️ Testing infrastructure endpoint...")
        response = requests.get(f"{base_url}/infrastructure")
        if response.status_code == 200:
            infrastructure = response.json()
            print(f"✅ Loaded {len(infrastructure)} infrastructure components")
            if infrastructure:
                print(f"   Sample infrastructure: {infrastructure[0]['type']} ({infrastructure[0]['id']})")
        else:
            print(f"❌ Infrastructure endpoint failed: {response.status_code}")
        
        # Test disruptions endpoint
        print("\n⚠️ Testing disruptions endpoint...")
        response = requests.get(f"{base_url}/disruptions")
        if response.status_code == 200:
            disruptions = response.json()
            print(f"✅ Loaded {len(disruptions)} disruptions")
            if disruptions:
                print(f"   Sample disruption: {disruptions[0]['type']} ({disruptions[0]['id']})")
        else:
            print(f"❌ Disruptions endpoint failed: {response.status_code}")
        
        # Test scenario loading
        scenarios = get_available_scenarios()
        if scenarios:
            print(f"\n🔄 Testing scenario loading...")
            scenario = scenarios[0]
            response = requests.post(f"{base_url}/scenarios/{scenario}/load")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Loaded scenario '{scenario}' successfully")
                print(f"   📊 Data counts: {data['data_counts']}")
            else:
                print(f"❌ Scenario loading failed: {response.status_code}")
        
        # Test health endpoint
        print("\n🏥 Testing health endpoint...")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
        
        # Test metrics endpoint
        print("\n📈 Testing metrics endpoint...")
        response = requests.get(f"{base_url}/metrics")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Metrics retrieved successfully")
            print(f"   🚂 Trains: {data['trains']['total']} total, {data['trains']['delayed']} delayed")
            print(f"   📍 Stations: {data['stations']['total']} total, {data['stations']['operational']} operational")
        else:
            print(f"❌ Metrics endpoint failed: {response.status_code}")
        
        print("\n🎉 API integration test completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

def test_data_loader():
    """Test the data loader directly"""
    print("\n📊 Testing Data Loader Directly")
    print("=" * 40)
    
    try:
        # Test loading default data
        print("🔍 Loading default data...")
        default_data = load_sample_data()
        print(f"✅ Default data loaded:")
        print(f"   📍 Stations: {len(default_data['stations'])}")
        print(f"   🚂 Trains: {len(default_data['trains'])}")
        print(f"   🏗️ Infrastructure: {len(default_data['infrastructure'])}")
        print(f"   ⚠️ Disruptions: {len(default_data['disruptions'])}")
        
        # Test loading scenario data
        scenarios = get_available_scenarios()
        print(f"\n🎭 Available scenarios: {scenarios}")
        
        for scenario in scenarios[:2]:  # Test first 2 scenarios
            print(f"\n📋 Testing {scenario} scenario...")
            scenario_data = load_sample_data(scenario)
            print(f"   📍 Stations: {len(scenario_data['stations'])}")
            print(f"   🚂 Trains: {len(scenario_data['trains'])}")
            print(f"   🏗️ Infrastructure: {len(scenario_data['infrastructure'])}")
            print(f"   ⚠️ Disruptions: {len(scenario_data['disruptions'])}")
        
        print("\n✅ Data loader test completed successfully!")
        
    except Exception as e:
        print(f"❌ Data loader test failed: {e}")

if __name__ == "__main__":
    # Test data loader first
    test_data_loader()
    
    # Test API integration
    test_api_endpoints()
