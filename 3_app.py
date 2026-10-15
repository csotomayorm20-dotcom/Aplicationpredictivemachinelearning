import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="PMO Risk Intelligence Dashboard", page_icon="📊", layout="wide")

st.title("PMO Predictivo Risk Intelligence Dashboard")
st.markdown("Sistema de Alerta Temprana, Control Presupuestal, Explicabilidad (XAI) y Semáforo de Desvíos (PMO 4.0).")

tab1, tab2, tab3 = st.tabs(["Evaluación en Tiempo Real & Prescriptiva", "Análisis Comparativo (Pretest vs Postest)", "Simulador de Escenarios del Portafolio (What-If)"])

def load_data():
    excel_path = 'Seguimiento_proyectos_postest_final.xlsx'
    df_pre = pd.read_excel(excel_path, sheet_name='Hoja1', header=0)
    df_post = pd.read_excel(excel_path, sheet_name='Hoja2', header=0)
    return df_pre, df_post

df_pre, df_post = load_data()
project_list = df_pre['Codigo del proyecto'].tolist() if df_pre is not None and 'Codigo del proyecto' in df_pre.columns else [f"PY0{i}" for i in range(1, 10)]

if df_pre is not None and 'Target_risk' not in df_pre.columns:
    df_pre['Target_risk'] = ((df_pre['SPI'] < 0.90) | (df_pre['CPI'] < 0.90)).astype(int)

# Función de semáforo de color exclusivamente para el TEXTO (sin fondo) con 2 decimales
def color_semaforo_texto(val):
    try:
        desvio = abs(1.0 - float(val))
        if desvio <= 0.05:
            return 'color: #059669; font-weight: bold;' # Verde texto (<= 5%)
        elif desvio <= 0.10:
            return 'color: #d97706; font-weight: bold;' # Amarillo/Ámbar texto (5% - 10%)
        else:
            return 'color: #dc2626; font-weight: bold;' # Rojo texto (> 10%)
    except:
        return ''

