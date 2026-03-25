import streamlit as st
import pandas as pd
import history_manager

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Dashboard Control de Red", layout="wide", page_icon="📈")
st.title("📊 Panel de Control y KPIs - Red de Sucursales")

# 2. CARGA DE DATOS SEGURO Y DINÁMICO
# Utilizamos la estrucutra real vista en "REPORTES DIARIOS"
# DIV, SUCURSAL, ZONA, REGION, TOTAL_VENTA, PRESUPUESTO, DESVIO_PESOS, DESVIO_PORC, MINORISTA, CONCURSO, REPESAJE

@st.cache_data
def load_data():
    csv_path = "historico_consolidado.csv"
    try:
        # Carga del CSV consolidado
        df = pd.read_csv(csv_path)
        df['ZONA'] = df['ZONA'].astype(str)
        return df
    except FileNotFoundError:
        st.warning(f"⚠️ No se encontró '{csv_path}'. Usando datos de prueba.")
        # ... (simulador)
    except Exception as e:
        st.error(f"❌ Error cargando los datos: {e}")
        return pd.DataFrame() # Fallback a vacio para que no rompa el resto
        data = {
            'FECHA': ['2026-03-22']*5,
            'DIV': ['R0118', 'U0110', 'U0062', 'U0120', 'U0116'],
            'SUCURSAL': ['C. PAZ', 'NEUQUEN', 'BARILOCHE', 'VIEDMA', 'TRELEW'],
            'ZONA': ['3', '4', '4', '3', '4'],
            'REGION': ['SUR', 'SUR', 'SUR', 'SUR', 'SUR'],
            'TOTAL_VENTA': [1500000, 850000, 1200000, 450000, 1900000],
            'PRESUPUESTO': [1400000, 900000, 1100000, 500000, 1800000],
            'DESVIO_PESOS': [100000, -50000, 100000, -50000, 100000],
            'DESVIO_PORC': [1.07, 0.94, 1.09, 0.90, 1.05],
            'MINORISTA': [500000, 300000, 400000, 150000, 600000],
            'CONCURSO': [150000, 50000, 120000, 20000, 250000],
            'REPESAJE': [10000, 5000, 8000, 2000, 12000],
            'ESTADO': ['Abierta', 'Abierta', 'Cerrada', 'Abierta', 'Abierta']
        }
        return pd.DataFrame(data)

df_base = load_data()

# 3. FILTROS EN SIDEBAR
st.sidebar.header("🔍 Filtros")

# Filtro de Fecha (novedad del consolidador)
fechas_disponibles = sorted(df_base['FECHA'].unique(), reverse=True)
fecha_seleccionada = st.sidebar.selectbox("📅 Seleccionar Fecha", fechas_disponibles)

# Filtrar df principal para esa fecha
df_fecha = df_base[df_base['FECHA'] == fecha_seleccionada]

zonas_disponibles = df_fecha['ZONA'].unique()
zona_seleccionada = st.sidebar.multiselect("Filtrar por Zona:", zonas_disponibles, default=zonas_disponibles)

if zona_seleccionada:
    df_filtrado = df_fecha[df_fecha['ZONA'].isin(zona_seleccionada)]
else:
    df_filtrado = df_fecha

# 4. SISTEMA DE ALERTAS (Sucursales cerradas)
sucursales_cerradas = df_filtrado[df_filtrado['ESTADO'] == 'Cerrada']
if not sucursales_cerradas.empty:
    st.warning(f"⚠️ Alerta Crítica: Hay {len(sucursales_cerradas)} sucursales cerradas o sin transmisión de datos hoy ({', '.join(sucursales_cerradas['SUCURSAL'].tolist())}).")

# 5. CÁLCULO DE KPIs BÁSICOS Y REALES
ventas_totales = df_filtrado['TOTAL_VENTA'].sum()
presupuesto_total = df_filtrado['PRESUPUESTO'].sum()
desvio_pesos_total = ventas_totales - presupuesto_total
cumplimiento_ppto = (ventas_totales / presupuesto_total) * 100 if presupuesto_total > 0 else 0

total_concurso = df_filtrado['CONCURSO'].sum()
total_repesaje = df_filtrado['REPESAJE'].sum()

st.subheader("📊 Métricas Generales (Zonas Seleccionadas)")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Ventas Totales", f"${ventas_totales:,.2f}")
col2.metric("Presupuesto", f"${presupuesto_total:,.2f}")
col3.metric("Desvío vs Ppto", f"${desvio_pesos_total:,.2f}", delta=f"{cumplimiento_ppto:.1f}%", delta_color="normal")
col4.metric("Sobres Concurso", f"${total_concurso:,.2f}")

st.divider()

# 6. PESTAÑAS: VISTA GENERAL, ANÁLISIS IA E HISTÓRICO
tab1, tab2, tab3 = st.tabs(["📋 Datos del Día", "🧠 Análisis AntiGravity", "🗓️ Histórico de Análisis"])

with tab1:
    st.subheader("Detalle por Sucursal")
    st.dataframe(df_filtrado[['DIV', 'SUCURSAL', 'ZONA', 'TOTAL_VENTA', 'PRESUPUESTO', 'DESVIO_PORC', 'CONCURSO', 'REPESAJE', 'ESTADO']], use_container_width=True)

with tab2:
    st.subheader("Análisis de Desempeño (Agente AntiGravity)")
    
    # Aquí es donde AntiGravity evaluaría en base a los datos actuales. Podría correrse dinámicamente:
    desvio_texto = f"Detectamos un cumplimiento del {cumplimiento_ppto:.1f}%. El desempeño en Sobres Concurso es de ${total_concurso:,.2f}."
    causa_texto = "Variación natural o problemas de fuerza mayor en sucursales especificadas (Ej. Bariloche cerrada)."
    recomendacion_texto = "Verificar conectividad de sucursales cerradas e impulsar ventas Minorista en zona 3 (Viedma) que está en rojo (90%)."
    
    with st.expander("Ver reporte detallado de IA", expanded=True):
        st.markdown(f"**📉 Situación Actual:** {desvio_texto}")
        st.markdown(f"**🔍 Causas Identificadas:** {causa_texto}")
        st.markdown(f"**💡 Recomendación Estratégica:** {recomendacion_texto}")
        
        # Botón para guardar insight en el histórico
        if st.button("💾 Guardar este análisis en el Histórico"):
            history_manager.guardar_insight(desvio_texto, causa_texto, recomendacion_texto)
            st.success("Análisis guardado exitosamente.")

with tab3:
    st.subheader("Histórico de Observaciones")
    st.write("Esta tabla mantiene documentados los reportes pasados para evaluar estrategias en el tiempo:")
    df_historial = history_manager.cargar_historico()
    
    if df_historial.empty:
        st.info("Aún no hay análisis históricos guardados.")
    else:
        st.dataframe(df_historial, use_container_width=True)
