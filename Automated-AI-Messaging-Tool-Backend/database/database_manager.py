import os
import json
import logging
import uuid
import time
import random
from typing import Optional, List, Dict, Any
from datetime import datetime
import pg8000
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
import psycopg2
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:cDtrtoOqpdkAzMcLSd%401847@localhost:5432/aimsgdb')
        
        # Parse connection parameters for pg8000
        parsed_url = urlparse(self.database_url)
        self.connection_params = {
            'host': parsed_url.hostname,
            'port': parsed_url.port or 5432,
            'user': parsed_url.username,
            'password': parsed_url.password,
            'database': parsed_url.path[1:] if parsed_url.path else 'aimsgdb'
        }
        
        # Initialize connection and cursor
        self.conn = None
        self.cursor = None
        self._connect()
    
    def _connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.cursor = self.conn.cursor()
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def _ensure_connection(self):
        """Ensure database connection is active"""
        try:
            self.cursor.execute("SELECT 1")
        except Exception:
            self._connect()
    
    def get_connection(self):
        """Get database connection"""
        try:
            conn = psycopg2.connect(self.database_url)
            return conn
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def create_scraping_job(self, userId: str, fileUploadId: str, job_type: str = "SCRAPING") -> Optional[str]:
        """Create a new scraping job and return the job ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Generate a unique job ID
            job_id = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT INTO scraping_jobs (id, "fileUploadId", status, "totalWebsites", "processedWebsites", "failedWebsites")
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (job_id, fileUploadId, "PENDING", 0, 0, 0))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Created scraping job with ID: {job_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"Error creating scraping job: {e}")
            return None
    
    def create_scraping_job_from_data(self, job_data: Dict[str, Any]) -> bool:
        """Create a scraping job from data dictionary"""
        try:
            job_id = str(uuid.uuid4())
            query = """
                INSERT INTO scraping_jobs (id, "fileUploadId", "totalWebsites", status, "processedWebsites", "failedWebsites", "createdAt", "updatedAt")
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            self.cursor.execute(query, (
                job_id,
                job_data.get('fileUploadId'),
                job_data.get('totalWebsites', 0),
                job_data.get('status', 'PENDING'),
                job_data.get('processedWebsites', 0),
                job_data.get('failedWebsites', 0)
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error creating scraping job: {e}")
            return False

    # Predefined Message Methods
    def create_predefined_message(self, message_data: Dict[str, Any]) -> bool:
        """Create a new predefined message"""
        try:
            message_id = str(uuid.uuid4())
            query = """
                INSERT INTO predefined_messages (id, title, content, message_type, industry, business_type, tone, is_active, usage_count, success_rate, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            self.cursor.execute(query, (
                message_id,
                message_data.get('title', ''),
                message_data.get('content', ''),
                message_data.get('messageType', 'general'),
                message_data.get('industry'),
                message_data.get('businessType'),
                message_data.get('tone', 'professional'),
                message_data.get('isActive', True),
                0,  # usage_count starts at 0
                0.0  # success_rate starts at 0.0
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error creating predefined message: {e}")
            return False

    def get_predefined_messages_by_criteria(self, industry: str = None, businessType: str = None, status: str = 'ACTIVE') -> List[Dict[str, Any]]:
        """Get predefined messages based on criteria"""
        try:
            where_conditions = ["status = %s"]
            params = [status]
            
            if industry:
                where_conditions.append("LOWER(industry) LIKE LOWER(%s)")
                params.append(f"%{industry}%")
            
            if businessType:
                where_conditions.append("LOWER(service) LIKE LOWER(%s)")
                params.append(f"%{businessType}%")
            
            where_clause = " AND ".join(where_conditions)
            
            query = f"""
                SELECT id, industry, service, message, "messageType", tone, status, "usageCount", "createdAt", "updatedAt"
                FROM predefined_messages
                WHERE {where_clause}
                ORDER BY "usageCount" ASC
            """
            
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            
            messages = []
            for row in results:
                messages.append({
                    'id': row[0],
                    'industry': row[1],
                    'service': row[2],
                    'message': row[3],
                    'messageType': row[4],
                    'tone': row[5],
                    'status': row[6],
                    'usageCount': row[7],
                    'createdAt': row[8].isoformat() if row[8] else None,
                    'updatedAt': row[9].isoformat() if row[9] else None
                })
            
            return messages
        except Exception as e:
            logger.error(f"Error getting predefined messages: {e}")
            return []

    def increment_predefined_message_usage(self, message_id: str) -> bool:
        """Increment usage count for predefined message"""
        try:
            query = """
                UPDATE predefined_messages 
                SET usage_count = usage_count + 1, updatedAt = NOW()
                WHERE id = %s
            """
            self.cursor.execute(query, (message_id,))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error incrementing predefined message usage: {e}")
            return False

    def get_predefined_message_statistics(self) -> Dict[str, Any]:
        """Get statistics about predefined message usage"""
        try:
            # Total messages
            self.cursor.execute("SELECT COUNT(*) FROM predefined_messages")
            total_messages = self.cursor.fetchone()[0]
            
            # Active messages
            self.cursor.execute("SELECT COUNT(*) FROM predefined_messages WHERE is_active = true")
            active_messages = self.cursor.fetchone()[0]
            
            # Total usage
            self.cursor.execute("SELECT COALESCE(SUM(usage_count), 0) FROM predefined_messages")
            total_usage = self.cursor.fetchone()[0]
            
            # Top messages
            self.cursor.execute("""
                SELECT id, title, usage_count, success_rate
                FROM predefined_messages
                ORDER BY usage_count DESC
                LIMIT 5
            """)
            top_messages = []
            for row in self.cursor.fetchall():
                top_messages.append({
                    'id': row[0],
                    'title': row[1],
                    'usageCount': row[2],
                    'successRate': float(row[3]) if row[3] else 0.0
                })
            
            return {
                'totalMessages': total_messages,
                'activeMessages': active_messages,
                'totalUsage': total_usage,
                'topMessages': top_messages
            }
        except Exception as e:
            logger.error(f"Error getting predefined message statistics: {e}")
            return {
                'totalMessages': 0,
                'activeMessages': 0,
                'totalUsage': 0,
                'topMessages': []
            }

    def update_predefined_message(self, message_id: str, message_data: Dict[str, Any]) -> bool:
        """Update existing predefined message"""
        try:
            query = """
                UPDATE predefined_messages 
                SET title = %s, content = %s, message_type = %s, industry = %s, businessType = %s, tone = %s, is_active = %s, updatedAt = NOW()
                WHERE id = %s
            """
            self.cursor.execute(query, (
                message_data.get('title'),
                message_data.get('content'),
                message_data.get('messageType'),
                message_data.get('industry'),
                message_data.get('businessType'),
                message_data.get('tone'),
                message_data.get('isActive'),
                message_id
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating predefined message: {e}")
            return False

    def delete_predefined_message(self, message_id: str) -> bool:
        """Delete predefined message"""
        try:
            query = "DELETE FROM predefined_messages WHERE id = %s"
            self.cursor.execute(query, (message_id,))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting predefined message: {e}")
            return False

    def get_predefined_message_by_id(self, message_id: str) -> Dict[str, Any]:
        """Get predefined message by ID"""
        try:
            query = """
                SELECT id, title, content, message_type, industry, business_type, tone, is_active, usage_count, success_rate, created_at, updated_at
                FROM predefined_messages
                WHERE id = %s
            """
            self.cursor.execute(query, (message_id,))
            row = self.cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'title': row[1],
                    'content': row[2],
                    'messageType': row[3],
                    'industry': row[4],
                    'businessType': row[5],
                    'tone': row[6],
                    'isActive': row[7],
                    'usageCount': row[8],
                    'successRate': float(row[9]) if row[9] else 0.0,
                    'createdAt': row[10].isoformat() if row[10] else None,
                    'updatedAt': row[11].isoformat() if row[11] else None
                }
            return None
        except Exception as e:
            logger.error(f"Error getting predefined message by ID: {e}")
            return None
    
    def update_scraping_job_status(self, job_id: str, status: str) -> bool:
        """Update scraping job status"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE scraping_jobs 
                SET status = %s, "updatedAt" = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (status, job_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Updated scraping job {job_id} status to: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating scraping job status: {e}")
            return False
    
    def update_scraping_job(self, job_id: str, status: str, totalWebsites: int = 0, 
                          processedWebsites: int = 0, failedWebsites: int = 0, result: str = None) -> bool:
        """Update scraping job with complete information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE scraping_jobs 
                SET status = %s, "totalWebsites" = %s, "processedWebsites" = %s, 
                    "failedWebsites" = %s, "updatedAt" = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (status, total_websites, processed_websites, failed_websites, job_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Updated scraping job {job_id}: status={status}, "
                       f"total_websites={totalWebsites}, processed_websites={processedWebsites}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating scraping job: {e}")
            return False
    
    def get_scraping_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get scraping job by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, "fileUploadId", status, "totalWebsites", "processedWebsites", 
                       "failedWebsites", "startedAt", "completedAt", "errorMessage", 
                       "createdAt", "updatedAt"
                FROM scraping_jobs 
                WHERE id = %s
            """, (job_id,))
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'fileUploadId': row[1],
                    'status': row[2],
                    'totalWebsites': row[3],
                    'processedWebsites': row[4],
                    'failedWebsites': row[5],
                    'startedAt': row[6],
                    'completedAt': row[7],
                    'errorMessage': row[8],
                    'createdAt': row[9],
                    'updatedAt': row[10]
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting scraping job: {e}")
            return None
    
    def create_website_data(self, userId: str, fileUploadId: str, url: str, 
                          title: str = None, content: str = None, metadata: str = None) -> Optional[str]:
        """Create website data record in the websites table"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Generate a unique website ID
            website_id = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT INTO websites (id, "userId", "fileUploadId", "websiteUrl", "scrapingStatus", "messageStatus", "updatedAt")
                VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (website_id, userId, fileUploadId, url, "COMPLETED", "PENDING"))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Created website data record with ID: {website_id} for URL: {url}")
            return website_id
            
        except Exception as e:
            logger.error(f"Error creating website data: {e}")
            return None
    
    def create_website_data_enhanced(self, userId: str, fileUploadId: str, url: str, 
                                   title: str = None, companyName: str = None, industry: str = None,
                                   businessType: str = None, contactFormUrl: str = None,
                                   has_contact_form: bool = False, aboutUsContent: str = None,
                                   scrapingStatus: str = "COMPLETED", error_message: str = None) -> Optional[str]:
        """Create enhanced website data record with detailed scraping information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Generate a unique website ID
            website_id = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT INTO websites (
                    id, "userId", "fileUploadId", "websiteUrl", "companyName", 
                    "industry", "businessType", "contactFormUrl", "hasContactForm", 
                    "aboutUsContent", "scrapingStatus", "errorMessage", "messageStatus", "updatedAt"
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (
                website_id, userId, fileUploadId, url, companyName,
                industry, businessType, contactFormUrl, has_contact_form,
                aboutUsContent, scrapingStatus, error_message, "PENDING"
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Created enhanced website data record with ID: {website_id} for URL: {url}")
            return website_id
            
        except Exception as e:
            logger.error(f"Error creating enhanced website data: {e}")
            return None
    
    def update_website_message(self, website_id: str, generatedMessage: str, messageStatus: str = "GENERATED") -> bool:
        """Update website with generated message"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE websites 
                SET "generatedMessage" = %s, "messageStatus" = %s, "updatedAt" = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (generatedMessage, messageStatus, website_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Updated website {website_id} with generated message")
            return True
            
        except Exception as e:
            logger.error(f"Error updating website message: {e}")
            return False
    
    def create_websites_batch(self, website_data_list: List[Dict[str, Any]]) -> bool:
        """Create multiple website records in batch with duplicate prevention"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            created_count = 0
            skipped_count = 0
            
            for website_data in website_data_list:
                # Check if website already exists for this fileUploadId and URL
                cursor.execute("""
                    SELECT id FROM websites 
                    WHERE "fileUploadId" = %s AND "websiteUrl" = %s
                """, (website_data.get('fileUploadId'), website_data.get('websiteUrl')))
                
                existing = cursor.fetchone()
                
                if existing:
                    logger.info(f"Website already exists, skipping: {website_data.get('websiteUrl')}")
                    skipped_count += 1
                    continue
                
                # Generate a unique website ID
                website_id = str(uuid.uuid4())
                
                cursor.execute("""
                    INSERT INTO websites (id, "userId", "fileUploadId", "websiteUrl", "scrapingStatus", "messageStatus", "updatedAt")
                    VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                """, (
                    website_id,
                    website_data.get('userId'),
                    website_data.get('fileUploadId'),
                    website_data.get('websiteUrl'),
                    website_data.get('scrapingStatus', 'PENDING'),
                    website_data.get('messageStatus', 'PENDING')
                ))
                created_count += 1
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Created {created_count} new website records, skipped {skipped_count} duplicates")
            return True
            
        except Exception as e:
            logger.error(f"Error creating websites batch: {e}")
            return False
    
    def get_website_data_by_file_upload(self, fileUploadId: str) -> List[Dict[str, Any]]:
        """Get all website data for a specific file upload"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, "userId", "fileUploadId", "websiteUrl", "companyName", 
                       "businessType", "industry", "aboutUsContent", "scrapingStatus", 
                       "messageStatus", "generatedMessage", "createdAt", "updatedAt"
                FROM websites 
                WHERE "fileUploadId" = %s
                ORDER BY "createdAt" DESC
            """, (fileUploadId,))
            
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return [
                {
                    'id': row[0],
                    'userId': row[1],
                    'fileUploadId': row[2],
                    'websiteUrl': row[3],
                    'companyName': row[4],
                    'businessType': row[5],
                    'industry': row[6],
                    'aboutUsContent': row[7],
                    'scrapingStatus': row[8],
                    'messageStatus': row[9],
                    'generatedMessage': row[10],
                    'createdAt': row[11],
                    'updatedAt': row[12]
                }
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"Error getting website data: {e}")
            return []

    def get_website_by_id(self, website_id: str) -> Optional[Dict[str, Any]]:
        """Get website data by ID"""
        try:
            query = """
                SELECT id, "userId", "fileUploadId", "websiteUrl", "companyName", "industry", 
                       "businessType", "contactFormUrl", "hasContactForm", "aboutUsContent", 
                       "scrapingStatus", "messageStatus", "generatedMessage", "createdAt", "updatedAt"
                FROM websites
                WHERE id = %s
            """
            self.cursor.execute(query, (website_id,))
            row = self.cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'userId': row[1],
                    'fileUploadId': row[2],
                    'websiteUrl': row[3],
                    'companyName': row[4],
                    'industry': row[5],
                    'businessType': row[6],
                    'contactFormUrl': row[7],
                    'hasContactForm': row[8],
                    'aboutUsContent': row[9],
                    'scrapingStatus': row[10],
                    'messageStatus': row[11],
                    'generatedMessage': row[12],
                    'createdAt': row[13].isoformat() if row[13] else None,
                    'updatedAt': row[14].isoformat() if row[14] else None
                }
            return None
        except Exception as e:
            logger.error(f"Error getting website by ID: {e}")
            return None

    def get_websites_with_messages(self, fileUploadId: str = None, userId: str = None) -> List[Dict[str, Any]]:
        """Get websites that have generated messages"""
        try:
            where_conditions = ['"generatedMessage" IS NOT NULL AND "generatedMessage" != \'\'']
            params = []
            
            if fileUploadId:
                where_conditions.append('"fileUploadId" = %s')
                params.append(fileUploadId)
            
            if userId:
                where_conditions.append('"userId" = %s')
                params.append(userId)
            
            where_clause = " AND ".join(where_conditions)
            
            query = f"""
                SELECT id, "userId", "fileUploadId", "websiteUrl", "companyName", "industry", 
                       "businessType", "contactFormUrl", "hasContactForm", "aboutUsContent", 
                       "scrapingStatus", "messageStatus", "generatedMessage", "createdAt", "updatedAt"
                FROM websites
                WHERE {where_clause}
                ORDER BY "createdAt" DESC
            """
            
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            
            websites = []
            for row in results:
                websites.append({
                    'id': row[0],
                    'userId': row[1],
                    'fileUploadId': row[2],
                    'websiteUrl': row[3],
                    'companyName': row[4],
                    'industry': row[5],
                    'businessType': row[6],
                    'contactFormUrl': row[7],
                    'hasContactForm': row[8],
                    'aboutUsContent': row[9],
                    'scrapingStatus': row[10],
                    'messageStatus': row[11],
                    'generatedMessage': row[12],
                    'createdAt': row[13].isoformat() if row[13] else None,
                    'updatedAt': row[14].isoformat() if row[14] else None
                })
            
            return websites
        except Exception as e:
            logger.error(f"Error getting websites with messages: {e}")
            return []

    def get_websites_without_messages(self, fileUploadId: str = None, userId: str = None) -> List[Dict[str, Any]]:
        """Get websites that don't have generated messages"""
        try:
            where_conditions = ['("generatedMessage" IS NULL OR "generatedMessage" != \'\')']
            params = []
            
            if fileUploadId:
                where_conditions.append('"fileUploadId" = %s')
                params.append(fileUploadId)
            
            if userId:
                where_conditions.append('"userId" = %s')
                params.append(userId)
            
            where_clause = " AND ".join(where_conditions)
            
            query = f"""
                SELECT id, "userId", "fileUploadId", "websiteUrl", "companyName", "industry", 
                       "businessType", "contactFormUrl", "hasContactForm", "aboutUsContent", 
                       "scrapingStatus", "messageStatus", "generatedMessage", "createdAt", "updatedAt"
                FROM websites
                WHERE {where_clause}
                ORDER BY "createdAt" DESC
            """
            
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            
            websites = []
            for row in results:
                websites.append({
                    'id': row[0],
                    'userId': row[1],
                    'fileUploadId': row[2],
                    'websiteUrl': row[3],
                    'companyName': row[4],
                    'industry': row[5],
                    'businessType': row[6],
                    'contactFormUrl': row[7],
                    'hasContactForm': row[8],
                    'aboutUsContent': row[9],
                    'scrapingStatus': row[10],
                    'messageStatus': row[11],
                    'generatedMessage': row[12],
                    'createdAt': row[13].isoformat() if row[13] else None,
                    'updatedAt': row[14].isoformat() if row[14] else None
                })
            
            return websites
        except Exception as e:
            logger.error(f"Error getting websites without messages: {e}")
            return []

    def get_websites_by_file_upload_id(self, fileUploadId: str) -> List[Dict[str, Any]]:
        """Get all websites for a specific file upload"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT id, "userId", "fileUploadId", "websiteUrl", "companyName", "industry", 
                       "businessType", "contactFormUrl", "hasContactForm", "aboutUsContent", 
                       "scrapingStatus", "messageStatus", "generatedMessage", "submissionStatus",
                       "submissionResponse", "submissionError", "submittedFormFields", "createdAt", "updatedAt"
                FROM websites 
                WHERE "fileUploadId" = %s
                ORDER BY "createdAt" DESC
            """
            
            cursor.execute(query, (fileUploadId,))
            results = cursor.fetchall()
            
            websites = []
            for row in results:
                websites.append({
                    'id': row[0],
                    'userId': row[1],
                    'fileUploadId': row[2],
                    'websiteUrl': row[3],
                    'companyName': row[4],
                    'industry': row[5],
                    'businessType': row[6],
                    'contactFormUrl': row[7],
                    'hasContactForm': row[8],
                    'aboutUsContent': row[9],
                    'scrapingStatus': row[10],
                    'messageStatus': row[11],
                    'generatedMessage': row[12],
                    'submissionStatus': row[13] or "PENDING",
                    'submissionResponse': row[14],
                    'submissionError': row[15],
                    'submittedFormFields': row[16],
                    'createdAt': row[17].isoformat() if row[17] else None,
                    'updatedAt': row[18].isoformat() if row[18] else None
                })
            
            cursor.close()
            conn.close()
            
            return websites
        except Exception as e:
            logger.error(f"Error getting websites by file upload ID: {e}")
            return []

    def get_next_file_upload_id(self) -> str:
        """Get the next available file upload ID starting from 1000"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get the maximum numeric ID from existing uploads
            cursor.execute("""
                SELECT MAX(CAST(id AS INTEGER)) 
                FROM file_uploads 
                WHERE id ~ '^[0-9]+$'
            """)
            result = cursor.fetchone()
            max_id = result[0] if result[0] else 999
            
            # Return next ID (start from 1000)
            next_id = max(max_id + 1, 1000)
            
            cursor.close()
            conn.close()
            
            logger.info(f"Generated next file upload ID: {next_id}")
            return str(next_id)
            
        except Exception as e:
            logger.error(f"Error getting next file upload ID: {e}")
            # Fallback to timestamp-based ID
            import time
            return str(int(time.time()))

    def create_file_upload(self, fileUploadId: str = None, userId: str = None, filename: str = None, 
                          originalName: str = None, fileSize: int = 0, fileType: str = "csv",
                          status: str = "PENDING", totalWebsites: int = 0, processedWebsites: int = 0,
                          failedWebsites: int = 0, totalChunks: int = 0, completedChunks: int = 0) -> str:
        """Create a file upload record and return the ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if file upload already exists
            if fileUploadId:
                cursor.execute("SELECT id FROM file_uploads WHERE id = %s", (fileUploadId,))
                existing = cursor.fetchone()
                
                if existing:
                    logger.info(f"File upload {fileUploadId} already exists, skipping creation")
                    cursor.close()
                    conn.close()
                    return fileUploadId
            
            values = (
                fileUploadId, userId, filename or "unknown", originalName or filename or "unknown",
                fileSize, fileType, status, totalWebsites, processedWebsites, failedWebsites, totalChunks, completedChunks
            )
            logger.info(f"Attempting to insert file_upload: {values}")
            
            cursor.execute("""
                INSERT INTO file_uploads (id, "userId", filename, "originalName", "fileSize", "fileType", status, "totalWebsites", "processedWebsites", "failedWebsites", "totalChunks", "completedChunks", "updatedAt")
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, values)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Created file upload record: {fileUploadId}")
            return fileUploadId
            
        except Exception as e:
            logger.error(f"Error creating file upload record: {e}. Values: {values}")
            return None
    
    def get_all_file_uploads(self) -> List[Dict[str, Any]]:
        """Get all file uploads (for admin view)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, "userId", filename, "originalName", "fileSize", 
                       "fileType", status, "totalWebsites", "processedWebsites", 
                       "failedWebsites", "createdAt", "updatedAt"
                FROM file_uploads 
                ORDER BY "createdAt" DESC
            """)
            
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if not rows:
                return []
            
            return [
                {
                    'id': row[0],
                    'userId': row[1],
                    'filename': row[2],
                    'originalName': row[3],
                    'fileSize': row[4],
                    'fileType': row[5],
                    'status': row[6],
                    'totalWebsites': row[7],
                    'processedWebsites': row[8],
                    'failedWebsites': row[9],
                    'createdAt': row[10],
                    'updatedAt': row[11]
                }
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"Error getting all file uploads: {e}")
            return []

    def get_user_file_uploads(self, userId: str) -> List[Dict[str, Any]]:
        """Get all file uploads for a user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, "userId", filename, "originalName", "fileSize", 
                       "fileType", status, "totalWebsites", "processedWebsites", 
                       "failedWebsites", "createdAt", "updatedAt"
                FROM file_uploads 
                WHERE "userId" = %s
                ORDER BY "createdAt" DESC
            """, (userId,))
            
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return [
                {
                    'id': row[0],
                    'userId': row[1],
                    'filename': row[2],
                    'originalName': row[3],
                    'fileSize': row[4],
                    'fileType': row[5],
                    'status': row[6],
                    'totalWebsites': row[7],
                    'processedWebsites': row[8],
                    'failedWebsites': row[9],
                    'createdAt': row[10],
                    'updatedAt': row[11]
                }
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"Error getting user file uploads: {e}")
            return []
    
    def update_file_upload(self, fileUploadId: str, update_data: Dict[str, Any]) -> bool:
        """Update file upload record"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Build dynamic update query
            set_clauses = []
            values = []
            
            for key, value in update_data.items():
                if key in ['status', 'totalWebsites', 'processedWebsites', 'failedWebsites', 
                          'totalChunks', 'completedChunks', 'processingStartedAt', 
                          'processingCompletedAt']:
                    set_clauses.append(f'"{key}" = %s')
                    values.append(value)
            
            if not set_clauses:
                logger.warning("No valid fields to update")
                return False
            
            # Add updatedAt timestamp
            set_clauses.append('"updatedAt" = CURRENT_TIMESTAMP')
            
            query = f"""
                UPDATE file_uploads 
                SET {', '.join(set_clauses)}
                WHERE id = %s
            """
            values.append(fileUploadId)
            
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Updated file upload {fileUploadId}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating file upload: {e}")
            return False
    
    def update_processing_chunk(self, chunk_id: str, update_data: Dict[str, Any]) -> bool:
        """Update processing chunk record"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Build dynamic update query
            set_clauses = []
            values = []
            
            for key, value in update_data.items():
                if key in ['status', 'processedRecords', 'failedRecords', 'startedAt', 
                          'completedAt', 'errorMessage']:
                    set_clauses.append(f'"{key}" = %s')
                    values.append(value)
            
            if not set_clauses:
                logger.warning("No valid fields to update")
                return False
            
            query = f"""
                UPDATE processing_chunks 
                SET {', '.join(set_clauses)}
                WHERE id = %s
            """
            values.append(chunk_id)
            
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Updated processing chunk {chunk_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating processing chunk: {e}")
            return False 

    def get_file_upload_by_id(self, fileUploadId: str) -> Optional[Dict[str, Any]]:
        """Get file upload by ID"""
        try:
            self._ensure_connection()
            
            query = """
                SELECT 
                    id,
                    "userId",
                    filename,
                    "originalName",
                    "fileSize",
                    "fileType",
                    status,
                    "totalWebsites",
                    "processedWebsites",
                    "failedWebsites",
                    "totalChunks",
                    "completedChunks",
                    "createdAt",
                    "updatedAt",
                    "processingStartedAt",
                    "processingCompletedAt"
                FROM file_uploads 
                WHERE id = %s
            """
            
            self.cursor.execute(query, (fileUploadId,))
            row = self.cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'userId': row[1],
                    'filename': row[2],
                    'originalName': row[3],
                    'fileSize': row[4],
                    'fileType': row[5],
                    'status': row[6],
                    'totalWebsites': row[7],
                    'processedWebsites': row[8],
                    'failedWebsites': row[9],
                    'totalChunks': row[10],
                    'completedChunks': row[11],
                    'createdAt': row[12].isoformat() if row[12] else None,
                    'updatedAt': row[13].isoformat() if row[13] else None,
                    'processingStartedAt': row[14].isoformat() if row[14] else None,
                    'processingCompletedAt': row[15].isoformat() if row[15] else None
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting file upload by ID: {e}")
            return None

    def update_website_with_scraping_data(self, fileUploadId: str, url: str, 
                                        title: str = None, companyName: str = None, industry: str = None,
                                        businessType: str = None, contactFormUrl: str = None,
                                        has_contact_form: bool = False, aboutUsContent: str = None,
                                        scrapingStatus: str = "COMPLETED", error_message: str = None) -> bool:
        """Update existing website record with scraping data"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE websites 
                SET "companyName" = %s, "industry" = %s, "businessType" = %s, 
                    "contactFormUrl" = %s, "hasContactForm" = %s, "aboutUsContent" = %s,
                    "scrapingStatus" = %s, "errorMessage" = %s, "updatedAt" = CURRENT_TIMESTAMP
                WHERE "fileUploadId" = %s AND "websiteUrl" = %s
            """, (
                companyName, industry, businessType, contactFormUrl, has_contact_form,
                aboutUsContent, scrapingStatus, error_message, fileUploadId, url
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Updated website data for URL: {url} in fileUploadId: {fileUploadId}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating website data: {e}")
            return False 

    def update_website_submission(self, website_id: str, submission_status: str, 
                                 submission_time: datetime, response_content: str = None, 
                                 error_message: str = None, submitted_form_fields: str = None) -> bool:
        """
        Update website submission status
        
        Args:
            website_id: ID of the website
            submission_status: Status of the submission (SUBMITTED, FAILED, PENDING)
            submission_time: When the submission was attempted
            response_content: Response page content after submission
            error_message: Error message if submission failed
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Update the website record with submission details
            cursor.execute("""
                UPDATE websites 
                SET "submissionStatus" = %s,
                    "submissionResponse" = %s,
                    "submissionError" = %s,
                    "submittedFormFields" = %s,
                    "updatedAt" = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (
                submission_status,
                response_content,
                error_message,
                submitted_form_fields,
                website_id
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Updated website submission status for ID: {website_id} to {submission_status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating website submission: {e}")
            return False

    def create_contact_inquiry(self, website_id: str, userId: str, contactFormUrl: str, 
                              submitted_message: str, status: str = "PENDING", 
                              response_content: str = None) -> Optional[str]:
        """
        Create a new contact inquiry record
        
        Args:
            website_id: ID of the website
            userId: ID of the user
            contactFormUrl: URL of the contact form
            submitted_message: Message that was submitted
            status: Status of the inquiry (PENDING, SUBMITTED, FAILED)
            response_content: Response content after submission
            
        Returns:
            Contact inquiry ID if successful, None otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            contact_inquiry_id = str(uuid.uuid4())
            
            # Get website data to extract user ID and file upload ID
            website_data = self.get_website_by_id(website_id)
            if not website_data:
                logger.error(f"Website not found: {website_id}")
                return None
                
            file_upload_id = website_data.get('fileUploadId')
            
            cursor.execute("""
                INSERT INTO contact_inquiries (
                    id, "firstName", "lastName", "email", "message", "status",
                    "websiteId", "fileUploadId", "websiteUrl", "submissionStatus",
                    "submissionResponse", "createdAt", "updatedAt"
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (
                contact_inquiry_id, 
                "AI",  # firstName - using placeholder since we don't have user details
                "Assistant",  # lastName - using placeholder since we don't have user details
                "ai@example.com",  # email - using placeholder since we don't have user details
                submitted_message,  # message
                status,  # status
                website_id,  # websiteId
                file_upload_id,  # fileUploadId
                website_data.get('websiteUrl', ''),  # websiteUrl
                status,  # submissionStatus
                response_content  # submissionResponse
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Created contact inquiry with ID: {contact_inquiry_id}")
            return contact_inquiry_id
            
        except Exception as e:
            logger.error(f"Error creating contact inquiry: {e}")
            return None

    def get_contact_inquiries_by_website(self, website_id: str) -> List[Dict[str, Any]]:
        """
        Get all contact inquiries for a specific website
        
        Args:
            website_id: ID of the website
            
        Returns:
            List of contact inquiry records
        """
        try:
            self._ensure_connection()
            
            query = """
                SELECT 
                    id, "websiteId", "userId", "contactFormUrl", "submittedMessage",
                    status, "submittedAt", "responseReceived", "responseContent",
                    "createdAt", "updatedAt"
                FROM contact_inquiries 
                WHERE "websiteId" = %s
                ORDER BY "createdAt" DESC
            """
            
            self.cursor.execute(query, (website_id,))
            rows = self.cursor.fetchall()
            
            inquiries = []
            for row in rows:
                inquiries.append({
                    'id': row[0],
                    'websiteId': row[1],
                    'userId': row[2],
                    'contactFormUrl': row[3],
                    'submittedMessage': row[4],
                    'status': row[5],
                    'submittedAt': row[6].isoformat() if row[6] else None,
                    'responseReceived': row[7],
                    'responseContent': row[8],
                    'createdAt': row[9].isoformat() if row[9] else None,
                    'updatedAt': row[10].isoformat() if row[10] else None
                })
            
            return inquiries
            
        except Exception as e:
            logger.error(f"Error getting contact inquiries: {e}")
            return []

    def get_contact_inquiries_by_user(self, userId: str) -> List[Dict[str, Any]]:
        """
        Get all contact inquiries for a specific user
        
        Args:
            userId: ID of the user
            
        Returns:
            List of contact inquiry records
        """
        try:
            self._ensure_connection()
            
            query = """
                SELECT 
                    ci.id, ci."websiteId", ci."userId", ci."contactFormUrl", ci."submittedMessage",
                    ci.status, ci."submittedAt", ci."responseReceived", ci."responseContent",
                    ci."createdAt", ci."updatedAt", w."websiteUrl", w."companyName"
                FROM contact_inquiries ci
                JOIN websites w ON ci."websiteId" = w.id
                WHERE ci."userId" = %s
                ORDER BY ci."createdAt" DESC
            """
            
            self.cursor.execute(query, (user_id,))
            rows = self.cursor.fetchall()
            
            inquiries = []
            for row in rows:
                inquiries.append({
                    'id': row[0],
                    'websiteId': row[1],
                    'userId': row[2],
                    'contactFormUrl': row[3],
                    'submittedMessage': row[4],
                    'status': row[5],
                    'submittedAt': row[6].isoformat() if row[6] else None,
                    'responseReceived': row[7],
                    'responseContent': row[8],
                    'createdAt': row[9].isoformat() if row[9] else None,
                    'updatedAt': row[10].isoformat() if row[10] else None,
                    'websiteUrl': row[11],
                    'companyName': row[12]
                })
            
            return inquiries
            
        except Exception as e:
            logger.error(f"Error getting contact inquiries by user: {e}")
            return []

    def get_all_contact_inquiries(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get all contact inquiries with pagination (for admin purposes)
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of contact inquiry records
        """
        try:
            self._ensure_connection()
            
            query = """
                SELECT 
                    ci.id, ci."websiteId", ci."fileUploadId", ci."websiteUrl", ci."submissionStatus",
                    ci.status, ci."submissionResponse", ci."submissionError",
                    ci."createdAt", ci."updatedAt", w."websiteUrl", w."companyName"
                FROM contact_inquiries ci
                JOIN websites w ON ci."websiteId" = w.id
                ORDER BY ci."createdAt" DESC
                LIMIT %s OFFSET %s
            """
            
            self.cursor.execute(query, (limit, offset))
            rows = self.cursor.fetchall()
            
            inquiries = []
            for row in rows:
                inquiries.append({
                    'id': row[0],
                    'websiteId': row[1],
                    'fileUploadId': row[2],
                    'websiteUrl': row[3],
                    'submissionStatus': row[4],
                    'status': row[5],
                    'submissionResponse': row[6],
                    'submissionError': row[7],
                    'createdAt': row[8].isoformat() if row[8] else None,
                    'updatedAt': row[9].isoformat() if row[9] else None,
                    'websiteUrl': row[10],
                    'companyName': row[11]
                })
            
            return inquiries
            
        except Exception as e:
            logger.error(f"Error getting all contact inquiries: {e}")
            return []

    def get_contact_inquiry_count(self) -> int:
        """
        Get total count of contact inquiries
        
        Returns:
            Total number of contact inquiries
        """
        try:
            self._ensure_connection()
            
            query = "SELECT COUNT(*) FROM contact_inquiries"
            self.cursor.execute(query)
            count = self.cursor.fetchone()[0]
            
            return count
            
        except Exception as e:
            logger.error(f"Error getting contact inquiry count: {e}")
            return 0
    
    def update_file_upload_status(self, fileUploadId: str, status: str) -> bool:
        """
        Update the status of a file upload
        
        Args:
            fileUploadId: ID of the file upload to update
            status: New status to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._ensure_connection()
            
            query = """
                UPDATE file_uploads 
                SET status = %s, "updatedAt" = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            
            self.cursor.execute(query, (status, fileUploadId))
            self.conn.commit()
            
            logger.info(f"Updated file upload {fileUploadId} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating file upload status: {e}")
            return False
    
    def create_websites_batch(self, website_data_list: List[Dict[str, Any]]) -> bool:
        """
        Create multiple websites in batch with duplicate prevention
        
        Args:
            website_data_list: List of website data dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._ensure_connection()
            
            created_count = 0
            skipped_count = 0
            
            for website_data in website_data_list:
                # Check if website already exists for this fileUploadId and URL
                self.cursor.execute("""
                    SELECT id FROM websites 
                    WHERE "fileUploadId" = %s AND "websiteUrl" = %s
                """, (website_data['fileUploadId'], website_data['websiteUrl']))
                
                existing = self.cursor.fetchone()
                
                if existing:
                    logger.info(f"Website already exists, skipping: {website_data['websiteUrl']}")
                    skipped_count += 1
                    continue
                
                query = """
                    INSERT INTO websites (
                        id, "userId", "fileUploadId", "websiteUrl", "contactFormUrl",
                        "scrapingStatus", "messageStatus", "createdAt", "updatedAt"
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                """
                
                website_id = str(uuid.uuid4())
                self.cursor.execute(query, (
                    website_id,
                    website_data['userId'],
                    website_data['fileUploadId'],
                    website_data['websiteUrl'],
                    website_data.get('contactFormUrl'),
                    website_data.get('scrapingStatus', 'PENDING'),
                    website_data.get('messageStatus', 'PENDING')
                ))
                created_count += 1
            
            self.conn.commit()
            logger.info(f"Created {created_count} new website records, skipped {skipped_count} duplicates")
            return True
            
        except Exception as e:
            logger.error(f"Error creating websites batch: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def update_file_upload(self, fileUploadId: str, update_data: Dict[str, Any]) -> bool:
        """
        Update file upload with multiple fields
        
        Args:
            fileUploadId: ID of the file upload to update
            update_data: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._ensure_connection()
            
            # Build dynamic UPDATE query
            set_clauses = []
            values = []
            
            for key, value in update_data.items():
                if key in ['totalWebsites', 'processedWebsites', 'failedWebsites', 'status']:
                    set_clauses.append(f'"{key}" = %s')
                    values.append(value)
            
            if not set_clauses:
                return False
            
            set_clauses.append('"updatedAt" = CURRENT_TIMESTAMP')
            values.append(fileUploadId)
            
            query = f"""
                UPDATE file_uploads 
                SET {', '.join(set_clauses)}
                WHERE id = %s
            """
            
            self.cursor.execute(query, values)
            self.conn.commit()
            
            logger.info(f"Updated file upload {fileUploadId} with {update_data}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating file upload: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def get_file_upload_by_id(self, fileUploadId: str) -> Optional[Dict[str, Any]]:
        """
        Get file upload by ID
        
        Args:
            fileUploadId: ID of the file upload to retrieve
            
        Returns:
            File upload data or None if not found
        """
        try:
            self._ensure_connection()
            
            query = """
                SELECT id, "userId", filename, "originalName", "fileSize", "fileType", 
                       status, "totalWebsites", "processedWebsites", "failedWebsites", 
                       "totalChunks", "completedChunks", "createdAt", "updatedAt"
                FROM file_uploads 
                WHERE id = %s
            """
            
            self.cursor.execute(query, (fileUploadId,))
            result = self.cursor.fetchone()
            
            if result:
                columns = [desc[0] for desc in self.cursor.description]
                return dict(zip(columns, result))
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting file upload by ID: {e}")
            return None 

    def get_file_uploads_by_user_id(self, userId: str) -> List[Dict[str, Any]]:
        """Get all file uploads for a specific user (alias for get_user_file_uploads)"""
        return self.get_user_file_uploads(userId) 

    def get_file_upload_by_original_name(self, original_name: str, userId: str) -> Optional[Dict[str, Any]]:
        """
        Get file upload by original filename and user ID
        
        Args:
            original_name: Original filename to search for
            userId: User ID to filter by
            
        Returns:
            File upload data or None if not found
        """
        try:
            self._ensure_connection()
            
            query = """
                SELECT id, "userId", filename, "originalName", "fileSize", "fileType", 
                       status, "totalWebsites", "processedWebsites", "failedWebsites", 
                       "totalChunks", "completedChunks", "createdAt", "updatedAt"
                FROM file_uploads 
                WHERE "originalName" = %s AND "userId" = %s
                ORDER BY "createdAt" DESC
                LIMIT 1
            """
            
            self.cursor.execute(query, (original_name, userId))
            result = self.cursor.fetchone()
            
            if result:
                columns = [desc[0] for desc in self.cursor.description]
                return dict(zip(columns, result))
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting file upload by original name: {e}")
            return None
    
    def get_website_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get website record by URL
        
        Args:
            url: Website URL to search for
            
        Returns:
            Website data or None if not found
        """
        try:
            self._ensure_connection()
            
            query = """
                SELECT id, "userId", "fileUploadId", "websiteUrl", "companyName", 
                       "businessType", "industry", "aboutUsContent", "scrapingStatus", 
                       "messageStatus", "generatedMessage", "createdAt", "updatedAt"
                FROM websites 
                WHERE "websiteUrl" = %s
                ORDER BY "updatedAt" DESC
                LIMIT 1
            """
            
            self.cursor.execute(query, (url,))
            result = self.cursor.fetchone()
            
            if result:
                columns = [desc[0] for desc in self.cursor.description]
                return dict(zip(columns, result))
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting website by URL: {e}")
            return None
    
    def get_website_by_id(self, website_id: str) -> Optional[Dict[str, Any]]:
        """
        Get website record by ID
        
        Args:
            website_id: Website ID to search for
            
        Returns:
            Website data or None if not found
        """
        try:
            self._ensure_connection()
            
            query = """
                SELECT id, "userId", "fileUploadId", "websiteUrl", "companyName", 
                       "businessType", "industry", "aboutUsContent", "scrapingStatus", 
                       "messageStatus", "generatedMessage", "contactFormUrl", "hasContactForm",
                       "createdAt", "updatedAt"
                FROM websites 
                WHERE id = %s
            """
            
            self.cursor.execute(query, (website_id,))
            result = self.cursor.fetchone()
            
            if result:
                columns = [desc[0] for desc in self.cursor.description]
                return dict(zip(columns, result))
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting website by ID: {e}")
            return None
    
    def update_website_submission_status(self, website_id: str, status: str, submitted_at: datetime = None, 
                                       error_message: str = None, response_received: bool = False, 
                                       submission_method: str = None) -> bool:
        """
        Update website submission status
        
        Args:
            website_id: Website ID to update
            status: New submission status
            submitted_at: When submission was made
            error_message: Error message if submission failed
            response_received: Whether response was received
            submission_method: Method used for submission
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._ensure_connection()
            
            # Build update query dynamically
            set_clauses = []
            values = []
            
            if status:
                set_clauses.append('"submissionStatus" = %s')
                values.append(status)
            
            if submitted_at:
                set_clauses.append('"submittedAt" = %s')
                values.append(submitted_at)
            
            if error_message is not None:
                set_clauses.append('"submissionErrorMessage" = %s')
                values.append(error_message)
            
            if response_received is not None:
                set_clauses.append('"responseReceived" = %s')
                values.append(response_received)
            
            if submission_method:
                set_clauses.append('"submissionMethod" = %s')
                values.append(submission_method)
            
            if not set_clauses:
                return False
            
            set_clauses.append('"updatedAt" = CURRENT_TIMESTAMP')
            values.append(website_id)
            
            query = f"""
                UPDATE websites 
                SET {', '.join(set_clauses)}
                WHERE id = %s
            """
            
            self.cursor.execute(query, values)
            self.conn.commit()
            
            logger.info(f"Updated website {website_id} submission status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating website submission status: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def create_form_submission(self, website_id: str, file_upload_id: str = None, user_id: str = None,
                              submission_status: str = "PENDING", submitted_message: str = "",
                              message_type: str = "general", contact_form_url: str = "",
                              form_fields_used: Dict = None, submission_method: str = "unknown",
                              submitted_at: datetime = None, response_received: bool = False,
                              error_message: str = None, retry_count: int = 0, max_retries: int = 3) -> bool:
        """
        Create a new form submission record
        
        Args:
            website_id: Website ID
            file_upload_id: File upload ID
            user_id: User ID
            submission_status: Status of submission
            submitted_message: Message that was submitted
            message_type: Type of message
            contact_form_url: URL of contact form
            form_fields_used: Fields used in form
            submission_method: Method used for submission
            submitted_at: When submission was made
            response_received: Whether response was received
            error_message: Error message if failed
            retry_count: Number of retry attempts
            max_retries: Maximum retry attempts
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._ensure_connection()
            
            # Convert form_fields_used to JSON string
            form_fields_json = json.dumps(form_fields_used) if form_fields_used else '{}'
            
            query = """
                INSERT INTO form_submissions (
                    id, website_id, file_upload_id, user_id, submission_status,
                    submitted_message, message_type, contact_form_url, form_fields_used,
                    submission_method, submitted_at, response_received, error_message,
                    retry_count, max_retries, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )
            """
            
            # Generate unique ID
            submission_id = f"sub_{int(time.time())}_{random.randint(1000, 9999)}"
            
            values = (
                submission_id, website_id, file_upload_id, user_id, submission_status,
                submitted_message, message_type, contact_form_url, form_fields_json,
                submission_method, submitted_at, response_received, error_message,
                retry_count, max_retries
            )
            
            self.cursor.execute(query, values)
            self.conn.commit()
            
            logger.info(f"Created form submission record {submission_id} for website {website_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating form submission: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def get_form_submission_by_id(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """
        Get form submission by ID
        
        Args:
            submission_id: Submission ID to retrieve
            
        Returns:
            Form submission data or None if not found
        """
        try:
            self._ensure_connection()
            
            query = """
                SELECT id, website_id, file_upload_id, user_id, submission_status,
                       submitted_message, message_type, contact_form_url, form_fields_used,
                       submission_method, submitted_at, response_received, error_message,
                       retry_count, max_retries, created_at, updated_at
                FROM form_submissions 
                WHERE id = %s
            """
            
            self.cursor.execute(query, (submission_id,))
            result = self.cursor.fetchone()
            
            if result:
                columns = [desc[0] for desc in self.cursor.description]
                submission_data = dict(zip(columns, result))
                
                # Parse form_fields_used JSON
                if submission_data.get('form_fields_used'):
                    try:
                        submission_data['form_fields_used'] = json.loads(submission_data['form_fields_used'])
                    except json.JSONDecodeError:
                        submission_data['form_fields_used'] = {}
                
                return submission_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting form submission by ID: {e}")
            return None
    
    def update_form_submission_status(self, submission_id: str, status: str, submitted_at: datetime = None,
                                    submission_method: str = None) -> bool:
        """
        Update form submission status
        
        Args:
            submission_id: Submission ID to update
            status: New status
            submitted_at: When submission was made
            submission_method: Method used for submission
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._ensure_connection()
            
            set_clauses = ['submission_status = %s']
            values = [status]
            
            if submitted_at:
                set_clauses.append('submitted_at = %s')
                values.append(submitted_at)
            
            if submission_method:
                set_clauses.append('submission_method = %s')
                values.append(submission_method)
            
            set_clauses.append('updated_at = CURRENT_TIMESTAMP')
            values.append(submission_id)
            
            query = f"""
                UPDATE form_submissions 
                SET {', '.join(set_clauses)}
                WHERE id = %s
            """
            
            self.cursor.execute(query, values)
            self.conn.commit()
            
            logger.info(f"Updated form submission {submission_id} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating form submission status: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def update_submission_retry_count(self, submission_id: str, retry_count: int) -> bool:
        """
        Update submission retry count
        
        Args:
            submission_id: Submission ID to update
            retry_count: New retry count
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._ensure_connection()
            
            query = """
                UPDATE form_submissions 
                SET retry_count = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            
            self.cursor.execute(query, (retry_count, submission_id))
            self.conn.commit()
            
            logger.info(f"Updated submission {submission_id} retry count to {retry_count}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating submission retry count: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def get_submissions_by_file_upload(self, file_upload_id: str) -> List[Dict[str, Any]]:
        """
        Get all form submissions for a file upload
        
        Args:
            file_upload_id: File upload ID to filter by
            
        Returns:
            List of form submission data
        """
        try:
            self._ensure_connection()
            
            query = """
                SELECT fs.id, fs.website_id, fs.submission_status, fs.submitted_message,
                       fs.message_type, fs.contact_form_url, fs.submission_method,
                       fs.submitted_at, fs.response_received, fs.error_message,
                       fs.retry_count, fs.max_retries, fs.created_at,
                       w."companyName", w."websiteUrl"
                FROM form_submissions fs
                JOIN websites w ON fs.website_id = w.id
                WHERE fs.file_upload_id = %s
                ORDER BY fs.created_at DESC
            """
            
            self.cursor.execute(query, (file_upload_id,))
            results = self.cursor.fetchall()
            
            submissions = []
            if results:
                columns = [desc[0] for desc in self.cursor.description]
                for result in results:
                    submission_data = dict(zip(columns, result))
                    submissions.append(submission_data)
            
            return submissions
            
        except Exception as e:
            logger.error(f"Error getting submissions by file upload: {e}")
            return []
    
    def get_submission_statistics(self, file_upload_id: str = None, user_id: str = None) -> Dict[str, Any]:
        """
        Get submission statistics
        
        Args:
            file_upload_id: Optional file upload ID to filter by
            user_id: Optional user ID to filter by
            
        Returns:
            Dictionary with submission statistics
        """
        try:
            self._ensure_connection()
            
            where_clause = ""
            values = []
            
            if file_upload_id:
                where_clause = "WHERE file_upload_id = %s"
                values.append(file_upload_id)
            elif user_id:
                where_clause = "WHERE user_id = %s"
                values.append(user_id)
            
            query = f"""
                SELECT 
                    COUNT(*) as total_submissions,
                    COUNT(CASE WHEN submission_status = 'SUBMITTED' THEN 1 END) as successful_submissions,
                    COUNT(CASE WHEN submission_status = 'FAILED' THEN 1 END) as failed_submissions,
                    COUNT(CASE WHEN submission_status = 'PENDING' THEN 1 END) as pending_submissions,
                    COUNT(CASE WHEN response_received = true THEN 1 END) as responses_received,
                    AVG(CASE WHEN submitted_at IS NOT NULL THEN EXTRACT(EPOCH FROM (submitted_at - created_at)) END) as avg_processing_time
                FROM form_submissions
                {where_clause}
            """
            
            self.cursor.execute(query, values)
            result = self.cursor.fetchone()
            
            if result:
                columns = [desc[0] for desc in self.cursor.description]
                stats = dict(zip(columns, result))
                
                # Calculate success rate
                if stats['total_submissions'] > 0:
                    stats['success_rate'] = (stats['successful_submissions'] / stats['total_submissions']) * 100
                else:
                    stats['success_rate'] = 0
                
                return stats
            
            return {
                'total_submissions': 0,
                'successful_submissions': 0,
                'failed_submissions': 0,
                'pending_submissions': 0,
                'responses_received': 0,
                'avg_processing_time': 0,
                'success_rate': 0
            }
            
        except Exception as e:
            logger.error(f"Error getting submission statistics: {e}")
            return {}
    
    def update_website_industry(self, website_id: str, industry: str, business_type: str, company_name: str) -> bool:
        """Update website industry, business type, and company name"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE websites 
                        SET industry = %s, "businessType" = %s, "companyName" = %s, "updatedAt" = NOW()
                        WHERE id = %s
                    """, (industry, business_type, company_name, website_id))
                    
                    if cursor.rowcount > 0:
                        logger.info(f"Updated website {website_id} with industry: {industry}, business_type: {business_type}")
                        return True
                    else:
                        logger.warning(f"No website found with ID {website_id}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error updating website industry: {e}")
            return False 