import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database with all required tables"""
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:cDtrtoOqpdkAzMcLSd%401847@103.215.159.51:5432/aimsgdb')
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        logger.info("Connected to database successfully")
        
        # Create tables
        create_tables(cursor)
        
        # Insert initial data
        insert_initial_data(cursor)
        
        conn.commit()
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def create_tables(cursor):
    """Create all required tables"""
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(255) PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255),
            "createdAt" TIMESTAMP DEFAULT NOW(),
            "updatedAt" TIMESTAMP DEFAULT NOW()
        )
    """)
    logger.info("Created users table")
    
    # File uploads table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS file_uploads (
            id VARCHAR(255) PRIMARY KEY,
            "userId" VARCHAR(255) NOT NULL,
            filename VARCHAR(255) NOT NULL,
            "originalName" VARCHAR(255) NOT NULL,
            "fileSize" BIGINT NOT NULL,
            "fileType" VARCHAR(50) NOT NULL,
            status VARCHAR(50) DEFAULT 'PENDING',
            "totalWebsites" INTEGER DEFAULT 0,
            "processedWebsites" INTEGER DEFAULT 0,
            "failedWebsites" INTEGER DEFAULT 0,
            "totalChunks" INTEGER DEFAULT 0,
            "completedChunks" INTEGER DEFAULT 0,
            "filePath" TEXT,
            "processingStartedAt" TIMESTAMP,
            "processingCompletedAt" TIMESTAMP,
            "createdAt" TIMESTAMP DEFAULT NOW(),
            "updatedAt" TIMESTAMP DEFAULT NOW()
        )
    """)
    logger.info("Created file_uploads table")
    
    # Processing chunks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processing_chunks (
            id VARCHAR(255) PRIMARY KEY,
            "fileUploadId" VARCHAR(255) NOT NULL,
            "chunkNumber" INTEGER NOT NULL,
            "startRow" INTEGER NOT NULL,
            "endRow" INTEGER NOT NULL,
            "totalRecords" INTEGER DEFAULT 0,
            "processedRecords" INTEGER DEFAULT 0,
            "failedRecords" INTEGER DEFAULT 0,
            status VARCHAR(50) DEFAULT 'PENDING',
            "startedAt" TIMESTAMP,
            "completedAt" TIMESTAMP,
            "errorMessage" TEXT,
            "createdAt" TIMESTAMP DEFAULT NOW(),
            "updatedAt" TIMESTAMP DEFAULT NOW()
        )
    """)
    logger.info("Created processing_chunks table")
    
    # Websites table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS websites (
            id VARCHAR(255) PRIMARY KEY,
            "fileUploadId" VARCHAR(255) NOT NULL,
            "userId" VARCHAR(255) NOT NULL,
            "websiteUrl" TEXT NOT NULL,
            "contactFormUrl" TEXT,
            "hasContactForm" BOOLEAN DEFAULT FALSE,
            "scrapingStatus" VARCHAR(50) DEFAULT 'PENDING',
            "messageStatus" VARCHAR(50) DEFAULT 'PENDING',
            "aboutUsContent" TEXT,
            "generatedMessage" TEXT,
            "confidence" DECIMAL(5,4),
            "createdAt" TIMESTAMP DEFAULT NOW(),
            "updatedAt" TIMESTAMP DEFAULT NOW()
        )
    """)
    logger.info("Created websites table")
    
    # Static content table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS static_content (
            id VARCHAR(255) PRIMARY KEY,
            type VARCHAR(100) NOT NULL,
            title VARCHAR(255),
            content TEXT,
            status VARCHAR(50) DEFAULT 'DRAFT',
            version INTEGER DEFAULT 1,
            "createdAt" TIMESTAMP DEFAULT NOW(),
            "updatedAt" TIMESTAMP DEFAULT NOW(),
            UNIQUE(type, version)
        )
    """)
    logger.info("Created static_content table")
    
    # Predefined messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predefined_messages (
            id VARCHAR(255) PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            message_type VARCHAR(50) NOT NULL DEFAULT 'general',
            industry VARCHAR(100),
            business_type VARCHAR(100),
            tone VARCHAR(50) DEFAULT 'professional',
            is_active BOOLEAN DEFAULT true,
            usage_count INTEGER DEFAULT 0,
            success_rate DECIMAL(5,2) DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    logger.info("Created predefined_messages table")
    
    # Scraping jobs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scraping_jobs (
            id VARCHAR(255) PRIMARY KEY,
            file_upload_id VARCHAR(255),
            total_websites INTEGER DEFAULT 0,
            status VARCHAR(50) DEFAULT 'PENDING',
            processed_websites INTEGER DEFAULT 0,
            failed_websites INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create message_categories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS message_categories (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            parent_id INTEGER REFERENCES message_categories(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Contact inquiries table
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
            "createdAt" TIMESTAMP DEFAULT NOW(),
            "updatedAt" TIMESTAMP DEFAULT NOW()
        )
    """)
    logger.info("Created contact_inquiries table")

def insert_initial_data(cursor):
    """Insert initial data into tables"""
    
    # Insert sample static content
    cursor.execute("""
        INSERT INTO static_content (id, type, title, content, status, version, "createdAt", "updatedAt")
        VALUES 
        ('about-1', 'about', 'About AI Messaging Tool', 'Our AI-powered messaging tool helps businesses generate personalized outreach messages.', 'PUBLISHED', 1, NOW(), NOW()),
        ('privacy-1', 'privacy', 'Privacy Policy', 'We respect your privacy and protect your data.', 'PUBLISHED', 1, NOW(), NOW()),
        ('terms-1', 'terms', 'Terms of Service', 'By using our service, you agree to these terms.', 'PUBLISHED', 1, NOW(), NOW())
        ON CONFLICT (type, version) DO NOTHING
    """)
    logger.info("Inserted initial static content")
    
    # Insert sample predefined messages
    cursor.execute("""
        INSERT INTO predefined_messages (id, industry, service, message, status, "usageCount", "createdAt", "updatedAt")
        VALUES 
        ('tech-web-1', 'Technology', 'Web Development', 'Hi there! I noticed your website could benefit from some modern updates. Would you be interested in discussing how we can improve your online presence?', 'ACTIVE', 0, NOW(), NOW()),
        ('marketing-seo-1', 'Marketing', 'SEO Services', 'Hello! I came across your website and noticed some opportunities to improve your search engine rankings. Would you like to discuss how we can help you get more organic traffic?', 'ACTIVE', 0, NOW(), NOW()),
        ('consulting-strategy-1', 'Consulting', 'Business Strategy', 'Hi! I''ve been following your company''s growth and would love to discuss potential collaboration opportunities. Are you open to a brief conversation about strategic partnerships?', 'ACTIVE', 0, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """)
    logger.info("Inserted initial predefined messages")

if __name__ == "__main__":
    init_database() 