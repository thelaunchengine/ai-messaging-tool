"""
Celery tasks for file processing
"""
from celery import current_task
from celery_app import celery_app
import time
import logging
from datetime import datetime
from typing import List, Dict, Any
import csv
import json
from database.database_manager import DatabaseManager
import pandas as pd
from urllib.parse import urlparse
from services.s3_service import S3Service

logger = logging.getLogger(__name__)

def validate_website_url(url: str) -> bool:
    """Validate website URL format"""
    try:
        # Basic URL validation
        parsed = urlparse(url)
        
        # Must have scheme and netloc
        if not parsed.scheme or not parsed.netloc:
            return False
        
        # Must be HTTP/HTTPS
        if parsed.scheme not in ['http', 'https']:
            return False
        
        # Must have valid domain
        if len(parsed.netloc.split('.')) < 2:
            return False
        
        return True
        
    except Exception:
        return False

def parse_csv_file(file_path: str, website_url_column: str = "websiteUrl", contact_form_url_column: str = "contactFormUrl") -> List[Dict]:
    """Parse CSV file with flexible column detection and mapping - supports both local files and S3 keys"""
    websites = []
    
    try:
        # Check if file_path is an S3 key (starts with 'uploads/')
        if file_path.startswith('uploads/'):
            # Download file from S3
            s3_service = S3Service()
            file_content = s3_service.download_file(file_path)
            if not file_content:
                raise Exception(f"Failed to download file from S3: {file_path}")
            
            # Parse CSV from memory
            content_str = file_content.decode('utf-8')
            reader = csv.DictReader(content_str.splitlines())
        else:
            # Local file
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
            
        for row in reader:
                # Use provided column mapping with fallback to flexible detection
                website_url = (
                    row.get(website_url_column) or
                    row.get('Website URL') or 
                    row.get('website_url') or 
                    row.get('website url') or
                    row.get('Website') or
                    row.get('URL') or
                    row.get('url') or
                    row.get('site') or
                    row.get('Site') or
                    row.get('domain') or
                    row.get('Domain')
                )
                
                contact_form_url = (
                    row.get(contact_form_url_column) or
                    row.get('Contact Form URL') or
                    row.get('contact_form_url') or
                    row.get('contact form url') or
                    row.get('website url contact') or
                    row.get('Contact Form') or
                    row.get('Contact') or
                    row.get('contact') or
                    row.get('form') or
                    row.get('Form') or
                    row.get('contact_url') or
                    row.get('contact url') or
                    row.get('form_url') or
                    row.get('form url') or
                    row.get('email') or
                    row.get('Email')
                )
                
                if website_url and validate_website_url(website_url):
                    # Validate contact form URL - allow about pages if they contain contact forms
                    if contact_form_url:
                        contact_form_url_lower = contact_form_url.lower()
                        about_patterns = ['about', 'about-us', 'aboutus', 'company', 'who-we-are', 'our-story']
                        if any(pattern in contact_form_url_lower for pattern in about_patterns):
                            logger.info(f"Contact form URL points to about page: {contact_form_url} for {website_url}")
                            # Don't clear it - this is a valid case where contact form is embedded in about page
                    
                    websites.append({
                        'website_url': website_url.strip(),
                        'contact_form_url': contact_form_url.strip() if contact_form_url else None
                    })
                elif website_url:
                    logger.warning(f"Invalid URL format: {website_url}")
    
    except Exception as e:
        logger.error(f"Error parsing CSV file {file_path}: {str(e)}")
        raise
    
    return websites

