from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import pandas as pd

app = FastAPI(title="PMO Risk Intelligence API")

# Cargar el modelo entrenado
with open('modelo_pmo_lightgbm.pkl', 'rb') as f:
    model = pickle.load(f)

class ProjectInput(BaseModel):
    project_id: str
    pct_plan: float
    pct_real: float
    spi: float
    cpi: float
    ppto_aprobado: float
    ppto_ejecutado: float
    tasa_acierto: float
    cobertura_monitoreo: float
    variacion_alcance: int
    tiempo_generacion_alertas: float
    severidad_riesgos: float
    explicabilidad_atribucion: float

@app.post("/predict")
def predict_risk(data: ProjectInput):
    # Diccionario con los nombres exactos de columnas usados en el entrenamiento
    input_df = pd.DataFrame([{
        '% Plan': data.pct_plan,
        '% Real': data.pct_real,
        'SPI': data.spi,
        'CPI': data.cpi,
        'PPTO aprobado': data.ppto_aprobado,
        'PPTO ejecutado': data.ppto_ejecutado,
        'Tasa de acierto en la detección de riesgos': data.tasa_acierto,
        'Cobertura de monitoreo %': data.cobertura_monitoreo,
        'Variación de alcance (CR)': data.variacion_alcance,
        'Tiempo de generación de alertas': data.tiempo_generacion_alertas,
        'Severidad de riesgos ': data.severidad_riesgos,
        'Nivel de Explicabilidad y Atribución Causal.': data.explicabilidad_atribucion
    }])
    
    pred = model.predict(input_df)[0]
    risk_level = "ALTO" if int(pred) == 1 else "BAJO / CONTROLADO"
    
    return {
        "project_id": data.project_id,
        "risk_level": risk_level,
        "prediction_raw": int(pred),
        "xai_metrics": {
            "tiempo_generacion_alertas": data.tiempo_generacion_alertas,
            "severidad_riesgos": data.severidad_riesgos,
            "nivel_explicabilidad": data.explicabilidad_atribucion
        }
    }