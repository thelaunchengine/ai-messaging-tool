const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient({
  datasources: {
    db: {
      url: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging'
    }
  }
});

async function debugPrisma() {
  try {
    console.log('Prisma client properties:');
    console.log('Available models:', Object.keys(prisma));
    console.log('User model exists:', !!prisma.user);
    console.log('Users model exists:', !!prisma.users);
    
    if (prisma.users) {
      console.log('✅ Found users model');
    } else {
      console.log('❌ No users model found');
    }
    
  } catch (error) {
    console.error('❌ Error:', error);
  } finally {
    await prisma.$disconnect();
  }
}

debugPrisma();
