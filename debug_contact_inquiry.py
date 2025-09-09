#!/usr/bin/env python3
import sys
import os

# Add the backend directory to Python path
sys.path.append('/home/xb3353/Automated-AI-Messaging-Tool-Backend')

from database.database_manager import DatabaseManager

def test_contact_inquiry_creation():
    try:
        print("Testing contact inquiry creation...")
        
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Test data
        website_id = "25b8a877-ba9a-42b1-bfd9-b99b35de74e1"
        userId = "cmdi7lqnj0000sbp8h98vwlco"  # From the website data
        contactFormUrl = "https://www.arauto505.com/contact-us/"
        submitted_message = "Test message for debugging"
        
        print(f"Website ID: {website_id}")
        print(f"User ID: {userId}")
        print(f"Contact Form URL: {contactFormUrl}")
        
        # Try to create a contact inquiry
        contact_inquiry_id = db_manager.create_contact_inquiry(
            website_id=website_id,
            userId=userId,
            contactFormUrl=contactFormUrl,
            submitted_message=submitted_message,
            status="PENDING",
            response_content="Test response"
        )
        
        if contact_inquiry_id:
            print(f"✅ Successfully created contact inquiry: {contact_inquiry_id}")
        else:
            print("❌ Failed to create contact inquiry")
            
        # Check if it was actually created
        count = db_manager.cursor.execute("SELECT COUNT(*) FROM contact_inquiries")
        print(f"Total contact inquiries in database: {count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_contact_inquiry_creation()
