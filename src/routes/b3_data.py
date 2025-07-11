from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from bullcapital_backend.orchestrator.tickerOrchestrator import pipeline


router = APIRouter(
    prefix="/b3",  # All routes in this file will start with /b3
    tags=["B3 Data"],  # Groups routes in the API docs
)

@router.get("/dados", summary="Obtém dados de ações da B3")
def get_dados(
    start_date: Optional[str] = Query(None, description="Data de início (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Data de fim (YYYY-MM-DD)"),
    period: Optional[str] = Query(None, description="Período (ex: '1mo', '1y')"),
    interval: Optional[str] = Query('1d', description="Intervalo (ex: '1d', '1wk')")
):
    """
    Endpoint para obter dados de ações da B3.
    Executa a pipeline de processamento e retorna os dados formatados.
    """
    df = pipeline(
        start_date=start_date,
        end_date=end_date,
        period=period,
        interval=interval
    )

    if df is None or df.empty:
        raise HTTPException(status_code=404, detail="Nenhum dado encontrado para os parâmetros fornecidos.")

    return df.to_dict(orient="records")