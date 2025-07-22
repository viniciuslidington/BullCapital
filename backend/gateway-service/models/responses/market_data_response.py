from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class StockDataResponse(BaseModel):
    symbol: str
    company_name: str
    current_price: float
    previous_close: float
    change: float
    change_percent: float
    volume: int
    avg_volume: Optional[int] = None # avg_volume é null no JSON, então Optional
    currency: str
    timezone: Optional[str] = None # timezone é null no JSON, então Optional
    last_updated: str # Pode ser datetime.date ou datetime.datetime se você quiser parsear datas