def parse_excel_file(file_path: str, website_url_column: str = "websiteUrl", contact_form_url_column: str = "contactFormUrl") -> List[Dict]:
    """Parse Excel file with flexible column detection and mapping"""
    websites = []
    
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Convert to list of dictionaries
        rows = df.to_dict('records')
        
        for row in rows:
            # Use provided column mapping with fallback to flexible detection
            website_url = None
            contact_form_url = None
            
            # First try the provided column names
            if website_url_column in df.columns and row.get(website_url_column):
                website_url = str(row[website_url_column])
            elif contact_form_url_column in df.columns and row.get(contact_form_url_column):
                contact_form_url = str(row[contact_form_url_column])
            
            # Fallback to flexible column detection
            if not website_url:
                for col in df.columns:
                    col_lower = col.lower()
                    if any(keyword in col_lower for keyword in ['website', 'url', 'site']):
                        if row.get(col):
                            website_url = str(row[col])
                            break
            
            if not contact_form_url:
                for col in df.columns:
                    col_lower = col.lower()
                    if any(keyword in col_lower for keyword in ['contact', 'form']):
                        if row.get(col):
                            contact_form_url = str(row[col])
                            break
            
            if website_url and validate_website_url(website_url):
                websites.append({
                    'website_url': website_url.strip(),
                    'contact_form_url': contact_form_url.strip() if contact_form_url else None
                })
            elif website_url:
                logger.warning(f"Invalid URL format: {website_url}")
    
    except Exception as e:
        logger.error(f"Error parsing Excel file {file_path}: {str(e)}")
        raise
    
    return websites

def extract_websites_from_file(file_path: str, file_type: str, website_url_column: str = "websiteUrl", contact_form_url_column: str = "contactFormUrl") -> List[Dict]:
    """Extract website URLs from uploaded file with enhanced parsing and column mapping"""
    if file_type.lower() == 'csv':
        return parse_csv_file(file_path, website_url_column, contact_form_url_column)
    elif file_type.lower() in ['xlsx', 'xls']:
        return parse_excel_file(file_path, website_url_column, contact_form_url_column)
    else:
        raise ValueError(f"Unsupported file format: {file_type}")

