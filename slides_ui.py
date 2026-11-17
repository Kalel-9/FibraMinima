"""Roteiro principal: demonstra exatamente o grafo e a comparação dos slides."""

from math import fsum, isclose
import streamlit as st

from graph import Edge, kruskal
from presentation_model import dijkstra_tree, prim
from resilience import reachable, shortest_route
from scenarios import presentation_scenario
from visual import draw_graph, money


def _set(key, value):
    st.session_state[key] = value


def _restore():
    for edge in presentation_scenario().edges:
        st.session_state[f"slides_distance_{edge.source}_{edge.target}"] = float(edge.weight)
    st.session_state["slides_price"] = 5.0
    st.session_state["slides_step"] = 0


def render_slides():
    scenario = presentation_scenario()
    ids = [v.id for v in scenario.vertices]
    st.session_state.setdefault("slides_price", 5.0)
    for edge in scenario.edges:
        st.session_state.setdefault(f"slides_distance_{edge.source}_{edge.target}", float(edge.weight))
    with st.sidebar:
        st.markdown("### Grafo da apresentação")
        st.caption("Rack R + 6 blocos · 10 trechos de duto · grafo não direcionado")
        with st.expander("Editar valores do exemplo"):
            with st.form("slides_inputs"):
                input_price = st.number_input("Preço por metro (R$)", min_value=.01, value=None,
                    step=.5, format="%.2f", key="slides_price")
                edited = []
                for edge in scenario.edges:
                    distance = st.number_input(f"{edge.source} ↔ {edge.target} (m)", min_value=.1,
                        value=None, step=1.0, format="%.1f",
                        key=f"slides_distance_{edge.source}_{edge.target}")
                    edited.append(Edge(edge.source, edge.target, distance))
                st.form_submit_button("Aplicar valores", type="primary", width="stretch")
        st.button("Restaurar exemplo dos slides", on_click=_restore, width="stretch", key="slides_reset")
        st.caption("Preço ilustrativo. Ao editar distâncias, os resultados podem diferir dos slides.")
        st.divider()
        st.markdown("**Roteiro em sala**")
        st.caption("1. Compare as três alternativas.\n\n2. Construa a MST passo a passo.\n\n"
                   "3. Compare o trajeto até D.\n\n4. Explique a falta de redundância e a extensão de Steiner.")

    if input_price is None or any(edge.weight is None for edge in edited):
        st.warning("Preencha o preço e todas as distâncias para calcular as alternativas.")
        st.stop()
    signature = tuple((e.source, e.target, e.weight) for e in edited)
    if st.session_state.get("slides_signature") != signature:
        st.session_state["slides_signature"] = signature
        st.session_state["slides_step"] = 0
    edges, price = edited, input_price
    mst = kruskal(ids, edges)
    paths = dijkstra_tree(ids, edges)
    prim_result = prim(ids, edges)
    total = fsum(e.weight for e in edges)
    alternatives = {"Cabear tudo": tuple(edges), "Caminhos mínimos (Dijkstra)": paths.selected,
                    "Árvore mínima (Kruskal)": mst.selected}
    totals = {name: fsum(e.weight for e in selected) for name, selected in alternatives.items()}

    st.markdown("## Planejamento de cabeamento óptico com grafos")
    st.write("**Como conectar todos os blocos ao rack usando a menor quantidade total de fibra?**")
    st.caption("Mesmo grafo nas três alternativas · vértices = rack e blocos · arestas = dutos · pesos = metros")
    st.session_state.setdefault("slides_choice", "Árvore mínima (Kruskal)")
    for column, (name, selected) in zip(st.columns(3), alternatives.items()):
        with column:
            st.button(f"{name} · {totals[name]:g} m", key=f"slides_choose_{name}", width="stretch",
                      on_click=_set, args=("slides_choice", name),
                      type="primary" if st.session_state.get("slides_choice", "Árvore mínima (Kruskal)") == name else "secondary")
    choice = st.radio("Alternativa em exibição", list(alternatives),
                      key="slides_choice", horizontal=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Fibra instalada", f"{totals[choice]:g} m")
    m2.metric("Custo estimado do cabo", money(totals[choice] * price))
    m3.metric("Economia da MST vs. tudo", f"{(total - mst.total) / total:.1%}")
    m4.metric("Economia da MST vs. Dijkstra", f"{(paths.total - mst.total) / paths.total:.1%}")

    graph_column, explain_column = st.columns([2.15, 1], gap="large")
    with explain_column:
        target = st.selectbox("Acompanhar bloco", ids[1:], index=3, key="slides_target")
        walk = st.toggle("Construir Kruskal passo a passo", key="slides_walk", value=False,
                         disabled=choice != "Árvore mínima (Kruskal)") and choice == "Árvore mínima (Kruskal)"
        step_index = min(st.session_state.get("slides_step", 0), len(mst.steps))
        if walk:
            st.button("Próxima aresta", key="slides_next", type="primary", width="stretch",
                      disabled=step_index == len(mst.steps), on_click=_set,
                      args=("slides_step", step_index + 1))
            back, end = st.columns(2)
            back.button("Recomeçar", key="slides_restart", on_click=_set, args=("slides_step", 0))
            end.button("Concluir", key="slides_finish", on_click=_set, args=("slides_step", len(mst.steps)))
            st.caption(f"{step_index}/{len(mst.steps)} decisões de Kruskal. A construção mostra apenas a MST.")
        st.markdown("**O que esta alternativa otimiza?**")
        if choice == "Cabear tudo":
            st.write("Instala todos os trechos disponíveis. Maior custo e mais opções de caminho dentro deste grafo.")
        elif choice == "Caminhos mínimos (Dijkstra)":
            st.write("Minimiza a distância individual de cada bloco até R. A árvore de predecessores reúne esses caminhos.")
            st.caption("Um cabo compartilhado é contado uma vez. Não somamos as distâncias dos seis blocos para calcular fibra instalada.")
        else:
            st.write("Minimiza a soma dos pesos para conectar todos os vértices, sem ciclos. Não garante o menor caminho individual até R.")
        st.caption(f"Prim confirma a MST: {prim_result.total:g} m. "
                   + ("Mesmo custo total de Kruskal." if isclose(mst.total, prim_result.total) else "Revise o resultado."))

    selected = alternatives[choice]
    if walk:
        selected = tuple(step.edge for step in mst.steps[:step_index] if step.accepted)
    route = shortest_route(selected, False, target, root="R")
    with graph_column:
        if walk:
            if step_index:
                st.info(mst.steps[step_index - 1].explanation)
            else:
                st.info("Comece pela aresta de menor peso. Aceite somente conexões que não formam ciclos.")
            st.caption(f"Construção da MST: {len(selected)} arestas aceitas · {fsum(e.weight for e in selected):g} m. "
                       "Os indicadores acima comparam os projetos completos.")
        st.plotly_chart(draw_graph(scenario.vertices, edges, {e.key for e in selected},
            route={e.key for e in route[1]} if route and not walk else set(),
            offline=set(ids) - reachable(selected, False, root="R") if walk else set(),
            dashed_available=True, show_all_weights=True, height=440),
            width="stretch", config={"displayModeBar": False})
        st.caption("Verde: trechos selecionados · azul: caminho até o bloco escolhido · cinza tracejado: não instalado. Desenho sem escala.")
        if walk:
            st.caption("Pontos em laranja ainda não possuem caminho até R na construção parcial.")
        if route:
            st.write(f"**R → {target}:** {' → '.join(route[0])} · **{fsum(e.weight for e in route[1]):g} m**")
        else:
            st.write(f"**R → {target}:** ainda não há caminho na construção parcial.")

    compare_tab, steps_tab, limits_tab = st.tabs(["Resultados dos slides", "Algoritmos e passos", "Limitações e extensões"])
    with compare_tab:
        st.dataframe([{"Alternativa": name, "Trechos instalados": len(selected),
                       "Fibra (m)": totals[name], "Custo estimado": money(totals[name] * price)}
                      for name, selected in alternatives.items()], hide_index=True, width="stretch")
        st.write(f"A MST usa **{total - mst.total:g} m a menos** que cabear tudo: "
                 f"economia estimada de **{money((total - mst.total) * price)}**.")
        st.caption("Cabear tudo é uma alternativa explícita de instalar os dez trechos; não representa um orçamento real já realizado.")
        rows = []
        for vertex in ids[1:]:
            path = shortest_route(mst.selected, False, vertex, root="R")
            rows.append({"Bloco": vertex, "Menor caminho desde R (m)": paths.distances[vertex],
                         "Caminho na MST (m)": fsum(e.weight for e in path[1])})
        st.dataframe(rows, hide_index=True, width="stretch")
    with steps_tab:
        st.markdown("**Kruskal + Union-Find:** ordenar por peso, aceitar se não formar ciclo e parar com V − 1 arestas. Complexidade O(E log E).")
        st.dataframe([{"Passo": i, "Aresta": f"{s.edge.source}–{s.edge.target}", "Peso (m)": s.edge.weight,
                       "Decisão": "Aceita" if s.accepted else "Rejeitada: ciclo", "Total (m)": s.total}
                      for i, s in enumerate(mst.steps, 1)], hide_index=True, width="stretch")
        remaining = [e for e in edges if e not in {s.edge for s in mst.steps}]
        if remaining:
            st.caption("Não analisadas após a parada: " + ", ".join(f"{e.source}–{e.target}" for e in remaining)
                       + ". Se continuássemos a varredura, seriam rejeitadas por formar ciclos, como ilustrado no slide 4.")
        st.markdown("**Dijkstra:** relaxa distâncias com pesos positivos usando uma fila de prioridade. "
                    "A árvore de predecessores dá o menor caminho de R a cada bloco; custo usual O((V + E) log V).")
        st.write("Ordem de distâncias finalizadas: " + " → ".join(paths.settled))
        st.markdown("**Prim:** cresce uma árvore desde R, escolhendo a menor aresta que alcança um novo vértice. "
                    "Lista de adjacência e heap: O(E log V). A checagem confirma o mesmo peso mínimo de Kruskal.")
        st.caption("Kruskal é uma escolha didática adequada para este grafo esparso; "
                   "não é universalmente mais rápido que Prim. O desempenho depende da representação e da implementação.")
    with limits_tab:
        st.write("A MST é um ponto de partida econômico, sem redundância nem capacidade por trecho. "
                 "O rompimento de uma de suas arestas pode desconectar blocos.")
        st.write("**Steiner — extensão conceitual:** permitir novos pontos de junção, com trajetos e custos definidos, "
                 "pode reduzir a instalação. O problema não é resolvido por esta MST e não está implementado.")
        st.caption("Um splitter é um equipamento real; não basta adicionar um vértice para modelar suas perdas, capacidade e custo.")
        st.write("A simulação anterior de falhas e reservas permanece acessível no roteiro de extensão. "
                 "Ela usa heurística de redundância e não muda os resultados da MST desta apresentação.")
        st.button("Abrir extensão de falhas e redundância", key="slides_open_extension",
                  on_click=_set, args=("app_route", "Extensão: falhas e redundância"))
