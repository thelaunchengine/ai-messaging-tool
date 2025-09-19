-- OPTIMIZED DATABASE SCHEMA UPDATES
-- These updates improve performance and add monitoring capabilities

-- Add new indexes for better performance
CREATE INDEX IF NOT EXISTS idx_websites_processing_status ON websites("scrapingStatus", "messageStatus");
CREATE INDEX IF NOT EXISTS idx_websites_batch_processing ON websites("fileUploadId", "createdAt");
CREATE INDEX IF NOT EXISTS idx_websites_error_tracking ON websites("errorMessage", "updatedAt");

-- Add new columns for progress tracking
ALTER TABLE websites ADD COLUMN IF NOT EXISTS "processingStartedAt" TIMESTAMP;
ALTER TABLE websites ADD COLUMN IF NOT EXISTS "processingCompletedAt" TIMESTAMP;
ALTER TABLE websites ADD COLUMN IF NOT EXISTS "retryCount" INTEGER DEFAULT 0;
ALTER TABLE websites ADD COLUMN IF NOT EXISTS "lastError" TEXT;
ALTER TABLE websites ADD COLUMN IF NOT EXISTS "processingDuration" INTEGER; -- in seconds

-- Add new columns for resource monitoring
ALTER TABLE websites ADD COLUMN IF NOT EXISTS "cpuUsage" DECIMAL(5,2);
ALTER TABLE websites ADD COLUMN IF NOT EXISTS "memoryUsage" DECIMAL(5,2);
ALTER TABLE websites ADD COLUMN IF NOT EXISTS "processingNotes" TEXT;

-- Create new table for progress tracking
CREATE TABLE IF NOT EXISTS scraping_progress (
    id VARCHAR PRIMARY KEY,
    file_upload_id VARCHAR REFERENCES file_uploads(id),
    total_websites INTEGER NOT NULL,
    completed_websites INTEGER DEFAULT 0,
    failed_websites INTEGER DEFAULT 0,
    current_batch INTEGER DEFAULT 0,
    total_batches INTEGER DEFAULT 0,
    status VARCHAR DEFAULT 'PENDING',
    start_time TIMESTAMP DEFAULT NOW(),
    last_update TIMESTAMP DEFAULT NOW(),
    estimated_completion TIMESTAMP,
    performance_metrics JSONB,
    error_log JSONB
);

-- Create index for progress tracking
CREATE INDEX IF NOT EXISTS idx_scraping_progress_file_upload ON scraping_progress("fileUploadId");
CREATE INDEX IF NOT EXISTS idx_scraping_progress_status ON scraping_progress("status");

-- Create new table for resource monitoring
CREATE TABLE IF NOT EXISTS resource_monitoring (
    id VARCHAR PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    cpu_usage DECIMAL(5,2),
    memory_usage DECIMAL(5,2),
    active_tasks INTEGER,
    queue_size INTEGER,
    database_connections INTEGER,
    worker_status JSONB
);

-- Create index for resource monitoring
CREATE INDEX IF NOT EXISTS idx_resource_monitoring_timestamp ON resource_monitoring("timestamp");

-- Update existing tables for better performance
ALTER TABLE file_uploads ADD COLUMN IF NOT EXISTS "processing_config" JSONB;
ALTER TABLE file_uploads ADD COLUMN IF NOT EXISTS "performance_metrics" JSONB;
