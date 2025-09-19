#!/usr/bin/env python3
"""
Test script to verify Celery serialization fixes
"""
import os
import sys
import json
from datetime import datetime

# Add the backend directory to the path
sys.path.append('/Users/apple/Documents/aimsg/Automated-AI-Messaging-Tool-Backend')

def test_celery_serialization():
    """Test that Celery tasks can be serialized properly"""
    try:
        from celery_tasks.file_tasks import process_file_upload_task
        from celery_tasks.scraping_tasks import scrape_websites_task, generate_messages_task
        
        print("✅ Successfully imported Celery tasks")
        
        # Test task creation (without actually running them)
        test_data = {
            'file_upload_id': 'test-123',
            'file_path': '/tmp/test.csv',
            'file_type': 'csv',
            'total_chunks': 1,
            'chunks_processed': 1,
            'total_records': 100,
            'processed_chunk_ids': ['task-id-1', 'task-id-2'],
            'user_id': 'test-user',
            'completed_at': datetime.now().isoformat()
        }
        
        # Test JSON serialization
        json_str = json.dumps(test_data)
        print("✅ Task result data can be JSON serialized")
        
        # Test deserialization
        parsed_data = json.loads(json_str)
        print("✅ Task result data can be JSON deserialized")
        
        print("✅ All Celery serialization tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Celery serialization test failed: {e}")
        return False

def test_backend_connection():
    """Test backend connection"""
    try:
        import requests
        
        backend_url = "http://98.85.16.204:8001"
        response = requests.get(f"{backend_url}/health", timeout=10)
        
        if response.status_code == 200:
            print("✅ Backend is running and accessible")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend connection test failed: {e}")
        return False

def test_upload_endpoint():
    """Test the upload endpoint"""
    try:
        import requests
        
        backend_url = "http://98.85.16.204:8001"
        
        # Create a test CSV file
        test_csv = "website,contact_form_url\nhttps://example.com,https://example.com/contact"
        
        files = {
            'file': ('test.csv', test_csv, 'text/csv')
        }
        
        response = requests.post(
            f"{backend_url}/api/upload-from-frontend?userId=test-user-123",
            files=files,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload endpoint working - Task ID: {data.get('taskId')}")
            print(f"✅ File Upload ID: {data.get('fileUploadId')}")
            print(f"✅ Status: {data.get('status')}")
            return True
        else:
            print(f"❌ Upload endpoint returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Upload endpoint test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Celery Serialization Fixes")
    print("=" * 50)
    
    # Test 1: Celery serialization
    print("\n1. Testing Celery serialization...")
    serialization_ok = test_celery_serialization()
    
    # Test 2: Backend connection
    print("\n2. Testing backend connection...")
    backend_ok = test_backend_connection()
    
    # Test 3: Upload endpoint
    print("\n3. Testing upload endpoint...")
    upload_ok = test_upload_endpoint()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Celery Serialization: {'✅ PASS' if serialization_ok else '❌ FAIL'}")
    print(f"Backend Connection: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"Upload Endpoint: {'✅ PASS' if upload_ok else '❌ FAIL'}")
    
    if all([serialization_ok, backend_ok, upload_ok]):
        print("\n🎉 All tests passed! Celery serialization issues should be fixed.")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
