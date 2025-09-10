const { PrismaClient } = require('@prisma/client');

async function migrateDatabase() {
  const prisma = new PrismaClient();
  
  try {
    console.log('Starting database migration...');
    
    // Test connection
    await prisma.$connect();
    console.log('✅ Database connection successful');
    
    // Run the migration
    await prisma.$executeRaw`
      CREATE TABLE IF NOT EXISTS "users" (
        "id" TEXT NOT NULL PRIMARY KEY,
        "name" TEXT,
        "email" TEXT NOT NULL UNIQUE,
        "username" TEXT NOT NULL UNIQUE,
        "password" TEXT,
        "role" TEXT NOT NULL DEFAULT 'USER',
        "emailVerified" TIMESTAMP(3),
        "image" TEXT,
        "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
        "updatedAt" TIMESTAMP(3) NOT NULL,
        "status" TEXT NOT NULL DEFAULT 'active',
        "resetToken" TEXT,
        "resetTokenExpiry" TIMESTAMP(3)
      );
    `;
    
    console.log('✅ Users table created successfully');
    
    // Create other essential tables
    await prisma.$executeRaw`
      CREATE TABLE IF NOT EXISTS "accounts" (
        "id" TEXT NOT NULL PRIMARY KEY,
        "userId" TEXT NOT NULL,
        "type" TEXT NOT NULL,
        "provider" TEXT NOT NULL,
        "providerAccountId" TEXT NOT NULL,
        "refresh_token" TEXT,
        "access_token" TEXT,
        "expires_at" INTEGER,
        "token_type" TEXT,
        "scope" TEXT,
        "id_token" TEXT,
        "session_state" TEXT,
        CONSTRAINT "accounts_provider_providerAccountId_key" UNIQUE ("provider", "providerAccountId")
      );
    `;
    
    await prisma.$executeRaw`
      CREATE TABLE IF NOT EXISTS "sessions" (
        "id" TEXT NOT NULL PRIMARY KEY,
        "sessionToken" TEXT NOT NULL UNIQUE,
        "userId" TEXT NOT NULL,
        "expires" TIMESTAMP(3) NOT NULL
      );
    `;
    
    await prisma.$executeRaw`
      CREATE TABLE IF NOT EXISTS "verification_tokens" (
        "identifier" TEXT NOT NULL,
        "token" TEXT NOT NULL UNIQUE,
        "expires" TIMESTAMP(3) NOT NULL,
        CONSTRAINT "verification_tokens_identifier_token_key" UNIQUE ("identifier", "token")
      );
    `;
    
    console.log('✅ All essential tables created successfully');
    console.log('🎉 Database migration completed!');
    
  } catch (error) {
    console.error('❌ Migration failed:', error);
    process.exit(1);
  } finally {
    await prisma.$disconnect();
  }
}

// Export the function for use in startup script
module.exports = { migrateDatabase };

// Only run migration if this file is executed directly and SKIP_DATABASE_MIGRATION is not set to 'true'
if (require.main === module) {
  if (process.env.SKIP_DATABASE_MIGRATION !== 'true') {
    migrateDatabase();
  } else {
    console.log('⏭️ Skipping database migration (SKIP_DATABASE_MIGRATION=true)');
  }
}
