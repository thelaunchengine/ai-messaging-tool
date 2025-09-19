#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor
import os

def get_users_from_database():
    """Connect to database and get all users with their email addresses"""
    
    # Database connection parameters
    db_params = {
        'host': '103.215.159.51',
        'port': 5432,
        'database': 'aimsgdb',
        'user': 'postgres',
        'password': 'password'
    }
    
    try:
        # Connect to the database
        print("🔌 Connecting to database...")
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Database connection successful!")
        
        # Query to get all users
        query = """
        SELECT id, email, name, "createdAt", "updatedAt"
        FROM users
        ORDER BY "createdAt" DESC
        """
        
        print("🔍 Executing query...")
        cursor.execute(query)
        users = cursor.fetchall()
        
        print(f"📊 Found {len(users)} users in the database")
        print("\n" + "="*80)
        print("👥 USERS LIST")
        print("="*80)
        
        if users:
            for i, user in enumerate(users, 1):
                print(f"\n{i}. User ID: {user['id']}")
                print(f"   Email: {user['email']}")
                print(f"   Name: {user['name'] or 'Not specified'}")
                print(f"   Created: {user['createdAt']}")
                print(f"   Updated: {user['updatedAt']}")
                print("-" * 50)
        else:
            print("❌ No users found in the database")
        
        # Also check if the users table exists and has any data
        cursor.execute("""
            SELECT table_name, table_rows 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'users'
        """)
        
        table_info = cursor.fetchone()
        if table_info:
            print(f"\n📋 Table 'users' exists")
        else:
            print(f"\n❌ Table 'users' does not exist")
        
        # Check table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        if columns:
            print(f"\n🏗️  Table structure:")
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                print(f"   - {col['column_name']}: {col['data_type']} ({nullable})")
        
        cursor.close()
        conn.close()
        print("\n✅ Database connection closed")
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    get_users_from_database()
