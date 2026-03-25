import pandas as pd
import os
import sys

def update_daily():
    if len(sys.argv) < 3:
        print("Uso: python update_daily_data.py <RUTA_AL_EXCEL_NUEVO> <FECHA_YYYY-MM-DD>")
        print('Ejemplo: python update_daily_data.py "C:\\Users\\pdbrito\\Desktop\\antigravity\\REPORTES DIARIOS\\ARCHIVO 23-03-2026 v10.3.xlsx" "2026-03-23"')
        return

    ruta_archivo = sys.argv[1]
    fecha_etiqueta = sys.argv[2]
    maestro_file = r"C:\Users\pdbrito\Desktop\antigravity\REPORTES DIARIOS\MAESTRO DE SUCURSALES v1.0.xlsx"
    output_file = "historico_consolidado.csv"

    if not os.path.exists(ruta_archivo):
        print(f"❌ Error: El archivo {ruta_archivo} no existe.")
        return

    print(f"-> Cargando el reporte del día: {fecha_etiqueta}...")
    try:
        df_suc = pd.read_excel(ruta_archivo, sheet_name="Sucursales", header=None)
    except Exception as e:
        print(f"❌ Error al leer hoja Sucursales en {ruta_archivo}: {e}")
        return
        
    df = df_suc.iloc[6:].copy()
    if df.empty:
        print("❌ Error: Reporte vacío.")
        return

    # HEURÍSTICA DE DETECCIÓN (igual que en build_historical)
    first_row = df.iloc[0]
    if "ZONA" in str(first_row.get(2, "")):
        mapping = {1: "SUCURSAL", 2: "ZONA", 3: "DIV", 4: "REGION_RAW"}
    else:
        mapping = {1: "DIV", 2: "SUCURSAL", 3: "ZONA", 4: "REGION_RAW"}
    
    mapping.update({6: "MINORISTA", 11: "TOTAL_VENTA", 12: "PRESUPUESTO", 13: "DESVIO_PESOS", 14: "DESVIO_PORC", 18: "CONCURSO", 24: "REPESAJE"})
    
    actual_rename = {k: v for k, v in mapping.items() if k in df.columns}
    df = df.rename(columns=actual_rename)
    for col in mapping.values():
        if col not in df.columns: df[col] = 0

    # Normalización para Merge
    df["DIV"] = df["DIV"].astype(str).str.strip().str.upper()
    df["SUC_NORM"] = df["SUCURSAL"].astype(str).str.strip().str.upper()

    # CRUZAR CON MAESTRO
    try:
        df_m = pd.read_excel(maestro_file)
        df_m['NIS'] = df_m['NIS'].astype(str).str.strip().str.upper()
        df_m['SUC_M'] = df_m['DENOMINACION'].astype(str).str.strip().str.upper()
        
        # 1. Merge por NIS
        df = df.merge(df_m[['NIS', 'REGION', 'DENOMINACION']], left_on='DIV', right_on='NIS', how='left', suffixes=('', '_m1'))
        # 2. Merge por Nombre
        df = df.merge(df_m[['SUC_M', 'REGION', 'DENOMINACION']], left_on='SUC_NORM', right_on='SUC_M', how='left', suffixes=('', '_m2'))
        
        df['REGION'] = df['REGION'].fillna(df['REGION_m2']).fillna(df['REGION_RAW'])
        df['SUCURSAL'] = df['DENOMINACION'].fillna(df['DENOMINACION_m2']).fillna(df['SUCURSAL'])
    except Exception as e:
        print(f"⚠️ Aviso: No se pudo cruzar con Maestro ({e}). Usando datos raw.")
        df['REGION'] = df['REGION_RAW']

    numeric_cols = ["MINORISTA", "TOTAL_VENTA", "PRESUPUESTO", "DESVIO_PESOS", "DESVIO_PORC", "CONCURSO", "REPESAJE"]
    for col in numeric_cols: 
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df_limpio = df[df["DIV"] != "NAN"].copy()
    
    def determine_estado(row):
        if row['TOTAL_VENTA'] == 0 and row['PRESUPUESTO'] > 0: return 'Cerrada'
        return 'Abierta'
        
    df_limpio['ESTADO'] = df_limpio.apply(determine_estado, axis=1)
    df_limpio['FECHA'] = fecha_etiqueta
    
    columnas_export = ['FECHA', 'DIV', 'SUCURSAL', 'ZONA', 'REGION', 'TOTAL_VENTA', 'PRESUPUESTO', 'DESVIO_PESOS', 'DESVIO_PORC', 'MINORISTA', 'CONCURSO', 'REPESAJE', 'ESTADO']
    df_final = df_limpio[columnas_export]
    
    # Anexar al histórico
    if os.path.exists(output_file):
        df_existente = pd.read_csv(output_file)
        
        # Opcional: Evitar duplicar si ya existe esa fecha
        df_existente = df_existente[df_existente['FECHA'] != fecha_etiqueta]
        
        df_consolidado = pd.concat([df_existente, df_final], ignore_index=True)
    else:
        df_consolidado = df_final
        
    df_consolidado.to_csv(output_file, index=False)
    print(f"✅ ¡Actualización exitosa! Se añadieron los datos de {fecha_etiqueta} a {output_file}.")

if __name__ == "__main__":
    update_daily()
