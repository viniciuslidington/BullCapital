import pandas as pd
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
csv_path = os.getenv("B3_CADASTRO_PATH")


def process_instrument_data(csv_file) -> pd.DataFrame:
    """
    Processa os dados do instrumento a partir de um arquivo CSV.

    Args:
        csv_file (str): Caminho para o arquivo CSV contendo os dados do instrumento.

    Returns:
        pd.DataFrame: DataFrame contendo os dados processados do instrumento.
    """
    try:
        df = pd.read_csv(csv_file, encoding="latin1", sep=";", low_memory=False, skiprows=1)

        # Filtro: apenas ações (categoria SHARES), no mercado à vista
        acoes_b3 = df[
            (df["SctyCtgyNm"] == "SHARES") &
            (df["MktNm"] == "EQUITY-CASH") &
            (df["SgmtNm"] == "CASH")
        ]

        # Seleciona colunas principais
        resultado = acoes_b3[["TckrSymb", "CrpnNm", "ISIN", "MktCptlstn"]]

        return resultado

        

    except Exception as e:
        print(f"Erro ao processar o arquivo {csv_file}: {e}")

df = process_instrument_data(csv_path)
print(df.head())  # Exibe as primeiras linhas do DataFrame
