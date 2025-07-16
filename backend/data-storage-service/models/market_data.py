from sqlalchemy import Column, Integer, String, Float, Date
from models.database import Base

class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    ticker = Column(String, index=True)
    data_inicio = Column(Date)
    data_fim = Column(Date)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Integer)
    symbol = Column(String)
    shortName = Column(String)
    longName = Column(String)
    sector = Column(String)
    industry = Column(String)
    exchange = Column(String)