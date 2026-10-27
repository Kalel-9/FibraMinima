"""Desenho simples do grafo, com distâncias em metros."""

import plotly.graph_objects as go
from graph import Edge, Vertex


def money(value: float) -> str:
    return "R$ " + f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def draw_graph(vertices: list[Vertex], edges: list[Edge], selected: set[tuple[str, str]],
               directed: bool = False) -> go.Figure:
    points = {v.id: v for v in vertices}
    fig = go.Figure()
    arcs = {(e.source, e.target) for e in edges}
    for edge in edges:
        a, b = points[edge.source], points[edge.target]
        chosen = ((edge.source, edge.target) if directed else edge.key) in selected
        color = "#0d9488" if chosen else "#94a3b8"
        # Se houver arcos opostos, desenha-os separados para distinguir sentidos.
        dx, dy = b.x - a.x, b.y - a.y
        length = (dx * dx + dy * dy) ** 0.5
        offset = 0.14 if directed and (edge.target, edge.source) in arcs else 0
        ox, oy = -dy / length * offset, dx / length * offset
        ax, ay, bx, by = a.x + ox, a.y + oy, b.x + ox, b.y + oy
        symbol = "→" if directed else "↔"
        fig.add_trace(go.Scatter(
            x=[ax, bx], y=[ay, by], mode="lines",
            line=dict(color=color, width=5 if chosen else 2),
            hovertemplate=f"{edge.source} {symbol} {edge.target}: {edge.weight:g} m<extra></extra>",
            showlegend=False,
        ))
        fig.add_annotation(
            x=(ax + bx) / 2, y=(ay + by) / 2,
            text=f"{edge.weight:g} m", showarrow=False,
            bgcolor="#f8fafc", borderpad=3, font=dict(size=12, color="#334155"),
        )
        if directed:
            fig.add_annotation(
                x=ax + dx * 0.80, y=ay + dy * 0.80,
                ax=ax + dx * 0.60, ay=ay + dy * 0.60,
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=3, arrowsize=1.4,
                arrowwidth=3 if chosen else 2, arrowcolor=color, text="",
            )
    fig.add_trace(go.Scatter(
        x=[v.x for v in vertices], y=[v.y for v in vertices],
        mode="markers+text", text=[v.id for v in vertices], textposition="top center",
        textfont=dict(size=16, color="#132c3e"),
        marker=dict(size=25, color="#132c3e", line=dict(color="white", width=2)),
        hoverinfo="text", showlegend=False,
    ))
    fig.update_layout(
        height=440, margin=dict(l=25, r=25, t=35, b=20),
        paper_bgcolor="#f8fafc", plot_bgcolor="#f8fafc",
        xaxis=dict(visible=False, range=[-0.7, 6.7]),
        yaxis=dict(visible=False, range=[-0.1, 4.7]),
    )
    return fig
