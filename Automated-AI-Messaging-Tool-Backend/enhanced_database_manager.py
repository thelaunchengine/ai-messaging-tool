#!/usr/bin/env python3
"""
Enhanced Database Manager with AI Message Support
Handles AI message storage, retrieval, and workflow integration
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncpg
from database_manager import DatabaseManager

logger = logging.getLogger(__name__)

class EnhancedDatabaseManager(DatabaseManager):
    """Enhanced database manager with AI workflow support"""
    
    async def update_website_ai_message(self, website_id: str, ai_message: str, generated_at: str) -> bool:
        """Update website with generated AI message"""
        try:
            async with self.pool.acquire() as conn:
                # Check if ai_message column exists, if not add it
                await self._ensure_ai_message_column(conn)
                
                # Update the website with AI message
                query = """
                UPDATE websites 
                SET ai_message = $1, ai_generated_at = $2, updated_at = NOW()
                WHERE id = $3
                """
                
                result = await conn.execute(query, ai_message, generated_at, website_id)
                logger.info(f"Updated AI message for website {website_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating AI message for website {website_id}: {str(e)}")
            return False
    
    async def _ensure_ai_message_column(self, conn):
        """Ensure ai_message and ai_generated_at columns exist"""
        try:
            # Check if columns exist
            check_query = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'websites' 
            AND column_name IN ('ai_message', 'ai_generated_at')
            """
            
            columns = await conn.fetch(check_query)
            existing_columns = [col['column_name'] for col in columns]
            
            # Add ai_message column if it doesn't exist
            if 'ai_message' not in existing_columns:
                await conn.execute("""
                    ALTER TABLE websites 
                    ADD COLUMN ai_message TEXT
                """)
                logger.info("Added ai_message column to websites table")
            
            # Add ai_generated_at column if it doesn't exist
            if 'ai_generated_at' not in existing_columns:
                await conn.execute("""
                    ALTER TABLE websites 
                    ADD COLUMN ai_generated_at TIMESTAMP
                """)
                logger.info("Added ai_generated_at column to websites table")
                
        except Exception as e:
            logger.error(f"Error ensuring AI message columns: {str(e)}")
    
    async def get_websites_by_file_upload(self, file_upload_id: str) -> List[Dict[str, Any]]:
        """Get all websites for a specific file upload with enhanced data"""
        try:
            async with self.pool.acquire() as conn:
                query = """
                SELECT 
                    w.id,
                    w.website_url,
                    w.company_name,
                    w.industry,
                    w.about_content,
                    w.status,
                    w.created_at,
                    w.updated_at,
                    w.ai_message,
                    w.ai_generated_at,
                    fu.id as file_upload_id
                FROM websites w
                JOIN file_uploads fu ON w.file_upload_id = fu.id
                WHERE fu.id = $1
                ORDER BY w.created_at ASC
                """
                
                rows = await conn.fetch(query, file_upload_id)
                
                websites = []
                for row in rows:
                    website = {
                        'id': row['id'],
                        'website_url': row['website_url'],
                        'company_name': row['company_name'],
                        'industry': row['industry'],
                        'about_content': row['about_content'],
                        'status': row['status'],
                        'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                        'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None,
                        'ai_message': row['ai_message'],
                        'ai_generated_at': row['ai_generated_at'].isoformat() if row['ai_generated_at'] else None,
                        'file_upload_id': row['file_upload_id']
                    }
                    websites.append(website)
                
                logger.info(f"Retrieved {len(websites)} websites for file upload {file_upload_id}")
                return websites
                
        except Exception as e:
            logger.error(f"Error retrieving websites for file upload {file_upload_id}: {str(e)}")
            return []
    
    async def get_ai_generation_status(self, file_upload_id: str) -> Dict[str, Any]:
        """Get AI generation status for a file upload"""
        try:
            async with self.pool.acquire() as conn:
                # Ensure columns exist
                await self._ensure_ai_message_column(conn)
                
                query = """
                SELECT 
                    COUNT(*) as total_websites,
                    COUNT(CASE WHEN ai_message IS NOT NULL THEN 1 END) as ai_messages_generated,
                    COUNT(CASE WHEN ai_message IS NULL THEN 1 END) as pending_ai_generation,
                    MIN(ai_generated_at) as first_generation,
                    MAX(ai_generated_at) as last_generation
                FROM websites w
                JOIN file_uploads fu ON w.file_upload_id = fu.id
                WHERE fu.id = $1
                """
                
                row = await conn.fetchrow(query, file_upload_id)
                
                if row:
                    return {
                        'file_upload_id': file_upload_id,
                        'total_websites': row['total_websites'],
                        'ai_messages_generated': row['ai_messages_generated'],
                        'pending_ai_generation': row['pending_ai_generation'],
                        'completion_percentage': round((row['ai_messages_generated'] / row['total_websites']) * 100, 2) if row['total_websites'] > 0 else 0,
                        'first_generation': row['first_generation'].isoformat() if row['first_generation'] else None,
                        'last_generation': row['last_generation'].isoformat() if row['last_generation'] else None,
                        'status': 'completed' if row['pending_ai_generation'] == 0 else 'in_progress'
                    }
                else:
                    return {
                        'file_upload_id': file_upload_id,
                        'status': 'not_found',
                        'message': 'File upload not found'
                    }
                    
        except Exception as e:
            logger.error(f"Error getting AI generation status: {str(e)}")
            return {
                'file_upload_id': file_upload_id,
                'status': 'error',
                'error': str(e)
            }
    
    async def get_websites_with_ai_messages(self, file_upload_id: str) -> List[Dict[str, Any]]:
        """Get websites that have AI messages generated"""
        try:
            async with self.pool.acquire() as conn:
                await self._ensure_ai_message_column(conn)
                
                query = """
                SELECT 
                    w.id,
                    w.website_url,
                    w.company_name,
                    w.industry,
                    w.about_content,
                    w.ai_message,
                    w.ai_generated_at,
                    w.status
                FROM websites w
                JOIN file_uploads fu ON w.file_upload_id = fu.id
                WHERE fu.id = $1 AND w.ai_message IS NOT NULL
                ORDER BY w.ai_generated_at DESC
                """
                
                rows = await conn.fetch(query, file_upload_id)
                
                websites = []
                for row in rows:
                    website = {
                        'id': row['id'],
                        'website_url': row['website_url'],
                        'company_name': row['company_name'],
                        'industry': row['industry'],
                        'about_content': row['about_content'],
                        'ai_message': row['ai_message'],
                        'ai_generated_at': row['ai_generated_at'].isoformat() if row['ai_generated_at'] else None,
                        'status': row['status']
                    }
                    websites.append(website)
                
                return websites
                
        except Exception as e:
            logger.error(f"Error retrieving websites with AI messages: {str(e)}")
            return []
    
    async def reset_ai_messages_for_file_upload(self, file_upload_id: str) -> bool:
        """Reset AI messages for a file upload (for regeneration)"""
        try:
            async with self.pool.acquire() as conn:
                await self._ensure_ai_message_column(conn)
                
                query = """
                UPDATE websites 
                SET ai_message = NULL, ai_generated_at = NULL, updated_at = NOW()
                WHERE file_upload_id = $1
                """
                
                result = await conn.execute(query, file_upload_id)
                logger.info(f"Reset AI messages for file upload {file_upload_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error resetting AI messages: {str(e)}")
            return False

if __name__ == "__main__":
    # Test the enhanced database manager
    async def test():
        db_manager = EnhancedDatabaseManager()
        await db_manager.connect()
        
        # Test getting AI generation status
        status = await db_manager.get_ai_generation_status("test_upload_id")
        print("AI Generation Status:", status)
        
        await db_manager.close()
    
    asyncio.run(test())
