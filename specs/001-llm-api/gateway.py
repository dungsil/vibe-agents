"""
LLM API Gateway

A proxy service for LLM API calls that tracks usage per project using virtual API keys.
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import sqlite3
import json
import uuid
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
import httpx
import yaml
import os

app = FastAPI(title="LLM API Gateway", version="1.0.0")
security = HTTPBearer()

# Database setup
DB_PATH = "gateway.db"

def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Virtual API keys table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS virtual_keys (
            id TEXT PRIMARY KEY,
            project_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    """)
    
    # Real API keys table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS real_keys (
            provider TEXT PRIMARY KEY,
            api_key TEXT NOT NULL,
            base_url TEXT
        )
    """)
    
    # Usage records table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usage_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            virtual_key_id TEXT,
            provider TEXT,
            endpoint TEXT,
            request_tokens INTEGER,
            response_tokens INTEGER,
            estimated_cost REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (virtual_key_id) REFERENCES virtual_keys (id)
        )
    """)
    
    conn.commit()
    conn.close()

class VirtualKeyCreate(BaseModel):
    project_name: str

class VirtualKeyResponse(BaseModel):
    id: str
    project_name: str
    created_at: str
    is_active: bool

class UsageStats(BaseModel):
    virtual_key_id: str
    project_name: str
    total_requests: int
    total_tokens: int
    estimated_cost: float

def get_virtual_key_info(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Validate virtual API key and return key info."""
    virtual_key = credentials.credentials
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, project_name, is_active FROM virtual_keys WHERE id = ? AND is_active = TRUE",
        (virtual_key,)
    )
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        raise HTTPException(status_code=401, detail="Invalid or inactive virtual API key")
    
    return {
        "id": result[0],
        "project_name": result[1],
        "is_active": result[2]
    }

def get_real_api_key(provider: str) -> Optional[str]:
    """Get real API key for a provider."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT api_key FROM real_keys WHERE provider = ?", (provider,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def log_usage(virtual_key_id: str, provider: str, endpoint: str, 
              request_tokens: int, response_tokens: int, estimated_cost: float):
    """Log usage statistics."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO usage_records (virtual_key_id, provider, endpoint, request_tokens, response_tokens, estimated_cost)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (virtual_key_id, provider, endpoint, request_tokens, response_tokens, estimated_cost))
    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()

@app.post("/admin/virtual-keys", response_model=VirtualKeyResponse)
async def create_virtual_key(key_create: VirtualKeyCreate):
    """Create a new virtual API key for a project."""
    virtual_key_id = str(uuid.uuid4())
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO virtual_keys (id, project_name) VALUES (?, ?)",
        (virtual_key_id, key_create.project_name)
    )
    conn.commit()
    
    cursor.execute(
        "SELECT id, project_name, created_at, is_active FROM virtual_keys WHERE id = ?",
        (virtual_key_id,)
    )
    result = cursor.fetchone()
    conn.close()
    
    return VirtualKeyResponse(
        id=result[0],
        project_name=result[1],
        created_at=result[2],
        is_active=result[3]
    )

@app.get("/admin/virtual-keys", response_model=List[VirtualKeyResponse])
async def list_virtual_keys():
    """List all virtual API keys."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, project_name, created_at, is_active FROM virtual_keys ORDER BY created_at DESC")
    results = cursor.fetchall()
    conn.close()
    
    return [
        VirtualKeyResponse(
            id=row[0],
            project_name=row[1],
            created_at=row[2],
            is_active=row[3]
        ) for row in results
    ]

@app.delete("/admin/virtual-keys/{key_id}")
async def revoke_virtual_key(key_id: str):
    """Revoke a virtual API key."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE virtual_keys SET is_active = FALSE WHERE id = ?", (key_id,))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Virtual key not found")
    conn.commit()
    conn.close()
    return {"message": "Virtual key revoked successfully"}

@app.get("/admin/usage-stats", response_model=List[UsageStats])
async def get_usage_stats():
    """Get usage statistics for all virtual keys."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            vk.id,
            vk.project_name,
            COUNT(ur.id) as total_requests,
            COALESCE(SUM(ur.request_tokens + ur.response_tokens), 0) as total_tokens,
            COALESCE(SUM(ur.estimated_cost), 0) as estimated_cost
        FROM virtual_keys vk
        LEFT JOIN usage_records ur ON vk.id = ur.virtual_key_id
        GROUP BY vk.id, vk.project_name
        ORDER BY vk.created_at DESC
    """)
    results = cursor.fetchall()
    conn.close()
    
    return [
        UsageStats(
            virtual_key_id=row[0],
            project_name=row[1],
            total_requests=row[2],
            total_tokens=row[3],
            estimated_cost=row[4]
        ) for row in results
    ]

@app.api_route("/v1/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_llm_request(
    request: Request,
    path: str,
    key_info: Dict[str, Any] = Depends(get_virtual_key_info)
):
    """Proxy LLM API requests to the actual provider."""
    # Determine provider based on path or headers
    provider = "openai"  # Default to OpenAI for now
    if "anthropic" in path.lower():
        provider = "anthropic"
    
    # Get real API key for provider
    real_api_key = get_real_api_key(provider)
    if not real_api_key:
        raise HTTPException(status_code=502, detail=f"No API key configured for provider: {provider}")
    
    # Determine base URL based on provider
    base_urls = {
        "openai": "https://api.openai.com",
        "anthropic": "https://api.anthropic.com"
    }
    base_url = base_urls.get(provider, "https://api.openai.com")
    
    # Prepare request
    url = f"{base_url}/v1/{path}"
    method = request.method
    headers = dict(request.headers)
    
    # Replace authorization header with real API key
    if provider == "openai":
        headers["Authorization"] = f"Bearer {real_api_key}"
    elif provider == "anthropic":
        headers["x-api-key"] = real_api_key
    
    # Remove host header to avoid conflicts
    headers.pop("host", None)
    
    # Get request body
    body = await request.body()
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=body,
                timeout=60.0
            )
        
        # Parse response to extract token usage (simplified)
        request_tokens = 0
        response_tokens = 0
        estimated_cost = 0.0
        
        if response.headers.get("content-type", "").startswith("application/json"):
            try:
                response_data = response.json()
                if "usage" in response_data:
                    usage = response_data["usage"]
                    request_tokens = usage.get("prompt_tokens", 0)
                    response_tokens = usage.get("completion_tokens", 0)
                    # Simplified cost calculation (would need actual pricing)
                    estimated_cost = (request_tokens * 0.0015 + response_tokens * 0.002) / 1000
            except:
                pass
        
        # Log usage
        log_usage(
            virtual_key_id=key_info["id"],
            provider=provider,
            endpoint=path,
            request_tokens=request_tokens,
            response_tokens=response_tokens,
            estimated_cost=estimated_cost
        )
        
        # Return response
        return response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
        
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Error connecting to LLM provider: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)