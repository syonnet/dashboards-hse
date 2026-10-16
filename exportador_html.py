import plotly.graph_objects as go
from datetime import datetime
from iconos import icon_info

def generar_html_ejecutivo(titulo: str, subtitulo: str, kpis: list, fig_gauge, fig_bar, fig_spline, fig_double, insight_txt: str = ""):
    """
    Genera un archivo HTML 100% autónomo (standalone), interactivo y responsive.
    Cualquier jefe o directivo puede abrirlo con doble clic sin tener Python instalado.
    """
    gauge_html = fig_gauge.to_html(full_html=False, include_plotlyjs=False, config={'responsive': True, 'displayModeBar': False})
    bar_html = fig_bar.to_html(full_html=False, include_plotlyjs=False, config={'responsive': True, 'displayModeBar': False})
    spline_html = fig_spline.to_html(full_html=False, include_plotlyjs=False, config={'responsive': True, 'displayModeBar': False})
    double_html = fig_double.to_html(full_html=False, include_plotlyjs=False, config={'responsive': True, 'displayModeBar': False})
    
    fecha_generacion = datetime.now().strftime("%d/%m/%Y %I:%M %p")

    # Renderizar tarjetas KPI
    cards_html = ""
    for k in kpis:
        cards_html += f"""
        <div class="mini-card">
            <div class="mini-icon" style="background: {k.get('bg', '#F1F5F9')}; color: {k.get('color', '#334155')};">
                {k.get('icon', '')}
            </div>
            <div>
                <div class="mini-title">{k.get('title', '')}</div>
                <div class="mini-value">{k.get('value', '')}</div>
            </div>
        </div>
        """

    insight_html = f"""
    <div class="insight-pill" style="display: flex; align-items: center; gap: 6px;">
        {icon_info(color='#0F766E', size=15)} <span>{insight_txt}</span>
    </div>
    """ if insight_txt else ""

    html_template = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo} - Reporte Ejecutivo</title>
    <!-- Plotly.js para interactividad total sin Python -->
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        body {{
            background-color: #F8FAFC;
            color: #1E293B;
            padding: 1.5rem;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        /* Header */
        .header {{
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 1rem 1.5rem;
            margin-bottom: 1.2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }}
        .header-title {{
            font-size: 1.4rem;
            font-weight: 800;
            color: #0F2942;
        }}
        .header-sub {{
            font-size: 0.82rem;
            color: #64748B;
            margin-top: 2px;
        }}
        .header-meta {{
            font-size: 0.75rem;
            color: #64748B;
            text-align: right;
        }}
        /* Grid Superior Responsivo */
        .top-grid {{
            display: grid;
            grid-template-columns: 1.5fr 1.3fr 1.5fr;
            gap: 1.2rem;
            margin-bottom: 1.2rem;
        }}
        .bottom-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.2rem;
            margin-bottom: 1.5rem;
        }}
        /* Tarjetas */
        .dash-card {{
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
            display: flex;
            flex-direction: column;
        }}
        .card-header {{
            font-size: 0.95rem;
            font-weight: 700;
            color: #111827;
            margin-bottom: 2px;
        }}
        .card-sub {{
            font-size: 0.75rem;
            color: #64748B;
            margin-bottom: 0.6rem;
        }}
        /* Mini Cards Grid (2 cols x 3 rows) */
        .kpi-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.65rem;
            height: 100%;
        }}
        .mini-card {{
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 0.75rem 0.85rem;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.02);
        }}
        .mini-icon {{
            width: 38px;
            height: 38px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            flex-shrink: 0;
        }}
        .mini-title {{
            font-size: 0.75rem;
            color: #64748B;
            font-weight: 600;
            line-height: 1.2;
        }}
        .mini-value {{
            font-size: 1.35rem;
            font-weight: 800;
            color: #111827;
            line-height: 1.1;
            margin-top: 2px;
        }}
        .insight-pill {{
            background: #F0FDFA;
            border: 1px solid #CCFBF1;
            border-radius: 6px;
            padding: 0.4rem 0.8rem;
            font-size: 0.76rem;
            color: #0F766E;
            margin-bottom: 0.6rem;
        }}
        /* Footer */
        .footer {{
            text-align: center;
            color: #94A3B8;
            font-size: 0.74rem;
            padding: 1.5rem 0;
            border-top: 1px solid #E2E8F0;
        }}
        /* MEDIA QUERIES RESPONSIVAS */
        @media (max-width: 1080px) {{
            .top-grid {{
                grid-template-columns: 1fr;
            }}
            .bottom-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        @media (max-width: 640px) {{
            body {{
                padding: 0.8rem;
            }}
            .kpi-grid {{
                grid-template-columns: 1fr;
            }}
            .header {{
                flex-direction: column;
                align-items: flex-start;
            }}
            .header-meta {{
                text-align: left;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div>
                <div class="header-title">{titulo}</div>
                <div class="header-sub">{subtitulo}</div>
            </div>
            <div class="header-meta">
                Reporte Ejecutivo Standalone<br>
                Generado: <b>{fecha_generacion}</b>
            </div>
        </div>

        <!-- Fila Superior -->
        <div class="top-grid">
            <div class="kpi-grid">
                {cards_html}
            </div>

            <div class="dash-card">
                <div class="card-header">Índice Global de Gestión</div>
                <div class="card-sub">Evaluación del corte vs Meta (80%)</div>
                <div style="flex-grow: 1; display: flex; align-items: center; justify-content: center;">
                    {gauge_html}
                </div>
            </div>

            <div class="dash-card">
                <div class="card-header">Desglose Operativo</div>
                <div class="card-sub">Cumplimiento porcentual por unidad</div>
                <div style="flex-grow: 1;">
                    {bar_html}
                </div>
            </div>
        </div>

        <!-- Fila Inferior -->
        <div class="bottom-grid">
            <div class="dash-card">
                <div class="card-header">Evolución Histórica</div>
                <div class="card-sub">Tendencia dinámica mes a mes</div>
                {insight_html}
                <div style="flex-grow: 1;">
                    {spline_html}
                </div>
            </div>

            <div class="dash-card">
                <div class="card-header">Metas Cumplidas vs. Desviaciones</div>
                <div class="card-sub">Seguimiento mensual de efectividad</div>
                <div style="flex-grow: 1;">
                    {double_html}
                </div>
            </div>
        </div>

        <!-- Footer Copyright -->
        <div class="footer">
            © 2026 Grupo Empresarial • Sistema Integrado de Gestión HSE • Confidencial • Documento de Uso Gerencial
        </div>
    </div>
</body>
</html>
"""
    return html_template
