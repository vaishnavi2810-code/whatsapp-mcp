# Stage 1: Build Go WhatsApp Bridge
FROM golang:1.21-alpine AS go-builder

WORKDIR /build
COPY whatsapp-bridge/ ./

RUN go mod download
RUN CGO_ENABLED=0 GOOS=linux go build -o whatsapp-bridge main.go

# Stage 2: Python MCP Server
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy Go bridge binary from stage 1
COPY --from=go-builder /build/whatsapp-bridge /usr/local/bin/whatsapp-bridge

# Copy Python MCP server files
COPY whatsapp-mcp-server/ ./

# Install Python dependencies using uv
RUN pip install --no-cache-dir uv && \
    uv pip install --system --no-cache .

# Expose port for SSE
EXPOSE 8000

# Start the MCP server
CMD ["python", "main.py"]
