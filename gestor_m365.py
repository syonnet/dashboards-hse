import os
import json
import urllib.request
import pandas as pd
import streamlit as st

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config_fuentes.json")

def obtener_config_fuentes():
    """Retorna la configuración de orígenes de datos (Local, OneDrive o SharePoint URL)."""
    default_config = {
        "hse_desempeno": {
            "descripcion": "Matriz de Indicadores HSE",
            "ruta_local_backup": os.path.join(os.path.dirname(os.path.abspath(__file__)), "dash_hse_desempeno", "data", "MATRIZ INDIC HSE.xlsx"),
            "ruta_o_url": ""
        },
        "hse_proactivos": {
            "descripcion": "Control de Indicadores Proactivos",
            "ruta_local_backup": os.path.join(os.path.dirname(os.path.abspath(__file__)), "dash_hse_proactivos", "data", "CONTROL INDICADORES PROACTIVOS.xlsx"),
            "ruta_o_url": ""
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
            if "url_hse_desempeno" in st.secrets["m365"] and st.secrets["m365"]["url_hse_desempeno"]:
                default_config["hse_desempeno"]["ruta_o_url"] = st.secrets["m365"]["url_hse_desempeno"]
            if "url_hse_proactivos" in st.secrets["m365"] and st.secrets["m365"]["url_hse_proactivos"]:
                default_config["hse_proactivos"]["ruta_o_url"] = st.secrets["m365"]["url_hse_proactivos"]
    except Exception:
        pass

    return default_config

def guardar_config_fuentes(config: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def obtener_excel_file(modulo_key: str):
    """
    Obtiene el archivo Excel ya sea desde:
    1. Una URL directa de SharePoint/OneDrive (?download=1)
    2. Una ruta sincronizada de OneDrive configurada o auto-detectada
    3. La carpeta local data/ del módulo como respaldo seguro.
    """
    cfg = obtener_config_fuentes().get(modulo_key, {})
    fuente = cfg.get("ruta_o_url", "").strip()
    backup_path = cfg.get("ruta_local_backup", "")
    if backup_path and not os.path.isabs(backup_path):
        backup_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), backup_path)

    # Caso 1: Es una URL web de SharePoint o OneDrive
    if fuente.startswith("http://") or fuente.startswith("https://"):
        try:
            url_descarga = fuente
            if "sharepoint.com" in fuente or "onedrive" in fuente:
                if "download=1" not in url_descarga:
                    sep = "&" if "?" in url_descarga else "?"
                    url_descarga = f"{url_descarga}{sep}download=1"
            
            req = urllib.request.Request(
                url_descarga, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read()
                # Validar que sea un archivo Excel binario real (.xlsx inicia con cabecera ZIP b'PK')
                if content.startswith(b'PK'):
                    import io
                    return io.BytesIO(content), None, "SharePoint / OneDrive (Nube M365)"
                else:
                    # SharePoint devolvió página HTML (login de Microsoft o acceso restringido)
                    msg_aviso = "El vínculo de SharePoint requiere inicio de sesión en navegador (SSO). Se activó el respaldo local."
                    if os.path.exists(backup_path):
                        return backup_path, None, f"Respaldo local ({msg_aviso})"
                    return None, f"El enlace proporcionado no entregó un archivo Excel (entregó página web HTML). Asegúrese de otorgar acceso 'Cualquier persona con el vínculo puede ver'.", "Acceso denegado M365"
        except Exception as e:
            if os.path.exists(backup_path):
                return backup_path, None, f"Respaldo local (Fallo conexión M365: {e})"
            return None, f"Error descargando desde SharePoint: {e}", "Error"

    # Caso 2: Es una ruta de archivo local de OneDrive configurada explícitamente
    if fuente and os.path.exists(fuente):
        return fuente, None, f"OneDrive Sincronizado ({os.path.basename(fuente)})"

    # Caso 3: Backup local dentro de la carpeta del módulo
    if os.path.exists(backup_path):
        return backup_path, None, "Carpeta local del proyecto"

    return None, f"No se encontró archivo para {modulo_key}", "No encontrado"
