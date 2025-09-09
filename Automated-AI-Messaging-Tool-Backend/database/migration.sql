-- Enhanced Status Tracking Migration
-- This script adds new columns for better status monitoring

-- Add new columns to websites table
ALTER TABLE websites ADD COLUMN IF NOT EXISTS "submissionStatus" VARCHAR(50) DEFAULT 'PENDING';
ALTER TABLE websites ADD COLUMN IF NOT EXISTS "messageGenerationError" TEXT;
ALTER TABLE websites ADD COLUMN IF NOT EXISTS "submissionError" TEXT;
ALTER TABLE websites ADD COLUMN IF NOT EXISTS "submittedFormFields" JSONB;
ALTER TABLE websites ADD COLUMN IF NOT EXISTS "submissionResponse" TEXT;

-- Add new columns to contact_inquiries table
ALTER TABLE contact_inquiries ADD COLUMN IF NOT EXISTS "submittedFormFields" JSONB;
ALTER TABLE contact_inquiries ADD COLUMN IF NOT EXISTS "submissionError" TEXT;
ALTER TABLE contact_inquiries ADD COLUMN IF NOT EXISTS "retryCount" INTEGER DEFAULT 0;
ALTER TABLE contact_inquiries ADD COLUMN IF NOT EXISTS "lastRetryAt" TIMESTAMP;

-- Update existing records with default values
UPDATE websites SET "submissionStatus" = 'PENDING' WHERE "submissionStatus" IS NULL;
UPDATE websites SET "messageStatus" = 'PENDING' WHERE "messageStatus" IS NULL;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_websites_submission_status ON websites("submissionStatus");
CREATE INDEX IF NOT EXISTS idx_websites_message_status ON websites("messageStatus");
CREATE INDEX IF NOT EXISTS idx_contact_inquiries_status ON contact_inquiries(status);

-- Log completion
SELECT 'Migration completed successfully. Enhanced status tracking columns added.' as result;
