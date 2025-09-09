import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';
import { getServerSession } from 'next-auth';
import { authOptions } from 'utils/authOptions';

const prisma = new PrismaClient();

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ userId: string }> }
) {
  try {
    const { userId } = await params;
    
    // Get user ID from the authenticated session
    const session = await getServerSession(authOptions);
    
    if (!session?.user?.id) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Check if user is admin
    const adminUser = await prisma.user.findUnique({
      where: { id: session.user.id },
      select: { role: true }
    });

    if (adminUser?.role !== 'ADMIN' && adminUser?.role !== 'admin') {
      return NextResponse.json(
        { error: 'Access denied. Admin privileges required.' },
        { status: 403 }
      );
    }

    // Get user details
    const user = await prisma.user.findUnique({
      where: { id: userId },
      select: { 
        id: true, 
        name: true, 
        email: true 
      }
    });

    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }

    // Helper function to properly escape CSV values
    const escapeCsvValue = (value: string | null | undefined): string => {
      if (value === null || value === undefined) return '';
      
      // Convert to string and handle special characters
      let str = String(value);
      
      // Replace special characters that might cause encoding issues
      str = str.replace(/®/g, '(R)');
      str = str.replace(/™/g, '(TM)');
      str = str.replace(/©/g, '(C)');
      str = str.replace(/"/g, '""'); // Escape double quotes
      
      // Replace newlines and carriage returns with spaces to keep content in one cell
      str = str.replace(/\r\n/g, ' '); // Windows line breaks
      str = str.replace(/\n/g, ' ');   // Unix line breaks
      str = str.replace(/\r/g, ' ');   // Mac line breaks
      
      // Remove multiple consecutive spaces
      str = str.replace(/\s+/g, ' ');
      
      // If the value contains comma or double quote, wrap in quotes
      if (str.includes(',') || str.includes('"')) {
        return `"${str}"`;
      }
      
      return str;
    };

    // Get all file uploads for this user
    const fileUploads = await prisma.fileUpload.findMany({
      where: { userId },
      include: {
        websites: {
          select: {
            id: true,
            websiteUrl: true,
            contactFormUrl: true,
            companyName: true,
            industry: true,
            scrapingStatus: true,
            messageStatus: true,
            generatedMessage: true,
            createdAt: true,
            updatedAt: true
          }
        }
      },
      orderBy: { createdAt: 'desc' }
    });

    // Generate CSV content
    const csvRows = [];
    
    // Add header
    csvRows.push([
      'Website URL',
      'Company Name',
      'Industry',
      'Scraping Status',
      'Message Status',
      'Generated Message',
      'Created Date'
    ].map(escapeCsvValue).join(','));

    // Add data rows
    fileUploads.forEach(fileUpload => {
      if (fileUpload.websites.length === 0) {
        // Add row for file with no websites
        csvRows.push([
          '',
          '',
          '',
          '',
          '',
          '',
          fileUpload.createdAt.toISOString()
        ].map(escapeCsvValue).join(','));
      } else {
        // Add row for each website
        fileUpload.websites.forEach(website => {
          csvRows.push([
            website.websiteUrl,
            website.companyName || '',
            website.industry || '',
            website.scrapingStatus,
            website.messageStatus,
            website.generatedMessage || '',
            website.createdAt.toISOString()
          ].map(escapeCsvValue).join(','));
        });
      }
    });

    const csvContent = csvRows.join('\n');
    
    // Set response headers for file download
    const response = new NextResponse(csvContent);
    response.headers.set('Content-Type', 'text/csv; charset=utf-8');
    response.headers.set('Content-Disposition', `attachment; filename="${user.name}_processed_reports.csv"`);
    response.headers.set('Cache-Control', 'no-cache');
    
    return response;
  } catch (error) {
    console.error('Error generating user report:', error);
    return NextResponse.json(
      { error: 'Failed to generate user report' },
      { status: 500 }
    );
  }
} 