const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient({
  datasources: {
    db: {
      url: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging'
    }
  }
});

async function testUserCreation() {
  try {
    console.log('Testing database connection...');
    await prisma.$connect();
    console.log('✅ Database connected successfully');
    
    console.log('Testing user creation...');
    const user = await prisma.users.create({
      data: {
        id: 'test-user-' + Date.now(),
        name: 'Test User',
        email: 'test' + Date.now() + '@example.com',
        username: 'testuser' + Date.now(),
        password: 'hashedpassword',
        role: 'USER',
        status: 'active',
        updatedAt: new Date()
      },
      select: {
        id: true,
        name: true,
        email: true,
        username: true,
        role: true,
        status: true,
        createdAt: true,
        updatedAt: true
      }
    });
    
    console.log('✅ User created successfully:', user);
    
    // Clean up
    await prisma.users.delete({
      where: { id: user.id }
    });
    console.log('✅ Test user deleted');
    
  } catch (error) {
    console.error('❌ Error:', error);
    console.error('Error details:', {
      message: error.message,
      code: error.code,
      meta: error.meta
    });
  } finally {
    await prisma.$disconnect();
  }
}

testUserCreation();
