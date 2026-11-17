"""Painel de apresentação: custo, redundância e falha de cabeamento."""

from html import escape
import streamlit as st

from graph import Edge, kruskal
from resilience import compare_plans, edge_id, reachable, shortest_route
from scenarios import environments
from ui import apply_style, hero, legend
from visual import comparison_chart, draw_graph, money
from slides_ui import render_slides

st.set_page_config(page_title="Fibra Mínima · Simulador de redes", page_icon="🌐", layout="wide")
apply_style()
with st.sidebar:
    route = st.radio("Roteiro da demonstração", ["Apresentação: MST e caminhos", "Extensão: falhas e redundância"],
                     key="app_route")
if route == "Apresentação: MST e caminhos":
    render_slides()
    st.stop()
scenarios = environments()
scenario_names = [s.name for s in scenarios]


def set_value(key, value):
    st.session_state[key] = value


with st.sidebar:
    st.markdown("### 🌐 FibraMínima")
    st.caption("Custo e continuidade da rede")
    presentation = st.toggle("Modo apresentação", value=True, key="view_presentation",
                             help="Compacta os controles superiores para destacar o grafo.")
    st.divider()
    st.markdown("**01 · Ambiente**")
    name = st.selectbox("Escolha o ambiente", scenario_names, key="view_environment")
    st.button("Apresentar prédio de 5 andares", key="demo_building", width="stretch",
              on_click=set_value, args=("view_environment", scenario_names[-1]))
    scenario = next(s for s in scenarios if s.name == name)
    ids = [v.id for v in scenario.vertices]
    symbol = "→" if scenario.directed else "↔"

    def label(edge):
        return f"{edge.source} {symbol} {edge.target}"

    st.caption(f"{len(ids)} pontos · {len(scenario.edges)} conexões possíveis")
    st.caption("Sentidos indicados pelas setas" if scenario.directed else "Cabos nos dois sentidos")
    st.divider()
    st.markdown("**02 · Configuração**")
    with st.expander("Editar distâncias e preço", expanded=False):
        with st.form(f"view_distances_{name}"):
            input_price = st.number_input("Preço do cabo por metro (R$)", min_value=.01,
                value=5.0, step=.5, format="%.2f", key=f"price_{name}")
            input_edges = []
            for edge in scenario.edges:
                distance = st.number_input(f"{label(edge)} (m)", min_value=.1,
                    value=float(edge.weight), step=1.0, format="%.1f",
                    key=f"distance_{name}_{edge.source}_{edge.target}")
                input_edges.append(Edge(edge.source, edge.target, distance))
            submitted = st.form_submit_button("Aplicar valores e recalcular", type="primary", width="stretch")
    st.caption("Os cenários já começam com valores de exemplo. Edite apenas se precisar.")
    st.divider()
    st.markdown("**Roteiro para apresentar**")
    st.caption("1. Escolha a rede econômica.\n\n2. Rompa a ligação crítica.\n\n"
               "3. Troque para a rede protegida.\n\n4. Compare o custo e os pontos conectados.")

result_key, plan_key = f"view_result_algorithms_{name}", f"plan_{name}"
if submitted or result_key not in st.session_state:
    with st.spinner("Comparando projetos e testando falhas…"):
        cheapest, frontier = compare_plans(ids, input_edges, scenario.directed)
    st.session_state[result_key] = (input_price, input_edges, cheapest, frontier)
    st.session_state[plan_key] = 0
    st.session_state[f"view_failure_{name}"] = "intact"
price, edges, cheapest, frontier = st.session_state[result_key]
if presentation:
    st.markdown("## Fibra Mínima · Algoritmos em grafos")
else:
    hero()
st.caption(name.split(" — ", 1)[-1] + " · Vértices: pontos de distribuição · Pesos: metros de cabo")
if scenario.directed:
    st.info("Extensão avançada: a base é uma arborescência mínima por enumeração. "
            "Kruskal é demonstrado nos ambientes sem setas, incluindo o prédio.")
else:
    st.caption("Kruskal constrói a base mínima → adição gulosa cria reservas → DFS testa a falha → Dijkstra encontra o trajeto.")
if not cheapest:
    st.error("Os trajetos disponíveis não permitem conectar todos os pontos ao rack.")
    st.stop()

plans = list(dict.fromkeys([*frontier, *cheapest]))
names = {plans[0]: "Base mínima"}
for i, option in enumerate(plans[1:], 1):
    names[option] = "Com 1 reserva" if i == 1 and len(plans) > 2 else "Reservas acumuladas"

st.markdown('<div class="step">01 · Compare o investimento</div>', unsafe_allow_html=True)
st.caption("A base tem custo mínimo. As reservas são construídas por regra gulosa, sem garantia de custo ótimo.")
presets = [("Econômica", frontier[0])]
if len(frontier) > 2:
    presets.append(("Com 1 reserva", frontier[1]))
