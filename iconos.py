"""
iconos.py - Librería de iconos vectoriales SVG limpios y profesionales.
Basados en el estándar Lucide Icons (utilizados en diseño corporativo moderno).
Elimina completamente la estética de emojis informales / generados por IA.
"""

def _svg(content: str, color: str = "currentColor", size: int = 20, stroke_width: float = 2.0) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke_width}" '
        f'stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; display: inline-block;">'
        f'{content}'
        f'</svg>'
    )

def icon_activity(color="currentColor", size=20):
    """Índice de Frecuencia / Pulso de actividad."""
    return _svg('<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>', color, size)

def icon_shield_check(color="currentColor", size=20):
    """Cumplimiento Global / Seguridad."""
    return _svg('<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/><path d="m9 12 2 2 4-4"/>', color, size)

def icon_shield_alert(color="currentColor", size=20):
    """Condiciones Inseguras / Alerta de Seguridad."""
    return _svg('<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/>', color, size)

def icon_alert_circle(color="currentColor", size=20):
    """Índice de Gravedad / Atención."""
    return _svg('<circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/>', color, size)

def icon_check_circle(color="currentColor", size=20):
    """Metas Cumplidas / Aprobado."""
    return _svg('<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>', color, size)

def icon_check_square(color="currentColor", size=20):
    """Acciones Correctivas / Planes de Acción."""
    return _svg('<polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>', color, size)

def icon_truck(color="currentColor", size=20):
    """Incidentes Vehiculares / Flota."""
    return _svg('<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18.5" r="2.5"/><circle cx="7" cy="18.5" r="2.5"/>', color, size)

def icon_award(color="currentColor", size=20):
    """Área Líder / Desempeño Superior."""
    return _svg('<circle cx="12" cy="8" r="6"/><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"/>', color, size)

def icon_megaphone(color="currentColor", size=20):
    """Charlas Prejornada / Comunicación."""
    return _svg('<path d="m3 11 18-5v12L3 13v-2z"/><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"/>', color, size)

def icon_users(color="currentColor", size=20):
    """Personal Capacitado / Equipo."""
    return _svg('<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>', color, size)

def icon_clipboard_check(color="currentColor", size=20):
    """Análisis de Riesgo (ART)."""
    return _svg('<rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/>', color, size)

def icon_file_text(color="currentColor", size=20):
    """Permisos de Trabajo (OSEA) / Documentación."""
    return _svg('<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/><line x1="10" x2="8" y1="9" y2="9"/>', color, size)

def icon_building(color="currentColor", size=20):
    """Portal Corporativo / Empresa."""
    return _svg('<rect width="16" height="20" x="4" y="2" rx="2" ry="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01"/><path d="M16 6h.01"/><path d="M12 6h.01"/><path d="M12 10h.01"/><path d="M12 14h.01"/><path d="M16 10h.01"/><path d="M16 14h.01"/><path d="M8 10h.01"/><path d="M8 14h.01"/>', color, size)

def icon_info(color="currentColor", size=16):
    """Diagnóstico / Insight."""
    return _svg('<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>', color, size, stroke_width=2.0)

def icon_download(color="currentColor", size=16):
    """Descargar."""
    return _svg('<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/>', color, size)

def icon_refresh(color="currentColor", size=16):
    """Actualizar datos."""
    return _svg('<path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 21h5v-5"/>', color, size)