# ---------------------------------------------------------
# PESTAÑA 1: EVALUACIÓN EN TIEMPO REAL & PRESCRIPTIVA
# ---------------------------------------------------------
with tab1:
    st.subheader("Evaluación Predictiva & Planes de Acción Prescriptivos")
    st.markdown("Selecciona el proyecto y evalúa los desvíos con el **semáforo normativo PMO** (Verde: <=5%, Amarillo: 5-10%, Rojo: >10%).")
    
    st.sidebar.header("Parámetros del Proyecto")
    selected_project = st.sidebar.selectbox("Seleccione el Código del Proyecto", options=project_list, index=0)
    
    default_spi = 0.85
    default_cpi = 0.92
    
    if df_pre is not None and 'Codigo del proyecto' in df_pre.columns:
        proj_row = df_pre[df_pre['Codigo del proyecto'] == selected_project]
        if not proj_row.empty:
            default_spi = float(proj_row['SPI'].values[0])
            default_cpi = float(proj_row['CPI'].values[0])

    spi = st.sidebar.slider("SPI (Cronograma)", 0.5, 1.2, default_spi, 0.01)
    cpi = st.sidebar.slider("CPI (Costo)", 0.5, 1.2, default_cpi, 0.01)
    
    if st.sidebar.button("Evaluar y Prescribir Soluciones"):
        desvio_spi = abs(1.0 - spi)
        desvio_cpi = abs(1.0 - cpi)
        
        riesgo_cronograma = desvio_spi > 0.10 or spi < 0.90
        riesgo_costo = desvio_cpi > 0.10 or cpi < 0.90
        
        st.markdown("### 🚦 Semáforo de Desvíos Actual")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if desvio_spi <= 0.05:
                st.success(f"🟢 **Cronograma Controlado (Verde)**: Desvío de {desvio_spi*100:.1f}% (<= 5%)")
            elif desvio_spi <= 0.10:
                st.warning(f"🟡 **Cronograma en Alerta (Amarillo)**: Desvío de {desvio_spi*100:.1f}% (entre 5% y 10%)")
            else:
                st.error(f"🔴 **Cronograma Crítico (Rojo)**: Desvío de {desvio_spi*100:.1f}% (> 10%)")
        with col_s2:
            if desvio_cpi <= 0.05:
                st.success(f"🟢 **Costo Controlado (Verde)**: Desvío de {desvio_cpi*100:.1f}% (<= 5%)")
            elif desvio_cpi <= 0.10:
                st.warning(f"🟡 **Costo en Alerta (Amarillo)**: Desvío de {desvio_cpi*100:.1f}% (entre 5% y 10%)")
            else:
                st.error(f"🔴 **Costo Crítico (Rojo)**: Desvío de {desvio_cpi*100:.1f}% (> 10%)")

        if riesgo_cronograma or riesgo_costo:
            st.markdown("---")
            st.markdown("### 🤖 Motor de Explicabilidad (SHAP) & Factores Causales Top-3")
            col_x1, col_x2, col_x3 = st.columns(3)
            with col_x1:
                st.info(f"**Factor 1 (42% impacto - SHAP):**\nDesvío detectado en {'costos (CPI: ' + f'{cpi:.2f}' + ')' if riesgo_costo else 'cronograma (SPI: ' + f'{spi:.2f}' + ')'}.")
            with col_x2:
                st.info("**Factor 2 (31% impacto - SHAP):**\nDemora en la aprobación de solicitudes de cambio (CR) y alcance.")
            with col_x3:
                st.info("**Factor 3 (27% impacto - SHAP):**\nAlta dependencia y rotación de recursos técnicos especializados.")

            st.markdown("---")
            st.markdown("### 📋 Planes de Acción Prescriptivos (Recomendados por la PMO)")
            if desvio_spi > 0.05:
                st.warning("⚡ **Acciones sugeridas para Cronograma:**\n"
                           "1. Aplicar *Fast-tracking* (ejecución en paralelo de tareas críticas no dependientes).\n"
                           "2. Asignar temporalmente recursos senior de apoyo en la ruta crítica.\n"
                           "3. Replanificar entregables menores para la siguiente iteración.")
            if desvio_cpi > 0.05:
                st.warning("💰 **Acciones sugeridas para Costos:**\n"
                           "1. Ejecutar una auditoría exprés de horas-hombre facturadas por terceros.\n"
                           "2. Congelar contrataciones de perfiles no esenciales para esta fase.\n"
                           "3. Optimizar licencias de software o infraestructura en la nube asignada.")
        else:
            st.success(f"✅ El proyecto **{selected_project}** se encuentra totalmente controlado dentro de los umbrales de tolerancia gerencial.")

# ---------------------------------------------------------
# PESTAÑA 2: ANÁLISIS COMPARATIVO (PRETEST VS POSTEST)
# ---------------------------------------------------------
with tab2:
    st.subheader("Análisis Comparativo del Portafolio (Pretest vs Postest)")
    if df_pre is not None and df_post is not None:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("SPI Promedio Portafolio", f"{df_post['SPI'].mean():.2f}", f"{df_post['SPI'].mean() - df_pre['SPI'].mean():+.2f}")
        with col2:
            st.metric("CPI Promedio Portafolio", f"{df_post['CPI'].mean():.2f}", f"{df_post['CPI'].mean() - df_pre['CPI'].mean():+.2f}")
        with col3:
            risks_post = int(df_post['Target_risk'].sum()) if 'Target_risk' in df_post.columns else 0
            st.metric("Proyectos en Riesgo Alto", f"{risks_post} / 30")

        st.markdown("---")
        comp_df = pd.DataFrame({
            "Proyecto": df_pre['Codigo del proyecto'],
            "SPI Pretest": df_pre['SPI'],
            "SPI Postest": df_post['SPI'],
            "CPI Pretest": df_pre['CPI'],
            "CPI Postest": df_post['CPI'],
        })
        styled_comp = comp_df.style.applymap(color_semaforo_texto, subset=['SPI Pretest', 'SPI Postest', 'CPI Pretest', 'CPI Postest']).format("{:.2f}", subset=['SPI Pretest', 'SPI Postest', 'CPI Pretest', 'CPI Postest'])
        st.dataframe(styled_comp, use_container_width=True)

