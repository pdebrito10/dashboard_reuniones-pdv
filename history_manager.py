import pandas as pd
import os
from datetime import datetime

HISTORY_FILE = "historico_ai.csv"

def init_history_file():
    """Initializes the CSV if it doesn't exist."""
    if not os.path.exists(HISTORY_FILE):
        df = pd.DataFrame(columns=["fecha", "desvio_detectado", "causa_probable", "recomendacion"])
        df.to_csv(HISTORY_FILE, index=False)

def cargar_historico():
    """Loads the history as a Pandas DataFrame."""
    init_history_file()
    try:
        df = pd.read_csv(HISTORY_FILE)
        return df
    except Exception as e:
        return pd.DataFrame(columns=["fecha", "desvio_detectado", "causa_probable", "recomendacion"])

def guardar_insight(desvio, causa, recomendacion):
    """Saves a new insight into the historical CSV."""
    init_history_file()
    nuevo_registro = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "desvio_detectado": desvio,
        "causa_probable": causa,
        "recomendacion": recomendacion
    }
    
    # Read existing
    df = pd.read_csv(HISTORY_FILE)
    
    # Append new row (using concat instead of append for modern pandas)
    df = pd.concat([df, pd.DataFrame([nuevo_registro])], ignore_index=True)
    
    # Save back
    df.to_csv(HISTORY_FILE, index=False)
    return True
