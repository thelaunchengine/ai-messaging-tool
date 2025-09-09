from database.database_manager import DatabaseManager
from datetime import datetime, timedelta

def test_task_metrics_logic():
    print("=== Testing Task Metrics Logic ===")
    
    try:
        db = DatabaseManager()
        file_uploads = db.get_all_file_uploads()
        print(f"Total uploads: {len(file_uploads)}")
        
        tasks = []
        
        for upload in file_uploads[-10:]:  # Last 10 uploads
            print(f"\nChecking upload: {upload.get('id')} - Status: {upload.get('status')}")
            
            if upload.get('status') in ['PENDING', 'PROCESSING', 'COMPLETED']:
                print(f"  Status matches criteria")
                
                # Calculate progress based on chunks
                total_chunks = upload.get('totalChunks', 0)
                completed_chunks = upload.get('completedChunks', 0)
                progress = int((completed_chunks / total_chunks * 100) if total_chunks > 0 else 0)
                print(f"  Progress: {progress}%")
                
                # Calculate duration
                created_at = upload.get('createdAt')
                duration = "0m 0s"
                if created_at:
                    print(f"  Created at: {created_at}")
                    print(f"  Created at type: {type(created_at)}")
                    
                    # Check if it's a datetime object
                    if isinstance(created_at, datetime):
                        now = datetime.now(created_at.tzinfo) if created_at.tzinfo else datetime.now()
                        diff = now - created_at
                        minutes = int(diff.total_seconds() // 60)
                        seconds = int(diff.total_seconds() % 60)
                        duration = f"{minutes}m {seconds}s"
                        print(f"  Duration: {duration}")
                        print(f"  Time difference: {diff}")
                        
                        # Only show tasks from last 24 hours
                        if diff > timedelta(hours=24):
                            print(f"  SKIPPING - older than 24 hours")
                            continue
                        else:
                            print(f"  INCLUDING - within 24 hours")
                    else:
                        print(f"  SKIPPING - created_at is not datetime: {type(created_at)}")
                        continue
                
                tasks.append({
                    "id": upload.get('id', 'unknown'),
                    "type": "file_processing",
                    "status": upload.get('status', 'UNKNOWN'),
                    "progress": progress,
                    "startTime": created_at or "2024-01-15T10:30:00Z",
                    "duration": duration,
                    "errorCount": upload.get('failedWebsites', 0)
                })
                print(f"  Added to tasks list")
            else:
                print(f"  Status does not match criteria")
        
        print(f"\nFinal tasks count: {len(tasks)}")
        return tasks
        
    except Exception as e:
        print(f"Error in task metrics: {e}")
        return []

if __name__ == "__main__":
    test_task_metrics_logic() 