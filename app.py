import streamlit as st
import pandas as pd
import history_manager

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Dashboard Control de Red", layout="wide", page_icon="📈")
st.title("📊 Panel de Control y KPIs - Red de Sucursales")

# 2. CARGA DE DATOS SEGURO Y DINÁMICO
@st.cache_data
def load_data():
    csv_path = "historico_consolidado.csv"
    try:
        df = pd.read_csv(csv_path)
        df['ZONA'] = df['ZONA'].astype(str)
        return df
    except FileNotFoundError:
        st.error(f"⚠️ No se encontró '{csv_path}'. Cargando datos de prueba.")
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
fechas_disponibles = sorted(df_base['FECHA'].unique(), reverse=True)
fecha_seleccionada = st.sidebar.selectbox("📅 Seleccionar Fecha", fechas_disponibles)
df_fecha = df_base[df_base['FECHA'] == fecha_seleccionada]

zonas_disponibles = df_fecha['ZONA'].unique()
zona_seleccionada = st.sidebar.multiselect("Filtrar por Zona:", zonas_disponibles, default=zonas_disponibles)

if zona_seleccionada:
    df_filtrado = df_fecha[df_fecha['ZONA'].isin(zona_seleccionada)]
else:
    df_filtrado = df_fecha

# 4. SISTEMA DE ALERTAS
sucursales_cerradas = df_filtrado[df_filtrado['ESTADO'] == 'Cerrada']
if not sucursales_cerradas.empty:
    st.warning(f"⚠️ Alerta: {len(sucursales_cerradas)} sucursales cerradas hoy.")

# 5. KPIs
ventas_totales = df_filtrado['TOTAL_VENTA'].sum()
presupuesto_total = df_filtrado['PRESUPUESTO'].sum()
cumplimiento = (ventas_totales / presupuesto_total) * 100 if presupuesto_total > 0 else 0

st.subheader(f"📊 Métricas para el día {fecha_seleccionada}")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Ventas Totales", f"${ventas_totales:,.0f}")
col2.metric("Presupuesto", f"${presupuesto_total:,.0f}")
col3.metric("Cumplimiento", f"{cumplimiento:.1f}%")
col4.metric("Sobres Concurso", f"${df_filtrado['CONCURSO'].sum():,.0f}")

st.divider()

# 6. PESTAÑAS
tab1, tab2, tab3 = st.tabs(["📋 Datos", "🧠 Análisis IA", "🗓️ Histórico IA"])

with tab1:
    st.dataframe(df_filtrado, use_container_width=True)

with tab2:
    st.subheader("Análisis AntiGravity")
    with st.expander("Ver reporte detallado", expanded=True):
        st.write(f"Situación: Cumplimiento del {cumplimiento:.1f}%.")
        if st.button("💾 Guardar en Histórico"):
            history_manager.guardar_insight(f"Cumplimiento {cumplimiento:.1f}%", "Causa detectada automáticamente", "Recomendación: Seguir KPI")
            st.success("Guardado.")

with tab3:
    st.dataframe(history_manager.cargar_historico(), use_container_width=True)
