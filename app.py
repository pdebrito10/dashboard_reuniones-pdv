import streamlit as st
import pandas as pd
import history_manager
import google.generativeai as genai
import os

# --- 1. CONFIGURACIÓN Y ESTILOS (Skills Identidad Correo) ---
st.set_page_config(page_title="Dashboard Control de Red - Correo Argentino", layout="wide", page_icon="📈")

# Colores Oficiales (Skill)
YELLOW = "#FFCE00"
BLUE = "#152663"
ALBA = "#FFFFFF"
GRAY = "#F9F9F9"

def apply_custom_styles():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
        
        html, body, [class*="css"] {{
            font-family: 'Montserrat', sans-serif;
            background-color: {GRAY};
        }}
        
        .main {{ background-color: {GRAY}; }}
        
        /* Sidebar Estilizado */
        [data-testid="stSidebar"] {{
            background-color: {BLUE};
        }}
        [data-testid="stSidebar"] * {{
            color: white !important;
        }}
        
        /* Métricas */
        .stMetric {{
            background-color: {ALBA};
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
            border-bottom: 4px solid {YELLOW};
        }}
        
        /* Botones Pill */
        .stButton>button {{
            background-color: {YELLOW} !important;
            color: {BLUE} !important;
            border-radius: 50px !important;
            font-weight: 700 !important;
            border: none !important;
            padding: 0.6rem 2.5rem !important;
            transition: all 0.3s ease;
        }}
        .stButton>button:hover {{
            transform: scale(1.05);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        /* Títulos */
        h1, h2, h3 {{
            color: {BLUE};
            font-weight: 700;
        }}
        </style>
    """, unsafe_allow_html=True)

apply_custom_styles()

# --- 2. CARGA DE DATOS ---
@st.cache_data
def load_data():
    csv_path = "historico_consolidado.csv"
    try:
        df = pd.read_csv(csv_path)
        df['ZONA'] = df['ZONA'].astype(str)
        df['FECHA'] = pd.to_datetime(df['FECHA'])
        return df
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame()

df_base = load_data()

# --- 3. SIDEBAR (LOGO Y NAVEGACIÓN) ---
with st.sidebar:
    # Buscar el logo con diferentes nombres posibles
    logo_files = ["logo-correo.png", "Logo-correo.png", "logo.png", "logo-correo.PNG"]
    logo_found = False
    for f in logo_files:
        if os.path.exists(f):
            st.image(f, width="stretch")
            logo_found = True
            break
    
    if not logo_found:
        st.title("📬 Correo Argentino")
    
    st.divider()
    page = st.radio("Navegación Principal", ["🏠 Inicio (Resumen)", "📅 Detalle Diario", "📚 Histórico IA"])
    st.divider()
    st.caption("Desarrollado para Gerencia de Red")

# --- 4. LÓGICA DE IA (GEMINI) ---
def get_ai_report(region, zona, sucursal, data_summary):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", None)
        if not api_key:
            return "⚠️ Error: GEMINI_API_KEY no configurada. Por favor cárgala en Streamlit Cloud Secrets."
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        target = f"Región {region}"
        if zona != "Todas": target += f", Zona {zona}"
        if sucursal != "Todas": target += f", Sucursal {sucursal}"
        
        prompt = f"""
        Actúa como un Consultor Estratégico Senior de Correo Argentino. 
        Debes preparar un informe ejecutivo para una reunión sobre el desempeño de {target}.
        
        Datos clave actuales:
        - Venta Total: ${data_summary['Venta']:,.0f}
        - Presupuesto: ${data_summary['Presupuesto']:,.0f}
        - Cumplimiento: {data_summary['Cumplimiento']:.1f}%
        - Sobres Concurso: {data_summary['Sobres']:.0f} u.
        - Recaudación Repesaje: ${data_summary['Repesaje']:,.0f}
        - Alertas de cierre: {data_summary['Alertas_Cerradas']} unidades.
        
        Formato del informe:
        1. DIAGNÓSTICO (Resumen del estado actual).
        2. DESVÍOS CRÍTICOS (Donde poner el ojo).
        3. AGENDA DE REUNIÓN (Puntos clave a tratar con los jefes regionales).
        4. ACCIONES RECOMENDADAS (Pasos a seguir).
        
        Usa un lenguaje corporativo, preciso y motivador. Enfocado en la mejora de KPIs.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error al conectar con Gemini: {e}"

# --- 5. LÓGICA DE PÁGINAS ---

if page == "🏠 Inicio (Resumen)":
    st.title("📊 Resumen Ejecutivo - Nivel Empresa")
    
    # KPIs Acumulados ( Impact Panel )
    venta_total = df_base['TOTAL_VENTA'].sum()
    presupuesto_total = df_base['PRESUPUESTO'].sum()
    desvio_abs = venta_total - presupuesto_total
    cumplimiento_total = (venta_total / presupuesto_total) * 100 if presupuesto_total > 0 else 0
    sobres_total = df_base['CONCURSO'].sum()
    repesaje_total = df_base['REPESAJE'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Venta Total Red", f"${venta_total:,.0f}")
    col2.metric("Desvío Acumulado", f"{cumplimiento_total-100:+.1f}%", f"${desvio_abs:,.0f}", delta_color="normal")
    col3.metric("Sobres Vendidos", f"{sobres_total:,.0f}", help="Volumen histórico acumulado")
    col4.metric("Recaudación Repesaje", f"${repesaje_total:,.0f}")
    
    st.divider()
    
    # Asistente IA para Reuniones
    st.subheader("🤖 Asistente Virtual para Reuniones")
    st.info("👋 ¿Te ayudo a preparar la próxima reunión? Dime con qué región es y te la preparo.")
    
    with st.container():
        c1, c2, c3 = st.columns(3)
        # Limpiar regiones para evitar TypeError con nulos
        regiones_validas = [r for r in df_base['REGION'].dropna().unique() if str(r).strip()]
        region_sel = c1.selectbox("Selecciona la Región", sorted(regiones_validas))
        
        df_reg = df_base[df_base['REGION'] == region_sel]
        # Limpiar zonas para evitar TypeError con nulos
        zonas_validas = [z for z in df_reg['ZONA'].dropna().unique() if str(z).strip()]
        zona_sel = c2.selectbox("Profundizar Zona (Opcional)", ["Todas"] + sorted(zonas_validas))
        
        df_zona = df_reg if zona_sel == "Todas" else df_reg[df_reg['ZONA'] == zona_sel]
        # Limpiar sucursales para evitar TypeError con nulos
        sucs_validas = [s for s in df_zona['SUCURSAL'].dropna().unique() if str(s).strip()]
        suc_sel = c3.selectbox("Sucursal Específica (Opcional)", ["Todas"] + sorted(sucs_validas))
        
        if st.button("🚀 Generar Informe de Reunión"):
            df_final = df_zona if suc_sel == "Todas" else df_zona[df_zona['SUCURSAL'] == suc_sel]
            
            # Resumen para la IA
            summary = {
                "Venta": df_final['TOTAL_VENTA'].sum(),
                "Presupuesto": df_final['PRESUPUESTO'].sum(),
                "Cumplimiento": (df_final['TOTAL_VENTA'].sum() / df_final['PRESUPUESTO'].sum()) * 100 if df_final['PRESUPUESTO'].sum() > 0 else 0,
                "Sobres": df_final['CONCURSO'].sum(),
                "Repesaje": df_final['REPESAJE'].sum(),
                "Alertas_Cerradas": len(df_final[df_final['ESTADO'] == 'Cerrada'])
            }
            
            with st.spinner(f"Analizando datos de {region_sel}..."):
                reporte = get_ai_report(region_sel, zona_sel, suc_sel, summary)
                st.success("✅ Informe preparado")
                st.markdown(f"---")
                st.markdown(reporte)
                
                # Opción de guardado
                if st.button("💾 Guardar en Historial de IA"):
                    history_manager.guardar_insight(f"Reunión {region_sel}", "Análisis Automático", str(reporte)[:1000])
                    st.toast("Guardado correctamente")

elif page == "📅 Detalle Diario":
    st.title("📅 Detalle de Operación Diaria")
    
    fechas_disp = sorted(df_base['FECHA'].dt.date.unique(), reverse=True)
    fecha_sel = st.sidebar.selectbox("📅 Seleccionar Fecha", fechas_disp)
    df_fecha = df_base[df_base['FECHA'].dt.date == fecha_sel]
    
    # Filtros adicionales en sidebar
    reg_disp = sorted(df_fecha['REGION'].unique())
    reg_sel = st.sidebar.multiselect("Filtrar Región:", reg_disp, default=reg_disp)
    
    df_f = df_fecha[df_fecha['REGION'].isin(reg_sel)] if reg_sel else df_fecha
    
    # Alerta de cierres
    cierres = df_f[df_f['ESTADO'] == 'Cerrada']
    if not cierres.empty:
        st.warning(f"⚠️ {len(cierres)} sucursales sin actividad el {fecha_sel}")
    
    st.dataframe(df_f, use_container_width=True)

elif page == "📚 Histórico IA":
    st.title("📚 Historial de Análisis Generados")
    st.write("Registros de los informes y recomendaciones previas.")
    st.dataframe(history_manager.cargar_historico(), use_container_width=True)

