"""Desenho dos projetos de rede para apresentação em sala."""

import plotly.graph_objects as go
from graph import Edge, Vertex


def money(value: float) -> str:
    return "R$ " + f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def draw_graph(vertices: list[Vertex], edges: list[Edge], selected: set[tuple[str, str]],
               directed: bool = False, failed: tuple[str, str] | None = None,
               offline: set[str] | None = None, route: set[tuple[str, str]] | None = None,
               show_available: bool = True, height: int = 520,
               dashed_available: bool = False, show_all_weights: bool = False,
               available_label: str = "Não instalado", failed_installed: bool = False) -> go.Figure:
    points = {v.id: v for v in vertices}
    building = len({v.x for v in vertices}) == 1
    fig = go.Figure()
    arcs = {(e.source, e.target) for e in edges}
    # O caminho ativo é desenhado por cima das demais linhas.
    def priority(edge):
        key = (edge.source, edge.target) if directed else edge.key
        return (key in selected, key in (route or ()), key == failed)

    for edge in sorted(edges, key=priority):
        a, b = points[edge.source], points[edge.target]
        key = (edge.source, edge.target) if directed else edge.key
        chosen = key in selected
        broken = key == failed and (chosen or failed_installed)
        if not chosen and not show_available and not broken:
            continue
        active = chosen and key in (route or ())
        color = "#dc2626" if broken else "#2563eb" if active else "#0d9488" if chosen else "#d4dee6"
        dx, dy = b.x - a.x, b.y - a.y
        length = (dx * dx + dy * dy) ** 0.5
        offset = .20 if directed and (edge.target, edge.source) in arcs else 0
        ox, oy = -dy / length * offset, dx / length * offset
        ax, ay, bx, by = a.x + ox, a.y + oy, b.x + ox, b.y + oy
        symbol = "→" if directed else "↔"
        bend = ((.85 + abs(dy) * .68) * (1 if edge.source == "Rack" else -1)
                if building and abs(dy) > 1 else 0)
        ts = [i / 30 for i in range(31)] if bend else [0, 1]
        state = "Cabo rompido" if broken else "Caminho ativo" if active else "Instalado" if chosen else available_label
        fig.add_trace(go.Scatter(
            x=[ax + dx * t + 4 * bend * t * (1 - t) for t in ts],
            y=[ay + dy * t for t in ts], mode="lines",
            line=dict(color=color, width=6 if active else 4 if chosen or broken else 1.5,
                      dash="dash" if broken or (not chosen and dashed_available) else "solid"),
            hovertemplate=f"<b>{edge.source} {symbol} {edge.target}</b><br>{edge.weight:g} m · {state}<extra></extra>",
            showlegend=False,
        ))
        # Os valores das alternativas ficam apenas no hover para reduzir ruído.
        if chosen or broken or not selected or show_all_weights:
            fig.add_annotation(
                x=(ax + bx) / 2 + bend + (.5 if building and not bend else 0),
                y=(ay + by) / 2,
                text=f"{edge.weight:g} m", showarrow=False, bgcolor="#ffffff",
                bordercolor="#e1e8ee", borderwidth=1, borderpad=4,
                font=dict(size=14, color="#334155"),
            )
        if directed:
            fig.add_annotation(
                x=ax + dx * .80, y=ay + dy * .80,
                ax=ax + dx * .60, ay=ay + dy * .60,
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=3, arrowsize=1.3,
                arrowwidth=3 if chosen else 1.5, arrowcolor=color, text="",
            )
    if building:
        for vertex in vertices:
            fig.add_shape(type="rect", x0=-2.5, x1=8.3, y0=vertex.y - .43, y1=vertex.y + .43,
                          fillcolor="#f3f6f9" if vertex.y % 2 else "#f9fbfc",
                          line_width=0, layer="below")
    fig.add_trace(go.Scatter(
        x=[v.x for v in vertices], y=[v.y for v in vertices], mode="markers+text",
        text=[v.id for v in vertices],
        textposition="middle left" if building else "top center",
        textfont=dict(size=18, color="#102b3f", family="Arial"),
        marker=dict(size=[34 if v.id in ("Rack", "R") else 29 for v in vertices],
                    symbol=["square" if v.id in ("Rack", "R") else "circle" for v in vertices],
                    color=["#b45309" if v.id in (offline or ()) else "#102b3f" if v.id in ("Rack", "R") else "#0d9488"
                           for v in vertices], line=dict(color="white", width=3)),
        hovertext=[f"{v.id} · " + ("Sem acesso ao rack" if v.id in (offline or ()) else "Conectado")
                   for v in vertices],
        hoverinfo="text", showlegend=False,
    ))
    fig.update_layout(
        height=height, margin=dict(l=35, r=35, t=35, b=25),
        paper_bgcolor="white", plot_bgcolor="white",
        xaxis=dict(visible=False, range=[-2.5, 8.3] if building else [-.9, 7.1], fixedrange=True),
        yaxis=dict(visible=False, range=[-.6, max(v.y for v in vertices) + .75], fixedrange=True),
        hoverlabel=dict(bgcolor="#102b3f", font_color="white", font_size=14),
        font=dict(family="Arial", color="#102b3f"),
    )
    return fig


def comparison_chart(plans, names, price, selected):
    """Custo das opções; a cor destaca o projeto que está em simulação."""
    plans = sorted(plans, key=lambda p: (p.meters, p.worst_loss))
    fig = go.Figure(go.Bar(
        x=[p.meters * price for p in plans], y=[names[p] for p in plans], orientation="h",
        marker_color=["#0d9488" if p == selected else "#d4e0e8" for p in plans],
        text=[money(p.meters * price) for p in plans], textposition="outside", cliponaxis=False,
        customdata=[[p.worst_loss, p.meters] for p in plans],
        hovertemplate="%{y}<br>%{text}<br>%{customdata[1]} m de cabo<br>Pior falha: %{customdata[0]} pontos sem acesso<extra></extra>",
    ))
    fig.update_layout(
        height=max(280, len(plans) * 40), margin=dict(l=10, r=100, t=10, b=20),
        paper_bgcolor="white", plot_bgcolor="white", font=dict(color="#102b3f", size=14),
        xaxis=dict(visible=False, range=[0, max(p.meters * price for p in plans) * 1.22], fixedrange=True),
        yaxis=dict(autorange="reversed", fixedrange=True), bargap=.35,
    )
    return fig
