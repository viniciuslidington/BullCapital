from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
import httpx
from typing import List, Optional
from models.responses.ai_financial_response import ChatResponse, MessageRequest, HealthResponse
from models.requests.ai_financial_request import ChatRequest, ConversationRequest

router = APIRouter()


AI_SERVICE_URL = "http://ai-service:8001/api/v1/ai"

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    Endpoint principal para conversar com o agente.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Forward request to AI service
            ai_response = await client.post(
                f"{AI_SERVICE_URL}/chat",
                json=request.dict(),
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
    
@router.get("/conversations/{conversation_id}", response_model=ChatResponse)
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


@router.get("/health", response_model=HealthResponse)
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
                return HealthResponse(
                    status="healthy",
                    service="AI Gateway",
                    timestamp=ai_response.json().get("timestamp")
                )
            else:
                return HealthResponse(
                    status="unhealthy",
                    service="AI Gateway", 
                    timestamp=None
                )
    except Exception:
        return HealthResponse(
            status="unhealthy",
            service="AI Gateway",
            timestamp=None
        ) 
