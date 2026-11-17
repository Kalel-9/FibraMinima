# Alinhamento entre os slides e o projeto

Nota de atualização: este relatório descreve o roteiro acadêmico preservado em
`academic_app.py`. A entrada padrão `app.py` agora abre a demonstração simplificada
de rompimento aleatório, solicitada posteriormente. As tabelas comparativas não
aparecem na tela principal.

Material analisado: PDF local `Cabeamento de Fibra com Grafos.pdf`, seis slides,
fornecido pelo grupo. O PDF original não foi modificado.

## Diagnóstico e decisões

| Conteúdo dos slides | Implementação anterior | Ajuste realizado |
|---|---|---|
| Rack R, blocos A a F e dez dutos (slide 2) | Quatro cenários, com outros pesos e topologias | Cenário principal reproduz os dez trechos e seus pesos |
| Cabear tudo, Dijkstra e MST no mesmo grafo (slide 3) | Base mínima e reservas gulosas | Comparação principal agora usa exatamente as três alternativas dos slides |
| 490 m, 340 m e 240 m (slides 3 e 5) | Outros totais, dependendo do cenário | Valores calculados e verificados por testes, sem fixar resultados na interface |
| Kruskal com Union-Find (slide 4) | Implementado e demonstrado | Preservado, com controles para avançar, concluir e reiniciar a construção |
| Prim confirma a MST (slide 4) | Ausente | Implementado com heap; confirma 240 m |
| Dijkstra como projeto de caminhos mínimos (slide 3) | Calculava apenas uma rota dentro da rede selecionada | Implementada árvore de predecessores desde R; cabos compartilhados contam uma vez |
| D a 155 m na MST e 105 m no menor caminho (slide 6) | Não reproduzido no grafo anterior | Destino D por padrão, com trajetos e tabela comparativa por bloco |
| 51% e 29% de economia (slide 5) | Sem as bases numéricas do PDF | Cálculos reais: aproximadamente 51,02% e 29,41% |
| Redundância como extensão (slide 6) | Era o centro da demonstração | Funcionalidade preservada em roteiro separado de falhas e redundância |
| Steiner como trabalho futuro (slides 3 e 6) | Não implementado | Mantido como extensão conceitual explicitamente identificada |

O roteiro principal abre por padrão. A extensão anterior pode ser aberta pelo
seletor lateral ou pelo botão na aba **Limitações e extensões**.

## Dados e resultados reproduzidos

Arestas do grafo não direcionado:

| Aresta | Peso (m) |
|---|---:|
| R-A | 40 |
| R-B | 55 |
| R-C | 70 |
| A-B | 30 |
| A-D | 65 |
| B-C | 45 |
| B-E | 50 |
| C-F | 60 |
| D-E | 35 |
| E-F | 40 |

- Todos os trechos: **490 m**.
- Árvore de caminhos mínimos: R-A, R-B, R-C, A-D, B-E e C-F, total **340 m**.
- MST: A-B, D-E, R-A, E-F, B-C e B-E, total **240 m**.
- Economia de material vs. tudo: **250 m**, aproximadamente **51,02%**.
- Economia vs. árvore de caminhos mínimos: **100 m**, aproximadamente **29,41%**.
- D na MST: R-A-B-E-D, **155 m**.
- Menor caminho até D: R-A-D, **105 m**.

No projeto de Dijkstra, o comprimento instalado é a soma dos cabos distintos da
árvore de predecessores. Somar as distâncias dos seis blocos daria **505 m** e
contaria trechos compartilhados várias vezes: esse não é o total instalado.

## Ambiguidades e divergências que permanecem no PDF

1. **Parada de Kruskal:** o slide 4 diz parar com V-1 = 6 arestas, mas lista
   outras quatro rejeições após a conclusão. O algoritmo mantém a parada correta.
   A interface identifica as quatro restantes como não analisadas; seriam rejeitadas
   por ciclos se a varredura continuasse. Sugestão para o slide: separar essas
   linhas sob “arestas restantes formariam ciclos”.
2. **Kruskal e grafos esparsos:** a preferência é razoável como escolha didática,
   mas não é uma superioridade universal. A implementação e as estruturas usadas
   determinam o desempenho. A interface deixa essa ressalva explícita.
3. **Steiner na capa:** a capa pode sugerir aplicação efetiva; os slides 3 e 6
   dizem que é extensão. O projeto segue essa definição de trabalho futuro.
   Sugestão de fala: “Steiner é uma possível extensão, não um algoritmo implementado”.
4. **“Máxima redundância”:** cabear tudo inclui todas as alternativas desse grafo,
   mas não garante proteção contra todas as falhas reais (equipamentos, energia,
   falhas múltiplas e dutos compartilhados).
5. **Economia:** o cenário é fictício. Os 51% comparam a alternativa explícita
   de instalar os dez trechos com a MST, não um orçamento de instalação real.
6. **Splitters:** pontos de Steiner não são automaticamente splitters físicos.
   Equipamentos exigiriam modelo adicional de custo, perdas e capacidade.
7. **Preenchimento:** capa ainda usa [Disciplina] e [Integrantes do grupo].

## Roteiro sugerido para apresentação

1. Abrir **Apresentação: MST e caminhos**, com os valores padrão.
2. Mostrar as alternativas de 490, 340 e 240 m.
3. Selecionar **Árvore mínima (Kruskal)** e ativar a construção passo a passo.
4. Avançar as seis arestas e explicar Union-Find e a união dos componentes.
5. Desativar o passo a passo e acompanhar o bloco D: 155 m na MST.
6. Selecionar **Caminhos mínimos (Dijkstra)**: D passa a 105 m, mas a rede usa 340 m.
7. Mostrar a confirmação de Prim e os percentuais da comparação.
8. Encerrar com as limitações. Se houver tempo, abrir a extensão de falhas no prédio.

## Organização da implementação

- `scenarios.py`: cenário dos slides e cenários anteriores preservados.
- `graph.py`: Kruskal original com Union-Find.
- `presentation_model.py`: Prim e árvore de caminhos mínimos por Dijkstra.
- `slides_ui.py`: demonstração principal alinhada ao PDF.
- `resilience.py`: Dijkstra por destino, DFS e reservas; extensão anterior preservada.
- `tests/test_presentation.py`: testes dos totais, caminhos, Prim, entradas e interface.

O PDF não foi reescrito. As observações acima devem ser consideradas na fala
ou em uma revisão posterior dos slides pelo grupo.
