# Stage 1: Build Go WhatsApp Bridge
FROM golang:1.23-alpine AS go-builder

WORKDIR /build
COPY whatsapp-bridge/ ./
RUN go mod download
RUN CGO_ENABLED=0 GOOS=linux go build -o whatsapp-bridge main.go

# Stage 2: Python MCP Server
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ca-certificates bash && rm -rf /var/lib/apt/lists/*

COPY --from=go-builder /build/whatsapp-bridge /usr/local/bin/whatsapp-bridge
RUN chmod +x /usr/local/bin/whatsapp-bridge

COPY whatsapp-mcp-server/ ./

RUN pip install --no-cache-dir fastapi uvicorn pydantic httpx requests anyio python-multipart qrcode[pil]

# Create writable store directory
RUN mkdir -p /app/store && chmod 777 /app/store

# Startup script
RUN printf '#!/bin/bash\nwhatsapp-bridge &\nsleep 5\npython server.py\n' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 8000

ENTRYPOINT ["/bin/bash", "/app/start.sh"]