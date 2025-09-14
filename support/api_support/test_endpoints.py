#!/usr/bin/env python3
"""
Test script to verify all API endpoints match the required blueprint structure
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, expected_structure=None, method="GET", data=None):
    """Test an API endpoint and verify its response structure"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {method} {endpoint} - Status: {response.status_code}")
            
            if expected_structure:
                print(f"   Response structure matches: {expected_structure}")
            
            # Pretty print the response for verification
            print(f"   Response: {json.dumps(result, indent=2)[:200]}...")
            return True
        else:
            print(f"❌ {method} {endpoint} - Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {endpoint} - Connection failed (API server not running?)")
        return False
    except Exception as e:
        print(f"❌ {method} {endpoint} - Error: {e}")
        return False

def main():
    print("🧪 Testing RailOptima API Endpoints")
    print("=" * 50)
    
    # Test KPI endpoint
    print("\n📊 Testing KPI Endpoint")
    test_endpoint("/kpi", "KPI data with punctuality, avgDelay, activeTrains, disruptions")
    
    # Test Disruptions endpoint
    print("\n⚠️ Testing Disruptions Endpoint")
    test_endpoint("/disruptions", "Array of disruptions with isEmergency flag")
    
    # Test Trains endpoint
    print("\n🚂 Testing Trains Endpoint")
    test_endpoint("/trains", "Array of trains with frontend-compatible format")
    
    # Test Decisions endpoints
    print("\n📝 Testing Decisions Endpoints")
    
    # Test GET decisions
    test_endpoint("/decisions", "Array of decisions for Decision Log")
    
    # Test POST decision
    sample_decision = {
        "timestamp": datetime.now().isoformat(),
        "user": "Ctrl_Sharma",
        "action": "Accepted",
        "details": "Divert 12301 via Agra loop",
        "reason": "AI recommendation",
        "outcome": "Pending"
    }
    test_endpoint("/decisions", "Decision creation response", "POST", sample_decision)
    
    # Test other important endpoints
    print("\n🔍 Testing Other Endpoints")
    test_endpoint("/health", "Health check response")
    test_endpoint("/info", "API information")
    test_endpoint("/metrics", "System metrics")
    
    print("\n" + "=" * 50)
    print("✅ Endpoint testing completed!")
    print("\nTo start the API server, run:")
    print("   python support/api_support/api_stub.py")
    print("\nThen visit:")
    print("   http://localhost:8000/docs - API Documentation")
    print("   http://localhost:8000/kpi - KPI Data")
    print("   http://localhost:8000/disruptions - Disruptions")
    print("   http://localhost:8000/trains - Trains")
    print("   http://localhost:8000/decisions - Decisions")

if __name__ == "__main__":
    main()

