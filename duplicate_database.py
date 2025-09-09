#!/usr/bin/env python3
import subprocess
import os
import urllib.parse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database connection details
db_url = os.getenv('DATABASE_URL')
if not db_url:
    print("Error: DATABASE_URL not found in environment")
    exit(1)

# Parse connection string properly
# postgresql://postgres:password@host:port/dbname
parsed = urllib.parse.urlparse(db_url)
username = parsed.username
password = urllib.parse.unquote(parsed.password)  # Decode URL-encoded password
host = parsed.hostname
port = parsed.port or 5432
source_db = parsed.path.lstrip('/')
target_db = source_db + '_copy'

print(f"Duplicating database {source_db} to {target_db}")
print(f"Host: {host}, Port: {port}, User: {username}")

try:
    # Drop target database if it exists
    print("Dropping existing target database...")
    subprocess.run([
        'psql', '-h', host, '-p', str(port), '-U', username, '-d', 'postgres',
        '-c', f'DROP DATABASE IF EXISTS {target_db};'
    ], env={'PGPASSWORD': password}, check=True)
    
    # Create new database
    print("Creating new target database...")
    subprocess.run([
        'psql', '-h', host, '-p', str(port), '-U', username, '-d', 'postgres',
        '-c', f'CREATE DATABASE {target_db};'
    ], env={'PGPASSWORD': password}, check=True)
    
    # Dump source database
    print("Dumping source database...")
    with open(f'{source_db}_backup.sql', 'w') as f:
        subprocess.run([
            'pg_dump', '-h', host, '-p', str(port), '-U', username, '-d', source_db
        ], env={'PGPASSWORD': password}, stdout=f, check=True)
    
    # Restore to target database
    print("Restoring to target database...")
    with open(f'{source_db}_backup.sql', 'r') as f:
        subprocess.run([
            'psql', '-h', host, '-p', str(port), '-U', username, '-d', target_db
        ], env={'PGPASSWORD': password}, stdin=f, check=True)
    
    # Clean up backup file
    os.remove(f'{source_db}_backup.sql')
    
    print(f"Database {target_db} duplicated successfully from {source_db}")
    
except subprocess.CalledProcessError as e:
    print(f"Error during database duplication: {e}")
    exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    exit(1)
