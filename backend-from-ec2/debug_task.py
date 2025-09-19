#!/usr/bin/env python3

import traceback
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from celery_worker import process_chunk_task
    print("Successfully imported process_chunk_task")
    
    # Test parameters
    chunk_id = 'cmceg6a0y0008sbgsjvow752a'
    chunk_number = 1
    start_row = 1
    end_row = 5
    file_path = '/Users/apple/Downloads/AIMessanging/uploads/cmcd4l1a40002sb81o01rysma/1751006691333_sample_websites_small.csv'
    file_type = 'csv'
    user_id = 'cmcd4l1a40002sb81o01rysma'
    
    print(f"Testing with parameters:")
    print(f"  chunk_id: {chunk_id}")
    print(f"  chunk_number: {chunk_number}")
    print(f"  start_row: {start_row}")
    print(f"  end_row: {end_row}")
    print(f"  file_path: {file_path}")
    print(f"  file_type: {file_type}")
    print(f"  user_id: {user_id}")
    
    # Check if file exists
    if os.path.exists(file_path):
        print(f"File exists: {file_path}")
        print(f"File size: {os.path.getsize(file_path)} bytes")
    else:
        print(f"File does not exist: {file_path}")
        sys.exit(1)
    
    # Try to call the function
    print("\nCalling process_chunk_task...")
    result = process_chunk_task(chunk_id, chunk_number, start_row, end_row, file_path, file_type, user_id)
    print(f"Success! Result: {result}")
    
except Exception as e:
    print(f"Error occurred: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1) 