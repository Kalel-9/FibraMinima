# Histórico de versões

## Em desenvolvimento

- Refatoração interna das telas e do desenho em funções menores, com limites
  compartilhados, nomes mais claros e estilos reunidos no módulo de interface.
  Comportamento, textos, algoritmos e controles preservados.

- Segunda guia para montar um prédio, preservando o exemplo fixo de quatro andares.
- Botão **Adicionar andar** com numeração automática e apenas um seletor de quantidade de racks.
- Andares consecutivos, sem lacunas; remoção apenas pelo topo da pilha de andares.
- Distâncias aleatórias de 8 a 16 m, com faixa ajustável e pesos mantidos durante a simulação.
- Anéis e duas prumadas gerados automaticamente para suportar uma ruptura por vez.
- Preço, destino e rompimento independentes entre as guias; desenho adaptado à quantidade de andares.

- Barra lateral removida da demonstração principal; preço por metro e controles
  de falha ao lado do grafo, com disposição compacta para notebook.

- Foco em um único prédio de quatro andares, com 2, 3, 4 e 5 racks por andar.
- 14 vértices, 13 trechos internos e seis conexões entre andares por duas prumadas.
- Desenho organizado por pavimento e seleção de andar/rack de destino.
- Todos os 19 cabos testados individualmente para manter o acesso após uma ruptura.

- Entrada principal simplificada: um grafo, rompimento aleatório e restauração.
- Cada sorteio remove um cabo em uso e recalcula a MST usando reservas já instaladas.
- Distinção entre investimento físico fixo e valor equivalente da árvore em uso.
- Tabelas e abas retiradas da entrada principal; roteiro anterior preservado em `academic_app.py`.

- Roteiro principal alinhado ao PDF: mesmo grafo, comparação de 490/340/240 m,
  exemplo do bloco D (155/105 m) e cálculo dos percentuais de economia.
- Prim confirma o custo da MST; Dijkstra gera a árvore de predecessores com
  contagem única dos cabos compartilhados.
- Construção de Kruskal por aresta, restauração do exemplo e relatório de alinhamento.
- Roteiro anterior de falhas e redundância preservado como extensão separada.

- Foco didático em Kruskal, DFS e Dijkstra, com decisões do Kruskal exibidas na tela.
- Até três alternativas: base mínima, primeira reserva e reservas acumuladas.
- Adição gulosa de reservas substitui a enumeração de todos os subconjuntos na
  interface; a busca exata continua disponível como referência para testes.
- Distinção explícita entre o ótimo da base mínima e a heurística de redundância.

- Modo apresentação com escolha rápida de três níveis de investimento.
- Grafo ampliado, controles laterais, legenda e comparação visual de custos.
- Botões para romper uma ligação crítica e restaurar a rede; a ruptura é mantida
  ao trocar de projeto para comparar a mesma falha.

- Cenário de prédio com cinco andares e trajetos de reserva.
- Comparação de projetos por preço e maior perda de acesso sob ruptura de um cabo.
- Simulação de falha com visualização dos pontos isolados e do trajeto alternativo.

## 1.0.0 — 2026-10-27

- Três ambientes com 3, 5 e 7 pontos e 3, 8 e 15 conexões.
- Kruskal no cenário não direcionado.
- Busca exata de arborescência mínima nos dois cenários direcionados.
- Entradas de distância e preço do cabo por metro.
- Visualização de ligações, sentidos, comprimento total e custo estimado.
- Execução local com Python ou configuração Docker Compose.
- Doze testes de algoritmo e interface.

## Histórico local anterior à versão 1

- `16dfe62`: exemplo inicial de um condomínio, reconstruído da versão
  registrada na conversa antes da criação do repositório; sete testes passaram.
- `787f07a`: estado atual com três condomínios, preservado antes da
  identificação formal da versão 1.0.0.