@celery_app.task(bind=True)
def process_file_upload_task(self, fileUploadId: str, file_path: str, file_type: str, total_chunks: int, userId: str, website_url_column: str = "websiteUrl", contact_form_url_column: str = "contactFormUrl"):
    # Handle both userId and user_id parameters for backward compatibility
    task_id = self.request.id
    logger.info(f"Starting file processing task {task_id} for upload {fileUploadId}")
    
    try:
        # Initialize database manager
        db = DatabaseManager()
        
        # Update status to PROCESSING
        db.update_file_upload(fileUploadId, {
            'status': 'PROCESSING',
            'processingStartedAt': datetime.now().isoformat()
        })
        
        # Process file in chunks
        processed_chunk_ids = []
        total_records = 0
        
        for chunk in range(total_chunks):
            try:
                # Process chunk
                chunk_result = process_chunk_task.delay(
                    chunk_id=f"{fileUploadId}-chunk-{chunk}",
                    chunk_number=chunk,
                    start_row=chunk * 100,
                    end_row=(chunk + 1) * 100,
                    file_path=file_path,
                    file_type=file_type
                )
                
                # Store only the task ID, not the AsyncResult object
                processed_chunk_ids.append(chunk_result.id)
                total_records += 100
                
                logger.info(f"Processed chunk {chunk + 1}/{total_chunks} with task ID: {chunk_result.id}")
                
            except Exception as chunk_error:
                logger.error(f"Error processing chunk {chunk}: {chunk_error}")
                # Don't fail the entire task for one chunk error
                continue
        
        # Update file upload status (without fake statistics)
        db.update_file_upload(fileUploadId, {
            'status': 'PENDING',  # Will be updated by website extraction
            'processingCompletedAt': datetime.now().isoformat(),
            'completedChunks': len(processed_chunk_ids)
            # totalWebsites and processedWebsites will be set by website extraction task
        })

        # Check if websites were already extracted to prevent duplicate processing
        existing_websites = db.get_websites_by_file_upload_id(fileUploadId)
        if existing_websites:
            logger.info(f"🔍 [DEBUG] Websites already exist for fileUploadId: {fileUploadId}, skipping duplicate extraction")
            logger.info(f"🔍 [DEBUG] Found {len(existing_websites)} existing websites")
            
            # Since websites already exist, trigger scraping and AI generation directly
            try:
                from celery_tasks.scraping_tasks import scrape_websites_task
                
                # Get website URLs for scraping
                website_urls = [website['websiteUrl'] for website in existing_websites]
                
                # Create scraping job
                scraping_job_data = {
                    'fileUploadId': fileUploadId,
                    'totalWebsites': len(existing_websites),
                    'status': 'PENDING',
                    'processedWebsites': 0,
                    'failedWebsites': 0
                }
                success = db.create_scraping_job_from_data(scraping_job_data)
                
                if success:
                    logger.info(f"Created scraping job for file upload {fileUploadId} with {len(existing_websites)} websites")
                    
                    # Start scraping task automatically
                    scraping_task = scrape_websites_task.delay(
                        fileUploadId=fileUploadId,
                        userId=userId,
                        websites=website_urls
                    )
                    
                    logger.info(f"Automatically triggered scraping task {scraping_task.id} for {len(website_urls)} websites")
                else:
                    logger.error(f"Failed to create scraping job for file upload {fileUploadId}")
                    
            except Exception as e:
                logger.error(f"Error triggering scraping for existing websites: {e}")
        else:
            # Only trigger website extraction if no websites exist yet
            logger.info(f"🔍 [DEBUG] About to trigger website extraction for fileUploadId: {fileUploadId}")
            logger.info(f"🔍 [DEBUG] Call stack: {self.request.id} - process_file_upload_task")
            logger.info(f"🔍 [DEBUG] File path: {file_path}, File type: {file_type}")
            logger.info(f"🔍 [DEBUG] Column mapping: {website_url_column}, {contact_form_url_column}")
            
            task = extract_websites_from_file_task.apply_async(
                args=[file_path, file_type, fileUploadId, userId, website_url_column, contact_form_url_column],
                countdown=2  # Small delay to ensure file processing is complete
            )
            
            logger.info(f"🔍 [DEBUG] Website extraction task triggered with task_id: {task.id}")
            
            # Don't include the AsyncResult object in the return value
            # Just log the task ID and continue

        # Task completed successfully
        final_result = {
            'file_upload_id': fileUploadId,
            'file_path': file_path,
            'file_type': file_type,
            'total_chunks': total_chunks,
            'chunks_processed': len(processed_chunk_ids),
            'total_records': total_records,
            'processed_chunk_ids': processed_chunk_ids,  # Store task IDs instead of AsyncResult objects
            'user_id': userId,
            'completed_at': datetime.now().isoformat()
        }
        
        logger.info(f"File processing task {task_id} completed successfully")
        return final_result
        
    except Exception as e:
        logger.error(f"File processing task {task_id} failed: {e}")
        # Don't immediately set status to FAILED - let the workflow continue
        # Only set to FAILED if this is a critical, unrecoverable error
        if "critical" in str(e).lower() or "unrecoverable" in str(e).lower():
            db.update_file_upload(fileUploadId, {
                'status': 'FAILED',
                'processingCompletedAt': datetime.now().isoformat()
            })
        else:
            # Set to ERROR instead of FAILED for recoverable errors
            db.update_file_upload(fileUploadId, {
                'status': 'ERROR',
                'processingCompletedAt': datetime.now().isoformat()
            })
        
        # Retry the task instead of immediately failing
        raise self.retry(countdown=60, max_retries=3, exc=e)

