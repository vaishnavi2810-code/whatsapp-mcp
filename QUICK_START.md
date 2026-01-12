# Quick Start Guide: WhatsApp MCP FastAPI

## 🚀 30-Second Setup

### Option 1: Docker Compose (Recommended)

```bash
# Start both services with one command
docker-compose up -d

# API available at: http://localhost:8000
# Go to http://localhost:8000/docs for interactive documentation
```

### Option 2: Manual Setup

**Step 1: Start Go Bridge**
```bash
cd whatsapp-bridge
go run main.go

# First time: Scan QR code with WhatsApp phone
# Next times: Automatic connection
```

**Step 2: Start FastAPI Server (in another terminal)**
```bash
cd whatsapp-mcp-server
pip install -e .
python api.py
```

**Step 3: Visit API Documentation**
```
http://localhost:8000/docs
```

---

## 📋 Common Tasks

### 1. Send a Text Message

**Via cURL:**
```bash
curl -X POST http://localhost:8000/messages/send \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "1234567890",
    "text": "Hello from API!"
  }'
```

**Via Python:**
```python
import requests

response = requests.post('http://localhost:8000/messages/send', json={
    'recipient': '1234567890',
    'text': 'Hello from Python!'
})
print(response.json())
```

**Via JavaScript:**
```javascript
fetch('http://localhost:8000/messages/send', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    recipient: '1234567890',
    text: 'Hello from JavaScript!'
  })
}).then(r => r.json()).then(console.log);
```

### 2. Get All Chats

```bash
curl http://localhost:8000/chats?limit=20
```

### 3. Search Messages

```bash
curl -X POST http://localhost:8000/messages/search \
  -H "Content-Type: application/json" \
  -d '{
    "chat_jid": "1234567890@s.whatsapp.net",
    "query": "hello",
    "limit": 10
  }'
```

### 4. Send a File

```bash
curl -X POST \
  -F "file=@/path/to/image.jpg" \
  "http://localhost:8000/messages/upload?recipient=1234567890"
```

### 5. Download Media from Message

```bash
curl http://localhost:8000/media/download/msg_12345 -o downloaded_file
```

### 6. Real-time Message Stream (WebSocket)

**JavaScript:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/messages');

