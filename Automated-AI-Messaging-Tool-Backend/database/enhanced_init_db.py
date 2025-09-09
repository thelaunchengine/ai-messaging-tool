#!/usr/bin/env python3
"""
Enhanced Database Initialization
Includes enhanced status tracking for message generation and form submission
"""
import psycopg2
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database with enhanced schema"""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host="localhost",
            database="ai_messaging_db",
            user="xb3353",
            password="password"
        )
        cursor = conn.cursor()
        
        # Create enhanced websites table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS websites (
            id VARCHAR(255) PRIMARY KEY,
            "fileUploadId" VARCHAR(255) NOT NULL,
            "userId" VARCHAR(255) NOT NULL,
            "websiteUrl" TEXT NOT NULL,
            "companyName" VARCHAR(255),
            "industry" VARCHAR(100),
            "businessType" VARCHAR(100),
            "contactFormUrl" TEXT,
            "hasContactForm" BOOLEAN DEFAULT FALSE,
            "scrapingStatus" VARCHAR(50) DEFAULT 'PENDING',
            "messageStatus" VARCHAR(50) DEFAULT 'PENDING',
            "submissionStatus" VARCHAR(50) DEFAULT 'PENDING',
            "aboutUsContent" TEXT,
            "generatedMessage" TEXT,
            "messageGenerationError" TEXT,
            "submissionError" TEXT,
            "submittedFormFields" JSONB,
            "submissionResponse" TEXT,
            "confidence" DECIMAL(5,4),
            "errorMessage" TEXT,
            "createdAt" TIMESTAMP DEFAULT NOW(),
            "updatedAt" TIMESTAMP DEFAULT NOW()
        )
        """)
        logger.info("Created enhanced websites table")
        
        # Create enhanced contact_inquiries table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contact_inquiries (
            id VARCHAR(255) PRIMARY KEY,
            "websiteId" VARCHAR(255) NOT NULL,
            "userId" VARCHAR(255) NOT NULL,
            "contactFormUrl" TEXT NOT NULL,
            "submittedMessage" TEXT NOT NULL,
            status VARCHAR(50) DEFAULT 'PENDING',
            "submittedAt" TIMESTAMP,
            "responseReceived" BOOLEAN DEFAULT FALSE,
            "responseContent" TEXT,
            "submittedFormFields" JSONB,
            "submissionError" TEXT,
            "retryCount" INTEGER DEFAULT 0,
            "lastRetryAt" TIMESTAMP,
            "createdAt" TIMESTAMP DEFAULT NOW(),
            "updatedAt" TIMESTAMP DEFAULT NOW()
        )
        """)
        logger.info("Created enhanced contact_inquiries table")
        
        # Create other necessary tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS file_uploads (
            "fileUploadId" VARCHAR(255) PRIMARY KEY,
            "userId" VARCHAR(255) NOT NULL,
            filename VARCHAR(255) NOT NULL,
            "originalName" VARCHAR(255),
            "fileSize" INTEGER,
            "fileType" VARCHAR(50),
            status VARCHAR(50) DEFAULT 'PENDING',
            "totalWebsites" INTEGER DEFAULT 0,
            "processedWebsites" INTEGER DEFAULT 0,
            "failedWebsites" INTEGER DEFAULT 0,
            "totalChunks" INTEGER DEFAULT 0,
            "completedChunks" INTEGER DEFAULT 0,
            "processingStartedAt" TIMESTAMP,
            "processingCompletedAt" TIMESTAMP,
            "createdAt" TIMESTAMP DEFAULT NOW(),
            "updatedAt" TIMESTAMP DEFAULT NOW()
        )
        """)
        logger.info("Created file_uploads table")
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_websites_file_upload_id ON websites("fileUploadId")')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_websites_message_status ON websites("messageStatus")')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_websites_submission_status ON websites("submissionStatus")')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contact_inquiries_website_id ON contact_inquiries("websiteId")')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contact_inquiries_status ON contact_inquiries(status)')
        
        # Commit changes
        conn.commit()
        logger.info("Database initialization completed successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def migrate_existing_database():
    """Migrate existing database to add new columns"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="ai_messaging_db",
            user="xb3353",
            password="password"
        )
        cursor = conn.cursor()
        
        # Add new columns to existing websites table
        alter_queries = [
            'ALTER TABLE websites ADD COLUMN IF NOT EXISTS "submissionStatus" VARCHAR(50) DEFAULT \'PENDING\'',
            'ALTER TABLE websites ADD COLUMN IF NOT EXISTS "messageGenerationError" TEXT',
            'ALTER TABLE websites ADD COLUMN IF NOT EXISTS "submissionError" TEXT',
            'ALTER TABLE websites ADD COLUMN IF NOT EXISTS "submittedFormFields" JSONB',
            'ALTER TABLE websites ADD COLUMN IF NOT EXISTS "submissionResponse" TEXT'
        ]
        
        for query in alter_queries:
            try:
                cursor.execute(query)
                logger.info(f"Added column: {query}")
            except Exception as e:
                logger.warning(f"Column might already exist: {e}")
        
        # Add new columns to existing contact_inquiries table
        contact_alter_queries = [
            'ALTER TABLE contact_inquiries ADD COLUMN IF NOT EXISTS "submittedFormFields" JSONB',
            'ALTER TABLE contact_inquiries ADD COLUMN IF NOT EXISTS "submissionError" TEXT',
            'ALTER TABLE contact_inquiries ADD COLUMN IF NOT EXISTS "retryCount" INTEGER DEFAULT 0',
            'ALTER TABLE contact_inquiries ADD COLUMN IF NOT EXISTS "lastRetryAt" TIMESTAMP'
        ]
        
        for query in contact_alter_queries:
            try:
                cursor.execute(query)
                logger.info(f"Added column: {query}")
            except Exception as e:
                logger.warning(f"Column might already exist: {e}")
        
        # Update existing records
        cursor.execute('UPDATE websites SET "submissionStatus" = \'PENDING\' WHERE "submissionStatus" IS NULL')
        cursor.execute('UPDATE websites SET "messageStatus" = \'PENDING\' WHERE "messageStatus" IS NULL')
        
        conn.commit()
        logger.info("Migration completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Enhanced Database Initialization")
    print("1. Initialize new database")
    print("2. Migrate existing database")
    
    choice = input("Enter choice (1 or 2): ")
    
    if choice == "1":
        success = init_database()
        print("✅ Database initialized successfully" if success else "❌ Database initialization failed")
    elif choice == "2":
        success = migrate_existing_database()
        print("✅ Migration completed successfully" if success else "❌ Migration failed")
    else:
        print("Invalid choice")
