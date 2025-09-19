import psycopg2
from database.database_manager import DatabaseManager

def test_direct_connection():
    print("=== Testing Direct Connection ===")
    try:
        conn = psycopg2.connect('postgresql://postgres:cDtrtoOqpdkAzMcLSd%401847@localhost:5432/aimsgdb')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM file_uploads")
        count = cursor.fetchone()
        print(f"Direct query count: {count[0]}")
        
        cursor.execute("SELECT id, status, \"createdAt\" FROM file_uploads ORDER BY \"createdAt\" DESC LIMIT 3")
        rows = cursor.fetchall()
        print(f"Direct query rows: {rows}")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Direct connection error: {e}")

def test_database_manager():
    print("\n=== Testing Database Manager ===")
    try:
        db = DatabaseManager()
        uploads = db.get_all_file_uploads()
        print(f"DatabaseManager count: {len(uploads)}")
        print(f"DatabaseManager uploads: {uploads[:2]}")
    except Exception as e:
        print(f"DatabaseManager error: {e}")

if __name__ == "__main__":
    test_direct_connection()
    test_database_manager() 