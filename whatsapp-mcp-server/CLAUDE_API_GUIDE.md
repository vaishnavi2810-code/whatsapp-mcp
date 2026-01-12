# Claude AI Chatbot API Integration

## Overview

The WhatsApp MCP Server now includes Claude AI-powered message analysis endpoints. These REST API endpoints allow external web clients to query WhatsApp messages and get intelligent insights powered by Claude.

## Architecture

```
Web Client / External App
      ↓ (HTTP Request)
FastAPI Server (Port 8000)
      ├─ Pydantic Validation
      ├─ Message Retrieval (SQLite)
      └─ Claude Analysis (Anthropic API)
            ↓
      Response with AI Insights
```

## Environment Setup

### 1. Install Dependencies

```bash
# Install Anthropic SDK
pip install anthropic>=0.37.0

# Or install via uv
uv pip install anthropic>=0.37.0
```

### 2. Set Anthropic API Key

```bash
# Export environment variable
export ANTHROPIC_API_KEY="sk-ant-..."

# Or set in .env file (if using python-dotenv)
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

## REST API Endpoints

### 1. POST `/analyze/query` - Flexible Message Analysis

**Purpose:** Retrieve messages based on flexible filters and analyze with Claude AI.

**Request Body:**
```json
{
  "after": "2026-01-11T00:00:00",
  "before": "2026-01-11T23:59:59",
  "contact_name": "John",
  "contact_phone": "+1234567890",
  "chat_jid": "1234567890@s.whatsapp.net",
  "keywords": ["project", "deadline"],
  "media_only": false,
  "query_type": "summarize",
  "custom_query": null,
  "max_messages": 100
}
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `after` | string (ISO-8601) | No | Messages after this datetime |
| `before` | string (ISO-8601) | No | Messages before this datetime |
| `contact_name` | string | No | Fuzzy match contact name |
| `contact_phone` | string | No | Exact phone number filter |
| `chat_jid` | string | No | Exact JID filter |
| `keywords` | array | No | List of search terms |
| `media_only` | boolean | No | Only media messages (default: false) |
| `query_type` | string | Yes | Analysis type: "summarize", "topics", "sentiment", "action_items", or "custom" |
| `custom_query` | string | No | Required if query_type="custom" |
| `max_messages` | integer | No | Max messages to retrieve (default: 100) |

**Response:**
```json
{
  "query_type": "summarize",
  "period": "2026-01-11",
  "messages_analyzed": 47,
  "analysis": "Today you had conversations about...",
  "metadata": {
    "topics": ["Project A", "Meeting"],
    "message_count": 47
  },
  "timestamp": "2026-01-11T15:30:45.123456"
}
```

**Example Requests:**

```bash
# Summarize today's messages
curl -X POST http://localhost:8000/analyze/query \
  -H "Content-Type: application/json" \
  -d '{
    "query_type": "summarize",
    "after": "2026-01-11T00:00:00",
    "before": "2026-01-11T23:59:59"
  }'

# Extract topics with keywords
curl -X POST http://localhost:8000/analyze/query \
  -H "Content-Type: application/json" \
  -d '{
    "query_type": "topics",
    "keywords": ["meeting", "deadline"],
    "max_messages": 50
  }'

# Custom analysis
curl -X POST http://localhost:8000/analyze/query \
  -H "Content-Type: application/json" \
  -d '{
    "query_type": "custom",
    "custom_query": "What are the main concerns expressed?",
    "max_messages": 100
  }'
```

---

### 2. POST `/analyze/daily-summary` - Daily Summary

**Purpose:** Quick shortcut to summarize all messages from a specific day.

**Request Body:**
```json
{
  "date": "2026-01-11",
  "include_media": true
}
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date` | string (YYYY-MM-DD) | No | Target date (defaults to today) |
| `include_media` | boolean | No | Include media messages (default: true) |

**Response:**
```json
{
  "query_type": "daily_summary",
  "period": "2026-01-11",
  "messages_analyzed": 127,
  "analysis": "Key topics from today...",
  "metadata": {
    "include_media": true,
    "message_count": 127
  },
  "timestamp": "2026-01-11T15:30:45.123456"
}
```

**Example Requests:**

```bash
# Summary for today
curl -X POST http://localhost:8000/analyze/daily-summary \
  -H "Content-Type: application/json" \
  -d '{}'

# Summary for specific date
curl -X POST http://localhost:8000/analyze/daily-summary \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-10",
    "include_media": false
  }'
```

