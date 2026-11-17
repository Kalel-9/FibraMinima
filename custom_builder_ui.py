"""Poucos campos para acrescentar andares e gerar distâncias de simulação."""

import streamlit as st

from custom_building import (
    DEFAULT_DISTANCE_RANGE,
    MAX_DISTANCE,
    MAX_FLOORS,
    MAX_RACKS,
    MIN_DISTANCE,
    MIN_FLOORS,
    MIN_RACKS,
    build_custom_building,
)
from scenarios import BuildingScenario


DEFAULT_FLOOR_COUNTS = {1: 2, 2: 4}


def _add_floor() -> None:
    counts = dict(st.session_state["custom_floor_counts"])
    if len(counts) >= MAX_FLOORS:
        return
    level = len(counts) + 1
    count = int(st.session_state["custom_new_racks"])
    counts[level] = count
    st.session_state["custom_floor_counts"] = counts
    st.toast(f"Andar {level} salvo com {count} racks.")


def _remove_floor() -> None:
    counts = dict(st.session_state["custom_floor_counts"])
    if len(counts) > MIN_FLOORS:
        counts.pop(max(counts))
        st.session_state["custom_floor_counts"] = counts
        st.toast("Último andar removido.")


def _apply_range() -> None:
    minimum = int(st.session_state["custom_min"])
    maximum = int(st.session_state["custom_max"])
    if minimum > maximum:
        st.session_state["custom_range_error"] = (
            "O mínimo precisa ser menor ou igual ao máximo. A faixa anterior foi mantida."
        )
        return
    st.session_state["custom_range"] = (minimum, maximum)
    st.session_state["custom_lengths"] = {}
    st.session_state.pop("custom_range_error", None)
    st.toast(f"Novas distâncias sorteadas na faixa de {minimum} a {maximum} m.")


def _initialize_state() -> dict[int, int]:
    st.session_state.setdefault("custom_floor_counts", DEFAULT_FLOOR_COUNTS.copy())
    st.session_state.setdefault("custom_range", DEFAULT_DISTANCE_RANGE)
    st.session_state.setdefault("custom_lengths", {})

    # Configurações de sessões antigas também passam a ter andares consecutivos.
    counts = st.session_state["custom_floor_counts"]
    sequential = {
        level: counts[old_level]
        for level, old_level in enumerate(sorted(counts), start=1)
    }
    if counts != sequential:
        st.session_state["custom_floor_counts"] = sequential
        st.session_state["custom_lengths"] = {}
    return sequential


def _render_range_controls() -> None:
    with st.popover("Faixa das distâncias aleatórias", width="stretch"):
        with st.form("custom_range_form"):
            minimum_column, maximum_column = st.columns(2)
            minimum_column.number_input(
                "Distância mínima (m)", min_value=MIN_DISTANCE, max_value=MAX_DISTANCE,
                value=DEFAULT_DISTANCE_RANGE[0], step=1, key="custom_min",
            )
            maximum_column.number_input(
                "Distância máxima (m)", min_value=MIN_DISTANCE, max_value=MAX_DISTANCE,
                value=DEFAULT_DISTANCE_RANGE[1], step=1, key="custom_max",
            )
            st.form_submit_button("Aplicar faixa e sortear", on_click=_apply_range)
        st.caption(
            "Racks vizinhos e ligações entre andares vizinhos usam a faixa escolhida. "
            "O cabo de fechamento de um anel é estimado pela soma dos trechos internos vizinhos, em rota de reserva separada."
        )
        st.caption(
            "As distâncias ficam fixas durante os rompimentos. Ao adicionar racks, "
            "apenas novos trechos recebem novos pesos. Aplicar a faixa sorteia o prédio inteiro novamente."
        )


def _render_floor_controls(floor_count: int) -> None:
    next_level = floor_count + 1
    limit_reached = next_level > MAX_FLOORS
    floors_column, remove_column, range_column = st.columns(3)

    with floors_column, st.popover("Adicionar andar", width="stretch", disabled=limit_reached):
        st.markdown(f"**Novo andar: {next_level}º**")
        st.caption("O próximo andar é numerado automaticamente. Escolha apenas quantos racks ele terá.")
        with st.form("custom_floor_form"):
            st.selectbox(
                "Quantidade de racks", options=list(range(MIN_RACKS, MAX_RACKS + 1)),
                index=1, key="custom_new_racks",
            )
            st.form_submit_button(
                "Salvar andar", type="primary", on_click=_add_floor, disabled=limit_reached,
            )
        st.caption("Até 8 andares e 10 racks por andar. Mínimo de dois racks para manter as duas prumadas.")

    with remove_column:
        st.button(
            "Remover último andar", key="custom_remove", on_click=_remove_floor,
            disabled=floor_count <= MIN_FLOORS, width="stretch",
            help="Remove o andar do topo. Os dois primeiros são mantidos para preservar as rotas de reserva.",
        )
    with range_column:
        _render_range_controls()


def render_builder() -> BuildingScenario:
    """Configura a topologia sem sortear novamente os trechos já existentes."""
    counts = _initialize_state()
    _render_floor_controls(len(counts))
    if "custom_range_error" in st.session_state:
        st.error(st.session_state["custom_range_error"])

    minimum, maximum = st.session_state["custom_range"]
    scenario = build_custom_building(
        st.session_state["custom_floor_counts"], minimum, maximum,
        previous=st.session_state["custom_lengths"],
    )
    st.session_state["custom_lengths"] = {edge.key: edge.weight for edge in scenario.edges}
    st.caption(
        f"Distâncias entre vizinhos: {minimum}–{maximum} m · Pesos fixos durante os rompimentos · Reservas automáticas"
    )
    return scenario
