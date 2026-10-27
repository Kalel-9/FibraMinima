# FibraMínima — três ambientes

Conectar todos os blocos a partir de um rack usando a menor quantidade total de cabo.
Informe preço por metro e distâncias dos trajetos; clique em **Encontrar melhor ligação**.

## Cenários

| Ambiente | Pontos | Conexões | Tipo | Algoritmo | Resultado padrão |
|---|---:|---:|---|---|---:|
| Condomínio pequeno | 3 | 3 | Não direcionado | Kruskal | 18 m |
| Condomínio médio | 5 | 8 | Direcionado | Enumeração exata de arborescências | 60 m |
| Condomínio grande | 7 | 15 | Direcionado | Enumeração exata de arborescências | 146 m |

Com o preço fictício de R$ 5/m: R$ 90, R$ 300 e R$ 730, respectivamente.
As distâncias são ilustrativas, editáveis e independem do desenho.

## Significado das setas

Nos ambientes 2 e 3, A → B permite alcançar B a partir de A, mas não o inverso.
O rack precisa alcançar todos os pontos seguindo as setas selecionadas.
A orientação é uma restrição didática do sentido de distribuição da rede,
não uma característica física do cabo. Arcos opostos são desenhados separados
para distinguir sentidos e pesos.

O objetivo é minimizar o total de cabo que conecta todos, não o caminho individual
mais curto de cada bloco ao rack. O modelo considera apenas cabo e preço uniforme
por metro, sem capacidade, equipamentos, mão de obra ou redundância.

## Algoritmos e complexidade

**Ambiente 1:** Kruskal encontra a árvore geradora mínima sem orientação.
Ordena arestas por peso e aceita conexões entre componentes diferentes.
Usa Union-Find e tem complexidade usual O(E log E).

**Ambientes 2 e 3:** Kruskal não resolve diretamente o problema direcionado.
Buscamos uma arborescência mínima com raiz no rack. Cada bloco recebe exatamente
um arco de entrada, enquanto o rack não recebe nenhum. Enumeramos todas essas
escolhas, descartamos as que não permitem alcançar todos desde o rack e escolhemos
a menor soma. Isso também descarta ciclos desconectados do rack.

Se d(v) é o número de arcos de entrada em cada bloco, há P = produto de d(v)
combinações: 16 no ambiente 2 e 216 no ambiente 3. A implementação custa
O(E + V × P). Pode crescer exponencialmente, portanto é destinada apenas aos
exemplos pequenos da aula. Não implementa Chu–Liu/Edmonds. Esse algoritmo seria
uma extensão adequada para grafos direcionados maiores.

Mais vértices, arcos e opções de entrada aumentam o tamanho da busca. Valores
numéricos maiores nos pesos, sozinhos, não aumentam o número de combinações.
Os resultados entre os cenários não são um benchmark de Kruskal contra enumeração:
são problemas diferentes, com grafos e restrições diferentes.

## Executar

Com Docker Desktop aberto em modo Linux:

```bash
docker compose up --build
```

Abra http://localhost:8501. Para encerrar: `docker compose down`.
O primeiro build precisa de internet. A porta fica acessível apenas no computador local.

Alternativa em Python 3.13 no PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m streamlit run app.py
```

## Organização

- `app.py`: seleção de ambiente, entradas e resultados.
- `scenarios.py`: os três grafos.
- `graph.py`: modelos e Kruskal.
- `directed.py`: enumeração exata da arborescência mínima.
- `visual.py`: grafos e setas com Plotly.
- `Dockerfile` e `compose.yaml`: execução em contêiner.

## Testes

```bash
python -m unittest discover -s tests -v
```

Os testes de interface exigem as dependências instaladas; sem Streamlit são ignorados.
Os testes direcionados verificam resultados, ciclos, sentido das ligações e desconexão.
