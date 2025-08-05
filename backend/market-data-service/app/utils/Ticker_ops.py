import pandas as pd
import yfinance as yf
import numpy as np


def safe_ticker_operation(symbol: str, operation):
        """Executa operação no ticker com tratamento de erro"""
        try:
            ticker = yf.Ticker(symbol.upper())
            result = operation(ticker)
            return result
        except Exception as e:
            raise ValueError(f"Erro ao executar operação no ticker {symbol}: {e}")

def convert_to_serializable(data):
        """Converte dados pandas/numpy para formato serializável"""
        if isinstance(data, pd.DataFrame):
            return data.fillna(0).to_dict(orient='records')
        elif isinstance(data, pd.Series):
            return data.fillna(0).to_dict()
        elif isinstance(data, np.ndarray):
            return data.tolist()
        elif isinstance(data, (np.integer, np.floating)):
            return float(data)
        elif isinstance(data, (int, float, str, bool, list, dict)):
            return data
        elif data is None or (hasattr(data, '__len__') and len(data) == 0):
            return None
        else:
            # Para valores únicos, verifica se é NaN
            try:
                if pd.isna(data):
                    return None
            except (ValueError, TypeError):
                pass
            return str(data)  # Converte para string como fallback
