"""Configuración explícita y exportación real; sin corridas sintéticas."""
import os
from pathlib import Path
import mlflow
from dotenv import load_dotenv

def configurar():
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5001"))
    return mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT_NAME", "oulad-apoyo-academico"))

def exportar_corridas():
    experimento = configurar()
    runs = mlflow.search_runs(experiment_ids=[experimento.experiment_id])
    destino = Path(__file__).resolve().parents[1] / "docs" / "corridas.csv"
    runs.to_csv(destino, index=False)
    return destino
