from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
import httpx
from typing import List, Optional
from models.requests.ai_financial_request import ChatRequest, ConversationRequest

router = APIRouter()


AI_SERVICE_URL = "http://ai-service:8001"

@router.post("/chat")
async def chat_with_agent(request: ChatRequest):
    """
    Endpoint principal para conversar com o agente.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Convert request to dict and handle UUIDs
            request_data = request.dict()
            # Convert UUIDs to strings for JSON serialization
            if request_data.get("user_id"):
                request_data["user_id"] = str(request_data["user_id"])
            if request_data.get("conversation_id"):
                request_data["conversation_id"] = str(request_data["conversation_id"])
            
            # Forward request to AI service
            ai_response = await client.post(
                f"{AI_SERVICE_URL}/chat",
                json=request_data,
                timeout=30.0
            )
            
            if ai_response.status_code != 200:
                raise HTTPException(
                    status_code=ai_response.status_code,
                    detail=f"AI service error: {ai_response.text}"
                )
            
            return ai_response.json()
        
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Recupera o histórico de uma conversa específica.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Forward request to AI service
            ai_response = await client.get(
                f"{AI_SERVICE_URL}/conversations/{conversation_id}",
                timeout=30.0
            )
            
            if ai_response.status_code != 200:
                raise HTTPException(
                    status_code=ai_response.status_code,
                    detail=f"AI service error: {ai_response.text}"
                )
            
            return ai_response.json()
        
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/conversations")
async def list_conversations(
    user_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    Lista todas as conversas disponíveis.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Build query parameters
            params = {
                "skip": skip,
                "limit": limit
            }
            if user_id is not None:
                params["user_id"] = user_id
            
            # Forward request to AI service
            ai_response = await client.get(
                f"{AI_SERVICE_URL}/conversations",
                params=params,
                timeout=30.0
            )
            
            if ai_response.status_code != 200:
                raise HTTPException(
                    status_code=ai_response.status_code,
                    detail=f"AI service error: {ai_response.text}"
                )
            
            return ai_response.json()
        
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



@router.get("/health")
async def health_check():
    """Endpoint de health check."""
    try:
        async with httpx.AsyncClient() as client:
            # Check AI service health
            ai_response = await client.get(
                f"{AI_SERVICE_URL}/health",
                timeout=10.0
            )
            
            if ai_response.status_code == 200:
                ai_data = ai_response.json()
                return {
                    "status": "healthy",
                    "service": "AI Gateway",
                    "timestamp": ai_data.get("timestamp", "")
                }
            else:
                from datetime import datetime
                return {
                    "status": "unhealthy",
                    "service": "AI Gateway", 
                    "timestamp": datetime.now().isoformat()
                }
    except Exception:
        from datetime import datetime
        return {
            "status": "unhealthy",
            "service": "AI Gateway",
            "timestamp": datetime.now().isoformat()
        } 
