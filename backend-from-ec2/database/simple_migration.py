#!/usr/bin/env python3
"""
Simple Migration Script
Adds enhanced status tracking columns to existing database
"""
import psycopg2

def migrate_database():
    try:
        print("Starting database migration...")
        
        # Connect to database
        conn = psycopg2.connect(
            host="localhost",
            database="ai_messaging_db",
            user="xb3353",
            password="password"
        )
        cursor = conn.cursor()
        
        print("✅ Connected to database")
        
        # Add new columns to websites table
        print("Adding columns to websites table...")
        website_columns = [
            'ALTER TABLE websites ADD COLUMN IF NOT EXISTS "submissionStatus" VARCHAR(50) DEFAULT \'PENDING\'',
            'ALTER TABLE websites ADD COLUMN IF NOT EXISTS "messageGenerationError" TEXT',
            'ALTER TABLE websites ADD COLUMN IF NOT EXISTS "submissionError" TEXT',
            'ALTER TABLE websites ADD COLUMN IF NOT EXISTS "submittedFormFields" JSONB',
            'ALTER TABLE websites ADD COLUMN IF NOT EXISTS "submissionResponse" TEXT'
        ]
        
        for query in website_columns:
            cursor.execute(query)
            print(f"✅ Added column to websites table")
        
        # Add new columns to contact_inquiries table
        print("Adding columns to contact_inquiries table...")
        contact_columns = [
            'ALTER TABLE contact_inquiries ADD COLUMN IF NOT EXISTS "submittedFormFields" JSONB',
            'ALTER TABLE contact_inquiries ADD COLUMN IF NOT EXISTS "submissionError" TEXT',
            'ALTER TABLE contact_inquiries ADD COLUMN IF NOT EXISTS "retryCount" INTEGER DEFAULT 0',
            'ALTER TABLE contact_inquiries ADD COLUMN IF NOT EXISTS "lastRetryAt" TIMESTAMP'
        ]
        
        for query in contact_columns:
            cursor.execute(query)
            print(f"✅ Added column to contact_inquiries table")
        
        # Update existing records
        print("Updating existing records...")
        cursor.execute('UPDATE websites SET "submissionStatus" = \'PENDING\' WHERE "submissionStatus" IS NULL')
        cursor.execute('UPDATE websites SET "messageStatus" = \'PENDING\' WHERE "messageStatus" IS NULL')
        
        # Commit changes
        conn.commit()
        print("✅ Migration completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_database()
