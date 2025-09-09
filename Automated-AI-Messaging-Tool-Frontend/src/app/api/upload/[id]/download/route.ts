import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';
import { getServerSession } from 'next-auth';
import { authOptions } from 'utils/authOptions';

const prisma = new PrismaClient();

export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id: fileUploadId } = await params;
    console.log('Download request for fileUploadId:', fileUploadId);
    
    // Get user from session
    const session = await getServerSession(authOptions);
    console.log('Session user:', session?.user?.id);
    
    if (!session?.user?.id) {
      console.log('No session found, returning 401');
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Get file upload details with processed websites
    const fileUpload = await prisma.fileUpload.findUnique({
      where: { id: fileUploadId },
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
            aboutUsContent: true,
            generatedMessage: true,
            errorMessage: true,
            createdAt: true,
            updatedAt: true
          }
        }
      }
    });

    console.log('FileUpload found:', !!fileUpload);
    if (fileUpload) {
      console.log('FileUpload userId:', fileUpload.userId);
      console.log('Session userId:', session.user.id);
      console.log('Number of websites:', fileUpload.websites.length);
    }

    if (!fileUpload) {
      console.log('File upload not found');
      return NextResponse.json(
        { error: 'File upload not found' },
        { status: 404 }
      );
    }

    // Check if user has permission to download this file
    if (fileUpload.userId !== session.user.id) {
      // Check if user is admin
      const user = await prisma.user.findUnique({
        where: { id: session.user.id },
        select: { role: true }
      });

      console.log('User role:', user?.role);

      if (user?.role !== 'ADMIN' && user?.role !== 'admin') {
        console.log('Access denied - not owner or admin');
        return NextResponse.json(
          { error: 'Access denied' },
          { status: 403 }
        );
      }
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

    // Generate CSV content with processed results
    const csvRows = [];
    
    // Add header
    csvRows.push([
      'Website URL',
      'Company Name',
      'Industry',
      'Contact Form URL',
      'Scraping Status',
      'Message Status',
      'About Us Content',
      'Generated Message',
      'Error Message',
      'Created Date'
    ].map(escapeCsvValue).join(','));

    // Add data rows
    if (fileUpload.websites.length === 0) {
      // Add row for file with no websites
      csvRows.push([
        '',
        '',
        '',
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
          website.contactFormUrl || '',
          website.scrapingStatus,
          website.messageStatus,
          website.aboutUsContent || '',
          website.generatedMessage || '',
          website.errorMessage || '',
          website.createdAt.toISOString()
        ].map(escapeCsvValue).join(','));
      });
    }

    const csvContent = csvRows.join('\n');
    console.log('Generated CSV with', csvRows.length, 'rows');
    
    // Set response headers for file download
    const response = new NextResponse(csvContent);
    response.headers.set('Content-Type', 'text/csv; charset=utf-8');
    response.headers.set('Content-Disposition', `attachment; filename="${fileUpload.originalName.replace(/\.[^/.]+$/, '')}_results.csv"`);
    response.headers.set('Cache-Control', 'no-cache');
    
    console.log('Returning successful download response');
    return response;
  } catch (error) {
    console.error('Error generating results CSV:', error);
    return NextResponse.json(
      { error: 'Failed to generate results CSV' },
      { status: 500 }
    );
  }
} 