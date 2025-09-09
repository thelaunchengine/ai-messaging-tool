#!/bin/bash
# Simple Database Migration Script
# Adds enhanced status tracking columns

echo "Starting simple database migration..."

# Database connection details
DB_HOST="localhost"
DB_NAME="ai_messaging_db"
DB_USER="xb3353"
DB_PASS="password"

# Function to run SQL command
run_sql() {
    local sql="$1"
    echo "Executing: $sql"
    PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "$sql"
}

# Add new columns to websites table
echo "Adding columns to websites table..."
run_sql 'ALTER TABLE websites ADD COLUMN IF NOT EXISTS "submissionStatus" VARCHAR(50) DEFAULT '\''PENDING'\'';'
run_sql 'ALTER TABLE websites ADD COLUMN IF NOT EXISTS "messageGenerationError" TEXT;'
run_sql 'ALTER TABLE websites ADD COLUMN IF NOT EXISTS "submissionError" TEXT;'
run_sql 'ALTER TABLE websites ADD COLUMN IF NOT EXISTS "submittedFormFields" JSONB;'
run_sql 'ALTER TABLE websites ADD COLUMN IF NOT EXISTS "submissionResponse" TEXT;'

# Add new columns to contact_inquiries table
echo "Adding columns to contact_inquiries table..."
run_sql 'ALTER TABLE contact_inquiries ADD COLUMN IF NOT EXISTS "submittedFormFields" JSONB;'
run_sql 'ALTER TABLE contact_inquiries ADD COLUMN IF NOT EXISTS "submissionError" TEXT;'
run_sql 'ALTER TABLE websites ADD COLUMN IF NOT EXISTS "retryCount" INTEGER DEFAULT 0;'
run_sql 'ALTER TABLE websites ADD COLUMN IF NOT EXISTS "lastRetryAt" TIMESTAMP;'

# Update existing records
echo "Updating existing records..."
run_sql 'UPDATE websites SET "submissionStatus" = '\''PENDING'\'' WHERE "submissionStatus" IS NULL;'
run_sql 'UPDATE websites SET "messageStatus" = '\''PENDING'\'' WHERE "messageStatus" IS NULL;'

echo "Migration completed!"
