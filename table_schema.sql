CREATE TABLE public._prisma_migrations (
    id character varying(36) NOT NULL,
    checksum character varying(64) NOT NULL,
    finished_at timestamp with time zone,
    migration_name character varying(255) NOT NULL,
    logs text,
    rolled_back_at timestamp with time zone,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    applied_steps_count integer DEFAULT 0 NOT NULL
);
CREATE TABLE public.accounts (
    id text NOT NULL,
    "userId" text NOT NULL,
    type text NOT NULL,
    provider text NOT NULL,
    "providerAccountId" text NOT NULL,
    refresh_token text,
    access_token text,
    expires_at integer,
    token_type text,
    scope text,
    id_token text,
    session_state text
);
CREATE TABLE public.contact_inquiries (
    id text NOT NULL,
    "firstName" text NOT NULL,
    "lastName" text NOT NULL,
    email text NOT NULL,
    message text NOT NULL,
    status text DEFAULT 'PENDING'::text NOT NULL,
    response text,
    "respondedAt" timestamp(3) without time zone,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL
);
CREATE TABLE public.file_uploads (
    id text NOT NULL,
    "userId" text NOT NULL,
    filename text NOT NULL,
    "originalName" text NOT NULL,
    "fileSize" integer NOT NULL,
    "fileType" text NOT NULL,
    status text DEFAULT 'PENDING'::text NOT NULL,
    "totalWebsites" integer DEFAULT 0 NOT NULL,
    "processedWebsites" integer DEFAULT 0 NOT NULL,
    "failedWebsites" integer DEFAULT 0 NOT NULL,
    "totalChunks" integer DEFAULT 0 NOT NULL,
    "completedChunks" integer DEFAULT 0 NOT NULL,
    "filePath" text,
    "processingStartedAt" timestamp(3) without time zone,
    "processingCompletedAt" timestamp(3) without time zone,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL
);
CREATE TABLE public.predefined_messages (
    id text NOT NULL,
    industry text NOT NULL,
    service text NOT NULL,
    message text NOT NULL,
    status text DEFAULT 'ACTIVE'::text NOT NULL,
    "usageCount" integer DEFAULT 0 NOT NULL,
    "createdBy" text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL,
    "messageType" text DEFAULT 'general'::text NOT NULL,
    tags text[],
    "targetAudience" text,
    tone text DEFAULT 'professional'::text NOT NULL
);
CREATE TABLE public.processing_chunks (
    id text NOT NULL,
    "fileUploadId" text NOT NULL,
    "chunkNumber" integer NOT NULL,
    "startRow" integer NOT NULL,
    "endRow" integer NOT NULL,
    "totalRecords" integer NOT NULL,
    "processedRecords" integer DEFAULT 0 NOT NULL,
    "failedRecords" integer DEFAULT 0 NOT NULL,
    status text DEFAULT 'PENDING'::text NOT NULL,
    "startedAt" timestamp(3) without time zone,
    "completedAt" timestamp(3) without time zone,
    "errorMessage" text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL
);
CREATE TABLE public.scraping_jobs (
    id text NOT NULL,
    "fileUploadId" text NOT NULL,
    status text DEFAULT 'PENDING'::text NOT NULL,
    "totalWebsites" integer NOT NULL,
    "processedWebsites" integer DEFAULT 0 NOT NULL,
    "failedWebsites" integer DEFAULT 0 NOT NULL,
    "startedAt" timestamp(3) without time zone,
    "completedAt" timestamp(3) without time zone,
    "errorMessage" text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL
);
CREATE TABLE public.sessions (
    id text NOT NULL,
    "sessionToken" text NOT NULL,
    "userId" text NOT NULL,
    expires timestamp(3) without time zone NOT NULL
);
CREATE TABLE public.static_content (
    id text NOT NULL,
    type text NOT NULL,
    title text NOT NULL,
    content text NOT NULL,
    status text DEFAULT 'DRAFT'::text NOT NULL,
    version integer DEFAULT 1 NOT NULL,
    "createdBy" text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL
);
CREATE TABLE public.users (
    id text NOT NULL,
    name text,
    email text NOT NULL,
    username text NOT NULL,
    password text,
    role text DEFAULT 'USER'::text NOT NULL,
    "emailVerified" timestamp(3) without time zone,
    image text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL,
    status text DEFAULT 'active'::text NOT NULL,
    "resetToken" text,
    "resetTokenExpiry" timestamp(3) without time zone
);
CREATE TABLE public.verification_tokens (
    identifier text NOT NULL,
    token text NOT NULL,
    expires timestamp(3) without time zone NOT NULL
);
CREATE TABLE public.websites (
    id text NOT NULL,
    "fileUploadId" text NOT NULL,
    "userId" text NOT NULL,
    "websiteUrl" text NOT NULL,
    "contactFormUrl" text,
    "hasContactForm" boolean DEFAULT false NOT NULL,
    "companyName" text,
    "businessType" text,
    industry text,
    "aboutUsContent" text,
    "scrapingStatus" text DEFAULT 'PENDING'::text NOT NULL,
    "messageStatus" text DEFAULT 'PENDING'::text NOT NULL,
    "generatedMessage" text,
    "sentMessage" text,
    "sentAt" timestamp(3) without time zone,
    "responseReceived" boolean DEFAULT false NOT NULL,
    "responseContent" text,
    "errorMessage" text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL
);
