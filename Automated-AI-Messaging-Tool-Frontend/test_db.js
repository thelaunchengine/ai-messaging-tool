const { PrismaClient } = require('@prisma/client');

async function checkDatabase() {
  const prisma = new PrismaClient();
  
  try {
    console.log('Checking database for FileUpload records...');
    const records = await prisma.fileUpload.findMany();
    console.log('Total FileUpload records:', records.length);
    
    if (records.length > 0) {
      console.log('Records found:');
      records.forEach((record, index) => {
        console.log(`${index + 1}. ID: ${record.id}, Status: ${record.status}, Created: ${record.createdAt}`);
      });
    } else {
      console.log('No FileUpload records found in database');
    }
  } catch (error) {
    console.error('Error checking database:', error);
  } finally {
    await prisma.$disconnect();
  }
}

checkDatabase(); 