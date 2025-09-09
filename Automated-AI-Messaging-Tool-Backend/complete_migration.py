#!/usr/bin/env python3
"""
Complete the database migration by adding missing columns
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database.database_manager import DatabaseManager
    
    print("=== COMPLETING DATABASE MIGRATION ===")
    print("Adding missing columns for contact form submission...")
    print()
    
    db = DatabaseManager()
    connection = db.get_connection()
    cursor = connection.cursor()
    
    # Check current columns
    print("🔍 CURRENT COLUMNS IN WEBSITES TABLE:")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'websites' 
        AND column_name LIKE '%submission%'
        ORDER BY column_name
    """)
    current_columns = cursor.fetchall()
    for col in current_columns:
        print(f"  ✅ {col[0]}: {col[1]}")
    
    print()
    
    # Add missing columns
    print("🔧 ADDING MISSING COLUMNS:")
    
    # Check if submittedFormFields column exists
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'websites' 
        AND column_name = 'submittedFormFields'
    """)
    if not cursor.fetchone():
        print("  ➕ Adding submittedFormFields column...")
        cursor.execute("""
            ALTER TABLE websites 
            ADD COLUMN "submittedFormFields" JSONB
        """)
        print("    ✅ submittedFormFields column added")
    else:
        print("  ✅ submittedFormFields column already exists")
    
    # Check if submissionResponse column exists
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'websites' 
        AND column_name = 'submissionResponse'
    """)
    if not cursor.fetchone():
        print("  ➕ Adding submissionResponse column...")
        cursor.execute("""
            ALTER TABLE websites 
            ADD COLUMN "submissionResponse" TEXT
        """)
        print("    ✅ submissionResponse column added")
    else:
        print("  ✅ submissionResponse column already exists")
    
    # Check if contact_inquiries table has all required columns
    print()
    print("🔍 CHECKING CONTACT_INQUIRIES TABLE:")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'contact_inquiries' 
        ORDER BY column_name
    """)
    contact_columns = cursor.fetchall()
    for col in contact_columns:
        print(f"  ✅ {col[0]}: {col[1]}")
    
    # Add missing columns to contact_inquiries if needed
    print()
    print("🔧 CHECKING FOR MISSING COLUMNS IN CONTACT_INQUIRIES:")
    
    required_contact_columns = [
        ('websiteId', 'TEXT'),
        ('fileUploadId', 'TEXT'),
        ('websiteUrl', 'TEXT'),
        ('submissionStatus', 'VARCHAR(50)'),
        ('submissionError', 'TEXT'),
        ('submittedFormFields', 'JSONB'),
        ('submissionResponse', 'TEXT'),
        ('retryCount', 'INTEGER'),
        ('lastRetryAt', 'TIMESTAMP')
    ]
    
    for col_name, col_type in required_contact_columns:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'contact_inquiries' 
            AND column_name = %s
        """, (col_name,))
        if not cursor.fetchone():
            print(f"  ➕ Adding {col_name} column...")
            cursor.execute(f"""
                ALTER TABLE contact_inquiries 
                ADD COLUMN "{col_name}" {col_type}
            """)
            print(f"    ✅ {col_name} column added")
        else:
            print(f"  ✅ {col_name} column already exists")
    
    # Set default values for existing records
    print()
    print("🔧 SETTING DEFAULT VALUES FOR EXISTING RECORDS:")
    
    # Update websites table
    cursor.execute("""
        UPDATE websites 
        SET "submissionStatus" = 'PENDING' 
        WHERE "submissionStatus" IS NULL
    """)
    websites_updated = cursor.rowcount
    print(f"  ✅ Updated {websites_updated} websites with default submissionStatus")
    
    # Update contact_inquiries table
    cursor.execute("""
        UPDATE contact_inquiries 
        SET "submissionStatus" = 'PENDING' 
        WHERE "submissionStatus" IS NULL
    """)
    inquiries_updated = cursor.rowcount
    print(f"  ✅ Updated {inquiries_updated} contact inquiries with default submissionStatus")
    
    # Commit changes
    connection.commit()
    
    print()
    print("🔍 VERIFICATION - FINAL COLUMN STATUS:")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'websites' 
        AND column_name LIKE '%submission%'
        ORDER BY column_name
    """)
    final_columns = cursor.fetchall()
    for col in final_columns:
        print(f"  ✅ {col[0]}: {col[1]}")
    
    cursor.close()
    connection.close()
    
    print()
    print("=== MIGRATION COMPLETED SUCCESSFULLY! ===")
    print("✅ All required columns added")
    print("✅ Default values set for existing records")
    print("✅ Database ready for contact form submission")
    
except Exception as e:
    print(f"❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()
