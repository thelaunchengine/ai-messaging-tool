import json
import boto3
import psycopg2
import os
from urllib.parse import urlparse

def lambda_handler(event, context):
    """
    Lambda function to restore database backup from S3 to RDS
    """
    
    # Get environment variables
    s3_bucket = os.environ['S3_BUCKET']
    s3_key = os.environ['S3_KEY']
    database_url = os.environ['DATABASE_URL']
    
    # Parse database URL
    parsed_url = urlparse(database_url)
    
    # Database connection parameters
    db_params = {
        'host': parsed_url.hostname,
        'port': parsed_url.port or 5432,
        'user': parsed_url.username,
        'password': parsed_url.password,
        'database': parsed_url.path[1:] if parsed_url.path else 'ai_messaging'
    }
    
    try:
        # Download SQL file from S3
        s3_client = boto3.client('s3')
        response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
        sql_content = response['Body'].read().decode('utf-8')
        
        # Connect to RDS database
        conn = psycopg2.connect(**db_params)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Clear existing database
        print("Clearing existing database...")
        cursor.execute("DROP SCHEMA IF EXISTS public CASCADE;")
        cursor.execute("CREATE SCHEMA public;")
        cursor.execute("GRANT ALL ON SCHEMA public TO postgres;")
        cursor.execute("GRANT ALL ON SCHEMA public TO public;")
        
        # Execute SQL backup
        print("Restoring database from backup...")
        cursor.execute(sql_content)
        
        # Verify restoration
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
        table_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Database migration completed successfully',
                'tables_restored': table_count
            })
        }
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
