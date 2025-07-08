import sys
import pandas as pd
print("[DEBUG] sys.path:", sys.path)

from .orchestrator.tickerOrchestrator import pipeline

if __name__ == "__main__":
   df =  pipeline()
   print(df.head())
    