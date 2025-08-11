#!/usr/bin/env python3

import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configurar chave OpenAI
os.environ["OPENAI_API_KEY"] = "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"

from app.agent.financial_agent import (
    obter_json_financeiro,
    calcular_valuation,
    calcular_multiplos,
    capm_calcular,
    agent
)

app = FastAPI(title="BullCapital AI Service", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str

@app.get("/health")
def health():
    return {"ok": True, "service": "BullCapital AI Service"}

@app.post("/chat")
def chat(payload: ChatRequest):
    try:
        content = agent.chat(payload.question)
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no chat: {str(e)}")

@app.get("/finance/{ticker}")
def finance_json(ticker: str):
    try:
        raw = obter_json_financeiro.entrypoint(ticker=ticker)
        return json.loads(raw)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro finance: {str(e)}")

@app.get("/valuation/{ticker}")
def valuation_markdown(ticker: str):
    try:
        md = calcular_valuation.entrypoint(ticker=ticker)
        return {"markdown": md}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro valuation: {str(e)}")

@app.get("/multiples/{ticker}")
def multiples_markdown(ticker: str):
    try:
        md = calcular_multiplos.entrypoint(ticker=ticker)
        return {"markdown": md}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro multiples: {str(e)}")

@app.get("/capm/{ticker}")
def capm_json(ticker: str):
    try:
        raw = capm_calcular.entrypoint(ticker=ticker)
        return json.loads(raw)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro CAPM: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando BullCapital AI Service na porta 8001...")
    uvicorn.run(app, host="127.0.0.1", port=8001) 