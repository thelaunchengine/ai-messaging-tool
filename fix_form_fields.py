#!/usr/bin/env python3
"""
Script to fix the form fields parameter in the form submission task
"""
import re
import json

def fix_form_fields_parameter():
    # Read the file
    with open('celery_tasks/form_submission_tasks.py', 'r') as f:
        content = f.read()
    
    # Find and replace the update_website_submission call
    old_pattern = r'(\s+success = db_manager\.update_website_submission\(\s+website_id=website\.get\(\'id\'\),\s+submission_status="SUBMITTED" if submission_result\[\'success\'\] else "FAILED",\s+submission_time=submission_result\[\'submission_time\'\],\s+response_content=submission_result\.get\(\'response_page\', \'\'\),\s+error_message=submission_result\.get\(\'error\', \'\'\)\s+\))'
    
    new_pattern = '''                success = db_manager.update_website_submission(
                    website_id=website.get('id'),
                    submission_status="SUBMITTED" if submission_result['success'] else "FAILED"
,

                    submission_time=submission_result['submission_time'],
                    response_content=submission_result.get('response_page', ''),
                    error_message=submission_result.get('error', ''),
                    submitted_form_fields=json.dumps(form_data) if form_data else None
                )'''
    
    # Replace the pattern
    updated_content = re.sub(old_pattern, new_pattern, content, flags=re.DOTALL)
    
    # Write the updated content back
    with open('celery_tasks/form_submission_tasks.py', 'w') as f:
        f.write(updated_content)
    
    print("✅ Form fields parameter added successfully!")

if __name__ == "__main__":
    fix_form_fields_parameter()
