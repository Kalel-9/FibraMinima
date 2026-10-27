"""Desenho simples do grafo, com distâncias em metros."""

import plotly.graph_objects as go
from graph import Edge, Vertex


def money(value: float) -> str:
    return "R$ " + f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def draw_graph(vertices: list[Vertex], edges: list[Edge], selected: set[tuple[str, str]]) -> go.Figure:
    points = {v.id: v for v in vertices}
    fig = go.Figure()
    for edge in edges:
        a, b = points[edge.source], points[edge.target]
        chosen = edge.key in selected
        fig.add_trace(go.Scatter(
            x=[a.x, b.x], y=[a.y, b.y], mode="lines",
            line=dict(color="#0d9488" if chosen else "#94a3b8", width=5 if chosen else 2),
            hovertemplate=f"{edge.source} ↔ {edge.target}: {edge.weight:g} m<extra></extra>",
            showlegend=False,
        ))
        fig.add_annotation(
            x=(a.x + b.x) / 2, y=(a.y + b.y) / 2,
            text=f"{edge.weight:g} m", showarrow=False,
            bgcolor="#f8fafc", borderpad=3, font=dict(size=12, color="#334155"),
        )
    fig.add_trace(go.Scatter(
        x=[v.x for v in vertices], y=[v.y for v in vertices],
        mode="markers+text", text=[v.id for v in vertices], textposition="top center",
        textfont=dict(size=16, color="#132c3e"),
        marker=dict(size=25, color="#132c3e", line=dict(color="white", width=2)),
        hoverinfo="text", showlegend=False,
    ))
    fig.update_layout(
        height=360, margin=dict(l=25, r=25, t=35, b=20),
        paper_bgcolor="#f8fafc", plot_bgcolor="#f8fafc",
        xaxis=dict(visible=False, range=[-0.7, 6.7]),
        yaxis=dict(visible=False, range=[-0.1, 4.1]),
    )
    return fig
