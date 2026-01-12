# Claude AI Chatbot API - Quick Reference

## TL;DR - Start Using in 5 Minutes

### 1. Set API Key
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

### 2. Start Server
```bash
cd whatsapp-mcp-server
python3 -m uvicorn api:app --port 8000
```

### 3. Make Request
```bash
curl -X POST http://localhost:8000/analyze/daily-summary \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## 4 Core Endpoints

### 📊 Daily Summary
```bash
POST /analyze/daily-summary
{ "date": "2026-01-11", "include_media": true }
```
→ Get quick summary of all messages from a date

### 🔍 Custom Query
```bash
POST /analyze/query
{
  "query_type": "summarize|topics|sentiment|action_items|custom",
  "after": "2026-01-11T00:00:00",
  "before": "2026-01-11T23:59:59",
  "max_messages": 100
}
```
→ Flexible analysis with filters

### 👤 Contact Summary
```bash
POST /analyze/contact-summary/{jid}?days=7&include_media=true
```
→ Analyze conversation with specific contact

### 🎯 Semantic Search
```bash
POST /analyze/search
{ "search_query": "meetings", "max_messages": 100 }
```
→ AI-powered concept search (not keyword matching)

---

## Query Types (for /analyze/query)

| Type | What It Does |
|------|---|
| **summarize** | Key topics, decisions, action items |
| **topics** | Main discussion topics |
| **sentiment** | Overall emotion/tone |
| **action_items** | Tasks and to-dos |
| **custom** | Your own analysis prompt |

---

## Real-World Examples

### Get Today's Summary
```bash
curl -X POST http://localhost:8000/analyze/daily-summary \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Find This Week's Action Items
```bash
curl -X POST http://localhost:8000/analyze/query \
  -H "Content-Type: application/json" \
  -d '{
    "query_type": "action_items",
    "after": "2026-01-05T00:00:00",
    "before": "2026-01-11T23:59:59"
  }'
```

### Analyze Conversation with John
```bash
curl -X POST "http://localhost:8000/analyze/contact-summary/1234567890@s.whatsapp.net?days=7" \
  -H "Content-Type: application/json"
```

### Search for Budget Discussions
```bash
curl -X POST http://localhost:8000/analyze/search \
  -H "Content-Type: application/json" \
  -d '{
    "search_query": "budget concerns",
    "max_messages": 100
  }'
```

### Custom Analysis
```bash
curl -X POST http://localhost:8000/analyze/query \
  -H "Content-Type: application/json" \
  -d '{
    "query_type": "custom",
    "custom_query": "What problems were mentioned?",
    "max_messages": 50
  }'
```

---

## Response Format

```json
{
  "query_type": "summarize",
  "period": "2026-01-11",
  "messages_analyzed": 47,
  "analysis": "Today you discussed...",
  "metadata": {
    "topics": ["Project A", "Meeting"],
    "message_count": 47
  },
  "timestamp": "2026-01-11T15:30:45Z"
}
```

---

## Environment Setup

| Step | Command |
|------|---------|
| Install SDK | `pip install anthropic>=0.37.0` |
| Set API Key | `export ANTHROPIC_API_KEY="sk-ant-..."` |
| Start Server | `python -m uvicorn api:app --port 8000` |
| Health Check | `curl http://localhost:8000/health` |
| View Docs | Open `http://localhost:8000/docs` |

---

## Common Filters

| Parameter | Example | Purpose |
|-----------|---------|---------|
| `after` | "2026-01-01T00:00:00" | Messages after this time |
| `before` | "2026-01-31T23:59:59" | Messages before this time |
| `keywords` | ["budget", "deadline"] | Search terms |
| `max_messages` | 50 | Limit message count |
| `media_only` | true | Only media messages |
| `days` | 7 | Days to look back |

---

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success ✓ |
| 400 | Bad request (invalid parameters) |
| 500 | Server error (API failure) |

---

## Python Integration

```python
import requests
from datetime import datetime

def analyze(query_type, **kwargs):
    r = requests.post(
        'http://localhost:8000/analyze/query',
        json={'query_type': query_type, **kwargs}
    )
    return r.json()

# Use it
result = analyze('summarize', 
    after='2026-01-11T00:00:00',
    before='2026-01-11T23:59:59'
)
print(result['analysis'])
```

---

## JavaScript Integration

```javascript
async function analyze(queryType, options = {}) {
  const r = await fetch('http://localhost:8000/analyze/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query_type: queryType,
      ...options,
    }),
  });
  return r.json();
}

// Use it
const result = await analyze('summarize', {
  after: '2026-01-11T00:00:00',
  before: '2026-01-11T23:59:59'
});
console.log(result.analysis);
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| API key not set | `export ANTHROPIC_API_KEY="sk-ant-..."` |
| No messages found | Check date format (ISO-8601) |
| Rate limit exceeded | Wait and retry, reduce max_messages |
| Slow responses | Reduce max_messages or use narrower dates |

---

## Files Created/Modified

- ✅ `claude.py` - Claude integration module
- ✅ `api.py` - REST endpoints (4 new)
- ✅ `whatsapp.py` - Enhanced message filtering
- ✅ `CLAUDE_API_GUIDE.md` - Full documentation
- ✅ `IMPLEMENTATION_SUMMARY.md` - Overview
- ✅ `test_claude_integration.py` - Tests (all pass ✓)

---

## Docs

- **Full Guide:** See CLAUDE_API_GUIDE.md
- **Implementation:** See IMPLEMENTATION_SUMMARY.md
- **Interactive Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

**Ready to integrate into your web app!**

Learn more: → Read CLAUDE_API_GUIDE.md
