import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';
import { z } from 'zod';

const prisma = new PrismaClient();

const createMessageSchema = z.object({
  industry: z.string().min(1),
  service: z.string().min(1),
  message: z.string().min(1),
  status: z.enum(['ACTIVE', 'INACTIVE']),
  messageType: z.enum(['general', 'partnership', 'inquiry', 'custom']),
  tone: z.enum(['professional', 'friendly', 'formal', 'casual']),
  targetAudience: z.string().optional(),
  tags: z.array(z.string()).optional()
});

export async function GET() {
  try {
    const messages = await prisma.predefinedMessage.findMany({ orderBy: { createdAt: 'desc' } });
    return NextResponse.json({ messages });
  } catch (error) {
    console.error('Error fetching predefined messages:', error);
    return NextResponse.json({ error: 'Failed to fetch messages' }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const validatedData = createMessageSchema.parse(body);
    const message = await prisma.predefinedMessage.create({ data: validatedData });
    return NextResponse.json({ message }, { status: 201 });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json({ error: 'Validation error', details: error.errors }, { status: 400 });
    }
    console.error('Error creating predefined message:', error);
    return NextResponse.json({ error: 'Failed to create message' }, { status: 500 });
  }
}
