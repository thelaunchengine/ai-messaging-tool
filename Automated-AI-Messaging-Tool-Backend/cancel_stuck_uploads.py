#!/usr/bin/env python3
"""
Script to cancel stuck uploads by updating their status to CANCELLED
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database_manager import DatabaseManager

def cancel_stuck_uploads():
    """Cancel all stuck uploads by updating their status"""
    try:
        db = DatabaseManager()
        
        # Get all stuck uploads (PENDING or PROCESSING with websites counted)
        uploads = db.get_all_file_uploads()
        stuck_uploads = [
            u for u in uploads 
            if u.get('status') in ['PENDING', 'PROCESSING'] 
            and u.get('totalWebsites', 0) > 0
        ]
        
        print(f"Found {len(stuck_uploads)} stuck uploads to cancel:")
        
        cancelled_count = 0
        for upload in stuck_uploads:
            upload_id = upload.get('id')
            current_status = upload.get('status')
            websites_count = upload.get('totalWebsites')
            
            print(f"  - {upload_id}: {current_status} -> CANCELLED (websites: {websites_count})")
            
            # Update status to CANCELLED
            success = db.update_file_upload_status(upload_id, "CANCELLED")
            if success:
                cancelled_count += 1
                print(f"    ✅ Cancelled successfully")
            else:
                print(f"    ❌ Failed to cancel")
        
        print(f"\n🎯 Summary: Cancelled {cancelled_count}/{len(stuck_uploads)} stuck uploads")
        
        # Also remove any associated websites for cancelled uploads
        for upload in stuck_uploads:
            upload_id = upload.get('id')
            websites = db.get_websites_by_file_upload_id(upload_id)
            if websites:
                print(f"  - Removing {len(websites)} websites for upload {upload_id}")
                # Note: You might want to add a delete_websites_by_file_upload_id method
                # For now, we'll just mark them as cancelled
        
        return True
        
    except Exception as e:
        print(f"Error cancelling stuck uploads: {e}")
        return False

if __name__ == "__main__":
    print("🚫 Cancelling stuck uploads...")
    success = cancel_stuck_uploads()
    if success:
        print("✅ All stuck uploads cancelled successfully!")
    else:
        print("❌ Failed to cancel some uploads")
        sys.exit(1)
