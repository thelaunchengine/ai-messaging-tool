const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient({
  datasources: {
    db: {
      url: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging'
    }
  }
});

async function checkUpload() {
  try {
    console.log('Checking upload ID: 7d2bcc5c-5d6b-4b16-8f83-1a33f0a20765');
    
    const upload = await prisma.file_uploads.findUnique({
      where: { id: '7d2bcc5c-5d6b-4b16-8f83-1a33f0a20765' },
      include: {
        websites: {
          select: {
            id: true,
            websiteUrl: true,
            companyName: true,
            scrapingStatus: true,
            messageStatus: true,
            submissionStatus: true,
            createdAt: true
          }
        },
        users: {
          select: {
            id: true,
            name: true,
            email: true
          }
        }
      }
    });
    
    if (upload) {
      console.log('\n✅ Upload found:');
      console.log('ID:', upload.id);
      console.log('Filename:', upload.filename);
      console.log('Original Name:', upload.originalName);
      console.log('Status:', upload.status);
      console.log('Created At:', upload.createdAt);
      console.log('User:', upload.users ? `${upload.users.name} (${upload.users.email})` : 'No user');
      console.log('Total Websites:', upload.websites.length);
      console.log('Websites:');
      upload.websites.forEach((website, index) => {
        console.log(`  ${index + 1}. ${website.websiteUrl}`);
        console.log(`     Company: ${website.companyName}`);
        console.log(`     Scraping: ${website.scrapingStatus}`);
        console.log(`     Message: ${website.messageStatus}`);
        console.log(`     Submission: ${website.submissionStatus}`);
        console.log(`     Created: ${website.createdAt}`);
      });
    } else {
      console.log('\n❌ Upload not found in database');
    }
    
    // Check if there are any similar uploads
    console.log('\n🔍 Checking for similar uploads...');
    const similarUploads = await prisma.file_uploads.findMany({
      where: {
        OR: [
          { filename: { contains: '7d2bcc5c' } },
          { originalName: { contains: '7d2bcc5c' } }
        ]
      },
      select: {
        id: true,
        filename: true,
        originalName: true,
        status: true,
        createdAt: true
      }
    });
    
    if (similarUploads.length > 0) {
      console.log('Similar uploads found:');
      similarUploads.forEach(upload => {
        console.log(`  - ${upload.id}: ${upload.filename} (${upload.status})`);
      });
    } else {
      console.log('No similar uploads found');
    }
    
    // Check recent uploads to see if this might be a different ID
    console.log('\n📅 Recent uploads (last 10):');
    const recentUploads = await prisma.file_uploads.findMany({
      orderBy: { createdAt: 'desc' },
      take: 10,
      select: {
        id: true,
        filename: true,
        originalName: true,
        status: true,
        createdAt: true
      }
    });
    
    recentUploads.forEach(upload => {
      console.log(`  - ${upload.id}: ${upload.filename} (${upload.status}) - ${upload.createdAt}`);
    });
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await prisma.$disconnect();
  }
}

checkUpload();
