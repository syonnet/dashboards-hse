import os
import re
import pandas as pd
import streamlit as st
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from gestor_m365 import obtener_excel_file

@st.cache_data(ttl=60)
def load_data():
    """Carga y procesa MATRIZ INDIC HSE.xlsx desde OneDrive, SharePoint o local."""
    excel_source, err, source_desc = obtener_excel_file("hse_desempeno")
    if err or excel_source is None:
        return None, err

    try:
        xl = pd.ExcelFile(excel_source, engine='openpyxl')
    except Exception as e:
        return None, f"Error al abrir Excel ({source_desc}): {e}"

    hojas = [h for h in xl.sheet_names if ('INDICADORES HSE' in h.upper() or 'MATRIZ' in h.upper() or 'HSE' in h.upper()) and 'GRAF' not in h.upper()]
    if not hojas:
        return None, f"No se encontró hoja 'INDICADORES HSE' en el archivo ({source_desc}). Hojas existentes: {xl.sheet_names}"

    data_by_year = {}
    patron_col = re.compile(r'^(TBG|BV|CNX|CSH|TUR)\s*[\n\s]*(ENE|FEB|MAR|ABR|MAY|JUN|JUL|AGO|SEP|OCT|NOV|DIC)$', re.IGNORECASE)

    for hoja in hojas:
        anio_match = re.search(r'20\d{2}', hoja)
        anio = anio_match.group(0) if anio_match else '2026'
        
        # Probar automáticamente la fila de encabezado correcta
        df = None
        for hr in [5, 4, 3, 2, 6]:
            try:
                candidate = xl.parse(hoja, header=hr)
                cols = [str(c).strip().replace('\n', ' ') for c in candidate.columns if pd.notna(c)]
                if any('SUB-PROCESO' in c or 'SUBPROCESO' in c for c in cols) and any('INDICADOR' in c for c in cols):
                    df = candidate
                    break
            except Exception:
                continue

        if df is None:
            continue

        col_subproc = next((c for c in df.columns if 'SUB' in str(c).upper() and 'PROC' in str(c).upper()), None)
        col_ind = next((c for c in df.columns if 'INDICADOR' in str(c).upper() and 'PLANT' in str(c).upper()), None)
        if not col_subproc or not col_ind:
            continue

        df[col_subproc] = df[col_subproc].ffill()
        df = df.dropna(subset=[col_ind])
        meta_col = next((c for c in df.columns if f'META {anio}' in str(c).upper()), None)
        if not meta_col:
            meta_col = next((c for c in df.columns if 'META' in str(c).upper()), None)

        records = []
        for col in df.columns:
            col_str = str(col).strip().replace('\n', ' ')
            m = patron_col.match(col_str)
            if m:
                base = m.group(1).upper()
                mes = m.group(2).upper()
                for _, row in df.iterrows():
                    val = row[col]
                    if pd.notna(val) and isinstance(val, (int, float)):
                        ind_nombre = str(row[col_ind]).strip().replace('\n', ' ')
                        abrev = str(row['ABREVIATURA']).strip().replace('\n', ' ') if 'ABREVIATURA' in row and pd.notna(row.get('ABREVIATURA')) else ''
                        subproc = str(row[col_subproc]).strip().replace('\n', ' ')
                        meta_str = str(row[meta_col]).strip() if meta_col in row and pd.notna(row[meta_col]) else '≥ 80%'

                        cumple, pct_cumpl = evaluar_meta(ind_nombre, abrev, meta_str, float(val))
                        records.append({
                            'anio': anio,
                            'subproceso': subproc,
                            'indicador': ind_nombre,
                            'abreviatura': abrev if abrev else ind_nombre[:10],
                            'meta_texto': meta_str,
                            'base': base,
                            'mes': mes,
                            'valor': float(val),
                            'cumple': cumple,
                            'pct_cumplimiento': pct_cumpl
                        })
        if records:
            data_by_year[anio] = pd.DataFrame(records)

    if not data_by_year:
        return None, f"El archivo de SharePoint ({source_desc}) se abrió, pero no se encontraron filas de métricas con formato TBG/BV/CNX/CSH/TUR ENE-DIC."

    meses_orden = {'ENE': 1, 'FEB': 2, 'MAR': 3, 'ABR': 4, 'MAY': 5, 'JUN': 6,
                   'JUL': 7, 'AGO': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DIC': 12}
    for anio in data_by_year:
        data_by_year[anio]['mes_num'] = data_by_year[anio]['mes'].map(meses_orden)
        data_by_year[anio] = data_by_year[anio].sort_values(['mes_num', 'subproceso', 'indicador'])

    return data_by_year, None

def evaluar_meta(indicador: str, abreviatura: str, meta_str: str, valor: float):
    abrev_upper = abreviatura.upper()
    ind_upper = indicador.upper()
    es_menor_mejor = (
        any(k in abrev_upper for k in ['IF', 'IG', 'TR', 'MCV', 'IEP', 'ILME']) or
        'FRECUENCIA' in ind_upper or
        'GRAVEDAD' in ind_upper or
        'INCIDENTE' in ind_upper or
        'ENFERMEDADES' in ind_upper or
        'ACCIDENTE' in ind_upper
    )
    nums = re.findall(r'(\d+[\.,]?\d*)', meta_str.replace(',', '.'))
    if not nums:
        meta_num = 0.80
    else:
        meta_num = float(nums[0])
        if '%' in meta_str or (meta_num > 1.0 and not es_menor_mejor):
            meta_num = meta_num / 100.0 if meta_num > 1.0 else meta_num

    if es_menor_mejor:
        cumple = (valor <= meta_num)
        pct_cumpl = 100.0 if valor <= meta_num else max(0.0, 100.0 - ((valor - meta_num) * 100.0))
    else:
        cumple = (valor >= (meta_num - 0.001))
        pct_cumpl = min(100.0, (valor / meta_num) * 100.0) if meta_num > 0 else 100.0
    return cumple, round(pct_cumpl, 1)

def get_modified_date():
    src, err, desc = obtener_excel_file("hse_desempeno")
    if isinstance(src, str) and os.path.exists(src):
        return os.path.getmtime(src)
    return None