@celery_app.task(bind=True)
def process_chunk_task(self, chunk_id: str, chunk_number: int, start_row: int, end_row: int, file_path: str, file_type: str):
    """
    Process a single chunk of a file
    """
    task_id = self.request.id
    db = DatabaseManager()
    
    try:
        logger.info(f"Starting chunk processing task {task_id} for chunk {chunk_number}")
        
        # Update chunk status
        db.update_processing_chunk(chunk_id, {
            'status': 'PROCESSING',
            'startedAt': datetime.now().isoformat()
        })
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': end_row - start_row,
                'status': f'Processing chunk {chunk_number}...',
                'chunk_id': chunk_id,
                'file_path': file_path
            }
        )
        
        # Simulate processing each row in the chunk
        records_processed = 0
        failed_records = 0
        
        for row_num in range(start_row, end_row + 1):
            # Simulate row processing
            time.sleep(0.1)
            
            progress = int((row_num - start_row + 1) / (end_row - start_row + 1) * 100)
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': row_num - start_row + 1,
                    'total': end_row - start_row + 1,
                    'progress': progress,
                    'status': f'Processing row {row_num} in chunk {chunk_number}',
                    'current_row': row_num
                }
            )
            
            # Simulate successful processing
            records_processed += 1
        
        # Update chunk status
        db.update_processing_chunk(chunk_id, {
            'status': 'COMPLETED',
            'processedRecords': records_processed,
            'failedRecords': failed_records,
            'completedAt': datetime.now().isoformat()
        })
        
        # Task completed successfully
        final_result = {
            'chunk_id': chunk_id,
            'chunk_number': chunk_number,
            'start_row': start_row,
            'end_row': end_row,
            'records_processed': records_processed,
            'file_path': file_path,
            'file_type': file_type,
            'status': 'completed',
            'completed_at': datetime.now().isoformat()
        }
        
        logger.info(f"Chunk processing task {task_id} completed successfully")
        return final_result
        
    except Exception as e:
        logger.error(f"Chunk processing task {task_id} failed: {e}")
        # Update chunk status to failed
        db.update_processing_chunk(chunk_id, {
            'status': 'FAILED',
            'errorMessage': str(e),
            'completedAt': datetime.now().isoformat()
        })
        raise self.retry(countdown=60, max_retries=3, exc=e)

