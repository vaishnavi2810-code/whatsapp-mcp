# WhatsApp MCP Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Web/Mobile)                    │
│  React / Vue / Angular / or any JavaScript framework            │
│  ✓ HTTP REST calls to /api/v1/* endpoints                       │
│  ✓ WebSocket connection to /ws/messages for real-time updates   │
└───────────────────────────────────────────────────────────────┬─┘
                                                                  │
                            HTTPS/WSS
                                                                  │
┌───────────────────────────────────────────────────────────────▼─┐
│                    FastAPI REST Server                          │
│                  (whatsapp-mcp-server/api.py)                   │
│                                                                  │
│  Port: 8000                                                      │
│                                                                  │
│  ├─ Contacts Endpoints      (search, list)                      │
│  ├─ Chats Endpoints         (list, get, filter)                 │
│  ├─ Messages Endpoints      (search, get context)               │
│  ├─ Send Endpoints          (text, file, audio)                 │
│  ├─ Media Endpoints         (download, upload)                  │
│  ├─ WebSocket Endpoint      (real-time messages)                │
│  ├─ Health Checks           (/health, /docs, /redoc)            │
│  └─ Documentation           (Swagger UI, OpenAPI spec)          │
└───────────────────────────────────────────────────────────────┬─┘
                                                                  │
                         Local HTTP
                                                                  │
┌───────────────────────────────────────────────────────────────▼─┐
│                  Go WhatsApp Bridge                              │
│              (whatsapp-bridge/main.go)                           │
│                                                                  │
│  Port: 8080                                                      │
│                                                                  │
│  ├─ WhatsApp Web Client     (whatsmeow library)                  │
│  ├─ SQLite Database         (messages.db, whatsapp.db)           │
│  ├─ REST API                (/api/send, /api/download)          │
│  ├─ Session Management      (QR code, auto-reconnect)           │
│  └─ Message Listener        (stores incoming messages)          │
└───────────────────────────────────────────────────────────────┬─┘
                                                                  │
                      WhatsApp Protocol
                                                                  │
┌───────────────────────────────────────────────────────────────▼─┐
│                    WhatsApp Servers                              │
│         (message delivery, media storage, authentication)        │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### 1. Send Message Flow

```
Frontend           FastAPI         Go Bridge        WhatsApp
   │                │                 │                │
   ├─POST /send────→│                 │                │
   │                ├─Validate───────→│                │
   │                ├─Call /api/send─→│                │
   │                │                 ├─Create msg────→│
   │                │                 ├─Send protobuf─→│
   │                │                 │                ├─Deliver
   │                │                 │←─ACK──────────┤
   │                │←─Response───────┤                │
   │←──200 OK───────┤                 │                │
   │                │                 │                │
```

### 2. Receive Message (WebSocket)

```
WhatsApp        Go Bridge           FastAPI         Frontend
   │                │                  │                │
   ├─New message───→│                  │                │
   │                ├─Parse msg───────→│                │
   │                ├─Store in DB      │                │
   │                │                  ├─Broadcast────→│
   │                │                  │                ├─Update UI
   │                │                  │                │
```

### 3. Download Media

```
Frontend           FastAPI         Go Bridge        WhatsApp
   │                │                 │                │
   ├─GET /download→│                 │                │
   │                ├─Call /api/dl────→│                │
   │                │                 ├─Fetch media──→│
   │                │                 │←─File────────┤
   │                │←─File data──────┤                │
   │←─Stream file──┤                 │                │
   │                │                 │                │
```

## Component Responsibilities

### Frontend (Web/Mobile App)
- User interface and interaction
- Form handling and validation
- Real-time message display via WebSocket
- Media upload/download UI

### FastAPI Server
- REST API endpoint management
- Request/response validation
- CORS handling
- WebSocket connection management
- Authentication/authorization
- Input sanitization

### Go WhatsApp Bridge
- WhatsApp protocol implementation
- QR code authentication
- Message encryption/decryption
- Media file handling
- SQLite database operations
- Session persistence

### WhatsApp Servers
- Message delivery
- Media storage and retrieval
- User authentication
- Group management

## Database Schema

### SQLite Databases

#### messages.db
```
┌─ chats table
│  ├─ jid (PRIMARY KEY)         "1234567890@s.whatsapp.net"
│  ├─ name                      "John Doe"
│  └─ last_message_time         2026-01-11T10:30:00
│
└─ messages table
   ├─ id (PRIMARY KEY)          "msg_abc123"
   ├─ chat_jid (FK)             "1234567890@s.whatsapp.net"
   ├─ sender                    "1234567890@s.whatsapp.net"
   ├─ content                   "Hello world!"
   ├─ timestamp                 2026-01-11T10:30:00
   ├─ is_from_me                true/false
   ├─ media_type                "image" / "video" / null
   ├─ filename                  "photo.jpg"
   ├─ url                       "https://mmg.whatsapp.net/..."
   └─ file_sha256               [BLOB]
```

#### whatsapp.db
```
Session storage (managed by Go bridge)
  - Private keys
  - Device info
  - Connection state
```

## Deployment Architectures

### Single Server (Docker)
```
┌─ Docker Host
│  ├─ Container: whatsapp-bridge:8080
│  └─ Container: whatsapp-api:8000
│     └─ Shared volume: /bridge-store
└─ Nginx reverse proxy on :443
```

### Kubernetes (Production)
```
┌─ Kubernetes Cluster
│  ├─ Deployment: whatsapp-bridge (1 replica)
│  │  └─ Service: bridge.default.svc
│  ├─ Deployment: whatsapp-api (3+ replicas)
│  │  ├─ Service: api.default.svc
│  │  └─ Ingress: api.yourdomain.com
│  ├─ PersistentVolume: /bridge-store
│  └─ ConfigMap: environment config
└─ Load Balancer (external)
```

### Traditional Server (Ubuntu)
```
┌─ VPS / Dedicated Server
│  ├─ Supervisor: whatsapp-bridge
│  ├─ Supervisor: whatsapp-api (gunicorn)
│  └─ Nginx reverse proxy
│     ├─ :443 → whatsapp-api:8000
│     └─ /ws → WhatsApp API:8000
└─ Systemd services / Cron jobs
```

## Request/Response Flow Examples

### Example 1: Send Text Message

**Request:**
```http
POST /messages/send HTTP/1.1
Host: api.yourdomain.com
Content-Type: application/json

{
  "recipient": "1234567890",
  "text": "Hello from API!",
  "is_group": false
}
```

**FastAPI Processing:**
1. Validate request with Pydantic model
2. Check recipient format
3. Call Go bridge REST API
4. Return response

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "message": "Message sent",
  "result": {
    "message_id": "msg_abc123",
    "timestamp": "2026-01-11T10:30:00"
  }
}
```

### Example 2: Get Chat Messages

**Request:**
```http
GET /chats/1234567890@s.whatsapp.net/messages?limit=20&page=0 HTTP/1.1
Host: api.yourdomain.com
```

**FastAPI Processing:**
1. Extract path params (jid)
2. Extract query params (limit, page)
3. Query SQLite via Go bridge
4. Convert Message objects to JSON
5. Return paginated results

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

[
  {
    "id": "msg_xyz",
    "timestamp": "2026-01-11T10:30:00",
    "sender": "1234567890@s.whatsapp.net",
    "content": "Hello!",
    "is_from_me": false,
    "chat_jid": "1234567890@s.whatsapp.net",
    "chat_name": "John Doe",
    "media_type": null
  },
  ...
]
```

### Example 3: WebSocket Real-time Messages

**Connection Establishment:**
```javascript
const ws = new WebSocket('ws://api.yourdomain.com/ws/messages');

ws.onopen = () => {
  console.log('Connected');
};

ws.onmessage = (event) => {
  const { type, data } = JSON.parse(event.data);
  
  if (type === 'message') {
    console.log('New message:', {
      from: data.sender,
      text: data.content,
      time: data.timestamp
    });
  }
};
```

**Server Broadcasting:**
```
Message arrives at WhatsApp → Go Bridge stores in DB
→ Go Bridge detects new message
→ FastAPI broadcasts to all connected WebSocket clients
→ Frontend updates UI in real-time
```

## Error Handling

### HTTP Status Codes
```
200 OK                - Request successful
400 Bad Request      - Invalid input (validation error)
401 Unauthorized     - Missing/invalid authentication
403 Forbidden        - User not authorized
404 Not Found        - Resource doesn't exist
429 Too Many Requests - Rate limit exceeded
500 Server Error     - Internal server error
503 Service Unavailable - Bridge or database down
```

### Error Response Format
```json
{
  "detail": "User-friendly error message"
}
```

## Performance Characteristics

### Message Operations
- Send message: ~500ms (includes network latency)
- Search messages: ~100ms (local database)
- Get chats: ~50ms (local database)
- Download media: Depends on file size

### Database
- SQLite can handle ~100k messages efficiently
- Indexed queries on timestamp and chat_jid
- Need migration to PostgreSQL for >1M messages

### Network
- HTTP/REST: Synchronous request-response
- WebSocket: Persistent bi-directional connection
- Payload size: <10KB typical message

## Security Layers

```
┌─ HTTPS/WSS (Transport Layer)
│  Encrypts data in transit
│
├─ CORS (Origin Validation)
│  Only allow requests from approved domains
│
├─ Authentication (Planned)
│  JWT tokens or API keys
│
├─ Input Validation (Pydantic)
│  Prevent injection attacks
│
└─ Database Security
   SQLite with proper access controls
```

## Scaling Strategy

### Phase 1: Single Server (Current)
- Docker Compose on single VPS
- SQLite database
- Suitable for: Personal use, small teams

### Phase 2: HA Setup
- Docker Compose on multiple servers
- PostgreSQL database (shared)
- Load balancer in front
- Suitable for: Medium deployments

### Phase 3: Kubernetes
- Horizontal pod autoscaling
- Redis caching layer
- Prometheus monitoring
- Suitable for: Large-scale production

---

**This architecture is modular and can scale from personal to enterprise use!**