---

### 3. POST `/analyze/contact-summary/{jid}` - Contact Conversation Summary

**Purpose:** Summarize conversation history with a specific contact.

**URL Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `jid` | string | Yes | Contact JID (e.g., "1234567890@s.whatsapp.net") |

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `days` | integer | No | Days to look back (default: 7) |
| `include_media` | boolean | No | Include media messages (default: true) |

**Response:**
```json
{
  "query_type": "contact_summary",
  "period": "John Doe: last 7 days",
  "messages_analyzed": 34,
  "analysis": "Your conversation with John focused on...",
  "metadata": {
    "contact_jid": "1234567890@s.whatsapp.net",
    "contact_name": "John Doe",
    "days_lookback": 7,
    "message_count": 34
  },
  "timestamp": "2026-01-11T15:30:45.123456"
}
```

**Example Requests:**

```bash
# Last 7 days with contact
curl -X POST "http://localhost:8000/analyze/contact-summary/1234567890@s.whatsapp.net" \
  -H "Content-Type: application/json"

# Last 30 days, no media
curl -X POST "http://localhost:8000/analyze/contact-summary/1234567890@s.whatsapp.net?days=30&include_media=false" \
  -H "Content-Type: application/json"
```

---

### 4. POST `/analyze/search` - Semantic Search

**Purpose:** Semantically search messages for relevance to a concept (not just keyword matching).

**Request Body:**
```json
{
  "search_query": "meetings",
  "after": "2026-01-01T00:00:00",
  "before": "2026-01-31T23:59:59",
  "chat_jid": "123456789@g.us",
  "max_messages": 100
}
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `search_query` | string | Yes | What to search for (concept, topic, or keyword) |
| `after` | string (ISO-8601) | No | Start datetime |
| `before` | string (ISO-8601) | No | End datetime |
| `chat_jid` | string | No | Filter by specific chat |
| `max_messages` | integer | No | Max messages to search (default: 100) |

**Response:**
```json
{
  "search_query": "meetings",
  "results": "Relevant content about meetings...",
  "message_count": 45,
  "period": "recent messages",
  "timestamp": "2026-01-11T15:30:45.123456"
}
```

**Example Requests:**

```bash
# Search for "decisions"
curl -X POST http://localhost:8000/analyze/search \
  -H "Content-Type: application/json" \
  -d '{
    "search_query": "decisions",
    "max_messages": 50
  }'

# Search in specific chat for "problems"
curl -X POST http://localhost:8000/analyze/search \
  -H "Content-Type: application/json" \
  -d '{
    "search_query": "problems",
    "chat_jid": "123456789@g.us",
    "after": "2026-01-01T00:00:00",
    "before": "2026-01-31T23:59:59"
  }'
```

---

## Query Types

### Available Analysis Types (for `/analyze/query`):

1. **summarize** - Generate a summary of conversations
   - Key topics discussed
   - Important messages/decisions
   - Action items
   - Overall conversation tone

2. **topics** - Extract main discussion topics
   - List of topics with descriptions
   - Context for each topic

3. **sentiment** - Analyze conversation sentiment
   - Overall emotion/tone
   - Mood shifts
   - Conflicts or positive interactions

4. **action_items** - Extract tasks and action items
   - What needs to be done
   - Responsibility assignment
   - Deadlines

5. **custom** - Custom analysis with your own prompt
   - Requires `custom_query` parameter
   - Ask any specific question about the messages

---

## Usage Examples

### Example 1: Daily Summary Report

```bash
curl -X POST http://localhost:8000/analyze/daily-summary \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-01-11"}'
```

**Use Case:** Morning briefing of all messages from yesterday

---

### Example 2: Analyze Conversation with Specific Contact

```bash
curl -X POST http://localhost:8000/analyze/contact-summary/1234567890@s.whatsapp.net?days=7 \
  -H "Content-Type: application/json"
```

**Use Case:** Get summary of ongoing discussions with a colleague

---

### Example 3: Find Action Items

```bash
curl -X POST http://localhost:8000/analyze/query \
  -H "Content-Type: application/json" \
  -d '{
    "query_type": "action_items",
    "after": "2026-01-01T00:00:00",
    "before": "2026-01-31T23:59:59"
  }'
