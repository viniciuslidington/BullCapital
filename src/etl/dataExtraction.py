#Data Extraction for ETL process
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)

def download_ticker(ticker, start_date, end_date, period, interval='1d'):
    # Extract historical stock data from Yahoo Finance
    
    if not period:

        logging.info(f"Using start date: {start_date}, end date: {end_date}, and interval: {interval} for ticker {ticker}")

        if not start_date:
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d') # Default to 3 months ago if no start date is provided
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
    else:
        start_date = None
        end_date = None
        logging.info(f"Using period: {period} and interval: {interval} for ticker {ticker}")


    try:
        yf.Ticker(ticker)
    except Exception as e:
        logging.error(f"Failed to initialize yfinance Ticker for {ticker}: {e}")
        return None
    
    try:
        data = yf.download(         # Download historical data for the ticker
            ticker,
            start=start_date,
            end=end_date,
            period=period,
            interval=interval,
            auto_adjust=True,
        )
    except Exception as e:
        logging.error(f"Failed to download data for {ticker} from Yahoo Finance: {e}")
        return None
    
    df = pd.DataFrame(data)  # Convert the data to a DataFrame
    
    if df.empty:
        logging.warning(f"No data found for {ticker} in the specified date range.")
        return None
    else:
        return df

df = download_ticker('aapl', None, None, '1y', '1d')
print(df.head())  # Display the first rows of the DataFrame