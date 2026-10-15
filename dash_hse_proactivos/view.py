import os
from datetime import datetime
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from .loader import load_data, get_modified_date
from exportador_html import generar_html_ejecutivo

def render_gauge(val: float):
    val_clamped = max(0.0, min(100.0, float(val)))
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=val_clamped,
        number={'suffix': " %", 'font': {'size': 26, 'color': '#111827', 'family': 'Segoe UI, sans-serif'}},
        gauge={
            'shape': 'angular',
            'axis': {
                'range': [0, 100],
                'tickvals': [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                'tickwidth': 1,
                'tickcolor': "#9CA3AF",
                'tickfont': {'size': 9, 'color': '#6B7280'}
            },
            'bar': {'color': '#1F2937', 'thickness': 0.18},
            'bgcolor': "#FFFFFF",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 45], 'color': '#EF4444'},
                {'range': [45, 75], 'color': '#FBBF24'},
                {'range': [75, 100], 'color': '#06B6D4'}
            ]
        }
    ))
    fig.update_layout(
        height=210,
        margin=dict(l=20, r=20, t=10, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Segoe UI, sans-serif'}
    )
    return fig

def render():
    df_ig, detalles, err = load_data()
    if err or df_ig is None:
        st.error(f"⚠️ {err if err else 'No se pudieron procesar datos de Proactivos desde SharePoint'}")
        return

    st.markdown("""
        <style>
        .dash-card {
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
            height: 100%;
        }
        .mini-card {
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 0.75rem 0.9rem;
            display: flex;
            align-items: center;
            gap: 12px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.02);
            min-height: 72px;
            margin-bottom: 0.65rem;
        }
        .mini-icon {
            width: 40px;
            height: 40px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3rem;
            flex-shrink: 0;
        }
        .mini-title {
            font-size: 0.78rem;
            color: #6B7280;
            font-weight: 600;
            margin: 0;
            line-height: 1.1;
        }
        .mini-value {
            font-size: 1.35rem;
            font-weight: 800;
            color: #111827;
            margin: 2px 0 0 0;
            line-height: 1.1;
        }
        .section-header {
            font-size: 0.95rem;
            font-weight: 700;
            color: #111827;
            margin-bottom: 0.1rem;
        }
        .section-sub {
            font-size: 0.75rem;
            color: #6B7280;
            margin-bottom: 0.4rem;
        }
        .filter-ribbon {
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 0.7rem 1.2rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        }
        .insight-pill {
            background: #F0FDFA;
            border: 1px solid #CCFBF1;
            border-radius: 6px;
            padding: 0.4rem 0.8rem;
            font-size: 0.76rem;
            color: #0F766E;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        /* RESPONSIVIDAD MEJORADA PARA TABLETS Y LAPTOPS */
        @media (max-width: 1200px) {
            .mini-card {
                padding: 0.55rem 0.7rem;
                gap: 8px;
            }
            .mini-value {
                font-size: 1.15rem;
            }
            .mini-icon {
                width: 34px;
                height: 34px;
                font-size: 1.1rem;
            }
        }
        @media (max-width: 900px) {
            [data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)

    # HEADER SUPERIOR
    mtime = get_modified_date()
    dt_str = datetime.fromtimestamp(mtime).strftime("%b %d, %Y %I:%M %p") if mtime else "Sep 1, 2026 10:42 AM"

    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown("""
            <div style="padding-top: 0.2rem;">
                <h3 style="font-size: 1.45rem; font-weight: 800; color: #111827; margin: 0; letter-spacing: -0.4px;">
                    Indicadores Proactivos HSE
                </h3>
                <p style="font-size: 0.8rem; color: #6B7280; margin: 2px 0 0 0;">
                    Cultura preventiva, charlas y aseguramiento operativo antes del incidente
                </p>
            </div>
        """, unsafe_allow_html=True)
    with col_h2:
        btn_col, txt_col = st.columns([1, 3])
        with btn_col:
            if st.button("🔄", key="ref_proactivos", help="Recargar datos de CONTROL INDICADORES PROACTIVOS.xlsx"):
                st.cache_data.clear()
                st.rerun()
        with txt_col:
            st.markdown(f"""
                <div style="font-size: 0.72rem; color: #6B7280; text-align: right; line-height: 1.2; padding-top: 5px;">
                    Data refreshed at<br><b>{dt_str}</b>
                </div>
            """, unsafe_allow_html=True)

    # FILTROS GERENCIALES DINÁMICOS
    meses_orden = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']
    meses_disp = [m for m in meses_orden if m in df_ig['mes'].unique()]
    sel_mes_default = len(meses_disp) - 1 if meses_disp else 0

    factores_dict = {
        'Todos los Factores (Consolidado IG)': 'I G',
        '📝 Análisis de Riesgo (ART)': 'ART',
        '🔍 Inspecciones de Campo (OPAS)': 'OPAS',
        '📢 Charlas Prejornada (IDPS)': 'IDPS',
        '🛡️ Condiciones Inseguras (IDS)': 'IDS',
        '👥 Entrenamientos (IENTS)': 'IENTS',
        '📋 Permisos de Trabajo (OSEA)': 'OSEA',
        '🎯 Planes de Acción (CAI)': 'CAI'
    }

    with st.container(border=True):
        pfc1, pfc2 = st.columns([1.2, 2.8])
        with pfc1:
            sel_mes = st.selectbox("🗓️ Mes de Evaluación", meses_disp, index=sel_mes_default, key="pro_mes")
        with pfc2:
            sel_factor_label = st.selectbox("⚡ Enfoque / Pilar Proactivo", list(factores_dict.keys()), index=0, key="pro_factor")
            sel_clave = factores_dict[sel_factor_label]

    # Filtrar datos de proactivos para el mes
    df_mes_ig = df_ig[df_ig['mes'] == sel_mes]

    def get_factor_val(clave, default=100.0):
        r = df_mes_ig[df_mes_ig['clave'] == clave]
        return float(r['porcentaje'].iloc[0]) if not r.empty else default

    art_pct = get_factor_val('ART', 100.0)
    opas_pct = get_factor_val('OPAS', 100.0)
    idps_pct = get_factor_val('IDPS', 96.0)
    ids_pct = get_factor_val('IDS', 100.0)
    ients_pct = get_factor_val('IENTS', 92.3)
    osea_pct = get_factor_val('OSEA', 100.0)
    cai_pct = get_factor_val('CAI', 83.3)
    ig_val = get_factor_val('I G', 96.3)

    gauge_val = ig_val if sel_clave == 'I G' else get_factor_val(sel_clave, 100.0)
    gauge_title = "Índice Global Gestión (IG)" if sel_clave == 'I G' else sel_factor_label.split('(')[0].strip()

    emp_cap = int(detalles.get('IENTS', {}).get('capacitados', {}).get(sel_mes, 0)) if detalles else 76

    # ==========================================
    # FILA SUPERIOR (ESTILO IMAGEN 1)
    # Sin contenedor exterior blanco vacío
    # ==========================================
    col_kpis, col_gauge, col_bar = st.columns([1.6, 1.4, 1.6])

    with col_kpis:
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            st.markdown(f"""
                <div class="mini-card">
                    <div class="mini-icon" style="background: #DCFCE7; color: #16A34A;">🛡️</div>
                    <div>
                        <div class="mini-title">Condiciones Inseguras (IDS)</div>
                        <div class="mini-value">{ids_pct:.1f} %</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with r1_c2:
            st.markdown(f"""
                <div class="mini-card">
                    <div class="mini-icon" style="background: #FFEDD5; color: #EA580C;">📢</div>
                    <div>
                        <div class="mini-title">Charlas Prejornada (IDPS)</div>
                        <div class="mini-value">{idps_pct:.1f} %</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        r2_c1, r2_c2 = st.columns(2)
        with r2_c1:
            st.markdown(f"""
                <div class="mini-card">
                    <div class="mini-icon" style="background: #FEE2E2; color: #DC2626;">👥</div>
                    <div>
                        <div class="mini-title">Personal Capacitado</div>
                        <div class="mini-value">{emp_cap}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with r2_c2:
            st.markdown(f"""
                <div class="mini-card">
                    <div class="mini-icon" style="background: #E0F2FE; color: #0284C7;">📝</div>
                    <div>
                        <div class="mini-title">Análisis de Riesgo (ART)</div>
                        <div class="mini-value">{art_pct:.1f} %</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        r3_c1, r3_c2 = st.columns(2)
        with r3_c1:
            st.markdown(f"""
                <div class="mini-card">
                    <div class="mini-icon" style="background: #F3E8FF; color: #9333EA;">📋</div>
                    <div>
                        <div class="mini-title">Permisos Trabajo (OSEA)</div>
                        <div class="mini-value">{osea_pct:.1f} %</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with r3_c2:
            st.markdown(f"""
                <div class="mini-card">
                    <div class="mini-icon" style="background: #FEF3C7; color: #D97706;">🎯</div>
                    <div>
                        <div class="mini-title">Acciones Incidentes (CAI)</div>
                        <div class="mini-value">{cai_pct:.1f} %</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with col_gauge:
        sub_title_gauge = f"{gauge_title} ({sel_mes})"
        st.markdown(f"""
            <div class="dash-card">
                <div class="section-header">{sub_title_gauge}</div>
                <div class="section-sub">Evaluación del pilar vs Meta (80%)</div>
        """, unsafe_allow_html=True)
        fig_gauge = render_gauge(gauge_val)
        st.plotly_chart(fig_gauge, use_container_width=True, key="pro_gauge")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_bar:
        st.markdown(f"""
            <div class="dash-card">
                <div class="section-header">Cumplimiento por Pilar ({sel_mes})</div>
                <div class="section-sub">% de ejecución en el mes seleccionado</div>
        """, unsafe_allow_html=True)

        fact_labels = ['ART', 'OPAS', 'IDPS', 'IDS', 'IENTS', 'OSEA', 'CAI']
        fact_vals = [art_pct, opas_pct, idps_pct, ids_pct, ients_pct, osea_pct, cai_pct]
        bar_colors = ['#EF4444' if f == sel_clave else '#312E81' for f in fact_labels]

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=fact_labels,
            y=fact_vals,
            marker=dict(color=bar_colors, cornerradius=4),
            text=[f"{v:.0f}%" for v in fact_vals],
            textposition='outside',
            width=0.45
        ))
        fig_bar.update_layout(
            height=210,
            margin=dict(l=10, r=10, t=10, b=10),
            yaxis=dict(range=[0, 115], showgrid=True, gridcolor="#F3F4F6", ticksuffix="%"),
            xaxis=dict(showgrid=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Segoe UI, sans-serif', size=11, color='#4B5563')
        )
        st.plotly_chart(fig_bar, use_container_width=True, key="pro_bar")
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    # ==========================================
    # FILA INFERIOR DINÁMICA: CON ALTA ACTIVIDAD Y RICA EN INFORMACIÓN
    # ==========================================
    col_spline, col_grouped = st.columns([1, 1])

    with col_spline:
        filtro_pilar_nom = "Consolidado IG" if sel_clave == 'I G' else sel_clave
        trend_df = df_ig[df_ig['clave'] == sel_clave].sort_values('mes_num')
        
        sel_row = trend_df[trend_df['mes'] == sel_mes]
        val_sel = float(sel_row['porcentaje'].iloc[0]) if not sel_row.empty else gauge_val
        delta_vs_meta = val_sel - 80.0
        delta_sign = "+" if delta_vs_meta >= 0 else ""

        st.markdown(f"""
            <div class="dash-card">
                <div class="section-header">Evolución Histórica Dinámica ({filtro_pilar_nom})</div>
                <div class="insight-pill">
                    💡 <b>Diagnóstico {sel_mes}:</b> Desempeño proactivo al <b>{val_sel:.1f}%</b> ({delta_sign}{delta_vs_meta:.1f}% vs Meta 80%).
                </div>
        """, unsafe_allow_html=True)

        if not trend_df.empty:
            min_v = float(trend_df['porcentaje'].min())
            max_v = float(trend_df['porcentaje'].max())
            y_lower = max(0.0, min_v - 4.0)
            y_upper = min(104.0, max_v + 3.5)

            marker_colors = ['#EF4444' if m == sel_mes else '#0E7490' for m in trend_df['mes']]
            marker_sizes = [12 if m == sel_mes else 7 for m in trend_df['mes']]

            custom_data = []
            for _, r in trend_df.iterrows():
                st_txt = "Cumple Meta (≥80%)" if r['porcentaje'] >= 80 else "Requiere Atención (<80%)"
                custom_data.append([st_txt, f"{r['porcentaje'] - 80:+.1f}% vs Meta 80%"])

            fig_spline = go.Figure()
            fig_spline.add_trace(go.Scatter(
                x=trend_df['mes'],
                y=trend_df['porcentaje'],
                mode='lines+markers+text',
                line=dict(color='#0E7490', width=3.5, shape='spline'),
                marker=dict(size=marker_sizes, color=marker_colors, line=dict(color='#FFFFFF', width=2)),
                text=[f"{v:.1f}%" for v in trend_df['porcentaje']],
                textposition='top center',
                textfont=dict(size=10, color='#0F766E', weight='bold'),
                fill='tozeroy',
                fillcolor='rgba(14, 116, 144, 0.08)',
                customdata=custom_data,
                hovertemplate=(
                    "<b>Mes: %{x}</b><br>" +
                    "📈 Desempeño: <b>%{y:.1f}%</b><br>" +
                    "🎯 Estado: <b>%{customdata[0]}</b><br>" +
                    "📊 Desviación: <b>%{customdata[1]}</b>" +
                    "<extra></extra>"
                )
            ))

            fig_spline.add_annotation(
                x=sel_mes,
                y=val_sel,
                text=f"<b>Corte {sel_mes}: {val_sel:.1f}%</b>",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="#EF4444",
                ax=0,
                ay=-36,
                bgcolor="#FFFFFF",
                bordercolor="#EF4444",
                borderwidth=1.5,
                borderpad=4,
                font=dict(size=10, color="#1F2937")
            )

            fig_spline.update_layout(
                height=265,
                margin=dict(l=10, r=10, t=15, b=10),
                yaxis=dict(range=[y_lower, y_upper], showgrid=True, gridcolor="#F3F4F6", ticksuffix="%"),
                xaxis=dict(showgrid=False),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Segoe UI, sans-serif', size=11, color='#4B5563')
            )
            st.plotly_chart(fig_spline, use_container_width=True, key="pro_spline")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_grouped:
        st.markdown(f"""
            <div class="dash-card">
                <div class="section-header">Actividades: Programadas vs. Realizadas ({filtro_pilar_nom})</div>
                <div class="section-sub">Volumen mensual reactivo al pilar proactivo</div>
        """, unsafe_allow_html=True)

        meses_group = [m for m in ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP'] if m in meses_disp]
        
        detalle_map = {
            'ART': ('ART', 'programados', 'realizados'),
            'OPAS': ('OPAS', 'programadas', 'realizadas'),
            'IDPS': ('IDPS', 'programados', 'realizados'),
            'IDS': ('IDS', 'detectadas', 'eliminadas'),
            'IENTS': ('IENTS', 'prog', 'capacitados'),
            'CAI': ('ICAI', 'propuestas', 'implementadas')
        }

        sheet_key, prog_key, ejec_key = detalle_map.get(sel_clave, ('IDPS', 'programados', 'realizados'))
        lbl_p = "Detectadas" if sel_clave == 'IDS' else ("Propuestas" if sel_clave == 'CAI' else "Programadas")
        lbl_e = "Eliminadas" if sel_clave == 'IDS' else ("Implementadas" if sel_clave == 'CAI' else "Realizadas")

        prog_series = []
        ejec_series = []
        for m in meses_group:
            p_val = detalles.get(sheet_key, {}).get(prog_key, {}).get(m, 6) if detalles else 6
            e_val = detalles.get(sheet_key, {}).get(ejec_key, {}).get(m, 6) if detalles else 6
            prog_series.append(p_val)
            ejec_series.append(e_val)

        fig_double = go.Figure()
        fig_double.add_trace(go.Bar(
            name=lbl_p,
            x=meses_group,
            y=prog_series,
            marker=dict(color='#A21CAF', cornerradius=3),
            text=[str(int(v)) for v in prog_series],
            textposition='outside'
        ))
        fig_double.add_trace(go.Bar(
            name=lbl_e,
            x=meses_group,
            y=ejec_series,
            marker=dict(color='#F59E0B', cornerradius=3),
            text=[str(int(v)) for v in ejec_series],
            textposition='outside'
        ))
        fig_double.update_layout(
            height=265,
            barmode='group',
            bargroupgap=0.1,
            bargap=0.35,
            margin=dict(l=10, r=10, t=25, b=10),
            yaxis=dict(range=[0, max(prog_series + ejec_series + [8]) + 2], showgrid=True, gridcolor="#F3F4F6"),
            xaxis=dict(showgrid=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
            font=dict(family='Segoe UI, sans-serif', size=11, color='#4B5563')
        )
        st.plotly_chart(fig_double, use_container_width=True, key="pro_double")
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    # SECCIÓN DE EXPORTACIÓN GERENCIAL AUTÓNOMA (PARA JEFES)
    kpis_export = [
        {'title': 'Condiciones Inseguras (IDS)', 'value': f"{ids_pct:.1f} %", 'icon': '🛡️', 'bg': '#DCFCE7', 'color': '#16A34A'},
        {'title': 'Charlas Prejornada (IDPS)', 'value': f"{idps_pct:.1f} %", 'icon': '📢', 'bg': '#FFEDD5', 'color': '#EA580C'},
        {'title': 'Personal Capacitado', 'value': f"{emp_cap}", 'icon': '👥', 'bg': '#FEE2E2', 'color': '#DC2626'},
        {'title': 'Análisis de Riesgo (ART)', 'value': f"{art_pct:.1f} %", 'icon': '📝', 'bg': '#E0F2FE', 'color': '#0284C7'},
        {'title': 'Permisos Trabajo (OSEA)', 'value': f"{osea_pct:.1f} %", 'icon': '📋', 'bg': '#F3E8FF', 'color': '#9333EA'},
        {'title': 'Acciones Incidentes (CAI)', 'value': f"{cai_pct:.1f} %", 'icon': '🎯', 'bg': '#FEF3C7', 'color': '#D97706'}
    ]
    insight_export = f"Diagnóstico {sel_mes}: Desempeño proactivo al {val_sel:.1f}% ({delta_sign}{delta_vs_meta:.1f}% vs Meta 80%)."

    html_export = generar_html_ejecutivo(
        titulo="Indicadores Proactivos HSE",
        subtitulo=f"Corte {sel_mes} • Enfoque: {filtro_pilar_nom}",
        kpis=kpis_export,
        fig_gauge=fig_gauge,
        fig_bar=fig_bar if 'fig_bar' in locals() else go.Figure(),
        fig_spline=fig_spline if 'fig_spline' in locals() else go.Figure(),
        fig_double=fig_double if 'fig_double' in locals() else go.Figure(),
        insight_txt=insight_export
    )

    c_exp_info, c_exp_btn = st.columns([2.5, 1.5])
    with c_exp_info:
        st.caption("💡 **Para Jefes / Directivos:** Descarga un archivo HTML 100% interactivo y ligero que se abre con doble clic en cualquier equipo sin necesitar Python ni servidores.")
    with c_exp_btn:
        st.download_button(
            label="📥 Descargar Reporte HTML (Para Jefes)",
            data=html_export,
            file_name=f"Reporte_HSE_Proactivos_{sel_mes}.html",
            mime="text/html",
            use_container_width=True,
            key="btn_dl_proactivos"
        )

    # COPYRIGHT FOOTER
    st.markdown("""
        <div style="text-align: center; color: #9CA3AF; font-size: 0.74rem; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #E5E7EB; letter-spacing: 0.3px;">
            © 2026 VOJ.DEV
        </div>
    """, unsafe_allow_html=True)
