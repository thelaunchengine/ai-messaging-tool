#!/usr/bin/env python3
import sys
import os

# Add the backend directory to Python path
sys.path.append('/home/xb3353/Automated-AI-Messaging-Tool-Backend')

from celery_tasks.form_submission_tasks import submit_contact_forms_task

def check_task_status(task_id):
    try:
        task = submit_contact_forms_task.AsyncResult(task_id)
        print(f"Task Status: {task.state}")
        print(f"Task Ready: {task.ready()}")
        
        if task.ready():
            if task.successful():
                print(f"Result: {task.result}")
            else:
                print(f"Error: {task.info}")
        else:
            print(f"Task still running...")
            if hasattr(task, 'info') and task.info:
                print(f"Progress: {task.info}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    task_id = "6695cfb6-17b2-4d2b-a4a9-396cc9070363"
    check_task_status(task_id)
