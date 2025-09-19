#!/usr/bin/env python3
"""
Script to restore database from local backup to AWS RDS
Run this from the remote server where the backup exists
"""

import os
import subprocess
import sys

def restore_database():
    """Restore database from backup to AWS RDS"""
    
    # AWS RDS connection details
    rds_host = "production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com"
    rds_port = "5432"
    rds_user = "postgres"
    rds_password = "AiMessaging2024Secure"
    rds_database = "ai_messaging"
    
    # Local backup file
    backup_file = "/home/xb3353/database_backup_20250821_153111.sql"
    
    # Set environment variable for password
    env = os.environ.copy()
    env['PGPASSWORD'] = rds_password
    
    try:
        print("Starting database restoration...")
        
        # First, clear the existing database
        print("Clearing existing database...")
        clear_cmd = [
            'psql',
            f'postgresql://{rds_user}:{rds_password}@{rds_host}:{rds_port}/{rds_database}',
            '-c', 'DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;'
        ]
        
        result = subprocess.run(clear_cmd, env=env, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error clearing database: {result.stderr}")
            return False
            
        print("Database cleared successfully")
        
        # Restore from backup
        print("Restoring from backup...")
        restore_cmd = [
            'psql',
            f'postgresql://{rds_user}:{rds_password}@{rds_host}:{rds_port}/{rds_database}',
            '-f', backup_file
        ]
        
        result = subprocess.run(restore_cmd, env=env, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error restoring database: {result.stderr}")
            return False
            
        print("Database restored successfully!")
        
        # Verify restoration
        print("Verifying restoration...")
        verify_cmd = [
            'psql',
            f'postgresql://{rds_user}:{rds_password}@{rds_host}:{rds_port}/{rds_database}',
            '-c', 'SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = \'public\';'
        ]
        
        result = subprocess.run(verify_cmd, env=env, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Verification successful: {result.stdout.strip()}")
            return True
        else:
            print(f"Verification failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error during restoration: {str(e)}")
        return False

if __name__ == "__main__":
    success = restore_database()
    sys.exit(0 if success else 1)
