import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';
import { z } from 'zod';

const prisma = new PrismaClient();

const createMessageSchema = z.object({
  industry: z.string().min(1),
  service: z.string().min(1),
  message: z.string().min(1),
  status: z.string().default('ACTIVE'),
  messageType: z.string().default('general'),
  tone: z.string().default('professional'),
  targetAudience: z.string().optional(),
  tags: z.array(z.string()).default([]),
  createdBy: z.string().optional()
});

export async function GET() {
  try {
    const messages = await prisma.predefined_messages.findMany({ orderBy: { createdAt: 'desc' } });
    return NextResponse.json({ messages });
  } catch (error) {
    console.error('Error fetching predefined messages:', error);
    return NextResponse.json({ error: 'Failed to fetch messages' }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    console.log('POST /api/predefined-messages called');
    const body = await request.json();
    console.log('Request body:', body);
    
    const validatedData = createMessageSchema.parse(body);
    console.log('Validated data:', validatedData);
    
    // Add required fields
    const dataWithTimestamps = {
      ...validatedData,
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      updatedAt: new Date()
    };
    console.log('Data with timestamps:', dataWithTimestamps);
    
    const message = await prisma.predefined_messages.create({ data: dataWithTimestamps });
    console.log('Created message:', message);
    return NextResponse.json({ message }, { status: 201 });
  } catch (error) {
    console.error('Error in POST /api/predefined-messages:', error);
    if (error instanceof z.ZodError) {
      console.error('Validation error details:', error.errors);
      return NextResponse.json({ error: 'Validation error', details: error.errors }, { status: 400 });
    }
    return NextResponse.json({ error: 'Failed to create message', details: error.message }, { status: 500 });
  }
}
