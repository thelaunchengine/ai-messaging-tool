# Use Node.js 20 Alpine as base image
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies with legacy peer deps
RUN npm ci --legacy-peer-deps

# Copy Prisma schema first
COPY prisma ./prisma

# Generate Prisma client
RUN npx prisma generate

# Copy rest of source code
COPY . .

# Expose port 3000
EXPOSE 3000

# Start the application in development mode
CMD ["sh", "-c", "npm run dev -- -H 0.0.0.0 -p ${PORT:-3000}"]
