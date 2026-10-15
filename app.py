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

    st.sidebar.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    if st.sidebar.button("🔄 Actualizar Datos", use_container_width=True):
        st.cache_data.clear()
        st.toast("Datos actualizados", icon="🔄")
        st.rerun()

    st.sidebar.caption("""
    ---
    © 2026 VOJ.DEV  
    Todos los derechos reservados.
    """)

    carpeta_modulo = dashboards_disponibles[seleccion]
    try:
        modulo = importlib.import_module(f"{carpeta_modulo}.view")
        modulo = importlib.reload(modulo)
        if hasattr(modulo, "render"):
            modulo.render()
        else:
            st.error(f"El módulo `{carpeta_modulo}.view` no tiene una función `render()`.")
    except Exception as e:
        st.error(f"Error al cargar el dashboard `{carpeta_modulo}`: {e}")
