# Stage 1: Build Go WhatsApp Bridge
FROM golang:1.23-alpine AS go-builder

WORKDIR /build
COPY whatsapp-bridge/ ./
RUN go mod download
RUN apk add --no-cache gcc musl-dev sqlite-dev
#run go env -w CGO_ENABLED=1
RUN CGO_ENABLED=1 GOOS=linux go build -o whatsapp-bridge main.go

# Stage 2: Python MCP Server
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y golang-go ca-certificates bash procps && rm -rf /var/lib/apt/lists/*

COPY --from=go-builder /build/whatsapp-bridge /usr/local/bin/whatsapp-bridge
RUN chmod +x /usr/local/bin/whatsapp-bridge

COPY whatsapp-mcp-server/ ./

RUN pip install --no-cache-dir fastapi uvicorn pydantic httpx requests anyio python-multipart qrcode[pil]

# Create writable store directory
RUN mkdir -p /app/store && chmod 777 /app/store

# Enhanced startup script with detailed logging
RUN printf '#!/bin/bash\n\
set -e\n\
\n\
echo "=========================================="\n\
echo "STARTUP SCRIPT BEGINS"\n\
echo "=========================================="\n\
echo "Current directory: $(pwd)"\n\
echo "Current user: $(whoami)"\n\
echo ""\n\
\n\
echo "=========================================="\n\
echo "Checking if whatsapp-bridge binary exists..."\n\
echo "=========================================="\n\
ls -la /usr/local/bin/whatsapp-bridge || echo "ERROR: Binary not found!"\n\
echo ""\n\
\n\
echo "=========================================="\n\
echo "Starting WhatsApp Bridge..."\n\
echo "=========================================="\n\
/usr/local/bin/whatsapp-bridge 2>&1 &\n\
BRIDGE_PID=$!\n\
echo "Bridge started with PID: $BRIDGE_PID"\n\
echo ""\n\
\n\
echo "Waiting for bridge to initialize..."\n\
for i in {1..15}; do\n\
    sleep 1\n\
    if ! kill -0 $BRIDGE_PID 2>/dev/null; then\n\
        echo "ERROR: Bridge process died after $i seconds!"\n\
        echo "Bridge may have crashed or failed to start"\n\
        break\n\
    fi\n\
    echo "Bridge still running... ($i/15)"\n\
done\n\
echo ""\n\
\n\
echo "=========================================="\n\
echo "Checking if bridge is listening on port 8080..."\n\
echo "=========================================="\n\
netstat -tulpn 2>/dev/null | grep 8080 || echo "No process listening on port 8080"\n\
echo ""\n\
\n\
echo "=========================================="\n\
echo "Starting Python API Server..."\n\
echo "=========================================="\n\
exec python server.py\n\
' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 8000

ENTRYPOINT ["/bin/bash", "/app/start.sh"]