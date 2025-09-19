#!/usr/bin/env python3
"""
Debug why contact form submission didn't trigger
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database.database_manager import DatabaseManager
    
    print("=== DEBUGGING CONTACT FORM SUBMISSION ===")
    upload_id = "cmemj7am20001py12k738glci"
    print(f"Upload ID: {upload_id}")
    print()
    
    db = DatabaseManager()
    
    # Check the specific website that should have triggered contact form
    websites = db.get_websites_by_file_upload_id(upload_id)
    
    if websites:
        for website in websites:
            if website.get('websiteUrl') == 'https://www.arauto505.com/about-us/':
                print(f"🔍 DEBUGGING: {website['websiteUrl']}")
                print(f"  Message Status: {website.get('messageStatus')}")
                print(f"  Generated Message: {'YES' if website.get('generatedMessage') else 'NO'}")
                print(f"  Submission Status: {website.get('submissionStatus')}")
                print(f"  Submission Error: {website.get('submissionError')}")
                print(f"  Submitted Form Fields: {website.get('submittedFormFields')}")
                print(f"  Submission Response: {website.get('submissionResponse')}")
                print()
                
                # Check if this website has the new columns
                print("🔍 CHECKING DATABASE COLUMNS:")
                try:
                    connection = db.get_connection()
                    cursor = connection.cursor()
                    cursor.execute("""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = 'websites' 
                        AND column_name IN ('submissionStatus', 'submissionError', 'submittedFormFields', 'submissionResponse')
                        ORDER BY column_name
                    """)
                    columns = cursor.fetchall()
                    if columns:
                        print("  ✅ New columns found:")
                        for col in columns:
                            print(f"    - {col[0]}: {col[1]}")
                    else:
                        print("  ❌ New columns NOT found - database migration may be incomplete")
                    
                    cursor.close()
                    connection.close()
                except Exception as e:
                    print(f"  ❌ Error checking columns: {e}")
                
                break
    
    print("\n=== DEBUG COMPLETE ===")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
