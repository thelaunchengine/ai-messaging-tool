import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from 'utils/authOptions';
import { prisma } from 'lib/prisma';

export async function GET(
  request: NextRequest,
  { params }: { params: { fileUploadId: string } }
) {
  try {
    const session = await getServerSession(authOptions);
    
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Check if user is admin
    const adminUser = await prisma.user.findUnique({
      where: { id: session.user.id },
      select: { role: true }
    });

    if (adminUser?.role !== 'ADMIN' && adminUser?.role !== 'admin') {
      return NextResponse.json({ error: 'Access denied. Admin privileges required.' }, { status: 403 });
    }

    const { fileUploadId } = params;

    // Get file upload with websites
    const fileUpload = await prisma.fileUpload.findUnique({
      where: { id: fileUploadId },
      include: {
        websites: {
          select: {
            websiteUrl: true,
            companyName: true,
            industry: true,
            contactFormUrl: true,
            scrapingStatus: true,
            messageStatus: true
          }
        }
      }
    });

    if (!fileUpload) {
      return NextResponse.json({ error: 'File upload not found' }, { status: 404 });
    }

    // Prepare CSV data with requested fields
    const csvData = fileUpload.websites.map(website => ({
      'Website URL': website.websiteUrl || '',
      'Company Name': website.companyName || '',
      'Industry': website.industry || '',
      'Website Contact Us URL': website.contactFormUrl || '',
      'Scraping Status': website.scrapingStatus || 'PENDING',
      'Message Submitted': website.messageStatus === 'SENT' ? 'Yes' : 'No'
    }));

    // Create CSV content
    const headers = Object.keys(csvData[0] || {});
    const csvContent = [
      headers.join(','),
      ...csvData.map(row => 
        headers.map(header => `"${row[header] || ''}"`).join(',')
      )
    ].join('\n');

    // Create response with CSV file
    const response = new NextResponse(csvContent);
    response.headers.set('Content-Type', 'text/csv');
    response.headers.set('Content-Disposition', `attachment; filename="${fileUpload.originalName.replace(/\.[^/.]+$/, '')}_results.csv"`);

    return response;

  } catch (error) {
    console.error('Download admin upload error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
