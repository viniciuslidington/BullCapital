from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional
from bullcapital_backend.orchestrator.tickerOrchestrator import pipeline

router = APIRouter()

@router.get("/b3/data", summary="Obter dados de ações da B3")
def get_b3_market_data(
    start_date: Optional[str] = Query(None, description="Data de início (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Data de fim (YYYY-MM-DD)"),
    period: Optional[str] = Query(None, description="Período (ex: '1mo', '1y')"),
    interval: Optional[str] = Query('1d', description="Intervalo (ex: '1d', '1wk')")
):
    """
    Endpoint para obter dados de ações da B3.
    
    Executa a pipeline de processamento e retorna os dados formatados.
    
    **Parâmetros:**
    - **start_date**: Data de início no formato YYYY-MM-DD
    - **end_date**: Data de fim no formato YYYY-MM-DD  
    - **period**: Período alternativo (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    - **interval**: Intervalo dos dados (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    
    **Nota:** Use start_date/end_date OU period, não ambos.
    """
    try:
        # Executar a pipeline com os parâmetros fornecidos
        df = pipeline()
        
        if df is None or df.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhum dado encontrado para os parâmetros fornecidos"
            )
        
        # Converter DataFrame para dict para serialização JSON
        data = df.to_dict('records')
        
        return {
            "data": data,
            "total_records": len(data),
            "parameters": {
                "start_date": start_date,
                "end_date": end_date,
                "period": period,
                "interval": interval
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar dados: {str(e)}"
        )

@router.get("/health", summary="Health Check do serviço de dados")
def market_data_health():
    """
    Verificação de saúde do serviço de dados de mercado.
    """
    return {
        "service": "market_data",
        "status": "healthy",
        "version": "1.0.0"
    }
