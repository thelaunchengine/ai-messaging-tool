const { PrismaClient } = require('@prisma/client');
const bcrypt = require('bcryptjs');

async function testAuth() {
  const prisma = new PrismaClient();
  
  try {
    console.log('Testing authentication...');
    
    // Test user lookup
    const userResult = await prisma.$queryRaw`SELECT * FROM users WHERE email = 'test@test.com' LIMIT 1`;
    const user = userResult[0];
    
    console.log('User found:', !!user);
    if (user) {
      console.log('User details:', {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role,
        status: user.status
      });
      
      // Test password verification
      const isPasswordValid = await bcrypt.compare('admin123', user.password);
      console.log('Password valid:', isPasswordValid);
    }
    
  } catch (error) {
    console.error('Auth test error:', error);
  } finally {
    await prisma.$disconnect();
  }
}

testAuth();
