"""Painel reutilizável: mesmo funcionamento para o exemplo e para o prédio criado."""

from collections.abc import Callable

import streamlit as st

from building_visual import draw_building
from custom_building import MAX_FLOORS
from failure_demo import Network, calculate_network, random_break
from graph import Edge
from resilience import shortest_route
from scenarios import BuildingScenario
from visual import money


WidgetKey = Callable[[str], str]


def stored_edge_key(value) -> tuple[str, str] | None:
    """Aceita pares atuais e objetos de arestas guardados por sessões antigas."""
    if isinstance(value, (tuple, list)) and len(value) == 2:
        return tuple(sorted(value))
    if hasattr(value, "source") and hasattr(value, "target"):
        return tuple(sorted((value.source, value.target)))
    return None


def _synchronize_state(scenario: BuildingScenario, key: WidgetKey) -> None:
    """Limpa a falha e ajusta destinos somente quando a topologia muda."""
    signature = tuple((edge.source, edge.target, edge.weight) for edge in scenario.edges)
    signature_key = key("network_signature")
    if signature_key in st.session_state and st.session_state[signature_key] != signature:
        st.session_state.pop(key("building4_failure"), None)
        st.session_state.pop(key("building4_previous"), None)
        floors_by_level = {floor.level: floor for floor in scenario.floors}
        selected_level = st.session_state.get(key("building4_target_floor"))
        if selected_level not in floors_by_level:
            st.session_state[key("building4_target_floor")] = max(floors_by_level)

        for level in range(1, MAX_FLOORS + 1):
            target_key = key(f"building4_target_{level}")
            if level not in floors_by_level:
                st.session_state.pop(target_key, None)
                continue
            targets = [rack for rack in floors_by_level[level].racks if rack != scenario.root]
            if st.session_state.get(target_key) not in targets:
                st.session_state[target_key] = targets[-1]
    st.session_state[signature_key] = signature


def _previous_edges(
    edge_lookup: dict[tuple[str, str], Edge],
    baseline: tuple[Edge, ...],
    key: WidgetKey,
) -> tuple[Edge, ...]:
    stored = st.session_state.get(key("building4_previous"))
    if stored is None:
        return baseline

    edges = []
    for value in stored:
        edge_key = stored_edge_key(value)
        if edge_key in edge_lookup:
            edges.append(edge_lookup[edge_key])
    return tuple(edges)


def _render_controls(
    scenario: BuildingScenario,
    network: Network,
    key: WidgetKey,
    break_cable: Callable[[], None],
    restore: Callable[[], None],
) -> tuple[float, str]:
    with st.container(key=key("building_controls")):
        price = st.number_input(
            "Preço por metro (R$)", min_value=0.01, value=5.0,
            step=0.5, format="%.2f", key=key("simple_price"),
        )
        st.button(
            "Romper cabo aleatório", key=key("simple_break"), type="primary",
            width="stretch", on_click=break_cable,
        )
        st.button(
            "Restaurar rede", key=key("simple_restore"), width="stretch",
            on_click=restore, disabled=network.failed is None,
        )
        level = st.selectbox(
            "Andar de destino", [floor.level for floor in reversed(scenario.floors)],
            format_func=lambda value: f"{value}º andar", key=key("building4_target_floor"),
        )
        floor = next(floor for floor in scenario.floors if floor.level == level)
        targets = [rack for rack in floor.racks if rack != scenario.root]
        target_key = key(f"building4_target_{level}")
        target = st.selectbox(
            "Rack para acompanhar", targets,
            index=0 if target_key in st.session_state else len(targets) - 1,
            format_func=lambda rack: f"Rack {rack}", key=target_key,
        )

        rack_count = len(scenario.vertices)
        if network.offline:
            st.error("Sem acesso: " + ", ".join(sorted(network.offline)))
        elif network.failed:
            failed = network.failed
            st.success(f"{failed.source} ↔ {failed.target} rompido.\n\n{rack_count}/{rack_count} racks conectados.")
        else:
            st.success(f"Rede pronta.\n\n{rack_count}/{rack_count} racks conectados.")
    return price, target


def _render_metrics(network: Network, previous_meters: float, price: float, rack_count: int) -> None:
    difference = network.active_meters - previous_meters
    length, cost, connected = st.columns(3)
    length.metric(
        "Trechos em uso", f"{network.active_meters:g} m",
        f"{difference:+g} m" if network.failed else None, delta_color="off",
    )
    cost.metric(
        "Valor equivalente dos trechos em uso", money(network.active_meters * price),
        money(difference * price) if network.failed else None, delta_color="off",
    )
    connected.metric("Racks conectados", f"{rack_count - len(network.offline)} / {rack_count}")


def _render_graph(
    scenario: BuildingScenario,
    network: Network,
    previous_edges: tuple[Edge, ...],
    target: str,
    key: WidgetKey,
    height: int,
) -> None:
    before = shortest_route(previous_edges, False, target, root=scenario.root)
    after = shortest_route(network.active, False, target, root=scenario.root)
    figure = draw_building(
        scenario, network.active,
        route={edge.key for edge in after[1]} if after else set(),
        failed=network.failed, offline=network.offline, height=height,
    )
    st.plotly_chart(
        figure, width="stretch", config={"displayModeBar": False}, key=key("building_graph"),
    )
    if network.failed and before:
        st.caption("Antes: " + " → ".join(before[0]) + f" · {sum(edge.weight for edge in before[1]):g} m")
    if after:
        st.write("**Caminho atual:** " + " → ".join(after[0]) + f" · **{sum(edge.weight for edge in after[1]):g} m**")


def render_network(
    scenario: BuildingScenario,
    prefix: str = "",
    title: str = "FibraMínima · Prédio de quatro andares",
) -> None:
    """Coordena cálculo, controles e desenho com estado independente por guia."""
    def key(name: str) -> str:
        return prefix + name

    _synchronize_state(scenario, key)
    ids = [vertex.id for vertex in scenario.vertices]
    edge_lookup = {edge.key: edge for edge in scenario.edges}
    failure_key = key("building4_failure")
    previous_key = key("building4_previous")
    failed = edge_lookup.get(stored_edge_key(st.session_state.get(failure_key)))
    network = calculate_network(ids, scenario.edges, scenario.root, failed)
    baseline = calculate_network(ids, scenario.edges, scenario.root)
    previous_edges = _previous_edges(edge_lookup, baseline.active, key)
    previous_meters = sum(edge.weight for edge in previous_edges)

    def break_cable() -> None:
        st.session_state[previous_key] = tuple(edge.key for edge in network.active)
        st.session_state[failure_key] = random_break(network.active).key

    def restore() -> None:
        st.session_state.pop(failure_key, None)
        st.session_state.pop(previous_key, None)

    st.markdown(f"## {title}")
    st.caption(f"{len(ids)} racks · {len(scenario.edges)} cabos · Rack principal: {scenario.root} · Duas prumadas entre andares")
    summary = st.container()
    graph_column, control_column = st.columns([3.8, 1.1], gap="large")
    with control_column:
        price, target = _render_controls(scenario, network, key, break_cable, restore)
    with summary:
        _render_metrics(network, previous_meters, price, len(ids))
    with graph_column:
        height = max(360, len(scenario.floors) * 100) if prefix else 440
        _render_graph(scenario, network, previous_edges, target, key, height)
