import os
import re
import sys
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from gestor_m365 import obtener_excel_file

@st.cache_data(ttl=60)
def load_data():
    """Carga y procesa exclusivamente CONTROL INDICADORES PROACTIVOS.xlsx desde OneDrive, SharePoint o local."""
    excel_source, err, source_desc = obtener_excel_file("hse_proactivos")
    if err or excel_source is None:
        return None, None, err

    try:
        xl = pd.ExcelFile(excel_source, engine='openpyxl')
    except Exception as e:
        return None, None, f"Error al abrir Excel ({source_desc}): {e}"

    hojas_gest = [h for h in xl.sheet_names if 'GEST' in h.upper()]
    if not hojas_gest:
        return None, None, f"No se encontró hoja de Gestión en el archivo ({source_desc})"
    hoja_ig = hojas_gest[0]
    df_raw = xl.parse(hoja_ig, header=None)

    header_idx = None
    for r in range(len(df_raw)):
        row_vals = [str(x).strip().upper() for x in df_raw.iloc[r].dropna()]
        if 'ENE' in row_vals and 'FEB' in row_vals:
            header_idx = r
            break

    if header_idx is None:
        return None, None, "No se encontró fila de meses en la hoja de Gestión"

    meses_cols = {}
    for col_idx in range(len(df_raw.columns)):
        val = str(df_raw.iloc[header_idx, col_idx]).strip().upper()
        if val in ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']:
            meses_cols[val] = col_idx

    factores_dict = {
        'ART': 'Análisis de Riesgo (ART)',
        'OPAS': 'Inspecciones Campo (OPAS)',
        'IDPS': 'Charlas Prejornada (IDPS)',
        'IDS': 'Condiciones Subestándar (IDS)',
        'IENTS': 'Entrenamientos (IENTS)',
        'OSEA': 'Permisos de Trabajo (OSEA)',
        'CAI': 'Planes Acción Incidentes (CAI)',
        'I G': 'Índice Global Gestión (IG)',
        'IE': 'Índice de Efectividad (IE)'
    }

    records_ig = []
    for r in range(header_idx + 1, len(df_raw)):
        for key in factores_dict:
            fila_texto = " ".join([str(x) for x in df_raw.iloc[r, :4].dropna()])
            if re.search(rf'\b{re.escape(key)}\b', fila_texto, re.IGNORECASE):
                for mes, col_c in meses_cols.items():
                    val = df_raw.iloc[r, col_c]
                    if pd.notna(val) and isinstance(val, (int, float)):
                        records_ig.append({
                            'clave': key,
                            'indicador': factores_dict[key],
                            'mes': mes,
                            'porcentaje': float(val) if float(val) <= 100 else float(val) / 100.0,
                            'es_global': (key in ['I G', 'IE'])
                        })
                break

    df_ig = pd.DataFrame(records_ig)
    meses_orden = {'ENE': 1, 'FEB': 2, 'MAR': 3, 'ABR': 4, 'MAY': 5, 'JUN': 6,
                   'JUL': 7, 'AGO': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DIC': 12}
    if not df_ig.empty:
        df_ig['mes_num'] = df_ig['mes'].map(meses_orden)
        df_ig = df_ig.sort_values(['mes_num', 'clave'])

    # Extraer métricas operativas de cada hoja
    detalles = {}
    if 'ART' in xl.sheet_names:
        detalles['ART'] = extraer_filas_meses(xl.parse('ART', header=None), ['programados', 'realizados'])
    if 'OPAS' in xl.sheet_names:
        detalles['OPAS'] = extraer_filas_meses(xl.parse('OPAS', header=None), ['programadas', 'realizadas', 'personas'])
    if 'IDPS' in xl.sheet_names:
        detalles['IDPS'] = extraer_filas_meses(xl.parse('IDPS', header=None), ['programados', 'realizados', 'previsto', 'asistentes'])
    if 'IDS' in xl.sheet_names:
        detalles['IDS'] = extraer_filas_meses(xl.parse('IDS', header=None), ['detectadas', 'eliminadas'])
    if 'IENTS' in xl.sheet_names:
        detalles['IENTS'] = extraer_filas_meses(xl.parse('IENTS', header=None), ['prog', 'capacitados'])
    if 'ICAI' in xl.sheet_names:
        detalles['ICAI'] = extraer_filas_meses(xl.parse('ICAI', header=None), ['propuestas', 'implementadas'])

    return df_ig, detalles, None

def extraer_filas_meses(df, keywords):
    meses_orden = {'ENE': 1, 'FEB': 2, 'MAR': 3, 'ABR': 4, 'MAY': 5, 'JUN': 6,
                   'JUL': 7, 'AGO': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DIC': 12}
    header_idx = None
    for r in range(len(df)):
        row_str = " ".join([str(x).upper() for x in df.iloc[r].dropna()])
        if 'ENE' in row_str and 'FEB' in row_str:
            header_idx = r
            break
    if header_idx is None:
        return {}

    meses_map = {}
    for col in range(len(df.columns)):
        m = str(df.iloc[header_idx, col]).strip().upper()
        if m in meses_orden:
            meses_map[m] = col

    result = {}
    for kw in keywords:
        for r in range(header_idx + 1, len(df)):
            label = str(df.iloc[r, 0] if pd.notna(df.iloc[r, 0]) else (df.iloc[r, 1] if len(df.columns) > 1 and pd.notna(df.iloc[r, 1]) else '')).strip()
            if kw.lower() in label.lower():
                series = {}
                for mes, col_c in meses_map.items():
                    val = df.iloc[r, col_c]
                    if pd.notna(val) and isinstance(val, (int, float)):
                        series[mes] = float(val)
                result[kw] = series
                break
    return result

def get_modified_date():
    src, err, desc = obtener_excel_file("hse_proactivos")
    if isinstance(src, str) and os.path.exists(src):
        return os.path.getmtime(src)
    return None