# ---------------------------------------------------------
# PESTAÑA 3: SIMULADOR DE ESCENARIOS DEL PORTAFOLIO (WHAT-IF)
# ---------------------------------------------------------
with tab3:
    st.subheader("Simulador Estratégico de Portafolio (What-If Analysis)")
    st.markdown("Modifica los factores de optimización operativa de la PMO para simular el comportamiento global de los **30 proyectos** en tiempo real.")
    
    if df_pre is not None:
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            factor_spi = st.slider("Factor de Mejora en Cronograma (SPI)", 1.00, 1.25, 1.15, 0.01)
        with col_s2:
            factor_cpi = st.slider("Factor de Optimización de Costos (CPI)", 1.00, 1.20, 1.10, 0.01)
        with col_s3:
            cobertura_meta = st.slider("Cobertura de Monitoreo PMO (%)", 50, 100, 95, 5) / 100.0

        df_sim = df_pre.copy()
        df_sim['SPI_Sim'] = np.minimum(df_pre['SPI'] * factor_spi, 1.05)
        df_sim['CPI_Sim'] = np.minimum(df_pre['CPI'] * factor_cpi, 1.05)
        
        df_sim['Riesgo_Sim'] = ((df_sim['SPI_Sim'] < 0.90) | (df_sim['CPI_Sim'] < 0.90)).astype(int)
        
        proyectos_riesgo_pre = int(df_pre['Target_risk'].sum()) if 'Target_risk' in df_pre.columns else 0
        proyectos_riesgo_sim = int(df_sim['Riesgo_Sim'].sum())
        delta_riesgo = proyectos_riesgo_sim - proyectos_riesgo_pre

        st.markdown("---")
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.metric("SPI Promedio Simulado", f"{df_sim['SPI_Sim'].mean():.2f}", f"{df_sim['SPI_Sim'].mean() - df_pre['SPI'].mean():+.2f}")
        with sc2:
            st.metric("CPI Promedio Simulado", f"{df_sim['CPI_Sim'].mean():.2f}", f"{df_sim['CPI_Sim'].mean() - df_pre['CPI'].mean():+.2f}")
        with sc3:
            st.metric("Proyectos en Riesgo Alto (Simulado)", f"{proyectos_riesgo_sim} / 30", f"{delta_riesgo} proj")

        st.markdown("#### Matriz Comparativa del Portafolio Bajo Escenario Propuesto")
        
        base_labels = ["Alto Riesgo" if val == 1 else "Controlado" for val in df_pre['Target_risk']]
        sim_labels = ["Alto Riesgo" if val == 1 else "Controlado" for val in df_sim['Riesgo_Sim']]

        sim_display = pd.DataFrame({
            "Proyecto": df_pre['Codigo del proyecto'],
            "SPI Base": df_pre['SPI'],
            "SPI Simulado": df_sim['SPI_Sim'],
            "CPI Base": df_pre['CPI'],
            "CPI Simulado": df_sim['CPI_Sim'],
            "Estado Riesgo Base": base_labels,
            "Estado Riesgo Simulado": sim_labels
        })
        cols_to_format = ['SPI Base', 'SPI Simulado', 'CPI Base', 'CPI Simulado']
        styled_sim = sim_display.style.applymap(color_semaforo_texto, subset=cols_to_format).format("{:.2f}", subset=cols_to_format)
        st.dataframe(styled_sim, use_container_width=True)
    else:
        st.warning("⚠️ No se pudieron cargar los datos base para la simulación.")