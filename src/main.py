from fastapi import FastAPI, Query
from orchestrator.tickerOrchestrator import pipeline
import pandas as pd

app = FastAPI()

@app.get("/api/pipeline")
def run_pipeline(
    start_date: str = Query(None),
    end_date: str = Query(None),
    period: str = Query(None),
    interval: str = Query("1d")
):
    df = pipeline(start_date, end_date, period, interval)
    if df is None or df.empty:
        return {"error": "No data found"}
    return df.to_dict(orient="records")