-- Fix database schema by adding proper primary keys and constraints

-- First, let's check if the users table exists and what it looks like
-- Add primary key to users table if it doesn't exist
DO $$
BEGIN
    -- Check if users table exists
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
        -- Check if id column exists and is primary key
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE table_name = 'users' AND constraint_type = 'PRIMARY KEY'
        ) THEN
            -- Add primary key constraint to id column
            ALTER TABLE users ADD CONSTRAINT users_pkey PRIMARY KEY (id);
        END IF;
        
        -- Add unique constraints if they don't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE table_name = 'users' AND constraint_name = 'users_email_key'
        ) THEN
            ALTER TABLE users ADD CONSTRAINT users_email_key UNIQUE (email);
        END IF;
        
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE table_name = 'users' AND constraint_name = 'users_username_key'
        ) THEN
            ALTER TABLE users ADD CONSTRAINT users_username_key UNIQUE (username);
        END IF;
        
        -- Add updatedAt column if it doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'updatedAt'
        ) THEN
            ALTER TABLE users ADD COLUMN "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP;
        END IF;
        
        -- Add status column if it doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'status'
        ) THEN
            ALTER TABLE users ADD COLUMN status TEXT NOT NULL DEFAULT 'active';
        END IF;
        
        -- Add resetToken columns if they don't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'resetToken'
        ) THEN
            ALTER TABLE users ADD COLUMN "resetToken" TEXT;
        END IF;
        
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'resetTokenExpiry'
        ) THEN
            ALTER TABLE users ADD COLUMN "resetTokenExpiry" TIMESTAMP(3);
        END IF;
        
        -- Add image column if it doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'image'
        ) THEN
            ALTER TABLE users ADD COLUMN image TEXT;
        END IF;
        
        -- Add emailVerified column if it doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'emailVerified'
        ) THEN
            ALTER TABLE users ADD COLUMN "emailVerified" TIMESTAMP(3);
        END IF;
        
        -- Add createdAt column if it doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'createdAt'
        ) THEN
            ALTER TABLE users ADD COLUMN "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP;
        END IF;
        
        -- Add role column if it doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'role'
        ) THEN
            ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'USER';
        END IF;
        
        -- Add password column if it doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'password'
        ) THEN
            ALTER TABLE users ADD COLUMN password TEXT;
        END IF;
        
        -- Add username column if it doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'username'
        ) THEN
            ALTER TABLE users ADD COLUMN username TEXT;
        END IF;
        
        -- Add name column if it doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'name'
        ) THEN
            ALTER TABLE users ADD COLUMN name TEXT;
        END IF;
        
        -- Add id column if it doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'id'
        ) THEN
            ALTER TABLE users ADD COLUMN id TEXT;
        END IF;
        
        -- Generate UUIDs for existing users if id is null
        UPDATE users SET id = gen_random_uuid()::text WHERE id IS NULL;
        
        -- Make id NOT NULL
        ALTER TABLE users ALTER COLUMN id SET NOT NULL;
        
        -- Make email NOT NULL
        ALTER TABLE users ALTER COLUMN email SET NOT NULL;
        
        -- Make username NOT NULL
        ALTER TABLE users ALTER COLUMN username SET NOT NULL;
        
        RAISE NOTICE 'Users table schema fixed successfully';
    ELSE
        RAISE NOTICE 'Users table does not exist';
    END IF;
END $$;
