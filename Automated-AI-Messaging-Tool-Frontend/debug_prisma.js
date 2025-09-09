console.log("Testing Prisma import...");

try {
  const client = require("./node_modules/.prisma/client");
  console.log("Client imported:", typeof client);
  console.log("Client keys:", Object.keys(client));
  
  if (client.PrismaClient) {
    console.log("PrismaClient found!");
    const prisma = new client.PrismaClient();
    console.log("Prisma instance created:", typeof prisma);
    console.log("Prisma methods:", Object.keys(prisma).filter(key => !key.startsWith("_")));
  } else {
    console.log("PrismaClient not found in client");
  }
} catch (error) {
  console.error("Error importing client:", error);
}
