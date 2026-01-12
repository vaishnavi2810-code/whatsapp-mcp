# WhatsApp MCP FastAPI Server

A FastAPI-based REST API for the WhatsApp MCP Server. Exposes all WhatsApp messaging functionality as HTTP endpoints, with WebSocket support for real-time message updates.

## Features

- ✅ **REST API** - Full HTTP API for all WhatsApp operations
- ✅ **WebSocket Support** - Real-time message streaming
- ✅ **CORS Enabled** - Ready for frontend integration
- ✅ **File Upload/Download** - Send and receive media
- ✅ **Auto Documentation** - Interactive Swagger UI at `/docs`
- ✅ **Error Handling** - Consistent error responses
- ✅ **Pagination** - Built-in pagination for chats/messages

## Prerequisites

1. **Go Bridge Running** - The WhatsApp bridge must be running:
   ```bash
   cd whatsapp-bridge
   go run main.go
   ```
   
2. **Python 3.11+** installed

3. **Dependencies installed**:
   ```bash
   pip install -e .
   ```

## Installation & Setup

### 1. Install Dependencies

```bash
cd whatsapp-mcp-server
pip install -e .
```

### 2. Start the Go Bridge (if not already running)

```bash
cd ../whatsapp-bridge
go run main.go
```

This will:
- Prompt for WhatsApp QR code scan (first time)
- Start REST API on `http://localhost:8080`
- Initialize SQLite databases

### 3. Start the FastAPI Server

```bash
cd ../whatsapp-mcp-server
python api.py
```

Or with uvicorn directly:

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health & Info

```
GET  /                 # API info
GET  /health           # Health check
```

### Contacts

```
GET  /contacts?q=search_term    # Search contacts
```

**Response:**
```json
[
  {
    "phone_number": "1234567890",
    "name": "John Doe",
    "jid": "1234567890@s.whatsapp.net"
  }
]
```

### Chats

```
GET  /chats?limit=20&page=0&sort=last_active    # List all chats
GET  /chats/{jid}                               # Get specific chat
GET  /chats/by-phone/{phone_number}             # Get chat by phone
GET  /contacts/{phone_number}/chats             # Get all chats with contact
```

**Response:**
```json
{
  "jid": "1234567890@s.whatsapp.net",
  "name": "John Doe",
  "last_message_time": "2026-01-11T10:30:00",
  "last_message": "Hello!",
  "last_sender": "1234567890@s.whatsapp.net",
  "last_is_from_me": false,
  "is_group": false
}
```

### Messages

```
POST /messages/search                           # Search messages
GET  /chats/{jid}/messages?limit=20&page=0     # Get chat messages
GET  /messages/{message_id}/context?before=5&after=5   # Get message with context
```

**Search Request:**
```json
{
  "after": "2026-01-01T00:00:00",
  "before": "2026-12-31T23:59:59",
  "sender_phone_number": "1234567890",
  "chat_jid": "1234567890@s.whatsapp.net",
  "query": "search text",
  "limit": 20,
  "page": 0
}
```

**Response:**
```json
[
  {
    "id": "msg_123",
    "timestamp": "2026-01-11T10:30:00",
    "sender": "1234567890@s.whatsapp.net",
    "content": "Hello world!",
    "is_from_me": false,
    "chat_jid": "1234567890@s.whatsapp.net",
    "chat_name": "John Doe",
    "media_type": null
  }
]
```

### Send Messages

```
POST /messages/send                  # Send text message
POST /messages/send-file             # Send file (image, video, document)
POST /messages/send-audio            # Send audio as voice message
POST /messages/upload                # Upload and send file directly
```

**Send Text Request:**
```json
{
  "recipient": "1234567890",
  "text": "Hello from API!",
  "is_group": false
}
```

**Send File Request:**
```json
{
  "recipient": "1234567890@s.whatsapp.net",
  "file_path": "/path/to/file.jpg",
  "is_group": false
}
```

**Upload File:**
```bash
curl -X POST \
  -F "file=@/path/to/image.jpg" \
  "http://localhost:8000/messages/upload?recipient=1234567890&is_group=false"
```

### Media Download

```
GET /media/download/{message_id}     # Download media from message
```

### WebSocket (Real-time)

```
WS  /ws/messages                    # Connect to message stream
```

