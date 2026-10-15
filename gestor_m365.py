import os
import json
import urllib.request
import pandas as pd
import streamlit as st

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config_fuentes.json")

URL_OFICIAL_DESEMPENO = "https://triboilgas.sharepoint.com/:x:/g/conexpet/IQClFWM9Iy38Q6dCQcc8Zv5SAWukkxhAyJgK-Y6kgFFVZZE?e=Y508VH"
URL_OFICIAL_PROACTIVOS = "https://triboilgas.sharepoint.com/:x:/g/conexpet/IQC9si9mkiwvR6ogIeeoXDweAQ31q6Y7ZB7xI-aLaUMi7qs?e=6LA1Fo"

def obtener_config_fuentes():
    """Retorna la configuración de orígenes de datos (Local, OneDrive o SharePoint URL)."""
    default_config = {
        "hse_desempeno": {
            "descripcion": "Matriz de Indicadores HSE",
            "ruta_local_backup": os.path.join(os.path.dirname(os.path.abspath(__file__)), "dash_hse_desempeno", "data", "MATRIZ INDIC HSE.xlsx"),
            "ruta_o_url": URL_OFICIAL_DESEMPENO
        },
        "hse_proactivos": {
            "descripcion": "Control de Indicadores Proactivos",
            "ruta_local_backup": os.path.join(os.path.dirname(os.path.abspath(__file__)), "dash_hse_proactivos", "data", "CONTROL INDICADORES PROACTIVOS.xlsx"),
            "ruta_o_url": URL_OFICIAL_PROACTIVOS
        }
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                default_config.update(saved)
        except Exception:
            pass

    # Soporte nativo para Streamlit Community Cloud (st.secrets)
    try:
        if hasattr(st, "secrets") and "m365" in st.secrets:
            sec_desemp = str(st.secrets["m365"].get("url_hse_desempeno", "")).strip()
            sec_proact = str(st.secrets["m365"].get("url_hse_proactivos", "")).strip()
            # Proteger contra secretos duplicados o idénticos
            if sec_desemp and sec_proact and sec_desemp != sec_proact:
                default_config["hse_desempeno"]["ruta_o_url"] = sec_desemp
                default_config["hse_proactivos"]["ruta_o_url"] = sec_proact
            elif sec_desemp and not sec_proact:
                default_config["hse_desempeno"]["ruta_o_url"] = sec_desemp
            elif sec_proact and not sec_desemp:
                default_config["hse_proactivos"]["ruta_o_url"] = sec_proact
    except Exception:
        pass

    return default_config

def guardar_config_fuentes(config: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def descargar_desde_fuente(fuente_url_o_path: str, backup_path: str):
    """Descarga o abre el archivo Excel desde una URL o ruta local."""
    if not fuente_url_o_path:
        if backup_path and os.path.exists(backup_path):
            return backup_path, None, "Respaldo local"
        return None, "No se configuró URL ni ruta", "No configurado"

    if fuente_url_o_path.startswith("http://") or fuente_url_o_path.startswith("https://"):
        try:
            url_descarga = fuente_url_o_path
            if "sharepoint.com" in fuente_url_o_path or "onedrive" in fuente_url_o_path:
                if "download=1" not in url_descarga:
                    sep = "&" if "?" in url_descarga else "?"
                    url_descarga = f"{url_descarga}{sep}download=1"
            
            import http.cookiejar
            cj = http.cookiejar.CookieJar()
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
            opener.addheaders = [
                ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            ]
            resp = opener.open(url_descarga, timeout=20)
            content = resp.read()

            if content.startswith(b'PK'):
                import io
                return io.BytesIO(content), None, "SharePoint Online (En vivo)"
            else:
                if backup_path and os.path.exists(backup_path):
                    return backup_path, None, "Respaldo local (SharePoint entregó página web)"
                return None, "El enlace de SharePoint no entregó un archivo Excel binario.", "Error de formato"
        except Exception as e:
            if backup_path and os.path.exists(backup_path):
                return backup_path, None, f"Respaldo local (Fallo conexión M365: {e})"
            return None, f"Error descargando desde SharePoint: {e}", "Error"

    if os.path.exists(fuente_url_o_path):
        return fuente_url_o_path, None, f"Archivo sincronizado ({os.path.basename(fuente_url_o_path)})"

    if backup_path and os.path.exists(backup_path):
        return backup_path, None, "Carpeta local del proyecto"

    return None, f"No se encontró archivo en {fuente_url_o_path}", "No encontrado"

def obtener_excel_file(modulo_key: str):
    """
    Obtiene el archivo Excel correspondiente a cada módulo.
    Detecta automáticamente si los enlaces de SharePoint están intercambiados
    analizando las hojas del Excel.
    """
    cfg = obtener_config_fuentes()
    
    fuente_solicitada = cfg.get(modulo_key, {}).get("ruta_o_url", "").strip()
    backup_solicitado = cfg.get(modulo_key, {}).get("ruta_local_backup", "")
    if backup_solicitado and not os.path.isabs(backup_solicitado):
        backup_solicitado = os.path.join(os.path.dirname(os.path.abspath(__file__)), backup_solicitado)

    # 1. Intentar con la fuente configurada para este módulo
    res, err, desc = descargar_desde_fuente(fuente_solicitada, backup_solicitado)
    if not err and res is not None:
        try:
            xl = pd.ExcelFile(res, engine='openpyxl')
            hojas = [str(h).upper() for h in xl.sheet_names]
            
            es_desempeno = any('INDICADORES HSE' in h or 'MATRIZ' in h for h in hojas)
            es_proactivos = any('ART' in h or 'OPAS' in h or 'GEST' in h or 'PROACT' in h for h in hojas)
            
            if modulo_key == "hse_desempeno" and es_desempeno:
                if hasattr(res, 'seek'):
                    res.seek(0)
                return res, None, desc
            elif modulo_key == "hse_proactivos" and es_proactivos:
                if hasattr(res, 'seek'):
                    res.seek(0)
                return res, None, desc
            
            # Si el archivo no corresponde al módulo solicitado, descargar de la URL oficial garantizada
            url_oficial = URL_OFICIAL_DESEMPENO if modulo_key == "hse_desempeno" else URL_OFICIAL_PROACTIVOS
            res_oficial, err_of, desc_of = descargar_desde_fuente(url_oficial, backup_solicitado)
            if not err_of and res_oficial is not None:
                if hasattr(res_oficial, 'seek'):
                    res_oficial.seek(0)
                return res_oficial, None, "SharePoint Online (En vivo)"
        except Exception:
            pass
            
        if hasattr(res, 'seek'):
            res.seek(0)
        return res, None, desc

    # 2. Si falló la fuente principal, intentar con la alterna
    otro_key = "hse_proactivos" if modulo_key == "hse_desempeno" else "hse_desempeno"
    fuente_alterna = cfg.get(otro_key, {}).get("ruta_o_url", "").strip()
    backup_alterno = cfg.get(otro_key, {}).get("ruta_local_backup", "")
    if backup_alterno and not os.path.isabs(backup_alterno):
        backup_alterno = os.path.join(os.path.dirname(os.path.abspath(__file__)), backup_alterno)
    res_alt, err_alt, desc_alt = descargar_desde_fuente(fuente_alterna, backup_alterno)
    if not err_alt and res_alt is not None:
        if hasattr(res_alt, 'seek'):
            res_alt.seek(0)
        return res_alt, None, f"{desc_alt} (Fuente alternativa)"

    return None, f"No se pudo cargar archivo para {modulo_key}: {err}", "Error"
