#!/usr/bin/env python3
import sys
import os
sys.path.append('/home/xb3353/Automated-AI-Messaging-Tool-Backend')

from celery_tasks.scraping_tasks import generate_messages_task

def trigger_ai_generation():
    """Trigger AI message generation for the fixed upload"""
    try:
        print("🚀 Triggering AI message generation...")
        
        upload_id = "b1eb86d5-6293-4d90-b3f4-d093b42c0c7d"
        
        # Trigger the AI message generation task
        task = generate_messages_task.delay(upload_id)
        
        print(f"✅ AI message generation task triggered successfully!")
        print(f"   Task ID: {task.id}")
        print(f"   Upload ID: {upload_id}")
        print(f"\n📋 Next steps:")
        print(f"   1. Monitor task progress with task ID: {task.id}")
        print(f"   2. Check upload status after completion")
        print(f"   3. Verify AI messages are properly generated")
        
        return task.id
        
    except Exception as e:
        print(f"❌ Error triggering AI generation: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    trigger_ai_generation()

