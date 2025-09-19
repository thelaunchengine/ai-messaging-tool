#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database.database_manager import DatabaseManager
    
    print('=== DATABASE SCHEMA CHECK ===')
    print('Testing basic database connection...')
    
    db = DatabaseManager()
    cursor = db.get_connection().cursor()
    
    # Check available tables
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cursor.fetchall()
    
    print('Available tables:')
    for table in tables:
        print(f'- {table[0]}')
    
    print('\n=== CHECKING WEBSITES TABLE STRUCTURE ===')
    try:
        cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'websites' ORDER BY ordinal_position")
        columns = cursor.fetchall()
        print('Websites table columns:')
        for col in columns:
            print(f'- {col[0]}: {col[1]}')
    except Exception as e:
        print(f'Error checking websites table: {e}')
    
    print('\n=== CHECKING CONTACT_INQUIRIES TABLE STRUCTURE ===')
    try:
        cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'contact_inquiries' ORDER BY ordinal_position")
        columns = cursor.fetchall()
        print('Contact_inquiries table columns:')
        for col in columns:
            print(f'- {col[0]}: {col[1]}')
    except Exception as e:
        print(f'Error checking contact_inquiries table: {e}')
    
    cursor.close()
    print('\n=== SCHEMA CHECK COMPLETE ===')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
