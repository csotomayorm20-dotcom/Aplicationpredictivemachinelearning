import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier

# Cargar el archivo Excel
excel_path = 'Seguimiento_proyectos_30_presupuestos_final.xlsx'
df = pd.read_excel(excel_path, sheet_name='Hoja1', header=1)

# Lista de características con los nombres exactos detectados en tu estructura
features = [
    '% Plan', 
    '% Real', 
    'SPI', 
    'CPI', 
    'PPTO aprobado', 
    'PPTO ejecutado', 
    'Tasa de acierto en la detección de riesgos', 
    'Cobertura de monitoreo %', 
    'Variación de alcance (CR)',
    'Tiempo de generación de alertas',
    'Severidad de riesgos ',
    'Nivel de Explicabilidad y Atribución Causal.'
]

# Filtrar solo las columnas existentes
valid_features = [f for f in features if f in df.columns]
print(f"Características válidas utilizadas: {valid_features}")

X = df[valid_features].copy()

# Limpiar columnas de texto que contengan unidades (ej. '2 horas' -> 2.0)
for col in X.columns:
    if X[col].dtype == 'object':
        X[col] = X[col].astype(str).str.extract(r'([0-9]+\.?[0-9]*)')[0]
        X[col] = pd.to_numeric(X[col], errors='coerce').fillna(0.0)

y = df['Target_risk']

# Entrenar modelo
model = RandomForestClassifier(random_state=42)
model.fit(X, y)

# Guardar modelo entrenado
with open('modelo_pmo_lightgbm.pkl', 'wb') as f:
    pickle.dump(model, f)

print("¡Modelo entrenado y guardado exitosamente tras limpiar los datos de texto!")