import os
import pg8000
from typing import List, Dict, Optional, Any
import json
from datetime import datetime
from dotenv import load_dotenv
import logging
import time
import random

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:cDtrtoOqpdkAzMcLSd%401847@103.215.159.51:5432/aimsgdb')
        logger.info(f"DatabaseManager initialized with URL: {self.db_url.split('@')[1] if '@' in self.db_url else 'default'}")
    
    def _parse_db_url(self, db_url: str) -> Dict:
        """Parse database URL into connection parameters"""
        # Remove postgresql:// prefix
        if db_url.startswith('postgresql://'):
            db_url = db_url[13:]
        
        # Split into user:pass@host:port/database
        if '@' in db_url:
            auth, rest = db_url.split('@', 1)
            if ':' in auth:
                user, password = auth.split(':', 1)
            else:
                user, password = auth, None
        else:
            user, password = None, None
            rest = db_url
        
        if '/' in rest:
            host_port, database = rest.split('/', 1)
        else:
            host_port, database = rest, None
        
        if ':' in host_port:
            host, port = host_port.split(':', 1)
            port = int(port)
        else:
            host, port = host_port, 5432
        
        return {
            'user': user,
            'password': password,
            'host': host,
            'port': port,
            'database': database
        }
    
    def get_connection(self):
        logger.debug("Getting database connection")
        try:
            conn_params = self._parse_db_url(self.db_url)
            conn = pg8000.Connection(**conn_params)
            logger.debug("Database connection established successfully")
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = False):
        logger.debug(f"Executing query: {query[:100]}...")
        logger.debug(f"Query parameters: {params}")
        
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if fetch:
                result = cursor.fetchall()
                # Convert to list of dicts
                if result and len(result) > 0:
                    columns = [desc[0] for desc in cursor.description]
                    result = [dict(zip(columns, row)) for row in result]
                logger.debug(f"Query returned {len(result)} rows")
                return result
            else:
                conn.commit()
                logger.debug("Query executed successfully")
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Database query failed: {str(e)}")
            logger.error(f"Query: {query}")
            logger.error(f"Parameters: {params}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def execute_query_one(self, query: str, params: tuple = None):
        logger.debug(f"Executing query_one: {query[:100]}...")
        logger.debug(f"Query parameters: {params}")
        
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            conn.commit()
            if result:
                # Convert to dict
                columns = [desc[0] for desc in cursor.description]
                result = dict(zip(columns, result))
            logger.debug(f"Query_one returned: {result is not None}")
            return result
        except Exception as e:
            logger.error(f"Database query_one failed: {str(e)}")
            logger.error(f"Query: {query}")
            logger.error(f"Parameters: {params}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    # File Upload Operations
    def get_file_upload(self, file_upload_id: str) -> Optional[Dict]:
        """Get file upload by ID"""
        logger.info(f"Getting file upload with ID: {file_upload_id}")
        query = """
            SELECT * FROM file_uploads 
            WHERE id = %s
        """
        result = self.execute_query_one(query, (file_upload_id,))
        logger.info(f"File upload found: {result is not None}")
        return result
    
    def update_file_upload(self, file_upload_id: str, data: Dict):
        """Update file upload"""
        logger.info(f"Updating file upload {file_upload_id} with data: {data}")
        set_clause = ", ".join([f'"{k}" = %s' for k in data.keys()])
        query = f"""
            UPDATE file_uploads 
            SET {set_clause}
            WHERE id = %s
        """
        params = list(data.values()) + [file_upload_id]
        logger.debug(f"Update query: {query}")
        logger.debug(f"Update parameters: {params}")
        
        try:
            result = self.execute_query(query, tuple(params))
            logger.info(f"File upload updated successfully, rows affected: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to update file upload: {str(e)}")
            raise
    
    def get_file_uploads_by_user(self, user_id: str) -> List[Dict]:
        """Get all file uploads for a user"""
        query = """
            SELECT * FROM file_uploads 
            WHERE "userId" = %s 
            ORDER BY "createdAt" DESC
        """
        return self.execute_query(query, (user_id,), fetch=True)
    
    # Processing Chunk Operations
    def get_processing_chunk(self, chunk_id: str) -> Optional[Dict]:
        """Get processing chunk by ID"""
        query = """
            SELECT * FROM processing_chunks 
            WHERE id = %s
        """
        return self.execute_query_one(query, (chunk_id,))
    
    def update_processing_chunk(self, chunk_id: str, data: Dict):
        """Update processing chunk"""
        set_clause = ", ".join([f'"{k}" = %s' for k in data.keys()])
        query = f"""
            UPDATE processing_chunks 
            SET {set_clause}
            WHERE id = %s
        """
        params = list(data.values()) + [chunk_id]
        return self.execute_query(query, tuple(params))
    
    def get_chunks_by_file_upload(self, file_upload_id: str) -> List[Dict]:
        """Get all chunks for a file upload"""
        query = """
            SELECT * FROM processing_chunks 
            WHERE "fileUploadId" = %s 
            ORDER BY "chunkNumber"
        """
        return self.execute_query(query, (file_upload_id,), fetch=True)
    
    # Website Operations
    def create_websites_batch(self, websites: List[Dict]):
        """Create multiple websites in batch"""
        if not websites:
            return
        
        def generate_cuid():
            """Generate a simple CUID-like ID"""
            timestamp = int(time.time() * 1000)
            random_part = random.randint(1000, 9999)
            return f"cmc{timestamp}{random_part}"
        
        query = """
            INSERT INTO websites (
                id, "fileUploadId", "userId", "websiteUrl", "contactFormUrl", 
                "hasContactForm", "scrapingStatus", "messageStatus", "createdAt", "updatedAt"
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """
        
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            for website in websites:
                website_id = generate_cuid()
                cursor.execute(query, (
                    website_id,
                    website['file_upload_id'],
                    website['user_id'],
                    website['website_url'],
                    website['contact_form_url'],
                    website['has_contact_form'],
                    website['scraping_status'],
                    website['message_status']
                ))
            conn.commit()
        finally:
            conn.close()
    
    def get_websites_by_file_upload(self, file_upload_id: str) -> List[Dict]:
        """Get all websites for a file upload"""
        query = """
            SELECT * FROM websites 
            WHERE "fileUploadId" = %s 
            ORDER BY "createdAt"
        """
        return self.execute_query(query, (file_upload_id,), fetch=True)
    
    def update_website(self, website_id: str, data: Dict):
        """Update website"""
        set_clause = ", ".join([f'"{k}" = %s' for k in data.keys()])
        query = f"""
            UPDATE websites 
            SET {set_clause}, "updatedAt" = NOW()
            WHERE id = %s
        """
        params = list(data.values()) + [website_id]
        return self.execute_query(query, tuple(params))
    
    def get_website_id_by_url(self, website_url: str) -> Optional[str]:
        """Get website ID by URL"""
        query = """
            SELECT id FROM websites 
            WHERE "websiteUrl" = %s
        """
        result = self.execute_query_one(query, (website_url,))
        return result['id'] if result else None
    
    def get_website(self, website_id: str) -> Optional[Dict]:
        """Get website by ID"""
        query = """
            SELECT * FROM websites 
            WHERE id = %s
        """
        return self.execute_query_one(query, (website_id,))
    
    def get_file_upload_id_by_job(self, job_id: str) -> Optional[str]:
        """Get file upload ID by scraping job ID"""
        query = """
            SELECT "fileUploadId" FROM scraping_jobs 
            WHERE id = %s
        """
        result = self.execute_query_one(query, (job_id,))
        return result['fileUploadId'] if result else None
    
    # Scraping Job Operations
    def create_scraping_job(self, file_upload_id: str, job_data: Dict) -> str:
        """Create a new scraping job"""
        def generate_cuid():
            """Generate a simple CUID-like ID"""
            timestamp = int(time.time() * 1000)
            random_part = random.randint(1000, 9999)
            return f"cmc{timestamp}{random_part}"
        
        job_id = generate_cuid()
        
        query = """
            INSERT INTO scraping_jobs (
                id, "fileUploadId", "status", "totalWebsites", "processedWebsites", "failedWebsites", "createdAt", "updatedAt"
            ) VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
        """
        
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (
                job_id,
                file_upload_id,
                job_data.get('status', 'PENDING'),
                job_data.get('totalWebsites', 0),
                job_data.get('processedWebsites', 0),
                job_data.get('failedWebsites', 0)
            ))
            conn.commit()
            return job_id
        finally:
            conn.close()
    
    def update_scraping_job(self, job_id: str, data: Dict):
        """Update scraping job"""
        set_clause = ", ".join([f'"{k}" = %s' for k in data.keys()])
        query = f"""
            UPDATE scraping_jobs 
            SET {set_clause}, "updatedAt" = NOW()
            WHERE id = %s
        """
        params = list(data.values()) + [job_id]
        return self.execute_query(query, tuple(params))
    
    def get_scraping_jobs_by_file_upload(self, file_upload_id: str) -> List[Dict]:
        """Get all scraping jobs for a file upload"""
        query = """
            SELECT * FROM scraping_jobs 
            WHERE "fileUploadId" = %s 
            ORDER BY "createdAt" DESC
        """
        return self.execute_query(query, (file_upload_id,), fetch=True)
    
    # Predefined Messages Operations
    def get_predefined_messages(self) -> List[Dict]:
        """Get all predefined messages"""
        query = """
            SELECT * FROM predefined_messages 
            ORDER BY "createdAt" DESC
        """
        return self.execute_query(query, fetch=True)
    
    def create_predefined_message(self, message_data: Dict):
        """Create a new predefined message"""
        query = """
            INSERT INTO predefined_messages (
                "message", "service", "industry", "status", "createdAt", "updatedAt"
            ) VALUES (%s, %s, %s, %s, NOW(), NOW())
        """
        return self.execute_query(query, (
            message_data['message'],
            message_data.get('service', 'general'),
            message_data.get('industry', 'general'),
            message_data.get('status', 'active')
        ))
    
    def update_predefined_message(self, message_id: str, data: Dict):
        """Update predefined message"""
        set_clause = ", ".join([f'"{k}" = %s' for k in data.keys()])
        query = f"""
            UPDATE predefined_messages 
            SET {set_clause}, "updatedAt" = NOW()
            WHERE id = %s
        """
        params = list(data.values()) + [message_id]
        return self.execute_query(query, tuple(params))
    
    def delete_predefined_message(self, message_id: str):
        """Delete predefined message"""
        query = "DELETE FROM predefined_messages WHERE id = %s"
        return self.execute_query(query, (message_id,))
    
    def cleanup_old_scraping_jobs(self, days: int = 30):
        """Clean up old scraping jobs"""
        query = """
            DELETE FROM scraping_jobs 
            WHERE "createdAt" < NOW() - INTERVAL '%s days'
        """
        return self.execute_query(query, (days,))
    
    def cleanup_old_file_uploads(self, days: int = 90):
        """Clean up old file uploads"""
        query = """
            DELETE FROM file_uploads 
            WHERE "createdAt" < NOW() - INTERVAL '%s days'
        """
        return self.execute_query(query, (days,)) 