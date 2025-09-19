-- Migration: Add Contact Form Submission Tables and Columns
-- Date: 2025-08-21
-- Description: Add support for tracking contact form submissions

-- Add new columns to websites table
ALTER TABLE websites 
ADD COLUMN IF NOT EXISTS "submissionStatus" VARCHAR DEFAULT 'PENDING',
ADD COLUMN IF NOT EXISTS "submittedAt" TIMESTAMP,
ADD COLUMN IF NOT EXISTS "submissionErrorMessage" TEXT,
ADD COLUMN IF NOT EXISTS "responseReceived" BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS "submissionMethod" VARCHAR;

-- Create form_submissions table
CREATE TABLE IF NOT EXISTS form_submissions (
    id VARCHAR PRIMARY KEY,
    website_id VARCHAR NOT NULL REFERENCES websites(id) ON DELETE CASCADE,
    file_upload_id VARCHAR REFERENCES file_uploads(id) ON DELETE CASCADE,
    user_id VARCHAR REFERENCES users(id) ON DELETE CASCADE,
    
    -- Submission Details
    submission_status VARCHAR DEFAULT 'PENDING',
    submitted_message TEXT NOT NULL,
    message_type VARCHAR DEFAULT 'general',
    
    -- Form Information
    contact_form_url VARCHAR,
    form_fields_used JSONB,
    submission_method VARCHAR DEFAULT 'unknown',
    
    -- Timing
    submitted_at TIMESTAMP,
    response_received_at TIMESTAMP,
    last_attempt_at TIMESTAMP,
    
    -- Response Tracking
    response_received BOOLEAN DEFAULT FALSE,
    response_content TEXT,
    response_source VARCHAR,
    
    -- Error Handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    
    -- Metadata
    sender_info JSONB,
    custom_prompt TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_form_submissions_website_id ON form_submissions(website_id);
CREATE INDEX IF NOT EXISTS idx_form_submissions_file_upload_id ON form_submissions(file_upload_id);
CREATE INDEX IF NOT EXISTS idx_form_submissions_user_id ON form_submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_form_submissions_status ON form_submissions(submission_status);
CREATE INDEX IF NOT EXISTS idx_form_submissions_created_at ON form_submissions(created_at);
CREATE INDEX IF NOT EXISTS idx_form_submissions_submitted_at ON form_submissions(submitted_at);

-- Create submission_attempts table for tracking retry attempts
CREATE TABLE IF NOT EXISTS submission_attempts (
    id VARCHAR PRIMARY KEY,
    submission_id VARCHAR NOT NULL REFERENCES form_submissions(id) ON DELETE CASCADE,
    attempt_number INTEGER NOT NULL,
    status VARCHAR NOT NULL,
    error_message TEXT,
    response_code INTEGER,
    response_time_ms INTEGER,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for submission_attempts
CREATE INDEX IF NOT EXISTS idx_submission_attempts_submission_id ON submission_attempts(submission_id);
CREATE INDEX IF NOT EXISTS idx_submission_attempts_attempted_at ON submission_attempts(attempted_at);

-- Create submission_responses table for tracking responses
CREATE TABLE IF NOT EXISTS submission_responses (
    id VARCHAR PRIMARY KEY,
    submission_id VARCHAR NOT NULL REFERENCES form_submissions(id) ON DELETE CASCADE,
    response_type VARCHAR NOT NULL,
    response_content TEXT,
    response_date TIMESTAMP,
    follow_up_needed BOOLEAN DEFAULT FALSE,
    follow_up_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for submission_responses
CREATE INDEX IF NOT EXISTS idx_submission_responses_submission_id ON submission_responses(submission_id);
CREATE INDEX IF NOT EXISTS idx_submission_responses_response_date ON submission_responses(response_date);

-- Add comments for documentation
COMMENT ON TABLE form_submissions IS 'Tracks contact form submissions made by the system';
COMMENT ON TABLE submission_attempts IS 'Tracks individual submission attempts for retry logic';
COMMENT ON TABLE submission_responses IS 'Tracks responses received from contact form submissions';

COMMENT ON COLUMN websites."submissionStatus" IS 'Current status of contact form submission (PENDING, SUBMITTING, SUBMITTED, FAILED, RESPONDED)';
COMMENT ON COLUMN websites."submittedAt" IS 'Timestamp when contact form was successfully submitted';
COMMENT ON COLUMN websites."submissionErrorMessage" IS 'Error message if contact form submission failed';
COMMENT ON COLUMN websites."responseReceived" IS 'Whether a response was received from the contact form submission';
COMMENT ON COLUMN websites."submissionMethod" IS 'Method used for submission (HTTP_POST, SELENIUM, AJAX, etc.)';

-- Create a view for easy access to submission statistics
CREATE OR REPLACE VIEW submission_statistics AS
SELECT 
    w."fileUploadId",
    w."userId",
    COUNT(*) as total_websites,
    COUNT(CASE WHEN w."submissionStatus" = 'SUBMITTED' THEN 1 END) as successful_submissions,
    COUNT(CASE WHEN w."submissionStatus" = 'FAILED' THEN 1 END) as failed_submissions,
    COUNT(CASE WHEN w."submissionStatus" = 'PENDING' THEN 1 END) as pending_submissions,
    COUNT(CASE WHEN w."responseReceived" = true THEN 1 END) as responses_received,
    ROUND(
        (COUNT(CASE WHEN w."submissionStatus" = 'SUBMITTED' THEN 1 END)::DECIMAL / COUNT(*)) * 100, 2
    ) as success_rate
FROM websites w
GROUP BY w."fileUploadId", w."userId";

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON form_submissions TO your_app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON submission_attempts TO your_app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON submission_responses TO your_app_user;
-- GRANT SELECT ON submission_statistics TO your_app_user;
