from fastapi import FastAPI, status, Depends
import logging
from typing import List
from sqlalchemy.orm import Session
from models.database import get_db
from models.schemas import MarketData as MarketDataSchema  # Exemplo de modelo
from models.market_data import MarketData as MarketDataORM
from models.database import Base, engine
from fastapi.responses import JSONResponse

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/data/bulk", status_code=status.HTTP_201_CREATED)
async def receive_bulk_market_data(market_data_list: List[MarketDataSchema], db: Session = Depends(get_db)):
    for entry in market_data_list:
        entry_dict = entry.dict()
        entry_dict.pop("id", None)
        db_entry = MarketDataORM(**entry_dict)
        db.add(db_entry)
    db.commit()
    return JSONResponse(
        content={"message": "Dados recebidos e armazenados com sucesso."},
        status_code=status.HTTP_201_CREATED
    )

@app.get("/api/data/{ticker}")
async def get_market_data(ticker: str, db: Session = Depends(get_db)):
    logger.info(f"Consulta GET para ticker: {ticker}")
    data = db.query(MarketDataORM).filter(MarketDataORM.ticker == ticker.upper()).all()
    if not data:
        return {"message": f"Nenhum dado encontrado para o ticker {ticker}."}
    return [d.as_dict() for d in data]  # Implemente as_dict() no modelo




