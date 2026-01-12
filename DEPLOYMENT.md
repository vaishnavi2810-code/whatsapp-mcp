# Deployment & Configuration Checklist

## Development Setup ✓

- [x] FastAPI server created (`api.py`)
- [x] REST endpoints for all WhatsApp operations
- [x] WebSocket support for real-time updates
- [x] Pydantic models for validation
- [x] CORS enabled (wildcard for development)
- [x] Interactive Swagger UI (`/docs`)
- [x] Python client library (`client.py`)

## Before Production Deployment

### Security

- [ ] **CORS Origins** - Update from `*` to specific domains in `api.py` line 36
  ```python
  allow_origins=["https://yourdomain.com", "https://app.yourdomain.com"]
  ```

- [ ] **Authentication** - Add JWT token validation
  ```python
  from fastapi import Depends, HTTPException
  from fastapi.security import HTTPBearer
  
  security = HTTPBearer()
  
  @app.get("/chats", dependencies=[Depends(security)])
  async def get_chats(...):
      ...
  ```

- [ ] **HTTPS/WSS** - Use reverse proxy (nginx/Caddy) with SSL certificates

- [ ] **Environment Variables** - Use `.env` file for sensitive config
  ```bash
  BRIDGE_URL=http://bridge:8080
  DATABASE_PATH=/var/lib/whatsapp/messages.db
  API_SECRET=your-secret-key-here
  ```

- [ ] **Rate Limiting** - Add per-user/IP limits
  ```python
  from slowapi import Limiter
  limiter = Limiter(key_func=get_remote_address)
  
  @app.get("/messages/send")
  @limiter.limit("10/minute")
  async def send_message(...):
      ...
  ```

### Performance

- [ ] **Database Optimization** - Add indexes to SQLite
  ```sql
  CREATE INDEX idx_messages_timestamp ON messages(timestamp);
  CREATE INDEX idx_messages_chat_jid ON messages(chat_jid);
  CREATE INDEX idx_chats_last_message_time ON chats(last_message_time);
  ```

- [ ] **Caching** - Add Redis cache for frequent queries
  ```python
  from fastapi_cache2 import FastAPICache2
  from fastapi_cache2.decorator import cache
  
  @cache(expire=300)
  async def get_chats(...):
      ...
  ```

- [ ] **Connection Pooling** - Use uvicorn workers
  ```bash
  gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker
  ```

### Monitoring & Logging

- [ ] **Logging** - Add structured logging
  ```python
  import logging
  
  logger = logging.getLogger("whatsapp-api")
  logger.info(f"Message sent to {recipient}")
  ```

- [ ] **Health Checks** - Implement comprehensive health endpoint
  ```python
  @app.get("/health/detailed")
  async def health_detailed():
      return {
          "status": "healthy",
          "database": check_db_connection(),
          "bridge": check_bridge_connection(),
          "timestamp": datetime.now()
      }
  ```

- [ ] **Monitoring** - Set up with Prometheus/Grafana
  ```python
  from prometheus_client import Counter, Histogram
  
  message_counter = Counter('messages_sent_total', 'Total messages sent')
  ```

- [ ] **Error Tracking** - Integrate Sentry or similar
  ```python
  import sentry_sdk
  sentry_sdk.init("your-sentry-dsn")
  ```

### Data Handling

- [ ] **Input Validation** - Already implemented with Pydantic, verify:
  - Phone number format validation
  - Message length limits
  - File size limits (set in upload handler)

- [ ] **Error Messages** - Don't expose internal details
  ```python
  # ❌ Bad
  raise HTTPException(detail=f"DB Error: {str(e)}")
  
  # ✓ Good
  raise HTTPException(detail="Failed to fetch messages")
  logger.error(f"DB Error: {str(e)}")
  ```

- [ ] **API Versioning** - Add version prefix to endpoints
  ```python
  @app.get("/api/v1/chats")
  async def get_chats(...):
      ...
  ```

### Database

- [ ] **Backup Strategy** - Regular SQLite backups
  ```bash
  0 2 * * * cp /path/to/messages.db /backups/messages-$(date +\%Y\%m\%d).db
  ```

- [ ] **Connection Limits** - SQLite default is 1 connection
  ```python
  sqlite3.connect(db_path, timeout=30, check_same_thread=False)
  ```

- [ ] **Query Timeouts** - Prevent long-running queries
  ```python
  cursor.execute("PRAGMA busy_timeout = 5000")
  ```

