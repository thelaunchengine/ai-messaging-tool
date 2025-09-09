const { PrismaClient } = require("./node_modules/.prisma/client");

const prisma = new PrismaClient();

async function checkUsers() {
  try {
    const users = await prisma.users.findMany();
    console.log("Users in database:");
    users.forEach(user => {
      console.log(`- ID: ${user.id}, Email: ${user.email}, Username: ${user.username}, Role: ${user.role}`);
    });
    
    // Check specifically for test@test.com
    const testUser = await prisma.users.findUnique({
      where: { email: "test@test.com" }
    });
    
    if (testUser) {
      console.log("\nTest user found:", {
        id: testUser.id,
        email: testUser.email,
        username: testUser.username,
        role: testUser.role
      });
    } else {
      console.log("\nTest user test@test.com not found");
    }
    
  } catch (error) {
    console.error("Error:", error);
  } finally {
    await prisma.$disconnect();
  }
}

checkUsers();
