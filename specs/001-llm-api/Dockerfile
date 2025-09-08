FROM oven/bun:1 as base

WORKDIR /app

# Copy package.json and install dependencies
COPY package.json ./
COPY tsconfig.json ./
RUN bun install

# Copy application code
COPY src/ ./src/

# Build the application
RUN bun run build

# Create data directory for database
RUN mkdir -p /app/data

# Initialize the gateway
RUN bun run src/cli.ts init

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["bun", "run", "src/gateway.ts"]