#!/usr/bin/env python3
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database.database_manager import DatabaseManager
    print("✅ Successfully imported DatabaseManager")
    
    def get_users():
        """Get all users from the database using existing DatabaseManager"""
        try:
            db_manager = DatabaseManager()
            print("✅ Database connection established")
            
            # Try to get users using a direct query
            try:
                # Get connection and cursor
                conn = db_manager.get_connection()
                cursor = conn.cursor()
                
                # Query for users
                query = """
                SELECT id, email, name, "createdAt", "updatedAt"
                FROM users
                ORDER BY "createdAt" DESC
                """
                
                print("🔍 Executing query for users...")
                cursor.execute(query)
                users = cursor.fetchall()
                
                print(f"📊 Found {len(users)} users in the database")
                print("\n" + "="*80)
                print("👥 USERS LIST")
                print("="*80)
                
                if users:
                    for i, user in enumerate(users, 1):
                        print(f"\n{i}. User ID: {user[0]}")
                        print(f"   Email: {user[1]}")
                        print(f"   Name: {user[2] or 'Not specified'}")
                        print(f"   Created: {user[3]}")
                        print(f"   Updated: {user[4]}")
                        print("-" * 50)
                else:
                    print("❌ No users found in the database")
                
                cursor.close()
                conn.close()
                
            except Exception as e:
                print(f"❌ Error querying users: {e}")
                print("🔍 Trying alternative approach...")
                
                # Try to get file uploads to see what user IDs exist
                try:
                    file_uploads = db_manager.get_all_file_uploads()
                    if file_uploads:
                        print(f"\n📁 Found {len(file_uploads)} file uploads")
                        print("🔍 User IDs from file uploads:")
                        
                        user_ids = set()
                        for upload in file_uploads:
                            user_id = upload.get('userId')
                            if user_id:
                                user_ids.add(user_id)
                        
                        if user_ids:
                            print(f"\n👥 Unique User IDs found: {len(user_ids)}")
                            for i, user_id in enumerate(sorted(user_ids), 1):
                                print(f"   {i}. {user_id}")
                        else:
                            print("❌ No user IDs found in file uploads")
                    else:
                        print("❌ No file uploads found")
                        
                except Exception as e2:
                    print(f"❌ Error getting file uploads: {e2}")
                    
        except Exception as e:
            print(f"❌ Error initializing database manager: {e}")
    
    if __name__ == "__main__":
        get_users()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔍 Trying to use the backend API instead...")
    
    # Try to use the backend API to get user information
    import requests
    
    def get_users_via_api():
        """Get users via the backend API"""
        try:
            # Get file upload history (which includes user IDs)
            response = requests.get("http://103.215.159.51:8000/api/file-uploads/history")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Found {len(data)} file uploads via API")
                
                user_ids = set()
                for upload in data:
                    user_id = upload.get('userId')
                    if user_id:
                        user_ids.add(user_id)
                
                if user_ids:
                    print(f"\n👥 Unique User IDs found: {len(user_ids)}")
                    for i, user_id in enumerate(sorted(user_ids), 1):
                        print(f"   {i}. {user_id}")
                else:
                    print("❌ No user IDs found")
            else:
                print(f"❌ API request failed with status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error calling API: {e}")
    
    if __name__ == "__main__":
        get_users_via_api()
