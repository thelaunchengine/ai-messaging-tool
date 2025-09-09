#!/usr/bin/env python3
"""
Fix database column mismatch issues by updating snake_case to camelCase
"""

import os
import sys
from pathlib import Path

def fix_database_columns():
    """Fix database column references from snake_case to camelCase"""
    
    # Files to check and fix
    files_to_check = [
        "celery_tasks/scraping_tasks.py",
        "database/database_manager.py", 
        "main.py"
    ]
    
    # Column mappings from snake_case to camelCase
    column_mappings = {
        "user_id": "userId",
        "file_upload_id": "fileUploadId", 
        "website_url": "websiteUrl",
        "contact_form_url": "contactFormUrl",
        "company_name": "companyName",
        "business_type": "businessType",
        "about_us_content": "aboutUsContent",
        "scraping_status": "scrapingStatus",
        "message_status": "messageStatus",
        "generated_message": "generatedMessage",
        "created_at": "createdAt",
        "updated_at": "updatedAt",
        "total_websites": "totalWebsites",
        "processed_websites": "processedWebsites",
        "failed_websites": "failedWebsites",
        "total_chunks": "totalChunks",
        "completed_chunks": "completedChunks",
        "original_name": "originalName",
        "file_size": "fileSize",
        "file_type": "fileType"
    }
    
    print("🔧 Fixing database column references...")
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            continue
            
        print(f"📁 Processing: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            changes_made = 0
            
            # Replace column references
            for snake_case, camel_case in column_mappings.items():
                # Replace in SQL queries (with quotes)
                content = content.replace(f'"{snake_case}"', f'"{camel_case}"')
                content = content.replace(f"'{snake_case}'", f"'{camel_case}'")
                
                # Replace in Python code (without quotes)
                content = content.replace(f'.{snake_case}', f'.{camel_case}')
                content = content.replace(f'["{snake_case}"]', f'["{camel_case}"]')
                content = content.replace(f"['{snake_case}']", f"['{camel_case}']")
                
                # Replace in variable assignments
                content = content.replace(f'{snake_case} =', f'{camel_case} =')
                content = content.replace(f'= {snake_case}', f'= {camel_case}')
                
                # Replace in function parameters
                content = content.replace(f'{snake_case}:', f'{camel_case}:')
                
                # Replace in f-strings
                content = content.replace(f'{{{snake_case}}}', f'{{{camel_case}}}')
                
                # Replace in comments
                content = content.replace(f'# {snake_case}', f'# {camel_case}')
                content = content.replace(f'""" {snake_case}', f'""" {camel_case}')
                content = content.replace(f"''' {snake_case}", f"''' {camel_case}")
            
            # Count changes
            if content != original_content:
                changes_made = content.count('userId') - original_content.count('user_id')
                changes_made += content.count('fileUploadId') - original_content.count('file_upload_id')
                changes_made += content.count('websiteUrl') - original_content.count('website_url')
                
                # Write updated content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Updated {file_path} with {changes_made} column reference changes")
            else:
                print(f"✅ No changes needed in {file_path}")
                
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    print("\n🎯 Database column fix completed!")
    print("📋 Summary of changes:")
    print("   - Updated snake_case column references to camelCase")
    print("   - Fixed SQL queries and Python code")
    print("   - Updated function parameters and variable names")
    print("\n🚀 Next steps:")
    print("   1. Restart the backend services")
    print("   2. Test the CSV upload workflow")
    print("   3. Verify AI message generation works")

if __name__ == "__main__":
    fix_database_columns()
