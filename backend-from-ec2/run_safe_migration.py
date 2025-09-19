#!/usr/bin/env python3
"""
Safe Database Migration Script
Adds new contact form tables and columns WITHOUT modifying existing data
"""

import sys
import os
import logging
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_safe_migration():
    """Run the safe database migration"""
    
    try:
        logger.info("🚀 Starting SAFE database migration...")
        logger.info("⚠️  This migration will ONLY ADD new structures")
        logger.info("⚠️  NO existing data will be modified or deleted")
        
        # Import database manager
        from database.database_manager import DatabaseManager
        
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Ensure connection
        db_manager._ensure_connection()
        
        logger.info("✅ Database connection established")
        
        # Step 1: Add new columns to websites table (SAFE - only adds if not exists)
        logger.info("🔧 Step 1: Adding new columns to websites table...")
        
        try:
            # Add submissionStatus column
            db_manager.cursor.execute("""
                ALTER TABLE websites 
                ADD COLUMN IF NOT EXISTS "submissionStatus" VARCHAR DEFAULT 'PENDING'
            """)
            logger.info("✅ Added submissionStatus column (or already existed)")
            
            # Add submittedAt column
            db_manager.cursor.execute("""
                ALTER TABLE websites 
                ADD COLUMN IF NOT EXISTS "submittedAt" TIMESTAMP
            """)
            logger.info("✅ Added submittedAt column (or already existed)")
            
            # Add submissionErrorMessage column
            db_manager.cursor.execute("""
                ALTER TABLE websites 
                ADD COLUMN IF NOT EXISTS "submissionErrorMessage" TEXT
            """)
            logger.info("✅ Added submissionErrorMessage column (or already existed)")
            
            # Add responseReceived column
            db_manager.cursor.execute("""
                ALTER TABLE websites 
                ADD COLUMN IF NOT EXISTS "responseReceived" BOOLEAN DEFAULT FALSE
            """)
            logger.info("✅ Added responseReceived column (or already existed)")
            
            # Add submissionMethod column
            db_manager.cursor.execute("""
                ALTER TABLE websites 
                ADD COLUMN IF NOT EXISTS "submissionMethod" VARCHAR
            """)
            logger.info("✅ Added submissionMethod column (or already existed)")
            
        except Exception as e:
            logger.error(f"❌ Error adding columns to websites table: {e}")
            return False
        
        # Step 2: Create form_submissions table (SAFE - only creates if not exists)
        logger.info("🔧 Step 2: Creating form_submissions table...")
        
        try:
            db_manager.cursor.execute("""
                CREATE TABLE IF NOT EXISTS form_submissions (
                    id VARCHAR PRIMARY KEY,
                    website_id VARCHAR NOT NULL REFERENCES websites(id) ON DELETE CASCADE,
                    file_upload_id VARCHAR REFERENCES file_uploads(id) ON DELETE CASCADE,
                    user_id VARCHAR REFERENCES users(id) ON DELETE CASCADE,
                    
                    -- Submission Details
                    submission_status VARCHAR DEFAULT 'PENDING',
                    submitted_message TEXT NOT NULL,
                    message_type VARCHAR DEFAULT 'general',
                    
                    -- Form Information
                    contact_form_url VARCHAR,
                    form_fields_used JSONB,
                    submission_method VARCHAR DEFAULT 'unknown',
                    
                    -- Timing
                    submitted_at TIMESTAMP,
                    response_received_at TIMESTAMP,
                    last_attempt_at TIMESTAMP,
                    
                    -- Response Tracking
                    response_received BOOLEAN DEFAULT FALSE,
                    response_content TEXT,
                    response_source VARCHAR,
                    
                    -- Error Handling
                    error_message TEXT,
                    retry_count INTEGER DEFAULT 0,
                    max_retries INTEGER DEFAULT 3,
                    
                    -- Metadata
                    sender_info JSONB,
                    custom_prompt TEXT,
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("✅ Created form_submissions table (or already existed)")
            
        except Exception as e:
            logger.error(f"❌ Error creating form_submissions table: {e}")
            return False
        
        # Step 3: Create submission_attempts table
        logger.info("🔧 Step 3: Creating submission_attempts table...")
        
        try:
            db_manager.cursor.execute("""
                CREATE TABLE IF NOT EXISTS submission_attempts (
                    id VARCHAR PRIMARY KEY,
                    submission_id VARCHAR NOT NULL REFERENCES form_submissions(id) ON DELETE CASCADE,
                    attempt_number INTEGER NOT NULL,
                    status VARCHAR NOT NULL,
                    error_message TEXT,
                    response_code INTEGER,
                    response_time_ms INTEGER,
                    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("✅ Created submission_attempts table (or already existed)")
            
        except Exception as e:
            logger.error(f"❌ Error creating submission_attempts table: {e}")
            return False
        
        # Step 4: Create submission_responses table
        logger.info("🔧 Step 4: Creating submission_responses table...")
        
        try:
            db_manager.cursor.execute("""
                CREATE TABLE IF NOT EXISTS submission_responses (
                    id VARCHAR PRIMARY KEY,
                    submission_id VARCHAR NOT NULL REFERENCES form_submissions(id) ON DELETE CASCADE,
                    response_type VARCHAR NOT NULL,
                    response_content TEXT,
                    response_date TIMESTAMP,
                    follow_up_needed BOOLEAN DEFAULT FALSE,
                    follow_up_notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("✅ Created submission_responses table (or already existed)")
            
        except Exception as e:
            logger.error(f"❌ Error creating submission_responses table: {e}")
            return False
        
        # Step 5: Create indexes (SAFE - only creates if not exists)
        logger.info("🔧 Step 5: Creating performance indexes...")
        
        try:
            # Indexes for form_submissions
            db_manager.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_form_submissions_website_id 
                ON form_submissions(website_id)
            """)
            
            db_manager.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_form_submissions_file_upload_id 
                ON form_submissions(file_upload_id)
            """)
            
            db_manager.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_form_submissions_user_id 
                ON form_submissions(user_id)
            """)
            
            db_manager.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_form_submissions_status 
                ON form_submissions(submission_status)
            """)
            
            db_manager.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_form_submissions_created_at 
                ON form_submissions(created_at)
            """)
            
            # Indexes for submission_attempts
            db_manager.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_submission_attempts_submission_id 
                ON submission_attempts(submission_id)
            """)
            
            db_manager.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_submission_attempts_attempted_at 
                ON submission_attempts(attempted_at)
            """)
            
            # Indexes for submission_responses
            db_manager.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_submission_responses_submission_id 
                ON submission_responses(submission_id)
            """)
            
            db_manager.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_submission_responses_response_date 
                ON submission_responses(response_date)
            """)
            
            logger.info("✅ Created all performance indexes (or already existed)")
            
        except Exception as e:
            logger.error(f"❌ Error creating indexes: {e}")
            return False
        
        # Commit all changes
        db_manager.conn.commit()
        logger.info("✅ All database changes committed successfully")
        
        # Verify the new structures
        logger.info("🔍 Verifying new database structures...")
        
        try:
            # Check if new columns exist in websites table
            db_manager.cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'websites' 
                AND column_name IN ('submissionStatus', 'submittedAt', 'submissionErrorMessage', 'responseReceived', 'submissionMethod')
                ORDER BY column_name
            """)
            
            new_columns = db_manager.cursor.fetchall()
            logger.info(f"✅ Found {len(new_columns)} new columns in websites table:")
            for col in new_columns:
                logger.info(f"  - {col[0]}")
            
            # Check if new tables exist
            db_manager.cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('form_submissions', 'submission_attempts', 'submission_responses')
                ORDER BY table_name
            """)
            
            new_tables = db_manager.cursor.fetchall()
            logger.info(f"✅ Found {len(new_tables)} new tables:")
            for table in new_tables:
                logger.info(f"  - {table[0]}")
                
        except Exception as e:
            logger.error(f"❌ Error verifying new structures: {e}")
            return False
        
        logger.info("🎉 Database migration completed successfully!")
        logger.info("📋 New contact form submission system is ready to use")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Fatal error during migration: {e}")
        if 'db_manager' in locals() and hasattr(db_manager, 'conn') and db_manager.conn:
            db_manager.conn.rollback()
            logger.info("🔄 Database changes rolled back for safety")
        return False

def main():
    """Main migration function"""
    
    print("🚀 Safe Database Migration for Contact Form System")
    print("=" * 60)
    print("⚠️  This migration will:")
    print("   ✅ ADD new columns to websites table")
    print("   ✅ CREATE new tables for contact form tracking")
    print("   ✅ CREATE performance indexes")
    print("   ❌ NOT modify any existing data")
    print("   ❌ NOT delete any existing tables")
    print()
    
    # Confirm before proceeding
    response = input("🤔 Do you want to proceed with the migration? (yes/no): ").lower().strip()
    
    if response not in ['yes', 'y']:
        print("❌ Migration cancelled by user")
        return
    
    print()
    print("🚀 Starting migration...")
    print()
    
    # Run migration
    if run_safe_migration():
        print()
        print("🎉 Migration completed successfully!")
        print("📋 Contact form submission system is now ready")
    else:
        print()
        print("❌ Migration failed - no changes were made to your database")
        print("🔍 Check the logs above for details")

if __name__ == "__main__":
    main()
