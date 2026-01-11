from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from typing import Optional, Dict, Any, List

# Import all WhatsApp functions
try:
    from whatsapp import (
        send_message as whatsapp_send_message,
        list_chats as whatsapp_list_chats,
        list_messages as whatsapp_list_messages,
        search_contacts as whatsapp_search_contacts,
        get_chat as whatsapp_get_chat,
    )
except ImportError as e:
    print(f"Warning: Could not import whatsapp module: {e}")
    # Define dummy functions for testing
    def whatsapp_send_message(recipient, message):
        return False, "WhatsApp bridge not available"
    def whatsapp_list_chats(**kwargs):
        return []
    def whatsapp_list_messages(**kwargs):
        return []
    def whatsapp_search_contacts(query):
        return []
    def whatsapp_get_chat(jid, include_last_message=True):
        return {}

app = FastAPI(title="WhatsApp MCP API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class SendMessageRequest(BaseModel):
    recipient: str
    message: str

class SearchContactsRequest(BaseModel):
    query: str

class ListChatsRequest(BaseModel):
    query: Optional[str] = None
    limit: int = 20
    page: int = 0

class GetChatRequest(BaseModel):
    chat_jid: str
    include_last_message: bool = True

# Root endpoint
@app.get("/")
async def root():
    return {
        "service": "whatsapp-mcp",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "send_message": "/api/send-message",
            "list_chats": "/api/list-chats",
            "list_messages": "/api/list-messages",
            "search_contacts": "/api/search-contacts"
        }
    }

# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "service": "whatsapp-mcp"}

# Send WhatsApp message
@app.post("/api/send-message")
async def api_send_message(request: SendMessageRequest):
    try:
        success, message = whatsapp_send_message(request.recipient, request.message)
        return {"success": success, "message": message}
    except Exception as e:
        return {"success": False, "error": str(e)}

# List chats - READ ONLY
@app.post("/api/list-chats")
async def api_list_chats(request: ListChatsRequest):
    try:
        chats = whatsapp_list_chats(
            query=request.query,
            limit=request.limit,
            page=request.page,
            include_last_message=True,
            sort_by="last_active"
        )
        return {"success": True, "chats": chats, "count": len(chats)}
    except Exception as e:
        return {"success": False, "error": str(e), "chats": []}

# List messages - READ ONLY
@app.get("/api/list-messages")
async def api_list_messages(
    chat_jid: Optional[str] = None,
    limit: int = 20,
    page: int = 0,
    query: Optional[str] = None
):
    try:
        messages = whatsapp_list_messages(
            chat_jid=chat_jid,
            limit=limit,
            page=page,
            query=query
        )
        return {"success": True, "messages": messages, "count": len(messages)}
    except Exception as e:
        return {"success": False, "error": str(e), "messages": []}

# Search contacts - READ ONLY
@app.post("/api/search-contacts")
async def api_search_contacts(request: SearchContactsRequest):
    try:
        contacts = whatsapp_search_contacts(request.query)
        return {"success": True, "contacts": contacts, "count": len(contacts)}
    except Exception as e:
        return {"success": False, "error": str(e), "contacts": []}

# Get specific chat - READ ONLY
@app.post("/api/get-chat")
async def api_get_chat(request: GetChatRequest):
    try:
        chat = whatsapp_get_chat(request.chat_jid, request.include_last_message)
        return {"success": True, "chat": chat}
    except Exception as e:
        return {"success": False, "error": str(e), "chat": None}

# Bridge status check
@app.get("/api/bridge-status")
async def bridge_status():
    """Check if WhatsApp bridge is responding"""
    try:
        # Try to list chats as a connection test
        chats = whatsapp_list_chats(limit=1, page=0)
        return {
            "connected": True,
            "message": "WhatsApp bridge is connected",
            "has_data": len(chats) > 0
        }
    except Exception as e:
        return {
            "connected": False,
            "message": f"Bridge error: {str(e)}",
            "error": str(e)
        }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Starting WhatsApp MCP server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)