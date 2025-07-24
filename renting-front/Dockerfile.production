# Multi-stage production build for React frontend
FROM node:18-alpine as builder

# Set build arguments
ARG BUILD_ENV=production

# Create app directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies needed for build)
# Don't set NODE_ENV=production yet as we need devDependencies for the build
RUN npm ci && npm cache clean --force

# Copy source code
COPY . .

# Set production environment for the build
ENV NODE_ENV=production

# Build the application
RUN npx vite build

# Production stage with a simple HTTP server
FROM node:18-alpine

# Install a simple HTTP server
RUN npm install -g serve

# Create app directory
WORKDIR /app

# Copy built application from builder stage
COPY --from=builder /app/dist .

# Create non-root user
RUN addgroup -g 1001 -S comfyrent && \
    adduser -S comfyrent -u 1001 -G comfyrent

# Set proper permissions
RUN chown -R comfyrent:comfyrent /app

# Switch to non-root user
USER comfyrent

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

# Expose port
EXPOSE 3000

# Start the application
CMD ["serve", "-s", ".", "-l", "3000"]
