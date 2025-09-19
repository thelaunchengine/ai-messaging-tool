-- Fix all models by adding primary keys

-- Add primary keys to all models
ALTER TABLE file_uploads ADD CONSTRAINT file_uploads_pkey PRIMARY KEY (id);
ALTER TABLE predefined_messages ADD CONSTRAINT predefined_messages_pkey PRIMARY KEY (id);
ALTER TABLE processing_chunks ADD CONSTRAINT processing_chunks_pkey PRIMARY KEY (id);
ALTER TABLE scraping_jobs ADD CONSTRAINT scraping_jobs_pkey PRIMARY KEY (id);
ALTER TABLE sessions ADD CONSTRAINT sessions_pkey PRIMARY KEY (id);
ALTER TABLE static_content ADD CONSTRAINT static_content_pkey PRIMARY KEY (id);
ALTER TABLE verification_tokens ADD CONSTRAINT verification_tokens_pkey PRIMARY KEY (token);
ALTER TABLE websites ADD CONSTRAINT websites_pkey PRIMARY KEY (id);

-- Add unique constraints
ALTER TABLE sessions ADD CONSTRAINT sessions_sessionToken_key UNIQUE (sessionToken);
ALTER TABLE verification_tokens ADD CONSTRAINT verification_tokens_identifier_token_key UNIQUE (identifier, token);
ALTER TABLE static_content ADD CONSTRAINT static_content_type_version_key UNIQUE (type, version);
ALTER TABLE processing_chunks ADD CONSTRAINT processing_chunks_fileUploadId_chunkNumber_key UNIQUE (fileUploadId, chunkNumber);
