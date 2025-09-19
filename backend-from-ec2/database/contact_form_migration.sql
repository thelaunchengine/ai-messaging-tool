-- Contact Form Submission Database Migration
-- SAFE: Only adds new columns, never removes existing data
-- Date: 2025-08-22

-- 1. Update contact_inquiries table with new columns
ALTER TABLE contact_inquiries 
ADD COLUMN IF NOT EXISTS "websiteId" TEXT,
ADD COLUMN IF NOT EXISTS "fileUploadId" TEXT,
ADD COLUMN IF NOT EXISTS "websiteUrl" TEXT,
ADD COLUMN IF NOT EXISTS "submissionStatus" VARCHAR(50) DEFAULT 'PENDING',
ADD COLUMN IF NOT EXISTS "submissionError" TEXT,
ADD COLUMN IF NOT EXISTS "submittedFormFields" JSONB,
ADD COLUMN IF NOT EXISTS "submissionResponse" TEXT,
ADD COLUMN IF NOT EXISTS "retryCount" INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS "lastRetryAt" TIMESTAMP;

-- 2. Update websites table with contact form submission tracking
ALTER TABLE websites 
ADD COLUMN IF NOT EXISTS "submissionStatus" VARCHAR(50) DEFAULT 'PENDING',
ADD COLUMN IF NOT EXISTS "messageGenerationError" TEXT,
ADD COLUMN IF NOT EXISTS "submissionError" TEXT,
ADD COLUMN IF NOT EXISTS "submittedFormFields" JSONB,
ADD COLUMN IF NOT EXISTS "submissionResponse" TEXT;

-- 3. Add foreign key constraints (only if columns don't already exist)
DO $$
BEGIN
    -- Add foreign key for websiteId if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'contact_inquiries_websiteId_fkey'
    ) THEN
        ALTER TABLE contact_inquiries 
        ADD CONSTRAINT contact_inquiries_websiteId_fkey 
        FOREIGN KEY ("websiteId") REFERENCES websites(id);
    END IF;
    
    -- Add foreign key for fileUploadId if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'contact_inquiries_fileUploadId_fkey'
    ) THEN
        ALTER TABLE contact_inquiries 
        ADD CONSTRAINT contact_inquiries_fileUploadId_fkey 
        FOREIGN KEY ("fileUploadId") REFERENCES file_uploads(id);
    END IF;
END $$;

-- 4. Update existing records to set default values
UPDATE contact_inquiries 
SET "submissionStatus" = 'PENDING' 
WHERE "submissionStatus" IS NULL;

UPDATE websites 
SET "submissionStatus" = 'PENDING' 
WHERE "submissionStatus" IS NULL;

-- 5. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_contact_inquiries_file_upload_id 
ON contact_inquiries("fileUploadId");

CREATE INDEX IF NOT EXISTS idx_contact_inquiries_website_id 
ON contact_inquiries("websiteId");

CREATE INDEX IF NOT EXISTS idx_websites_submission_status 
ON websites("submissionStatus");

-- 6. Verify the changes
SELECT 'Migration completed successfully!' as status;
