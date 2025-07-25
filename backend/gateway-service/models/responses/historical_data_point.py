from pydantic import BaseModel, Field
from typing import Optional

class HistoricalDataPoint(BaseModel):
    date: str = Field(..., description="Data no formato YYYY-MM-DD")
    open: float = Field(..., description="Preço de abertura")
    high: float = Field(..., description="Preço máximo")
    low: float = Field(..., description="Preço mínimo")
    close: float = Field(..., description="Preço de fechamento")
    volume: int = Field(..., description="Volume negociado")
    adj_close: Optional[float] = Field(default=None, description="Preço de fechamento ajustado")
