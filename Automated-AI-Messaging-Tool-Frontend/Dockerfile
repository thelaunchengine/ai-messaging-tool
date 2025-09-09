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

# Start the application with database migration and pre-compilation
CMD ["sh", "-c", "echo 'Starting database migration...' && node migrate-db.js && echo 'Migration completed, pre-compiling routes...' && npm run dev -- -H 0.0.0.0 -p ${PORT:-3000} & sleep 30 && curl -s http://localhost:3000/ > /dev/null && curl -s http://localhost:3000/api/auth/providers > /dev/null && curl -s http://localhost:3000/login > /dev/null && echo 'Pre-compilation completed' && wait"]