if len(frontier) > 1:
    presets.append(("Mais protegida", frontier[-1]))
for column, (title, option) in zip(st.columns(len(presets)), presets):
    i = plans.index(option)
    active = st.session_state.get(plan_key, 0) == i
    with column.container(border=not presentation):
        pill = "Projeto em exibição" if active else f"{option.meters:g} metros de cabo"
        detail = "Mantém todos conectados em qualquer ruptura única." if option.worst_loss == 0 else f"Na pior ruptura, {option.worst_loss} ponto(s) podem perder acesso."
        if not presentation:
            st.markdown(f'<div class="pill">{pill}</div><div class="preset-title">{title}</div>'
                        f'<div class="preset-price">{money(option.meters * price)}</div>'
                        f'<div class="preset-detail">{detail}</div>', unsafe_allow_html=True)
        st.button(f"{title} · {money(option.meters * price)}" if presentation else f"Ver rede {title.lower()}",
                  key=f"preset_{title}", width="stretch",
                  type="primary" if active else "secondary", on_click=set_value, args=(plan_key, i))
        if presentation:
            st.caption("Tolera qualquer ruptura única" if option.worst_loss == 0 else
                       f"Pior ruptura: {option.worst_loss} sem acesso")

with st.expander("Detalhes das alternativas", expanded=not presentation):
    plan_index = st.selectbox("Projeto em exibição", range(len(plans)), key=plan_key,
        format_func=lambda i: f"{names[plans[i]]} · {money(plans[i].meters * price)}")
plan = plans[plan_index]
failure_key = f"view_failure_{name}"
if st.session_state.get(failure_key) is None:
    st.session_state[failure_key] = "intact"
failed_id = st.session_state[failure_key]
if failed_id == "intact":
    failed_id = None
failed = next((e for e in edges if edge_id(e, scenario.directed) == failed_id), None)
offline = set(ids) - reachable(plan.edges, scenario.directed, failed=failed)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Cabo necessário", f"{plan.meters:g} m")
m2.metric("Custo estimado do cabo", money(plan.meters * price))
m3.metric("Pontos conectados agora", f"{len(ids) - 1 - len(offline)} / {len(ids) - 1}")
m4.metric("Sem acesso na pior ruptura", f"{plan.worst_loss} pontos")

