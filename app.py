"""Dashboard Aspirantes · Procuraduría 2026."""

import streamlit as st

from datos import cargar_datos
from charts import (
    chart_estado, chart_gauge, chart_convocatoria, chart_causal,
)

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Aspirantes · Procuraduría 2026",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
.block-container { padding-top: 1.5rem; }
.kpi-card {
    background: #fff; border: 1px solid #e5e8ef; border-radius: 12px;
    padding: 16px; box-shadow: 0 2px 8px rgba(20,30,60,.06);
}
.kpi-label { font-size: 12px; color: #6b7280; text-transform: uppercase;
             letter-spacing: .4px; font-weight: 600; }
.kpi-value { font-size: 28px; font-weight: 700; margin-top: 6px; }
.kpi-total .kpi-value { color: #2f5bea; }
.kpi-ok .kpi-value    { color: #16a34a; }
.kpi-no .kpi-value    { color: #dc2626; }
.kpi-pct .kpi-value   { color: #2044b8; }
.disclaimer {
    background: #fffbeb; border: 1px solid #fde68a; border-left: 4px solid #f59e0b;
    border-radius: 8px; padding: 12px 16px; font-size: 12.5px;
    color: #78350f; line-height: 1.55;
}
.disclaimer a { color: #b45309; font-weight: 600; }
.ficha-badge {
    display: inline-block; padding: 12px 18px; border-radius: 12px;
    font-size: 20px; font-weight: 800; margin-bottom: 18px;
}
.ficha-ok  { background: #dcfce7; color: #166534; }
.ficha-no  { background: #fee2e2; color: #991b1b; }
.chip {
    background: #eef2ff; color: #2044b8; padding: 4px 9px;
    border-radius: 99px; font-size: 12px; font-weight: 600;
    display: inline-block; margin: 2px 4px 2px 0;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# CARGA
# ------------------------------------------------------------
df, actualizado = cargar_datos()

if df.empty:
    st.error("No se encontró `datos.parquet`. Genera el archivo con "
             "`python convertir.py` y vuelve a cargar la app.")
    st.stop()

# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
with st.sidebar:
    st.markdown("### 📊 Dashboard Aspirantes")
    st.caption("Procuraduría · Convocatoria 2026")

    st.markdown("#### 🔍 Buscar aspirante")
    with st.form("form_buscar"):
        registro_input = st.text_input(
            "N° de Registro", placeholder="Ej: 100230",
            label_visibility="collapsed",
        )
        buscar = st.form_submit_button(
            "Buscar aspirante", use_container_width=True,
        )

    st.markdown("#### Filtros globales")
    conv_sel = st.multiselect(
        "Convocatoria",
        sorted(df["convocatoria"].dropna().unique().tolist()),
    )
    estado_sel = st.multiselect(
        "Estado",
        [e for e in ["Admitido", "No admitido"] if e in df["estado"].unique()],
    )
    limpiar = st.button("Limpiar todo", use_container_width=True)

    st.markdown("#### Información")
    st.caption(f"Total en BD: **{len(df):,}**")
    if actualizado:
        st.caption(f"Snapshot: **{actualizado[:16].replace('T', ' ')}**")
    st.caption("Datos de referencia · no oficiales.")

if limpiar:
    st.rerun()

# ------------------------------------------------------------
# AVISO LEGAL
# ------------------------------------------------------------
st.markdown("""
<div class="disclaimer">
<b>⚠️ Aviso importante</b><br>
Esta herramienta es de carácter <b>informativo y no oficial</b>. No sustituye la
información publicada por la Procuraduría General de la Nación. Para verificar datos,
presentar reclamaciones o realizar trámites, consulte los canales oficiales:
<a href="https://meritoconstruyendoexcelencia.com.co" target="_blank">meritoconstruyendoexcelencia.com.co</a> y
<a href="https://www.procuraduria.gov.co" target="_blank">www.procuraduria.gov.co</a>.<br>
<span style="font-size:11.5px;opacity:.85;">Fundamento: Ley 1712 de 2014 (Transparencia)
y Ley 2016 de 2020 (Código de Integridad del Servicio Público).</span>
</div>
""", unsafe_allow_html=True)
st.write("")

# ------------------------------------------------------------
# VISTA INDIVIDUAL
# ------------------------------------------------------------
if buscar and registro_input.strip():
    reg = registro_input.strip()
    match = df[df["registro"] == reg]

    st.subheader("Ficha del aspirante")

    if match.empty:
        st.error(f"No se encontró el registro **{reg}**.")
    else:
        a = match.iloc[0]
        es_admitido = a["estado"] == "Admitido"
        clase = "ficha-ok" if es_admitido else "ficha-no"
        icono = "✅" if es_admitido else "❌"

        st.markdown(
            f"<div class='ficha-badge {clase}'>{icono} {a['estado']}</div>",
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        c1.metric("N° Registro", a["registro"])
        c2.metric("Convocatoria", a["convocatoria"] or "—")

        st.markdown("**Causal de inadmisión**")
        st.info(a["causalTexto"] or "Sin causal registrada.")

        if a["categorias"]:
            chips = "".join(
                f"<span class='chip'>{c}</span>" for c in a["categorias"]
            )
            st.markdown(chips, unsafe_allow_html=True)

    st.stop()

# ------------------------------------------------------------
# VISTA GLOBAL
# ------------------------------------------------------------
filtrado = df.copy()
if conv_sel:
    filtrado = filtrado[filtrado["convocatoria"].isin(conv_sel)]
if estado_sel:
    filtrado = filtrado[filtrado["estado"].isin(estado_sel)]

st.subheader("Consulta de resultados")
st.caption("Aspirantes 2026 · Procuraduría General de la Nación")

if filtrado.empty:
    st.warning("No hay datos con los filtros seleccionados.")
    st.stop()

total = len(filtrado)
admitidos = int((filtrado["estado"] == "Admitido").sum())
no_admitidos = int((filtrado["estado"] == "No admitido").sum())
pct = round(admitidos / total * 100, 1) if total else 0.0

# ---------- KPIs ----------
c1, c2, c3, c4 = st.columns(4)
for col, cls, label, value in [
    (c1, "kpi-total", "Total aspirantes", f"{total:,}"),
    (c2, "kpi-ok",    "Admitidos",        f"{admitidos:,}"),
    (c3, "kpi-no",    "No admitidos",     f"{no_admitidos:,}"),
    (c4, "kpi-pct",   "% Admitidos",      f"{pct:.1f}%"),
]:
    col.markdown(
        f"<div class='kpi-card {cls}'>"
        f"<div class='kpi-label'>{label}</div>"
        f"<div class='kpi-value'>{value}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.write("")

# ---------- Gráficos ----------
g1, g2 = st.columns(2)
with g1:
    st.markdown("#### Distribución por Estado")
    por_estado = (
        filtrado["estado"].value_counts()
        .rename_axis("estado").reset_index(name="count")
    )
    st.plotly_chart(chart_estado(por_estado), use_container_width=True)

with g2:
    st.markdown("#### % Admitidos vs No admitidos")
    st.plotly_chart(
        chart_gauge(admitidos, no_admitidos, pct),
        use_container_width=True,
    )

st.markdown("#### Registros por Convocatoria")
por_conv = (
    filtrado.groupby("convocatoria", observed=True).size()
    .reset_index(name="total").sort_values("convocatoria")
)
st.plotly_chart(chart_convocatoria(por_conv), use_container_width=True)

st.markdown("#### Causales de inadmisión (Top 10 · menciones)")
no_adm = filtrado[filtrado["estado"] == "No admitido"]
if no_adm.empty:
    st.info("No hay no admitidos en la selección.")
else:
    explotado = no_adm.explode("categorias")
    por_causal = (
        explotado["categorias"].value_counts()
        .head(10).rename_axis("categoria").reset_index(name="count")
    )
    st.plotly_chart(chart_causal(por_causal), use_container_width=True)

# ---------- Tabla y export ----------
st.markdown("#### Detalle")
tabla = (
    filtrado[["registro", "convocatoria", "estado", "causalTexto"]]
    .rename(columns={"registro": "N° Registro", "causalTexto": "Causal"})
)
st.dataframe(tabla, use_container_width=True, hide_index=True)

st.download_button(
    "📥 Exportar CSV",
    data=tabla.to_csv(index=False).encode("utf-8-sig"),
    file_name="aspirantes_filtrados.csv",
    mime="text/csv",
)
