#!/usr/bin/env python3
"""
Test script to manually trigger contact form submission
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append('/home/xb3353/Automated-AI-Messaging-Tool-Backend')

from celery_app import celery_app
from celery_tasks.form_submission_tasks import submit_contact_forms_task

def test_contact_form_submission():
    """Test contact form submission for existing websites"""
    
    # Website data from the database
    websites_data = [
        {
            'id': 'e193b470-9558-4978-8cfd-3f2fcfacfbff',
            'websiteUrl': 'http://Arauto505.com',
            'contactFormUrl': 'https://www.arauto505.com/contact-us/',
            'generatedMessage': 'Subject: Collaboration Opportunity: A&R Auto Sales LLC & [Sender Company Name]\n\nDear A&R Auto Sales LLC Team,\n\nAs a fellow e-commerce business specializing in [Sender Company\'s Specialization], we\'ve been impressed by A&R Auto Sales LLC\'s success in the Albuquerque market. We believe our services could significantly enhance your online presence and customer experience.\n\nWe\'d value the opportunity to discuss potential collaborations that leverage our expertise in [briefly describe your area of expertise] to boost your sales and streamline your operations.\n\nWould you be available for a brief introductory call next week to explore this further? Please let me know your availability.\n\nSincerely,\n\nJohn Smith\n[Sender Company Name]\n[Phone Number]\n[Email Address]'
        },
        {
            'id': '7d7c99ad-d596-48a6-9f40-e498bb57f6c9',
            'websiteUrl': 'https://agents.farmers.com/ca/santa-clarita/randa-nasrawi',
            'contactFormUrl': 'https://www.farmers.com/contact-us/',
            'generatedMessage': 'Subject: Collaboration Opportunity: Farmers Insurance & [Your Company Name]\n\nDear [Contact Person Name],\n\nFind a Farmers Insurance® Agent in Santa Clarita, CA | Farmers Insurance® is a respected leader in the insurance industry, and we at [Your Company Name] are impressed by your technological advancements and broad reach. We specialize in [Your Company\'s Service/Product] for businesses, and believe our solutions could significantly enhance your operational efficiency.\n\nGiven Farmers Insurance\'s scale and commitment to serving clients, a partnership presents substantial mutual benefits. We\'d be delighted to discuss how our technology can streamline your processes and improve customer experiences.\n\nWould you be available for a brief introductory call next week to explore potential collaboration opportunities? Please let me know what time works best for you.\n\nSincerely,\n\n[Your Name]\n[Your Title]\n[Your Company]\n[Your Contact Information]'
        }
    ]
    
    print(f"🚀 Testing contact form submission for {len(websites_data)} websites...")
    
    try:
        # Trigger the task
        task = submit_contact_forms_task.delay(
            websites_with_messages=websites_data,
            user_config=None
        )
        
        print(f"✅ Task triggered successfully!")
        print(f"📋 Task ID: {task.id}")
        print(f"📊 Task Status: {task.status}")
        
        return task.id
        
    except Exception as e:
        print(f"❌ Error triggering task: {e}")
        return None

if __name__ == "__main__":
    task_id = test_contact_form_submission()
    if task_id:
        print(f"\n🎯 Task submitted with ID: {task_id}")
        print("📝 Check the Celery worker logs for execution details")
    else:
        print("\n💥 Failed to submit task")
