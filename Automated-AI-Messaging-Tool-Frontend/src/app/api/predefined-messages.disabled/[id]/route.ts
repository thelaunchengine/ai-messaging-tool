import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';
import { z } from 'zod';

const prisma = new PrismaClient();

const updateMessageSchema = z.object({
  industry: z.string().min(1).optional(),
  service: z.string().min(1).optional(),
  message: z.string().min(10).optional(),
  status: z.enum(['ACTIVE', 'INACTIVE']).optional(),
  messageType: z.enum(['general', 'partnership', 'inquiry', 'custom']).optional(),
  tone: z.enum(['professional', 'friendly', 'formal', 'casual']).optional(),
  targetAudience: z.string().optional(),
  tags: z.array(z.string()).optional()
});

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const message = await prisma.predefinedMessage.findUnique({
      where: { id }
    });

    if (!message) {
      return NextResponse.json({ error: 'Message not found' }, { status: 404 });
    }

    return NextResponse.json({ message });
  } catch (error) {
    console.error('Error fetching predefined message:', error);
    return NextResponse.json({ error: 'Failed to fetch message' }, { status: 500 });
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const body = await request.json();
    const validatedData = updateMessageSchema.parse(body);

    // Check if message exists
    const existingMessage = await prisma.predefinedMessage.findUnique({
      where: { id }
    });

    if (!existingMessage) {
      return NextResponse.json({ error: 'Message not found' }, { status: 404 });
    }

    const updatedMessage = await prisma.predefinedMessage.update({
      where: { id },
      data: {
        ...validatedData,
        updatedAt: new Date()
      }
    });

    return NextResponse.json({
      message: 'Predefined message updated successfully',
      data: updatedMessage
    });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        {
          error: 'Validation error',
          details: error.errors
        },
        { status: 400 }
      );
    }

    console.error('Error updating predefined message:', error);
    return NextResponse.json({ error: 'Failed to update message' }, { status: 500 });
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    // Check if message exists
    const existingMessage = await prisma.predefinedMessage.findUnique({
      where: { id }
    });

    if (!existingMessage) {
      return NextResponse.json({ error: 'Message not found' }, { status: 404 });
    }

    await prisma.predefinedMessage.delete({
      where: { id }
    });

    return NextResponse.json({ message: 'Predefined message deleted successfully' });
  } catch (error) {
    console.error('Error deleting predefined message:', error);
    return NextResponse.json({ error: 'Failed to delete message' }, { status: 500 });
  }
}
