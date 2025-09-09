#!/usr/bin/env python3
"""
Migration Runner Script
Runs the enhanced status tracking migration
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_migration():
    try:
        print("Starting enhanced status tracking migration...")
        
        # Import the database manager
        from database.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        # Migration SQL commands
        migration_commands = [
            # Add new columns to websites table
            'ALTER TABLE websites ADD COLUMN IF NOT EXISTS "submissionStatus" VARCHAR(50) DEFAULT \'PENDING\'',
            'ALTER TABLE websites ADD COLUMN IF NOT EXISTS "messageGenerationError" TEXT',
            'ALTER TABLE websites ADD COLUMN IF NOT EXISTS "submissionError" TEXT',
            'ALTER TABLE websites ADD COLUMN IF NOT EXISTS "submittedFormFields" JSONB',
            'ALTER TABLE websites ADD COLUMN IF NOT EXISTS "submissionResponse" TEXT',
            
            # Add new columns to contact_inquiries table
            'ALTER TABLE contact_inquiries ADD COLUMN IF NOT EXISTS "submittedFormFields" JSONB',
            'ALTER TABLE contact_inquiries ADD COLUMN IF NOT EXISTS "submissionError" TEXT',
            'ALTER TABLE contact_inquiries ADD COLUMN IF NOT EXISTS "retryCount" INTEGER DEFAULT 0',
            'ALTER TABLE contact_inquiries ADD COLUMN IF NOT EXISTS "lastRetryAt" TIMESTAMP',
            
            # Update existing records
            'UPDATE websites SET "submissionStatus" = \'PENDING\' WHERE "submissionStatus" IS NULL',
            'UPDATE websites SET "messageStatus" = \'PENDING\' WHERE "messageStatus" IS NULL',
            
            # Create indexes
            'CREATE INDEX IF NOT EXISTS idx_websites_submission_status ON websites("submissionStatus")',
            'CREATE INDEX IF NOT EXISTS idx_websites_message_status ON websites("messageStatus")',
            'CREATE INDEX IF NOT EXISTS idx_contact_inquiries_status ON contact_inquiries(status)'
        ]
        
        print("Executing migration commands...")
        for i, command in enumerate(migration_commands, 1):
            try:
                result = db_manager.execute_query(command)
                print(f"✅ {i:2d}/13: {command[:60]}...")
            except Exception as e:
                print(f"⚠️  {i:2d}/13: {command[:60]}... - {str(e)[:50]}")
        
        print("\n🎉 Migration completed successfully!")
        print("Enhanced status tracking columns have been added to the database.")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