## Deployment Options

### Option 1: Docker Compose (Recommended for small-medium deployments)

```bash
# 1. Build images
docker-compose build

# 2. Start services
docker-compose up -d

# 3. View logs
docker-compose logs -f whatsapp-api

# 4. Stop services
docker-compose down
```

**File:** `docker-compose.yml` (already created)

### Option 2: Kubernetes (Large scale)

```yaml
# whatsapp-api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: whatsapp-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: whatsapp-api
  template:
    metadata:
      labels:
        app: whatsapp-api
    spec:
      containers:
      - name: api
        image: whatsapp-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: BRIDGE_URL
          value: "http://whatsapp-bridge:8080"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Option 3: Traditional Server (Ubuntu/CentOS)

```bash
# 1. Install dependencies
apt-get install python3.11 python3-pip nginx supervisor

# 2. Clone/setup project
git clone <repo>
cd whatsapp-mcp-server
pip install -r requirements.txt

# 3. Setup Supervisor for process management
# /etc/supervisor/conf.d/whatsapp-api.conf
[program:whatsapp-api]
command=gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker
directory=/path/to/whatsapp-mcp-server
user=whatsapp
autostart=true
autorestart=true

# 4. Setup Nginx as reverse proxy
# /etc/nginx/sites-available/whatsapp-api
upstream whatsapp_api {
    server 127.0.0.1:8000;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://whatsapp_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /ws {
        proxy_pass http://whatsapp_api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}

# 5. Start services
supervisorctl reread
supervisorctl update
systemctl restart nginx
```

## Post-Deployment

### Verification Checklist

- [ ] API responds to health check
  ```bash
  curl https://api.yourdomain.com/health
  ```

- [ ] WebSocket connection works
  ```bash
  wscat -c wss://api.yourdomain.com/ws/messages
  ```

- [ ] Swagger UI accessible at `/docs`

- [ ] Can send message successfully
  ```bash
  curl -X POST https://api.yourdomain.com/messages/send \
    -H "Authorization: Bearer TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"recipient":"1234567890","text":"Test"}'
  ```

- [ ] File upload works with size limits

- [ ] Database queries are fast (<500ms)

- [ ] No errors in logs: `docker-compose logs -f`

### Monitoring Setup

#### Prometheus Metrics
```python
# Add to api.py
from prometheus_client import Counter, Histogram, generate_latest
import time

request_count = Counter('http_requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('http_request_duration_seconds', 'Request duration', ['endpoint'])

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start = time.time()
    request_count.labels(method=request.method, endpoint=request.url.path).inc()
    response = await call_next(request)
    duration = time.time() - start
    request_duration.labels(endpoint=request.url.path).observe(duration)
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

#### Grafana Dashboard
Create dashboard with:
- Requests per minute
- Average response time
- Error rate
- WebSocket connections
- Database query performance

## Rollback Plan

If something goes wrong:

```bash
# 1. Stop current deployment
docker-compose down

# 2. Restore from backup
cp /backups/messages-backup.db ./whatsapp-bridge/store/messages.db

# 3. Redeploy previous version
git checkout <previous-commit>
docker-compose build
docker-compose up -d
```

## Maintenance

### Weekly
- [ ] Check logs for errors
- [ ] Verify backups completed
- [ ] Monitor disk usage

### Monthly
- [ ] Update dependencies: `pip list --outdated`
- [ ] Database optimization: `VACUUM; ANALYZE;`
- [ ] Review and rotate API tokens

### Quarterly
- [ ] Security audit
- [ ] Performance analysis
- [ ] Update SSL certificates

## Support & Troubleshooting

**API not responding**
```bash
docker-compose logs whatsapp-api
curl -v http://localhost:8000/health
```

**WebSocket connection fails**
```javascript
// Check in browser console
const ws = new WebSocket('ws://localhost:8000/ws/messages');
ws.onerror = (e) => console.error(e);
```

**Database is slow**
```sql
-- Check database integrity
PRAGMA integrity_check;

-- Optimize
VACUUM;
ANALYZE;

-- Check query plan
EXPLAIN QUERY PLAN SELECT ...;
```

**High memory usage**
```bash
# Check top processes
top -p $(pgrep -f "uvicorn api")

# Reduce connection pool or add caching
```

---

**Before Going Live: Ensure all security items are checked! ✓**
