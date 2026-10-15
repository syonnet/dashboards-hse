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
    data_by_year, err = load_data()
    if err or not data_by_year:
        st.error(f"⚠️ {err}")
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
                    HSE Desempeño Operativo
                </h3>
                <p style="font-size: 0.8rem; color: #6B7280; margin: 2px 0 0 0;">
                    Seguimiento dinámico gerencial de cumplimiento y accidentabilidad
                </p>
            </div>
        """, unsafe_allow_html=True)
    with col_h2:
        btn_col, txt_col = st.columns([1, 3])
        with btn_col:
            if st.button("🔄", key="ref_desempeno", help="Recargar datos de MATRIZ INDIC HSE.xlsx"):
                st.cache_data.clear()
                st.rerun()
        with txt_col:
            st.markdown(f"""
                <div style="font-size: 0.72rem; color: #6B7280; text-align: right; line-height: 1.2; padding-top: 5px;">
                    Data refreshed at<br><b>{dt_str}</b>
                </div>
            """, unsafe_allow_html=True)

    # BARRA DE FILTROS GERENCIALES
    anios_disp = sorted(list(data_by_year.keys()), reverse=True)
    
    with st.container(border=True):
        fc1, fc2, fc3, fc4 = st.columns([1, 1, 1.2, 1.6])
        with fc1:
            sel_anio = st.selectbox("📅 Año", anios_disp, index=0, key="des_anio")
            df_year = data_by_year.get(sel_anio, pd.DataFrame())

        meses_orden = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']
        meses_disp = [m for m in meses_orden if not df_year.empty and m in df_year['mes'].unique()]
        sel_mes_default = len(meses_disp) - 1 if meses_disp else 0

        with fc2:
            sel_mes = st.selectbox("🗓️ Mes de Corte", meses_disp, index=sel_mes_default, key="des_mes")

        bases_disp = ["Todas las Bases"] + sorted(list(df_year['base'].unique()))
        with fc3:
            sel_base = st.selectbox("📍 Base / Locación", bases_disp, index=0, key="des_base")

        subproc_disp = ["Todos los Subprocesos"] + sorted(list(df_year['subproceso'].unique()))
        with fc4:
            sel_subproc = st.selectbox("📑 Subproceso / Área", subproc_disp, index=0, key="des_subproc")

    # FILTRADO DINÁMICO EN CASCADA
    df_scope = df_year.copy()
    if sel_base != "Todas las Bases":
        df_scope = df_scope[df_scope['base'] == sel_base]
    if sel_subproc != "Todos los Subprocesos":
        df_scope = df_scope[df_scope['subproceso'] == sel_subproc]

    df_mes = df_scope[df_scope['mes'] == sel_mes]

    total_ind = len(df_mes)
    cumplen_n = len(df_mes[df_mes['cumple'] == True])
    no_cumplen_n = total_ind - cumplen_n
    pct_global = (cumplen_n / total_ind * 100.0) if total_ind > 0 else 0.0

    if_row = df_mes[df_mes['abreviatura'].str.upper() == 'IF'] if not df_mes.empty else pd.DataFrame()
    if_val = float(if_row['valor'].iloc[0]) if not if_row.empty else 0.0

    ig_row = df_mes[df_mes['abreviatura'].str.upper() == 'IG'] if not df_mes.empty else pd.DataFrame()
    ig_val = float(ig_row['valor'].iloc[0]) if not if_row.empty else 0.0

    mcv_row = df_mes[df_mes['abreviatura'].str.upper() == 'MCV'] if not df_mes.empty else pd.DataFrame()
    mcv_val = float(mcv_row['valor'].iloc[0]) if not mcv_row.empty else 0.0

    if not df_mes.empty:
        sub_top = df_mes.groupby('subproceso')['pct_cumplimiento'].mean().sort_values(ascending=False)
        sub_top_nombre = sub_top.index[0] if not sub_top.empty else "N/A"
        sub_top_nombre = sub_top_nombre.split('(')[0].replace('SEGURIDAD INDUSTRIAL', 'Seguridad').replace('SALUD OCUPACIONAL', 'Salud').strip()
        sub_top_val = sub_top.iloc[0] if not sub_top.empty else 0.0
    else:
        sub_top_nombre, sub_top_val = "N/A", 0.0

    # ==========================================
    # FILA SUPERIOR (ESTILO IMAGEN 1)
    # Sin contenedor exterior blanco vacío
    # ==========================================
    col_kpis, col_gauge, col_bar = st.columns([1.6, 1.4, 1.6])

    with col_kpis:
        # Fila 1 de mini-cards directas
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            st.markdown(f"""
                <div class="mini-card">
                    <div class="mini-icon" style="background: #E0F2FE; color: #0284C7;">📄</div>
                    <div>
                        <div class="mini-title">Índice Frecuencia (IF)</div>
                        <div class="mini-value">{if_val:.2f}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with r1_c2:
            st.markdown(f"""
                <div class="mini-card">
                    <div class="mini-icon" style="background: #FEF3C7; color: #D97706;">🛡️</div>
                    <div>
                        <div class="mini-title">Cumplimiento Global</div>
                        <div class="mini-value">{pct_global:.1f} %</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # Fila 2 de mini-cards
        r2_c1, r2_c2 = st.columns(2)
        with r2_c1:
            st.markdown(f"""
                <div class="mini-card">
                    <div class="mini-icon" style="background: #F3E8FF; color: #9333EA;">⚠️</div>
                    <div>
                        <div class="mini-title">Índice Gravedad (IG)</div>
                        <div class="mini-value">{ig_val:.2f}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with r2_c2:
            st.markdown(f"""
                <div class="mini-card">
                    <div class="mini-icon" style="background: #DCFCE7; color: #16A34A;">🎯</div>
                    <div>
                        <div class="mini-title">Metas Cumplidas</div>
                        <div class="mini-value">{cumplen_n} / {total_ind}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # Fila 3 de mini-cards
        r3_c1, r3_c2 = st.columns(2)
        with r3_c1:
            st.markdown(f"""
                <div class="mini-card">
                    <div class="mini-icon" style="background: #FFEDD5; color: #EA580C;">🚗</div>
                    <div>
                        <div class="mini-title">Incid. Vehiculares (MCV)</div>
                        <div class="mini-value">{mcv_val:.2f}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with r3_c2:
            st.markdown(f"""
                <div class="mini-card">
                    <div class="mini-icon" style="background: #F1F5F9; color: #334155;">⭐</div>
                    <div>
                        <div class="mini-title">Área Líder ({sub_top_nombre[:10]})</div>
                        <div class="mini-value">{sub_top_val:.0f} %</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with col_gauge:
        sub_title_gauge = f"{sel_base} • {sel_mes}" if sel_base != "Todas las Bases" else f"General • {sel_mes}"
        st.markdown(f"""
            <div class="dash-card">
                <div class="section-header">Cumplimiento HSE ({sub_title_gauge})</div>
                <div class="section-sub">Tasa consolidada según filtros activos</div>
        """, unsafe_allow_html=True)
        fig_gauge = render_gauge(pct_global)
        st.plotly_chart(fig_gauge, use_container_width=True, key="des_gauge")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_bar:
        if sel_base == "Todas las Bases":
            card_title = f"Cumplimiento por Base ({sel_mes})"
            card_sub = "% de metas cumplidas por cada base operativa"
            group_col = 'base'
        else:
            card_title = f"Desglose por Subproceso ({sel_base} • {sel_mes})"
            card_sub = "% de cumplimiento por departamento"
            group_col = 'subproceso'

        st.markdown(f"""
            <div class="dash-card">
                <div class="section-header">{card_title}</div>
                <div class="section-sub">{card_sub}</div>
        """, unsafe_allow_html=True)

        if not df_mes.empty:
            bar_df = df_mes.groupby(group_col)['pct_cumplimiento'].mean().reset_index().sort_values('pct_cumplimiento', ascending=False)
            bar_x = [str(x)[:12] for x in bar_df[group_col]]
            
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                x=bar_x,
                y=bar_df['pct_cumplimiento'],
                marker=dict(color='#312E81', cornerradius=4),
                text=[f"{v:.0f}%" for v in bar_df['pct_cumplimiento']],
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
            st.plotly_chart(fig_bar, use_container_width=True, key="des_bar")
        else:
            st.info("Sin registros para los filtros seleccionados.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    # ==========================================
    # FILA INFERIOR DINÁMICA: CON ALTA ACTIVIDAD Y RICA EN INFORMACIÓN
    # ==========================================
    col_spline, col_grouped = st.columns([1, 1])

    with col_spline:
        filtro_txt = []
        if sel_base != "Todas las Bases":
            filtro_txt.append(sel_base)
        if sel_subproc != "Todos los Subprocesos":
            filtro_txt.append(sel_subproc[:15])
        scope_lbl = " • ".join(filtro_txt) if filtro_txt else "General Corporativo"

        # Calcular serie de tendencia
        trend_df = df_scope.groupby(['mes_num', 'mes'])['pct_cumplimiento'].mean().reset_index().sort_values('mes_num')

        # Buscar datos del mes seleccionado para el insight gerencial
        sel_row = trend_df[trend_df['mes'] == sel_mes]
        val_sel = float(sel_row['pct_cumplimiento'].iloc[0]) if not sel_row.empty else pct_global
        delta_vs_meta = val_sel - 80.0
        delta_sign = "+" if delta_vs_meta >= 0 else ""

        st.markdown(f"""
            <div class="dash-card">
                <div class="section-header">Evolución Histórica Dinámica ({scope_lbl})</div>
                <div class="insight-pill">
                    💡 <b>Diagnóstico {sel_mes}:</b> Desempeño al <b>{val_sel:.1f}%</b> ({delta_sign}{delta_vs_meta:.1f}% vs Meta 80%). <b>{cumplen_n}</b> metas alcanzadas de <b>{total_ind}</b>.
                </div>
        """, unsafe_allow_html=True)

        if not trend_df.empty:
            # Escala dinámica sensible para darle dinamismo y "actividad" a la curva
            min_v = float(trend_df['pct_cumplimiento'].min())
            max_v = float(trend_df['pct_cumplimiento'].max())
            # Holgura de 3% a 4% para que los valles y picos se aprecien claramente
            y_lower = max(0.0, min_v - 4.0)
            y_upper = min(104.0, max_v + 3.5)

            marker_colors = ['#EF4444' if m == sel_mes else '#0E7490' for m in trend_df['mes']]
            marker_sizes = [12 if m == sel_mes else 7 for m in trend_df['mes']]

            # Preparar textos de tooltip detallado
            custom_data = []
            for _, r in trend_df.iterrows():
                m_sub = df_scope[df_scope['mes'] == r['mes']]
                c_ok = len(m_sub[m_sub['cumple'] == True])
                tot = len(m_sub)
                st_txt = "Cumple Meta (≥80%)" if r['pct_cumplimiento'] >= 80 else "Requiere Atención (<80%)"
                custom_data.append([st_txt, f"{c_ok} de {tot} metas", f"{r['pct_cumplimiento'] - 80:+.1f}% vs 80%"])

            fig_spline = go.Figure()

            # Área sombreada bajo la curva
            fig_spline.add_trace(go.Scatter(
                x=trend_df['mes'],
                y=trend_df['pct_cumplimiento'],
                mode='lines+markers+text',
                line=dict(color='#0E7490', width=3.5, shape='spline'),
                marker=dict(size=marker_sizes, color=marker_colors, line=dict(color='#FFFFFF', width=2)),
                text=[f"{v:.1f}%" for v in trend_df['pct_cumplimiento']],
                textposition='top center',
                textfont=dict(size=10, color='#0F766E', weight='bold'),
                fill='tozeroy',
                fillcolor='rgba(14, 116, 144, 0.08)',
                customdata=custom_data,
                hovertemplate=(
                    "<b>Mes: %{x}</b><br>" +
                    "📈 Cumplimiento: <b>%{y:.1f}%</b><br>" +
                    "🎯 Estado: <b>%{customdata[0]}</b><br>" +
                    "📋 Indicadores: <b>%{customdata[1]}</b><br>" +
                    "📊 Desviación: <b>%{customdata[2]}</b>" +
                    "<extra></extra>"
                )
            ))

            # Anotación destacada en el mes seleccionado
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
            st.plotly_chart(fig_spline, use_container_width=True, key="des_spline")
        else:
            st.info("Sin datos para graficar la evolución.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_grouped:
        st.markdown(f"""
            <div class="dash-card">
                <div class="section-header">Metas Cumplidas vs. Desviaciones ({scope_lbl})</div>
                <div class="section-sub">Volumen mensual de indicadores en meta vs alertas</div>
        """, unsafe_allow_html=True)

        mes_stats = []
        for m in meses_disp:
            sub_m = df_scope[df_scope['mes'] == m]
            c_ok = len(sub_m[sub_m['cumple'] == True])
            c_no = len(sub_m[sub_m['cumple'] == False])
            mes_stats.append({'mes': m, 'cumplen': c_ok, 'desviaciones': c_no})
        df_stats = pd.DataFrame(mes_stats)

        if not df_stats.empty and (df_stats['cumplen'].sum() > 0 or df_stats['desviaciones'].sum() > 0):
            fig_double = go.Figure()
            fig_double.add_trace(go.Bar(
                name='En Meta',
                x=df_stats['mes'],
                y=df_stats['cumplen'],
                marker=dict(color='#A21CAF', cornerradius=3),
                text=df_stats['cumplen'],
                textposition='outside'
            ))
            fig_double.add_trace(go.Bar(
                name='Requiere Acción',
                x=df_stats['mes'],
                y=df_stats['desviaciones'],
                marker=dict(color='#F59E0B', cornerradius=3),
                text=df_stats['desviaciones'],
                textposition='outside'
            ))
            fig_double.update_layout(
                height=265,
                barmode='group',
                bargroupgap=0.1,
                bargap=0.35,
                margin=dict(l=10, r=10, t=25, b=10),
                yaxis=dict(range=[0, max(df_stats['cumplen'].tolist() + [10]) + 8], showgrid=True, gridcolor="#F3F4F6"),
                xaxis=dict(showgrid=False),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
                font=dict(family='Segoe UI, sans-serif', size=11, color='#4B5563')
            )
            st.plotly_chart(fig_double, use_container_width=True, key="des_double")
        else:
            st.info("Sin datos para comparar cumplimiento mensual.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    # SECCIÓN DE EXPORTACIÓN GERENCIAL AUTÓNOMA (PARA JEFES)
    kpis_export = [
        {'title': 'Índice Frecuencia (IF)', 'value': f"{if_val:.2f}", 'icon': '📄', 'bg': '#E0F2FE', 'color': '#0284C7'},
        {'title': 'Cumplimiento Global', 'value': f"{pct_global:.1f} %", 'icon': '🛡️', 'bg': '#FEF3C7', 'color': '#D97706'},
        {'title': 'Índice Gravedad (IG)', 'value': f"{ig_val:.2f}", 'icon': '⚠️', 'bg': '#F3E8FF', 'color': '#9333EA'},
        {'title': 'Metas Cumplidas', 'value': f"{cumplen_n} / {total_ind}", 'icon': '🎯', 'bg': '#DCFCE7', 'color': '#16A34A'},
        {'title': 'Incid. Vehiculares (MCV)', 'value': f"{mcv_val:.2f}", 'icon': '🚗', 'bg': '#FFEDD5', 'color': '#EA580C'},
        {'title': f'Área Líder ({sub_top_nombre[:10]})', 'value': f"{sub_top_val:.0f} %", 'icon': '⭐', 'bg': '#F1F5F9', 'color': '#334155'}
    ]
    insight_export = f"Diagnóstico {sel_mes}: Desempeño al {val_sel:.1f}% ({delta_sign}{delta_vs_meta:.1f}% vs Meta 80%). {cumplen_n} metas alcanzadas de {total_ind}."

    html_export = generar_html_ejecutivo(
        titulo="HSE Desempeño Operativo",
        subtitulo=f"Corte {sel_mes} {sel_anio} • {scope_lbl}",
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
            file_name=f"Reporte_HSE_Desempeno_{sel_mes}_{sel_anio}.html",
            mime="text/html",
            use_container_width=True,
            key="btn_dl_desempeno"
        )

    # COPYRIGHT FOOTER
    st.markdown("""
        <div style="text-align: center; color: #9CA3AF; font-size: 0.74rem; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #E5E7EB; letter-spacing: 0.3px;">
            © 2026 VOJ.DEV
        </div>
    """, unsafe_allow_html=True)