```

**Use Case:** Get a checklist of all tasks mentioned this month

---

### Example 4: Semantic Search

```bash
curl -X POST http://localhost:8000/analyze/search \
  -H "Content-Type: application/json" \
  -d '{
    "search_query": "budget concerns",
    "max_messages": 100
  }'
```

**Use Case:** Find all discussions related to budget issues (not just keyword "budget")

---

### Example 5: Custom Analysis

```bash
curl -X POST http://localhost:8000/analyze/query \
  -H "Content-Type: application/json" \
  -d '{
    "query_type": "custom",
    "custom_query": "What are the main bottlenecks mentioned?",
    "keywords": ["blocked", "stuck", "delayed"],
    "max_messages": 75
  }'
```

**Use Case:** Get specific insights tailored to your question

---

## Web Application Integration

### React/JavaScript Example

```javascript
// Call analyze query endpoint
async function analyzeMessages(queryType, options = {}) {
  const response = await fetch('http://localhost:8000/analyze/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query_type: queryType,
      ...options,
    }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}

// Usage
const result = await analyzeMessages('summarize', {
  after: '2026-01-11T00:00:00',
  before: '2026-01-11T23:59:59',
});

console.log(result.analysis);
```

---

### Python Example

```python
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def analyze_messages(query_type, **kwargs):
    """Analyze messages with Claude AI."""
    response = requests.post(
        f"{BASE_URL}/analyze/query",
        json={
            "query_type": query_type,
            **kwargs,
        }
    )
    response.raise_for_status()
    return response.json()

# Get daily summary
today = datetime.now().date()
result = analyze_messages(
    "summarize",
    after=f"{today}T00:00:00",
    before=f"{today}T23:59:59"
)

print(result['analysis'])
```

---

## Error Handling

All endpoints return standard HTTP error responses:

### 400 Bad Request
- Invalid request parameters
- Missing required fields
- Invalid date format

```json
{
  "detail": "custom_query required when query_type='custom'"
}
```

### 500 Internal Server Error
- Claude API failure
- Database errors
- Anthropic API rate limiting

```json
{
  "detail": "Analysis failed: API rate limit exceeded"
}
```

---

## Performance Considerations

1. **Message Context Window**: Default limit is 100 messages to manage API costs
2. **Time Ranges**: More specific date ranges = fewer messages = lower costs
3. **Caching**: Consider caching daily summaries (they don't change)
4. **Batch Operations**: Group multiple analyses for efficiency

---

## API Costs

Costs depend on Claude model usage and message volume:

- **Input tokens**: ~$3 per million tokens (Claude 3.5 Sonnet)
- **Output tokens**: ~$15 per million tokens

For 100 messages (~20KB text), expect ~$0.005-0.01 per analysis request.

---

## Production Checklist

- [ ] Set `ANTHROPIC_API_KEY` securely (e.g., GitHub secrets, AWS Secrets Manager)
- [ ] Add API key authentication to `/analyze/*` endpoints (JWT or API key)
- [ ] Restrict CORS to specific domains (not wildcard)
- [ ] Add rate limiting per API key
- [ ] Implement request logging/monitoring
- [ ] Set up error alerting (Sentry, etc.)
- [ ] Add request timeout handling
- [ ] Document API in OpenAPI/Swagger
- [ ] Test with production message volumes

---

## Troubleshooting

### "ANTHROPIC_API_KEY environment variable not set"
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python api.py
```

### "No messages found for the specified criteria"
- Check date filters (use ISO-8601 format)
- Verify the Go bridge is running and messages are in database
- Try broader date range

### "Analysis failed: API rate limit exceeded"
- Wait a moment and retry
- Reduce `max_messages` parameter
- Batch requests with delays

### Slow responses
- Reduce `max_messages` parameter
- Use more specific date ranges
- Consider caching results

---

## Testing the API

Use the Swagger UI at: `http://localhost:8000/docs`

Or test with curl:

```bash
# Health check
curl http://localhost:8000/health

# Daily summary
curl -X POST http://localhost:8000/analyze/daily-summary \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## Next Steps

1. Deploy the FastAPI server to production
2. Secure API with authentication
3. Build web dashboard to use these endpoints
4. Implement caching for frequently accessed summaries
5. Add rate limiting and monitoring
6. Consider adding streaming responses for long analyses
