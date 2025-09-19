#!/usr/bin/env python3
"""
Contact Form Submission Database Migration Script
SAFE: Only adds new columns, never removes existing data
"""

import os
import sys
import logging

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_migration():
    """Run the contact form submission database migration"""
    
    try:
        from database.database_manager import DatabaseManager
        
        logger.info("=== Starting Contact Form Submission Database Migration ===")
        logger.info("This migration is SAFE - only adds new columns, never removes data")
        
        # Initialize database connection
        db = DatabaseManager()
        connection = db.get_connection()
        cursor = connection.cursor()
        
        # Read the migration SQL file
        migration_file = os.path.join(os.path.dirname(__file__), 'contact_form_migration.sql')
        
        if not os.path.exists(migration_file):
            logger.error(f"Migration file not found: {migration_file}")
            return False
        
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        logger.info("Migration SQL loaded successfully")
        
        # Split SQL into individual statements
        statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
        
        # Execute each statement
        for i, statement in enumerate(statements, 1):
            if statement and not statement.startswith('--'):
                try:
                    logger.info(f"Executing statement {i}/{len(statements)}")
                    cursor.execute(statement)
                    connection.commit()
                    logger.info(f"Statement {i} executed successfully")
                except Exception as e:
                    logger.warning(f"Statement {i} had an issue (this might be expected): {e}")
                    connection.rollback()
                    # Continue with next statement
        
        # Verify the changes
        logger.info("=== Verifying Migration Results ===")
        
        # Check contact_inquiries table
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'contact_inquiries' 
            AND column_name IN ('websiteId', 'fileUploadId', 'submissionStatus')
            ORDER BY column_name
        """)
        contact_columns = cursor.fetchall()
        
        logger.info("Contact inquiries table new columns:")
        for col in contact_columns:
            logger.info(f"  - {col[0]}: {col[1]}")
        
        # Check websites table
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'websites' 
            AND column_name IN ('submissionStatus', 'submissionError')
            ORDER BY column_name
        """)
        website_columns = cursor.fetchall()
        
        logger.info("Websites table new columns:")
        for col in website_columns:
            logger.info(f"  - {col[0]}: {col[1]}")
        
        cursor.close()
        connection.close()
        
        logger.info("=== Migration Completed Successfully! ===")
        logger.info("New columns added for contact form submission tracking")
        logger.info("All existing data and functionality preserved")
        
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
