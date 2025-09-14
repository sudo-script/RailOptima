#!/usr/bin/env python3
"""
Test script to verify API integration with optimizer data
This script tests the complete data flow from optimizer files to API endpoints
"""

import requests
import json
import time
import sys
import os

# API base URL
API_BASE_URL = "http://localhost:8000"

def test_api_connection():
    """Test basic API connectivity"""
    print("🔍 Testing API connection...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running and accessible")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def test_optimizer_status():
    """Test optimizer integration status"""
    print("\n🔍 Testing optimizer integration status...")
    try:
        response = requests.get(f"{API_BASE_URL}/optimizer/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Optimizer status endpoint working")
            print(f"   Schedule data loaded: {data['optimizer_integration']['schedule_data_loaded']}")
            print(f"   Audit data loaded: {data['optimizer_integration']['audit_data_loaded']}")
            print(f"   Conflict data loaded: {data['optimizer_integration']['conflict_data_loaded']}")
            print(f"   Visualization data loaded: {data['optimizer_integration']['visualization_data_loaded']}")
            return True
        else:
            print(f"❌ Optimizer status returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing optimizer status: {e}")
        return False

def test_optimizer_schedule():
    """Test optimized schedule data endpoint"""
    print("\n🔍 Testing optimized schedule endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/optimizer/schedule", timeout=10)
        if response.status_code == 200:
            data = response.json()
            schedule_items = data.get('schedule_data', {}).get('schedule', [])
            print(f"✅ Optimized schedule endpoint working - {len(schedule_items)} schedule items")
            if schedule_items:
                print(f"   Sample train: {schedule_items[0].get('train_id', 'N/A')}")
            return True
        else:
            print(f"❌ Optimized schedule returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing optimized schedule: {e}")
        return False

def test_trains_endpoint():
    """Test trains endpoint with real data"""
    print("\n🔍 Testing trains endpoint with real data...")
    try:
        response = requests.get(f"{API_BASE_URL}/trains", timeout=10)
        if response.status_code == 200:
            trains = response.json()
            print(f"✅ Trains endpoint working - {len(trains)} trains")
            if trains:
                sample_train = trains[0]
                print(f"   Sample train: {sample_train.get('id', 'N/A')} - {sample_train.get('name', 'N/A')}")
                print(f"   Status: {sample_train.get('status', 'N/A')}, Delay: {sample_train.get('delay', 0)} min")
            return True
        else:
            print(f"❌ Trains endpoint returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing trains endpoint: {e}")
        return False

def test_audit_endpoint():
    """Test audit report endpoint"""
    print("\n🔍 Testing audit report endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/audit/report", timeout=10)
        if response.status_code == 200:
            data = response.json()
            audit_records = data.get('audit_data', [])
            print(f"✅ Audit report endpoint working - {len(audit_records)} audit records")
            return True
        else:
            print(f"❌ Audit report returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing audit report: {e}")
        return False

def test_conflicts_endpoint():
    """Test conflicts endpoint"""
    print("\n🔍 Testing conflicts endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/optimizer/conflicts", timeout=10)
        if response.status_code == 200:
            data = response.json()
            conflicts = data.get('conflicts', [])
            print(f"✅ Conflicts endpoint working - {len(conflicts)} conflicts")
            return True
        else:
            print(f"❌ Conflicts endpoint returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing conflicts endpoint: {e}")
        return False

def test_visualization_endpoint():
    """Test visualization reports endpoint"""
    print("\n🔍 Testing visualization reports endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/visualization/reports", timeout=10)
        if response.status_code == 200:
            data = response.json()
            viz_data = data.get('visualization_data', {})
            files = viz_data.get('files', [])
            print(f"✅ Visualization reports endpoint working - {len(files)} files")
            if files:
                print(f"   Available files: {', '.join(files[:3])}{'...' if len(files) > 3 else ''}")
            return True
        else:
            print(f"❌ Visualization reports returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing visualization reports: {e}")
        return False

def test_data_reload():
    """Test data reload functionality"""
    print("\n🔍 Testing data reload functionality...")
    try:
        response = requests.post(f"{API_BASE_URL}/optimizer/reload", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print("✅ Data reload endpoint working")
            print(f"   Schedule items: {data['data_counts']['schedule_items']}")
            print(f"   Audit records: {data['data_counts']['audit_records']}")
            print(f"   Conflicts: {data['data_counts']['conflicts']}")
            print(f"   Visualization files: {data['data_counts']['visualization_files']}")
            return True
        else:
            print(f"❌ Data reload returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing data reload: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 RailOptima API Integration Test")
    print("=" * 50)
    
    # Check if API is running
    if not test_api_connection():
        print("\n❌ API is not running. Please start the API server first.")
        print("   Run: python support/api_support/api_stub.py")
        sys.exit(1)
    
    # Run all tests
    tests = [
        test_optimizer_status,
        test_optimizer_schedule,
        test_trains_endpoint,
        test_audit_endpoint,
        test_conflicts_endpoint,
        test_visualization_endpoint,
        test_data_reload
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API integration is working correctly.")
        print("\n📋 Available endpoints:")
        print("   • /trains - Real train data from optimizer")
        print("   • /optimizer/schedule - Optimized schedule data")
        print("   • /optimizer/conflicts - Conflict detection results")
        print("   • /audit/report - Audit and validation data")
        print("   • /visualization/reports - Visualization files")
        print("   • /optimizer/status - Integration status")
        print("   • /optimizer/reload - Reload data from files")
    else:
        print("⚠️  Some tests failed. Check the API logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
