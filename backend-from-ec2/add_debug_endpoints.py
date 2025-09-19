#!/usr/bin/env python3
"""
Add debug endpoints to main.py
"""
import os

# Read the main.py file
with open('main.py', 'r') as f:
    content = f.read()

# Find the line before if __name__ == "__main__":
lines = content.split('\n')
insert_index = None

for i, line in enumerate(lines):
    if 'if __name__ == "__main__":' in line:
        insert_index = i
        break

if insert_index is not None:
    # Create the debug endpoints code
    debug_endpoints = '''# Debug endpoints for upload troubleshooting
@app.get("/api/upload/{upload_id}/scraping-jobs")
async def get_scraping_jobs(upload_id: str):
    """Get scraping jobs for a specific upload"""
    try:
        db = DatabaseManager()
        connection = db.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT id, status, "createdAt", "updatedAt"
            FROM scraping_jobs 
            WHERE "fileUploadId" = %s
            ORDER BY "createdAt" DESC
        """, (upload_id,))
        
        jobs = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return {
            "jobs": [
                {
                    "id": job[0],
                    "status": job[1],
                    "createdAt": job[2].isoformat() if job[2] else None,
                    "updatedAt": job[3].isoformat() if job[3] else None
                }
                for job in jobs
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching scraping jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/upload/{upload_id}/contact-inquiries")
async def get_contact_inquiries(upload_id: str):
    """Get contact inquiries for a specific upload"""
    try:
        db = DatabaseManager()
        inquiries = db.get_all_contact_inquiries()
        
        # Filter for this upload
        upload_inquiries = [
            inquiry for inquiry in inquiries 
            if inquiry.get("fileUploadId") == upload_id
        ]
        
        return {
            "inquiries": [
                {
                    "id": inquiry.get("id"),
                    "websiteUrl": inquiry.get("websiteUrl"),
                    "status": inquiry.get("status"),
                    "submissionStatus": inquiry.get("submissionStatus"),
                    "message": inquiry.get("message"),
                    "createdAt": inquiry.get("createdAt").isoformat() if inquiry.get("createdAt") else None
                }
                for inquiry in upload_inquiries
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching contact inquiries: {e}")
        raise HTTPException(status_code=500, detail=str(e))
'''
    
    # Insert the debug endpoints
    lines.insert(insert_index, debug_endpoints)
    
    # Write back to file
    with open('main.py', 'w') as f:
        f.write('\n'.join(lines))
    
    print("Debug endpoints added successfully!")
else:
    print("Could not find the insertion point in main.py")
