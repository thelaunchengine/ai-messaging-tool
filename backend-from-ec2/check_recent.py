from database.database_manager import DatabaseManager
from datetime import datetime, timedelta

db = DatabaseManager()
uploads = db.get_all_file_uploads()
now = datetime.now()

recent = []
for u in uploads:
    created_at = u.get('createdAt')
    if isinstance(created_at, datetime):
        diff = now - created_at
        if diff <= timedelta(hours=24):
            recent.append(u)

print(f'Uploads in last 24 hours: {len(recent)}')
for u in recent[:5]:
    print(f'  {u.get("id")} - {u.get("createdAt")} - {u.get("status")}') 