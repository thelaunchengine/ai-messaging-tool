const { PrismaClient } = require('@prisma/client');

async function testDatabase() {
  const prisma = new PrismaClient();
  
  try {
    console.log('Testing database connection...');
    
    // Test basic connection
    const result = await prisma.$queryRaw`SELECT 1 as test`;
    console.log('Basic connection test:', result);
    
    // Check users table
    const users = await prisma.$queryRaw`SELECT id, email, name, role, status FROM users LIMIT 5`;
    console.log('Users in database:', users);
    
    // Check if we have any users
    const userCount = await prisma.$queryRaw`SELECT COUNT(*) as count FROM users`;
    console.log('Total users:', userCount);
    
  } catch (error) {
    console.error('Database error:', error);
  } finally {
    await prisma.$disconnect();
  }
}

testDatabase();
