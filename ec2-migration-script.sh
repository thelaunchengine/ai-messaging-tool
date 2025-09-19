#!/bin/bash

# Database Migration Script for EC2 Instance
echo "🚀 Starting database migration process..."

# Update system
echo "📦 Updating system packages..."
yum update -y

# Install PostgreSQL client
echo "📦 Installing PostgreSQL client..."
yum install -y postgresql15

# Install AWS CLI v2
echo "📦 Installing AWS CLI v2..."
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

# Download database backup from S3
echo "📥 Downloading database backup from S3..."
aws s3 cp s3://ai-messaging-tool-production-backups/database-backup.sql /tmp/database-backup.sql

# Set environment variables
export PGPASSWORD="AiMessaging2024Secure"
RDS_HOST="production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com"
RDS_PORT="5432"
RDS_USER="postgres"
RDS_DB="ai_messaging"

# Test connection
echo "🔍 Testing connection to RDS..."
psql -h $RDS_HOST -p $RDS_PORT -U $RDS_USER -d $RDS_DB -c "SELECT 'Connection successful!' as status;"

if [ $? -eq 0 ]; then
    echo "✅ Connection successful!"
    
    # Clear existing database
    echo "🧹 Clearing existing database..."
    psql -h $RDS_HOST -p $RDS_PORT -U $RDS_USER -d $RDS_DB -c "DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;"
    
    # Restore from backup
    echo "📤 Restoring database from backup..."
    psql -h $RDS_HOST -p $RDS_PORT -U $RDS_USER -d $RDS_DB -f /tmp/database-backup.sql
    
    if [ $? -eq 0 ]; then
        echo "✅ Database restoration completed successfully!"
        
        # Verify restoration
        echo "🔍 Verifying restoration..."
        psql -h $RDS_HOST -p $RDS_PORT -U $RDS_USER -d $RDS_DB -c "SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = 'public';"
        
        echo "🎉 Database migration completed successfully!"
        echo "Migration completed at: $(date)" > /tmp/migration-complete.txt
    else
        echo "❌ Database restoration failed!"
        echo "Restoration failed at: $(date)" > /tmp/migration-failed.txt
        exit 1
    fi
else
    echo "❌ Connection to RDS failed!"
    echo "Connection failed at: $(date)" > /tmp/migration-failed.txt
    exit 1
fi
