"""Três ambientes de cabeamento, com e sem orientação."""

import streamlit as st
from graph import Edge, kruskal
from directed import minimum_arborescence
from scenarios import environments
from visual import draw_graph, money

st.set_page_config(page_title="FibraMínima", page_icon="🌐", layout="wide")
st.title("Conectar gastando menos")
scenarios = environments()
name = st.selectbox("Escolha o ambiente", [s.name for s in scenarios])
scenario = next(s for s in scenarios if s.name == name)
st.write("Conecte todos os blocos ao rack usando a menor quantidade total de cabo.")
st.caption(f"{len(scenario.vertices)} pontos · {len(scenario.edges)} conexões com pesos em metros · "
           + ("grafo direcionado" if scenario.directed else "grafo não direcionado"))
if scenario.directed:
    st.info("Siga as setas: Rack → A permite alcançar A a partir do rack. "
            "A ligação inversa só existe se houver outra seta. "
            "Todos os blocos precisam ser alcançáveis a partir do rack.")
    st.caption("As setas são uma restrição didática do sentido de distribuição da rede; "
               "não representam uma propriedade física do cabo.")

with st.form(f"distances_{name}"):
    price = st.number_input("Preço do cabo por metro (R$)", min_value=0.01,
                            value=5.0, step=0.5, format="%.2f", key=f"price_{name}")
    st.write("**Quantos metros de cabo seriam necessários em cada trajeto?**")
    edges = []
    columns = st.columns(3)
    symbol = "→" if scenario.directed else "↔"
    for i, edge in enumerate(scenario.edges):
        distance = columns[i % 3].number_input(
            f"{edge.source} {symbol} {edge.target} (m)", min_value=0.1,
            value=float(edge.weight), step=1.0, format="%.1f",
            key=f"distance_{name}_{edge.source}_{edge.target}",
        )
        edges.append(Edge(edge.source, edge.target, distance))
    submitted = st.form_submit_button("Encontrar melhor ligação", type="primary")

selected = set()
if submitted:
    ids = [v.id for v in scenario.vertices]
    result = minimum_arborescence(ids, edges) if scenario.directed else kruskal(ids, edges)
    if result.connected:
        selected = {(e.source, e.target) if scenario.directed else e.key for e in result.selected}
        st.success("Todos os pontos conectados a partir do rack!")
        meters, cost = st.columns(2)
        meters.metric("Cabo necessário", f"{result.total:g} m")
        cost.metric("Custo estimado do cabo", money(result.total * price))
        st.write("Ligações escolhidas: " + "; ".join(
            f"{e.source} {symbol} {e.target}" for e in result.selected) + ".")
    else:
        st.error("Não é possível alcançar todos os pontos a partir do rack.")
    if scenario.directed:
        st.caption(f"Busca exata: {result.candidates} combinações de entradas examinadas.")
else:
    st.caption("Informe os valores e clique no botão para ver quais ligações usar.")

st.plotly_chart(draw_graph(scenario.vertices, edges, selected, directed=scenario.directed), width="stretch")
st.caption("Verde = ligação escolhida · cinza = alternativa disponível. Desenho sem escala.")
st.write("**A conta:** metros de cabo escolhidos × preço por metro.")
if scenario.directed:
    st.write("**Algoritmo:** busca exata por enumeração de arborescências. "
             "Testa uma entrada por bloco, descarta as combinações que não permitem "
             "alcançar todos os pontos desde o rack e escolhe a de menor soma.")
    st.caption("A quantidade de combinações é o produto dos números de entradas possíveis "
               "dos blocos. Pode crescer exponencialmente; usamos apenas exemplos pequenos. "
               "Kruskal não se aplica diretamente a esses grafos.")
else:
    st.caption("Algoritmo: Kruskal, O(E log E). Escolhe as menores arestas sem formar ciclos.")
st.caption("Mais pontos e conexões aumentam o tamanho do problema; apenas aumentar os valores "
           "dos pesos não aumenta a quantidade de combinações. "
           "Estimativa considera apenas cabo, com preço uniforme por metro.")
