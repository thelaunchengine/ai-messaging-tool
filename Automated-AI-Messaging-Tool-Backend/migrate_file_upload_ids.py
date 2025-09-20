#!/usr/bin/env python3
"""
Migration script to change file upload IDs from UUID to auto-incrementing integers starting from 1000.
This script will:
1. Create a new file_uploads table with integer ID
2. Create a new websites table with integer fileUploadId
3. Migrate existing data
4. Drop old tables and rename new ones
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

def get_database_connection():
    """Get database connection"""
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging')
    return psycopg2.connect(database_url)

def migrate_file_upload_ids():
    """Migrate file upload IDs from UUID to auto-incrementing integers"""
    
    print("🚀 Starting file upload ID migration...")
    
    try:
        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                
                # Step 1: Create new file_uploads table with integer ID
                print("📋 Creating new file_uploads table with integer ID...")
                cursor.execute("""
                    CREATE TABLE file_uploads_new (
                        id SERIAL PRIMARY KEY,
                        "userId" TEXT NOT NULL,
                        filename TEXT NOT NULL,
                        "originalName" TEXT NOT NULL,
                        "fileSize" INTEGER NOT NULL,
                        "fileType" TEXT NOT NULL,
                        status TEXT NOT NULL,
                        "totalWebsites" INTEGER NOT NULL DEFAULT 0,
                        "processedWebsites" INTEGER NOT NULL DEFAULT 0,
                        "failedWebsites" INTEGER NOT NULL DEFAULT 0,
                        "totalChunks" INTEGER NOT NULL DEFAULT 0,
                        "completedChunks" INTEGER NOT NULL DEFAULT 0,
                        "filePath" TEXT,
                        "processingStartedAt" TIMESTAMP,
                        "processingCompletedAt" TIMESTAMP,
                        "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
                        "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW()
                    );
                """)
                
                # Step 2: Create new websites table with integer fileUploadId
                print("📋 Creating new websites table with integer fileUploadId...")
                cursor.execute("""
                    CREATE TABLE websites_new (
                        id TEXT PRIMARY KEY,
                        "fileUploadId" INTEGER NOT NULL REFERENCES file_uploads_new(id) ON DELETE CASCADE,
                        "userId" TEXT NOT NULL,
                        "websiteUrl" TEXT NOT NULL,
                        "contactFormUrl" TEXT,
                        "hasContactForm" BOOLEAN NOT NULL DEFAULT FALSE,
                        "companyName" TEXT,
                        "businessType" TEXT,
                        "industry" TEXT,
                        "aboutUsContent" TEXT,
                        "scrapingStatus" TEXT NOT NULL DEFAULT 'PENDING',
                        "messageStatus" TEXT NOT NULL DEFAULT 'PENDING',
                        "generatedMessage" TEXT,
                        "sentMessage" TEXT,
                        "sentAt" TIMESTAMP,
                        "responseReceived" BOOLEAN NOT NULL DEFAULT FALSE,
                        "responseContent" TEXT,
                        "errorMessage" TEXT,
                        "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
                        "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW(),
                        "submissionStatus" VARCHAR(50),
                        "submissionResponse" TEXT,
                        "submissionError" TEXT,
                        "submittedFormFields" TEXT
                    );
                """)
                
                # Step 3: Get existing file uploads and create mapping
                print("📊 Getting existing file uploads...")
                cursor.execute("SELECT * FROM file_uploads ORDER BY \"createdAt\" ASC")
                existing_uploads = cursor.fetchall()
                
                print(f"Found {len(existing_uploads)} existing file uploads")
                
                # Create UUID to new ID mapping
                uuid_to_new_id = {}
                new_id_counter = 1000
                
                # Step 4: Migrate file uploads data
                print("🔄 Migrating file uploads data...")
                for upload in existing_uploads:
                    old_id = upload[0]  # id is first column
                    uuid_to_new_id[old_id] = new_id_counter
                    
                    cursor.execute("""
                        INSERT INTO file_uploads_new (
                            id, "userId", filename, "originalName", "fileSize", "fileType", 
                            status, "totalWebsites", "processedWebsites", "failedWebsites",
                            "totalChunks", "completedChunks", "filePath", 
                            "processingStartedAt", "processingCompletedAt", "createdAt", "updatedAt"
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """, (
                        new_id_counter, upload[1], upload[2], upload[3], upload[4], upload[5],
                        upload[6], upload[7], upload[8], upload[9], upload[10], upload[11],
                        upload[12], upload[13], upload[14], upload[15], upload[16]
                    ))
                    
                    new_id_counter += 1
                
                print(f"✅ Migrated {len(existing_uploads)} file uploads")
                
                # Step 5: Migrate websites data
                print("🔄 Migrating websites data...")
                cursor.execute("SELECT * FROM websites")
                existing_websites = cursor.fetchall()
                
                migrated_websites = 0
                for website in existing_websites:
                    old_file_upload_id = website[1]  # fileUploadId is second column
                    
                    if old_file_upload_id in uuid_to_new_id:
                        new_file_upload_id = uuid_to_new_id[old_file_upload_id]
                        
                        cursor.execute("""
                            INSERT INTO websites_new (
                                id, "fileUploadId", "userId", "websiteUrl", "contactFormUrl",
                                "hasContactForm", "companyName", "businessType", "industry",
                                "aboutUsContent", "scrapingStatus", "messageStatus",
                                "generatedMessage", "sentMessage", "sentAt", "responseReceived",
                                "responseContent", "errorMessage", "createdAt", "updatedAt",
                                "submissionStatus", "submissionResponse", "submissionError", "submittedFormFields"
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            )
                        """, (
                            website[0], new_file_upload_id, website[2], website[3], website[4],
                            website[5], website[6], website[7], website[8], website[9], website[10],
                            website[11], website[12], website[13], website[14], website[15],
                            website[16], website[17], website[18], website[19], website[20],
                            website[21], website[22], website[23]
                        ))
                        
                        migrated_websites += 1
                    else:
                        print(f"⚠️  Warning: No mapping found for fileUploadId {old_file_upload_id}")
                
                print(f"✅ Migrated {migrated_websites} websites")
                
                # Step 6: Drop old tables and rename new ones
                print("🔄 Replacing old tables with new ones...")
                cursor.execute("DROP TABLE websites CASCADE")
                cursor.execute("DROP TABLE file_uploads CASCADE")
                cursor.execute("ALTER TABLE file_uploads_new RENAME TO file_uploads")
                cursor.execute("ALTER TABLE websites_new RENAME TO websites")
                
                # Step 7: Create indexes
                print("📋 Creating indexes...")
                cursor.execute("CREATE INDEX idx_websites_file_upload_id ON websites(\"fileUploadId\")")
                cursor.execute("CREATE INDEX idx_websites_user_id ON websites(\"userId\")")
                cursor.execute("CREATE INDEX idx_file_uploads_user_id ON file_uploads(\"userId\")")
                
                # Step 8: Update sequence to start from next available number
                cursor.execute("SELECT MAX(id) FROM file_uploads")
                max_id = cursor.fetchone()[0]
                if max_id:
                    cursor.execute(f"ALTER SEQUENCE file_uploads_id_seq RESTART WITH {max_id + 1}")
                    print(f"✅ Updated sequence to start from {max_id + 1}")
                
                conn.commit()
                print("🎉 Migration completed successfully!")
                
                # Step 9: Verify migration
                print("🔍 Verifying migration...")
                cursor.execute("SELECT COUNT(*) FROM file_uploads")
                file_upload_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM websites")
                website_count = cursor.fetchone()[0]
                
                print(f"✅ File uploads: {file_upload_count}")
                print(f"✅ Websites: {website_count}")
                
                # Show sample of new IDs
                cursor.execute("SELECT id, \"originalName\", \"createdAt\" FROM file_uploads ORDER BY id LIMIT 5")
                sample_uploads = cursor.fetchall()
                print("📋 Sample of new file upload IDs:")
                for upload in sample_uploads:
                    print(f"  ID: {upload[0]}, Name: {upload[1]}, Created: {upload[2]}")
                
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_file_upload_ids()
