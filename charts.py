"""Gráficos Plotly del dashboard."""

import plotly.express as px
import plotly.graph_objects as go

VERDE = "#16a34a"
ROJO  = "#dc2626"
AZUL  = "#2f5bea"


def chart_estado(df_estado):
    colors = [VERDE if e == "Admitido" else ROJO if e == "No admitido" else AZUL
              for e in df_estado["estado"]]
    fig = go.Figure(go.Pie(
        labels=df_estado["estado"],
        values=df_estado["count"],
        hole=0.55,
        marker_colors=colors,
    ))
    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        height=300,
        legend=dict(orientation="h", y=-0.1),
    )
    return fig


def chart_funnel(admitidos, no_admitidos):
    total = admitidos + no_admitidos
    if total == 0:
        fig = go.Figure()
        fig.update_layout(height=300, margin=dict(t=10, b=10))
        return fig

    fig = go.Figure(go.Funnel(
        y=["Total", "Admitidos", "No admitidos"],
        x=[total, admitidos, no_admitidos],
        textinfo="value+percent initial",
        textfont=dict(size=13, color="white"),
        marker=dict(color=[AZUL, VERDE, ROJO]),
        connector={"line": {"color": "#cbd5e1", "width": 1}},
    ))
    fig.update_layout(
        height=300,
        margin=dict(t=10, b=10, l=10, r=10),
        showlegend=False,
        funnelgap=0.02,
    )
    return fig
    
def chart_convocatoria(df_conv):
    fig = px.bar(df_conv, x="convocatoria", y="total", text="total",
                 color_discrete_sequence=[AZUL])
    fig.update_layout(
        height=320, margin=dict(t=10, b=10),
        xaxis_title=None, yaxis_title=None, showlegend=False,
    )
    return fig


def chart_causal(df_causal):
    df = df_causal.sort_values("count", ascending=True)
    fig = px.bar(df, x="count", y="categoria", orientation="h", text="count",
                 color_discrete_sequence=[ROJO])
    fig.update_layout(
        height=320, margin=dict(t=10, b=10),
        xaxis_title=None, yaxis_title=None, showlegend=False,
    )
    return fig
