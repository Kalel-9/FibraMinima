"""Exemplo preservado e construtor de prédios em duas guias independentes."""

import streamlit as st

from building_panel import render_network
from custom_builder_ui import render_builder
from scenarios import four_floor_building
from ui import apply_building_style

def main() -> None:
    st.set_page_config(
        page_title="Fibra Mínima · Prédios e cabeamento",
        page_icon="🌐",
        layout="wide",
    )
    apply_building_style()

    example_tab, builder_tab = st.tabs(["Prédio de exemplo", "Montar meu prédio"])
    with example_tab:
        render_network(four_floor_building())
    with builder_tab:
        custom = render_builder()
        render_network(custom, prefix="custom_", title="FibraMínima · Meu prédio")


if __name__ == "__main__":
    main()