st.markdown("")
map_column, control_column = st.columns([2.25, 1], gap="large")
with control_column:
    st.markdown('<div class="step">02 · Teste a rede</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("### O que acontece se romper?")
        critical = max(plan.edges, key=lambda e: len(set(ids) - reachable(plan.edges, scenario.directed, failed=e)))
        st.button("Romper ligação crítica", key="break_critical", type="primary", width="stretch",
                  on_click=set_value, args=(failure_key, edge_id(critical, scenario.directed)),
                  help="Escolhe o cabo instalado cuja ruptura deixa mais pontos sem acesso.")
        st.button("Restaurar cabo", key="restore", width="stretch", disabled=failed is None,
                  on_click=set_value, args=(failure_key, "intact"))
        lookup = {edge_id(e, scenario.directed): e for e in edges}
        selected_ids = {edge_id(e, scenario.directed) for e in plan.edges}
        options = ["intact", *sorted(lookup, key=lambda k: (k not in selected_ids, k))]
        st.selectbox("Ou escolha o cabo rompido", options, key=failure_key,
            format_func=lambda k: "Nenhum · rede intacta" if k == "intact" else label(lookup[k]) +
            ("" if k in selected_ids else " · não instalado neste projeto"))
        st.caption("A ruptura escolhida é mantida ao trocar de projeto para comparar a mesma falha.")
        if failed and failed not in plan.edges:
            st.info("Este projeto não usa o cabo rompido; a falha não afeta sua rede.")
        target = st.selectbox("Acompanhar conexão até", ids[1:], index=len(ids) - 2, key=f"target_{name}")
        show_available = st.toggle("Mostrar cabos não instalados", value=False, key="view_show_available")
    extra = plan.meters * price - cheapest[0].meters * price
    st.caption(f"Investimento adicional sobre a rede mais barata: **{money(extra)}**.")

with map_column:
    st.markdown('<div class="step">03 · Observe o resultado</div>', unsafe_allow_html=True)
    with st.container(border=True):
        if offline:
            st.warning(f"{len(offline)} ponto(s) perderam acesso: " + ", ".join(v for v in ids if v in offline))
        else:
            st.success("Todos os pontos continuam conectados ao rack.")
        before = shortest_route(plan.edges, scenario.directed, target)
        after = shortest_route(plan.edges, scenario.directed, target, failed=failed)
        route = {edge_id(e, scenario.directed) for e in after[1]} if after else set()
        st.plotly_chart(draw_graph(scenario.vertices, edges, selected_ids, scenario.directed,
            failed=failed_id, offline=offline, route=route, show_available=show_available,
            height=420 if presentation else 520),
            width="stretch", config={"displayModeBar": False, "scrollZoom": False})
        legend()
        if failed:
            st.caption("Antes da falha: " + " → ".join(before[0]))
        text = " → ".join(after[0]) if after else f"Não existe caminho até {target} pelos cabos restantes."
        st.markdown(f'<div class="route{" off" if after is None else ""}"><b>Trajeto ativo</b><br>{escape(text)}</div>', unsafe_allow_html=True)
        st.caption("Distâncias em metros. Posições no desenho são ilustrativas.")

st.markdown("### Quanto custa cada nível de proteção?")
model_tab, table_tab, chart_tab = st.tabs(["Algoritmos e passos", "Tabela de projetos", "Comparação visual"])
with chart_tab:
    with st.container(border=True):
        st.plotly_chart(comparison_chart(plans, names, price, plan), width="stretch", config={"displayModeBar": False})
        st.caption("A barra verde representa o projeto em exibição. Mais proteção pode exigir mais cabo.")
with table_tab:
    rows = []
    for option in plans:
        row = {"Projeto": names[option], "Cabo": f"{option.meters:g} m", "Custo": money(option.meters * price),
               "Pior perda (pontos)": option.worst_loss,
               "Rupturas sem perda": f"{option.safe_failures}/{len(option.edges)}"}
        if failed:
            row["Perda nesta ruptura"] = str(len(ids) - len(reachable(option.edges, scenario.directed, failed=failed))) if failed in option.edges else "Não usa esse cabo"
        rows.append(row)
    st.dataframe(rows, hide_index=True, width="stretch")
    st.caption("Pior perda: maior número de pontos isolados entre todas as rupturas individuais. "
               "Rupturas sem perda: quantos cabos podem romper, um por vez, sem desconectar nenhum ponto.")
    with st.expander("Cabos instalados no projeto em exibição"):
        st.write("; ".join(label(e) for e in plan.edges))
with model_tab:
    st.markdown("**Vértices** representam rack e pontos de distribuição. **Arestas** representam cabos possíveis. "
                "**Pesos** são as distâncias em metros. O custo é a soma dos metros instalados multiplicada pelo preço por metro.")
    if not scenario.directed:
        base = kruskal(ids, edges)
        st.markdown("**1. Kruskal — construir a rede econômica.** Ordena as arestas por peso e aceita "
                    "as que conectam componentes distintos. Union-Find identifica ciclos. "
                    "A base tem V − 1 arestas e o menor comprimento total. Complexidade: O(E log E).")
        st.dataframe([{"Passo": i, "Aresta": label(step.edge), "Peso (m)": step.edge.weight,
                       "Decisão": "Aceita" if step.accepted else "Rejeitada: formaria ciclo",
                       "Componentes": step.components, "Total (m)": step.total}
                      for i, step in enumerate(base.steps, 1)], hide_index=True, width="stretch")
        st.caption("Kruskal para ao conectar todos os pontos; as arestas restantes não precisam ser analisadas.")
    else:
        st.markdown("**1. Base direcionada — extensão.** Enumera uma entrada por vértice não raiz, "
                    "descarta ciclos desconectados e escolhe a arborescência mínima. "
                    "Kruskal não se aplica diretamente. Esse método pode crescer exponencialmente.")
    st.markdown("**2. Regra gulosa — adicionar reservas.** Testa cada cabo ainda não instalado e escolhe "
                "o que mais reduz a soma dos pontos isolados nos testes de falha por metro adicional. "
                "Repete até eliminar as perdas ou não encontrar melhoria. A regra não garante o menor custo da redundância.")
    st.markdown("**3. DFS — verificar alcance.** Parte do rack e visita os vizinhos pelos cabos ativos. "
                "Os pontos não visitados ficam sem acesso. Cada busca custa O(V + E). "
                "Nos testes de proteção, repetimos a busca removendo um cabo por vez.")
    st.markdown("**4. Dijkstra — encontrar o caminho disponível.** Usa os pesos positivos e uma fila de "
                "prioridade para encontrar o trajeto mais curto até o destino. "
                "Custo usual: O((V + E) log V). Caminho mínimo e rede de custo mínimo são objetivos diferentes.")
    if after:
        st.write(f"Trajeto mostrado no grafo: **{' → '.join(after[0])}** · "
                 f"**{sum(e.weight for e in after[1]):g} m**.")
    st.info("O modelo supõe pontos intermediários capazes de encaminhar a conexão. "
            "Redundância real exige equipamentos e configuração compatíveis. O preço inclui apenas cabo; "
            "não simulamos falha de equipamento, energia ou vários cabos rompidos no mesmo duto.")
