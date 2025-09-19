from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

# Create Celery app
celery_app = Celery(
    'ai_messaging_tool',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task
def test_task(message: str):
    """Simple test task"""
    return f"Task completed: {message}"

@celery_app.task
def process_websites_task(websites: list, message_type: str = "general"):
    """Process websites in background"""
    results = []
    for website in websites:
        # Simulate processing
        result = {
            'website_url': website.get('url', ''),
            'status': 'processed',
            'message_type': message_type
        }
        results.append(result)
    return results

@celery_app.task
def process_chunk_task(chunk_id: str, chunk_number: int, start_row: int, end_row: int, file_path: str, file_type: str, user_id: str = None):
    """Process a file chunk in background"""
    # Simulate processing
    return {
        'chunk_id': chunk_id,
        'chunk_number': chunk_number,
        'status': 'completed',
        'processed_rows': end_row - start_row
    }

if __name__ == '__main__':
    celery_app.start() 