@celery_app.task(bind=True)
def extract_websites_from_file_task(self, file_path: str, file_type: str, fileUploadId: str = None, userId: str = None, website_url_column: str = "websiteUrl", contact_form_url_column: str = "contactFormUrl"):
    """
    Extract websites from file and save to database
    """
    task_id = self.request.id
    db = DatabaseManager()
    
    # 🔍 DEBUG: Track task execution
    import traceback
    logger.info(f"🔍 [DEBUG] ===== WEBSITE EXTRACTION TASK STARTED =====")
    logger.info(f"🔍 [DEBUG] Task ID: {task_id}")
    logger.info(f"🔍 [DEBUG] File upload ID: {fileUploadId}")
    logger.info(f"🔍 [DEBUG] File path: {file_path}")
    logger.info(f"🔍 [DEBUG] File type: {file_type}")
    logger.info(f"🔍 [DEBUG] User ID: {userId}")
    logger.info(f"🔍 [DEBUG] Call stack:")
    for line in traceback.format_stack():
        logger.info(f"🔍 [DEBUG]   {line.strip()}")
    logger.info(f"🔍 [DEBUG] ===========================================")
    
    try:
        logger.info(f"Starting website extraction task {task_id} from file {file_path}")
        
        # Check if websites already exist for this fileUploadId to prevent duplicates
        if fileUploadId:
            logger.info(f"🔍 [DEBUG] Checking for existing websites for fileUploadId: {fileUploadId}")
            existing_websites = db.get_websites_by_file_upload_id(fileUploadId)
            logger.info(f"🔍 [DEBUG] Found {len(existing_websites)} existing websites")
            if existing_websites:
                logger.warning(f"🔍 [DEBUG] DUPLICATE DETECTED! Websites already exist for fileUploadId {fileUploadId}. Skipping extraction to prevent duplicates.")
                return {
                    'file_path': file_path,
                    'file_type': file_type,
                    'websites_extracted': len(existing_websites),
                    'websites': [{'url': w['websiteUrl'], 'contact_form_url': w.get('contactFormUrl')} for w in existing_websites],
                    'completed_at': datetime.now().isoformat(),
                    'status': 'skipped_duplicate'
                }
        
        # Add a small delay to prevent race conditions between simultaneous calls
        import time
        logger.info(f"🔍 [DEBUG] Adding 1-second delay to prevent race conditions")
        time.sleep(1)
        
        # Double-check after delay to ensure no duplicates were created by another task
        if fileUploadId:
            logger.info(f"🔍 [DEBUG] Double-checking for duplicates after delay")
            existing_websites = db.get_websites_by_file_upload_id(fileUploadId)
            logger.info(f"🔍 [DEBUG] Found {len(existing_websites)} websites after delay")
            if existing_websites:
                logger.warning(f"🔍 [DEBUG] DUPLICATE DETECTED AFTER DELAY! Websites were created by another task for fileUploadId {fileUploadId}. Skipping extraction.")
                return {
                    'file_path': file_path,
                    'file_type': file_type,
                    'websites_extracted': len(existing_websites),
                    'websites': [{'url': w['websiteUrl'], 'contact_form_url': w.get('contactFormUrl')} for w in existing_websites],
                    'completed_at': datetime.now().isoformat(),
                    'status': 'skipped_duplicate'
                }
        
        # Read the actual file with enhanced parsing
        websites = []
        
        try:
            # Use enhanced file parsing with column mapping
            parsed_websites = extract_websites_from_file(file_path, file_type, website_url_column, contact_form_url_column)
            
            # Convert to expected format
            for website in parsed_websites:
                websites.append({
                    'url': website['website_url'],
                    'contact_form_url': website['contact_form_url']
                })
                
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {str(e)}")
            raise
        
        logger.info(f"Extracted {len(websites)} websites from file")
        
        # Save websites to database
        website_data_list = []
        for website in websites:
            website_data = {
                'userId': userId,
                'fileUploadId': fileUploadId,
                'websiteUrl': website['url'],
                'scrapingStatus': 'PENDING',
                'messageStatus': 'PENDING'
            }
            website_data_list.append(website_data)
        
        if website_data_list:
            success = db.create_websites_batch(website_data_list)
            if not success:
                logger.error("Failed to save websites to database")
                raise Exception("Database save failed")
        
        # Update file upload with website count and status
        if fileUploadId:
            db.update_file_upload(fileUploadId, {
                'totalWebsites': len(websites),
                'processedWebsites': 0,  # Will be updated by scraping task
                'status': 'COMPLETED'  # Mark as completed after website extraction
            })
            
            # Create scraping job automatically after website extraction
            try:
                scraping_job_data = {
                    'fileUploadId': fileUploadId,
                    'totalWebsites': len(websites),
                    'status': 'PENDING',
                    'processedWebsites': 0,
                    'failedWebsites': 0
                }
                success = db.create_scraping_job_from_data(scraping_job_data)
                if success:
                    logger.info(f"Created scraping job for file upload {fileUploadId} with {len(websites)} websites")
                    
                    # AUTOMATICALLY TRIGGER SCRAPING TASK
                    from celery_tasks.scraping_tasks import scrape_websites_task
                    
                    # Get website URLs for scraping
                    website_urls = [website['url'] for website in websites]
                    
                    # Start scraping task automatically
                    scraping_task = scrape_websites_task.delay(
                        fileUploadId=fileUploadId,
                        userId=userId,
                        websites=website_urls
                    )
                    
                    logger.info(f"Automatically triggered scraping task {scraping_task.id} for {len(website_urls)} websites")
                    
                else:
                    logger.error(f"Failed to create scraping job for file upload {fileUploadId}")
            except Exception as e:
                logger.error(f"Error creating scraping job: {e}")
        
        final_result = {
            'file_path': file_path,
            'file_type': file_type,
            'websites_extracted': len(websites),
            'websites': websites,
            'completed_at': datetime.now().isoformat()
        }
        
        logger.info(f"Website extraction task {task_id} completed successfully")
        return final_result
        
    except Exception as e:
        logger.error(f"Website extraction task {task_id} failed: {e}")
        raise self.retry(countdown=60, max_retries=3, exc=e) 