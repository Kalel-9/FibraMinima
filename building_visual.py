"""Grafo organizado por andar, com racks internos e duas prumadas."""

import plotly.graph_objects as go

from graph import Edge, Vertex
from scenarios import BuildingScenario


def _add_floor_bands(
    figure: go.Figure, scenario: BuildingScenario, points: dict[str, Vertex],
) -> None:
    for floor in scenario.floors:
        y = points[floor.racks[0]].y
        internal = sum(
            edge.source in floor.racks and edge.target in floor.racks
            for edge in scenario.edges
        )
        cable_label = (
            "1 trecho interno<br>(aresta)"
            if internal == 1
            else f"{internal} trechos internos<br>(arestas)"
        )
        figure.add_shape(
            type="rect", x0=-0.2, x1=11.5, y0=y - 0.95, y1=y + 0.95,
            fillcolor="#f0f5f9" if floor.level % 2 else "#f9fbfd",
            line=dict(color="#e2eaf0", width=1), layer="below",
        )
        figure.add_annotation(
            x=0, y=y, xanchor="left", showarrow=False,
            text=f"<b>{floor.level}º ANDAR</b><br>{len(floor.racks)} racks (vértices)<br>{cable_label}",
            align="left", font=dict(size=14, color="#526777"),
        )


def _add_cables(
    figure: go.Figure,
    scenario: BuildingScenario,
    points: dict[str, Vertex],
    selected: set[tuple[str, str]],
    route: set[tuple[str, str]],
    failed: Edge | None,
) -> None:
    def priority(edge: Edge) -> tuple[bool, bool, bool]:
        return edge.key in selected, edge.key in route, edge == failed

    for edge in sorted(scenario.edges, key=priority):
        source, target = points[edge.source], points[edge.target]
        chosen = edge.key in selected
        broken = edge == failed
        in_route = edge.key in route
        if broken:
            color = "#dc2626"
        elif in_route:
            color = "#2563eb"
        elif chosen:
            color = "#0d9488"
        else:
            color = "#acbccb"

        # O fechamento de cada anel passa por baixo dos demais trechos do andar.
        same_floor = source.y == target.y
        closes_ring = (
            same_floor
            and abs(target.x - source.x) > 6
            and sum(vertex.y == source.y for vertex in scenario.vertices) > 2
        )
        bend = -0.65 if closes_ring else 0
        times = [index / 30 for index in range(31)] if bend else [0, 1]
        status = "Cabo rompido" if broken else "Em uso" if chosen else "Reserva instalada"

        figure.add_trace(go.Scatter(
            x=[source.x + (target.x - source.x) * time for time in times],
            y=[
                source.y + (target.y - source.y) * time + 4 * bend * time * (1 - time)
                for time in times
            ],
            mode="lines",
            line=dict(
                color=color,
                width=6 if in_route else 4 if chosen or broken else 2,
                dash="dash" if broken or not chosen else "solid",
            ),
            hovertemplate=(
                f"<b>Rack {edge.source} ↔ Rack {edge.target}</b>"
                f"<br>{edge.weight:g} m · {status}<extra></extra>"
            ),
            showlegend=False,
        ))
        if chosen or broken:
            figure.add_annotation(
                x=(source.x + target.x) / 2 + (0 if same_floor else -0.48 if source.x == 2 else 0.48),
                y=(source.y + target.y) / 2 + bend + (0.23 if same_floor and not bend else 0),
                text=f"{edge.weight:g} m", showarrow=False, bgcolor="white",
                bordercolor="#dce5ec", borderwidth=1, borderpad=3,
                font=dict(size=13, color="#334155"),
            )


def _add_racks(
    figure: go.Figure, scenario: BuildingScenario, offline: frozenset[str],
) -> None:
    figure.add_trace(go.Scatter(
        x=[vertex.x for vertex in scenario.vertices],
        y=[vertex.y for vertex in scenario.vertices],
        mode="markers+text",
        text=[vertex.id for vertex in scenario.vertices],
        textposition="top center",
        textfont=dict(size=17, color="#102b3f"),
        marker=dict(
            size=[33 if vertex.id == scenario.root else 27 for vertex in scenario.vertices],
            symbol=["square" if vertex.id == scenario.root else "circle" for vertex in scenario.vertices],
            color=[
                "#b45309" if vertex.id in offline else "#102b3f" if vertex.id == scenario.root else "#0d9488"
                for vertex in scenario.vertices
            ],
            line=dict(color="white", width=3),
        ),
        hovertext=[
            f"Rack {vertex.id}"
            + (" · Principal" if vertex.id == scenario.root else "")
            + (" · Sem acesso" if vertex.id in offline else " · Conectado")
            for vertex in scenario.vertices
        ],
        hoverinfo="text", showlegend=False,
    ))


def draw_building(
    scenario: BuildingScenario,
    active: tuple[Edge, ...],
    route: set[tuple[str, str]],
    failed: Edge | None = None,
    offline: frozenset[str] = frozenset(),
    height: int = 630,
) -> go.Figure:
    """Desenha andares, cabos e racks, preservando a ordem das camadas."""
    points = {vertex.id: vertex for vertex in scenario.vertices}
    selected = {edge.key for edge in active}
    figure = go.Figure()

    _add_floor_bands(figure, scenario, points)
    _add_cables(figure, scenario, points, selected, route, failed)
    _add_racks(figure, scenario, offline)

    top = max(vertex.y for vertex in scenario.vertices)
    figure.update_layout(
        height=height, paper_bgcolor="white", plot_bgcolor="white",
        margin=dict(l=10, r=10, t=5, b=10),
        xaxis=dict(visible=False, range=[-0.4, 11.7], fixedrange=True),
        yaxis=dict(visible=False, range=[-1.1, top + 1.45], fixedrange=True),
        hoverlabel=dict(bgcolor="#102b3f", font_color="white", font_size=14),
    )
    return figure