ws.onopen = () => {
  console.log('Connected to message stream');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('New message:', message);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

---

## 🎯 Frontend Integration Examples

### React Component

```javascript
import React, { useState, useEffect } from 'react';

function WhatsAppChat() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [recipientPhone, setRecipientPhone] = useState('');

  useEffect(() => {
    // Connect to WebSocket for real-time messages
    const ws = new WebSocket('ws://localhost:8000/ws/messages');
    
    ws.onmessage = (event) => {
      const { type, data } = JSON.parse(event.data);
      if (type === 'message') {
        setMessages(prev => [data, ...prev]);
      }
    };

    return () => ws.close();
  }, []);

  const sendMessage = async () => {
    if (!inputValue.trim() || !recipientPhone.trim()) return;

    try {
      const response = await fetch('http://localhost:8000/messages/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          recipient: recipientPhone,
          text: inputValue
        })
      });

      if (response.ok) {
        setInputValue('');
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '20px' }}>
      <h1>WhatsApp Chat</h1>
      
      <input
        type="text"
        placeholder="Recipient phone number"
        value={recipientPhone}
        onChange={(e) => setRecipientPhone(e.target.value)}
        style={{ width: '100%', padding: '8px', marginBottom: '10px' }}
      />

      <div style={{ height: '300px', border: '1px solid #ccc', padding: '10px', marginBottom: '10px', overflowY: 'auto' }}>
        {messages.map((msg, idx) => (
          <div key={idx} style={{ marginBottom: '10px', padding: '8px', backgroundColor: msg.is_from_me ? '#DCF8C6' : '#E3E3E3', borderRadius: '8px' }}>
            <strong>{msg.sender}:</strong> {msg.content}
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', gap: '10px' }}>
        <input
          type="text"
          placeholder="Type message..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          style={{ flex: 1, padding: '8px' }}
        />
        <button onClick={sendMessage} style={{ padding: '8px 16px', cursor: 'pointer' }}>
          Send
        </button>
      </div>
    </div>
  );
}

export default WhatsAppChat;
```

### Vue 3 Component

```vue
<template>
  <div class="chat-container">
    <h1>WhatsApp Chat</h1>
    
    <input
      v-model="recipientPhone"
      type="text"
      placeholder="Recipient phone number"
    />

    <div class="messages">
      <div v-for="msg in messages" :key="msg.id" :class="{ 'from-me': msg.is_from_me }">
        <strong>{{ msg.sender }}:</strong> {{ msg.content }}
      </div>
    </div>

    <div class="input-area">
      <input v-model="inputValue" @keyup.enter="sendMessage" placeholder="Type message..." />
      <button @click="sendMessage">Send</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const messages = ref([]);
const inputValue = ref('');
const recipientPhone = ref('');

onMounted(() => {
  const ws = new WebSocket('ws://localhost:8000/ws/messages');
  
  ws.onmessage = (event) => {
    const { type, data } = JSON.parse(event.data);
    if (type === 'message') {
      messages.value.unshift(data);
    }
  };
});

const sendMessage = async () => {
  if (!inputValue.value.trim() || !recipientPhone.value.trim()) return;

  await fetch('http://localhost:8000/messages/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      recipient: recipientPhone.value,
      text: inputValue.value
    })
  });

  inputValue.value = '';
};
</script>

<style scoped>
.chat-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.messages {
  height: 300px;
  border: 1px solid #ccc;
  padding: 10px;
  margin: 10px 0;
  overflow-y: auto;
}

.messages div {
  margin-bottom: 10px;
  padding: 8px;
  border-radius: 8px;
  background-color: #e3e3e3;
}

.messages div.from-me {
  background-color: #dcf8c6;
  margin-left: 20px;
}

.input-area {
  display: flex;
  gap: 10px;
}

input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

button {
  padding: 8px 16px;
  background-color: #25D366;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #20BA58;
}
</style>
```

---

## 🔗 API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| GET | `/contacts` | Search contacts |
| GET | `/chats` | List chats |
| GET | `/chats/{jid}` | Get chat details |
| POST | `/messages/search` | Search messages |
| POST | `/messages/send` | Send text message |
| POST | `/messages/upload` | Upload and send file |
| POST | `/messages/send-file` | Send file from path |
| POST | `/messages/send-audio` | Send audio message |
| GET | `/media/download/{message_id}` | Download media |
| WS | `/ws/messages` | Real-time message stream |

---

## 🐛 Troubleshooting

**"Connection refused on port 8080"**
- Go bridge not running. Start it: `cd whatsapp-bridge && go run main.go`

**"WebSocket connection failed"**
- Check CORS is enabled (it should be by default)
- Verify correct host/port in WebSocket URL
- Check browser console for errors

**"Module 'fastapi' not found"**
- Install dependencies: `pip install -e .`

**"File not found: messages.db"**
- Run Go bridge at least once to create database
- Check path in whatsapp.py `MESSAGES_DB_PATH`

**Port already in use**
- Change port: `uvicorn api:app --port 8001`
- Or kill process: `lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill`

---

## 📚 Full Documentation

For complete API documentation, visit:
- **Interactive Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Spec**: http://localhost:8000/openapi.json

---

## 🚀 Next Steps

1. **Customize** - Update CORS origins, add authentication
2. **Deploy** - Use Docker Compose for production
3. **Monitor** - Add logging and error tracking
4. **Scale** - Run multiple API instances behind load balancer
5. **Security** - Add rate limiting, API keys, HTTPS

---

Enjoy building with WhatsApp MCP! 🎉
