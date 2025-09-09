# Use Node.js 18 Alpine as base image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies
RUN npm ci

# Copy Prisma schema first
COPY prisma ./prisma

# Generate Prisma client
RUN npx prisma generate

# Copy rest of source code
COPY . .

# Build the application for production
RUN npm run build

# Expose port 3000
EXPOSE 3000

# Start the application in production mode
CMD ["sh", "-c", "npm start -- -H 0.0.0.0 -p ${PORT:-3000}"]
