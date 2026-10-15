import os
import sys
import importlib
import streamlit as st

# Configuración de la aplicación
st.set_page_config(
    page_title="Portal de Dashboards Ejecutivos",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos globales de interfaz
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #F8FAFC;
        border-right: 1px solid #E2E8F0;
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

def descubrir_dashboards():
    """
    Escanea el directorio raíz buscando carpetas que comiencen con 'dash_'
    y que contengan un módulo view.py con la función render().
    """
    nombres_personalizados = {
        "dash_hse_desempeno": "🛡️ HSE Desempeño Operativo",
        "dash_hse_proactivos": "⚡ HSE Indicadores Proactivos"
    }

    modulos = {}
    for entry in sorted(os.listdir(BASE_DIR)):
        full_path = os.path.join(BASE_DIR, entry)
        if os.path.isdir(full_path) and entry.startswith("dash_"):
            view_path = os.path.join(full_path, "view.py")
            if os.path.exists(view_path):
                label = nombres_personalizados.get(entry, f"📊 {entry.replace('dash_', '').replace('_', ' ').title()}")
                modulos[label] = entry
    return modulos

dashboards_disponibles = descubrir_dashboards()

# BARRA LATERAL
st.sidebar.markdown("""
    <div style="padding: 0.5rem 0 1rem 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 1rem;">
        <h3 style="color: #0F2942; margin: 0; font-size: 1.15rem; font-weight: 800; letter-spacing: -0.3px;">
            🏢 PORTAL DE REPORTES
        </h3>
        <p style="color: #64748B; font-size: 0.78rem; margin: 2px 0 0 0;">
            Tableros de Control Ejecutivos
        </p>
    </div>
""", unsafe_allow_html=True)

if not dashboards_disponibles:
    st.sidebar.warning("No se encontraron carpetas con formato `dash_*`.")
    st.info("Crea una carpeta `dash_[nombre]` con su archivo `view.py` para visualizarlo aquí.")
else:
    seleccion = st.sidebar.radio(
        "Selecciona el Dashboard:",
        list(dashboards_disponibles.keys()),
        index=0
    )

    # PANEL DE CONEXIÓN M365 / ONEDRIVE
    from gestor_m365 import obtener_config_fuentes, guardar_config_fuentes, obtener_excel_file
    
    with st.sidebar.expander("☁️ Conexión M365 / OneDrive", expanded=False):
        st.markdown("<p style='font-size:0.8rem; color:#475569;'>Configura los enlaces de <b>SharePoint</b> o rutas de <b>OneDrive</b> para sincronización automática en vivo.</p>", unsafe_allow_html=True)
        
        cfg = obtener_config_fuentes()
        
        # Estado actual
        _, _, estado_desemp = obtener_excel_file("hse_desempeno")
        _, _, estado_proact = obtener_excel_file("hse_proactivos")
        
        st.markdown(f"""
        <div style="background:#F1F5F9; border-radius:6px; padding:6px 10px; font-size:0.75rem; margin-bottom:10px;">
            <b>Desempeño HSE:</b> <span style="color:#0284C7;">{estado_desemp}</span><br>
            <b>Proactivos HSE:</b> <span style="color:#0284C7;">{estado_proact}</span>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("form_fuentes_m365"):
            st.markdown("<b style='font-size:0.78rem;'>1. Matriz Desempeño HSE (URL o Ruta):</b>", unsafe_allow_html=True)
            url_desemp = st.text_input(
                "HSE Desempeño",
                value=cfg.get("hse_desempeno", {}).get("ruta_o_url", ""),
                placeholder="https://empresa.sharepoint.com/... o C:\\Users\\...\\OneDrive",
                label_visibility="collapsed"
            )
            
            st.markdown("<b style='font-size:0.78rem;'>2. Control Proactivos HSE (URL o Ruta):</b>", unsafe_allow_html=True)
            url_proact = st.text_input(
                "HSE Proactivos",
                value=cfg.get("hse_proactivos", {}).get("ruta_o_url", ""),
                placeholder="https://empresa.sharepoint.com/... o C:\\Users\\...\\OneDrive",
                label_visibility="collapsed"
            )
            
            guardar_btn = st.form_submit_button("💾 Guardar Configuración", use_container_width=True)
            if guardar_btn:
                cfg["hse_desempeno"]["ruta_o_url"] = url_desemp.strip()
                cfg["hse_proactivos"]["ruta_o_url"] = url_proact.strip()
                guardar_config_fuentes(cfg)
                st.cache_data.clear()
                st.success("¡Configuración guardada y caché actualizada!")
                st.rerun()

        if st.button("🔄 Refrescar Datos (Caché M365)", use_container_width=True):
            st.cache_data.clear()
            st.toast("Datos recargados desde M365", icon="🔄")
            st.rerun()

    st.sidebar.caption("""
    ---
    © 2026 VOJ.DEV  
    Todos los derechos reservados.
    """)

    carpeta_modulo = dashboards_disponibles[seleccion]
    try:
        modulo = importlib.import_module(f"{carpeta_modulo}.view")
        if hasattr(modulo, "render"):
            modulo.render()
        else:
            st.error(f"El módulo `{carpeta_modulo}.view` no tiene una función `render()`.")
    except Exception as e:
        st.error(f"Error al cargar el dashboard `{carpeta_modulo}`: {e}")
