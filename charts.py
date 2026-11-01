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


def chart_gauge(admitidos, no_admitidos, pct):
    if admitidos + no_admitidos == 0:
        fig = go.Figure(go.Indicator(
            mode="number", value=0,
            number={"suffix": "%", "font": {"color": AZUL}},
        ))
        fig.update_layout(height=300, margin=dict(t=10, b=10))
        return fig

    fig = go.Figure(go.Pie(
        values=[admitidos, no_admitidos],
        labels=["Admitidos", "No admitidos"],
        hole=0.7,
        marker_colors=[VERDE, ROJO],
        sort=False,
        direction="clockwise",
    ))
    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10), height=300,
        annotations=[dict(
            text=(f"{pct:.1f}%<br>"
                  f"<span style='font-size:11px;color:#6b7280'>admitidos</span>"),
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=22, color="#2044b8"),
        )],
        legend=dict(orientation="h", y=-0.1),
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
