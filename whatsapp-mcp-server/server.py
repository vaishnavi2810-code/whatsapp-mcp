from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os
from typing import Optional, Dict, Any, List
from whatsapp import send_message as whatsapp_send_message

app = FastAPI()

class SendMessageRequest(BaseModel):
    recipient: str
    message: str

@app.get("/health")
async def health():
    return {"status": "ok", "service": "whatsapp-mcp"}

@app.post("/api/send-message")
async def api_send_message(request: SendMessageRequest):
    try:
        success, message = whatsapp_send_message(request.recipient, request.message)
        return {"success": success, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)