**Connect:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/messages');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('New message:', data);
};
```

**Message Format:**
```json
{
  "type": "message",
  "data": {
    "id": "msg_123",
    "timestamp": "2026-01-11T10:30:00",
    "sender": "1234567890@s.whatsapp.net",
    "content": "Incoming message",
    "is_from_me": false,
    "chat_jid": "1234567890@s.whatsapp.net"
  }
}
```

## Interactive Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI where you can:
- View all endpoints with parameters
- Try API calls directly in browser
- See request/response models
- Test WebSocket connections

## Example: Frontend Integration

### React Example

```javascript
import { useState, useEffect } from 'react';

function ChatApp() {
  const [chats, setChats] = useState([]);
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    // Fetch chats
    fetch('http://localhost:8000/chats')
      .then(r => r.json())
      .then(data => setChats(data));

    // WebSocket for real-time messages
    const ws = new WebSocket('ws://localhost:8000/ws/messages');
    ws.onmessage = (event) => {
      const { type, data } = JSON.parse(event.data);
      if (type === 'message') {
        setMessages(prev => [data, ...prev]);
      }
    };

    return () => ws.close();
  }, []);

  const sendMessage = async (recipient, text) => {
    await fetch('http://localhost:8000/messages/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ recipient, text, is_group: false })
    });
  };

  return (
    <div>
      <h1>WhatsApp Chat</h1>
      {/* Render chats and messages */}
    </div>
  );
}
```

### Vue 3 Example

```vue
<template>
  <div>
    <h1>WhatsApp Messages</h1>
    <div v-for="msg in messages" :key="msg.id">
      <p><strong>{{ msg.sender }}:</strong> {{ msg.content }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const messages = ref([]);

onMounted(() => {
  const ws = new WebSocket('ws://localhost:8000/ws/messages');
  
  ws.onmessage = (event) => {
    const { type, data } = JSON.parse(event.data);
    if (type === 'message') {
      messages.value.unshift(data);
    }
  };
});

const sendMessage = async (recipient, text) => {
  await fetch('http://localhost:8000/messages/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ recipient, text, is_group: false })
  });
};
</script>
```

## Environment Variables

Create a `.env` file for configuration (optional):

```env
# Server
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# WhatsApp Bridge
BRIDGE_URL=http://localhost:8080/api

# Database
MESSAGES_DB_PATH=../whatsapp-bridge/store/messages.db
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Status Codes:**
- `200` - OK
- `400` - Bad request (validation error)
- `404` - Resource not found
- `500` - Server error

## Performance Tips

1. **Pagination** - Always use `limit` and `page` for large queries
2. **Filtering** - Use `chat_jid` or `sender_phone_number` to narrow results
3. **WebSocket** - Prefer WebSocket for real-time updates over polling
4. **File Streaming** - Media downloads are streamed, not buffered

## Production Deployment

### Using Gunicorn + Uvicorn

```bash
pip install gunicorn
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Security Checklist

- [ ] Change CORS origins from `*` to specific domains
- [ ] Add authentication (JWT tokens)
- [ ] Use HTTPS/WSS in production
- [ ] Implement rate limiting
- [ ] Add request validation middleware
- [ ] Run behind reverse proxy (nginx, etc.)

## Troubleshooting

### Connection Refused on Port 8080
- Ensure Go bridge is running: `cd whatsapp-bridge && go run main.go`
- Check bridge is listening: `lsof -i :8080`

### WebSocket Connection Failed
- Check CORS is enabled
- Verify WebSocket URL matches server host/port
- Browser console will show connection errors

### Media Upload Fails
- Ensure `/tmp/whatsapp-api-uploads` directory is writable
- Check file size limits
- Verify file format is supported by WhatsApp

## API Rate Limits

Currently unlimited. Implement in production:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/chats")
@limiter.limit("30/minute")
async def get_chats(request: Request):
    ...
```

## Contributing

To extend the API with more endpoints:

1. Add the function to [whatsapp.py](whatsapp.py) if needed
2. Create a Pydantic model for request/response
3. Add endpoint to [api.py](api.py)
4. Test via `/docs` UI
5. Update this README

## License

Same as parent project

## Support

For issues:
1. Check logs: `uvicorn api:app --log-level debug`
2. Test endpoint via Swagger UI at `/docs`
3. Verify Go bridge is running and healthy
4. Check WebSocket connection in browser DevTools
