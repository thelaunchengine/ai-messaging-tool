#!/usr/bin/env python3
import sys
import os

# Add the backend directory to Python path
sys.path.append('/home/xb3353/Automated-AI-Messaging-Tool-Backend')

from celery_tasks.scraping_tasks import generate_messages_task

def check_ai_task_status(task_id):
    try:
        task = generate_messages_task.AsyncResult(task_id)
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
    task_id = "1b005f7e-ab0f-4fbc-8715-6e94b16e3ffb"
    check_ai_task_status(task_id)
