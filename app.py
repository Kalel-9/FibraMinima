"""Demonstração mínima de cabeamento com Kruskal."""

import streamlit as st
from graph import Edge, kruskal, sample_graph
from visual import draw_graph, money

st.set_page_config(page_title="FibraMínima", page_icon="🌐")
st.title("Conectar gastando menos")
st.write("Precisamos ligar os blocos A e B ao rack usando a menor quantidade de cabo.")
vertices, default_edges = sample_graph()

with st.form("distances"):
    price = st.number_input("Preço do cabo por metro (R$)", min_value=0.01,
                            value=5.0, step=0.5, format="%.2f", key="price")
    st.write("**Quantos metros de cabo seriam necessários em cada trajeto?**")
    edges = []
    for column, edge in zip(st.columns(3), default_edges):
        distance = column.number_input(
            f"{edge.source} ↔ {edge.target} (m)", min_value=0.1,
            value=float(edge.weight), step=1.0, format="%.1f",
            key=f"distance_{edge.source}_{edge.target}",
        )
        edges.append(Edge(edge.source, edge.target, distance))
    submitted = st.form_submit_button("Encontrar melhor ligação", type="primary")

selected = set()
if submitted:
    result = kruskal([v.id for v in vertices], edges)
    selected = {edge.key for edge in result.selected}
    st.success("Todos os pontos conectados!")
    meters, cost = st.columns(2)
    meters.metric("Cabo necessário", f"{result.total:g} m")
    cost.metric("Custo estimado do cabo", money(result.total * price))
    st.write("Ligações escolhidas: " + " e ".join(
        f"{edge.source} ↔ {edge.target}" for edge in result.selected
    ) + ".")
else:
    st.info("Informe os valores e clique no botão para ver quais ligações usar.")

st.plotly_chart(draw_graph(vertices, edges, selected), width="stretch")
st.caption("Verde = ligação escolhida · cinza = alternativa disponível. Desenho sem escala.")
st.write("**A conta:** metros de cabo escolhidos × preço por metro.")
st.caption("Algoritmo: Kruskal. O objetivo é conectar todos os pontos com menos cabo. "
           "Simulação considera apenas o cabo, sem equipamentos ou mão de obra.")
