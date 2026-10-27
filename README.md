# FibraMínima — demonstração mínima

Objetivo: conectar um rack e dois blocos usando a menor quantidade de cabo.

## Como demonstrar

1. Informe o preço do cabo por metro: exemplo fictício de R$ 5.
2. Informe a distância de cada trajeto permitido: Rack–A = 10 m,
   Rack–B = 25 m e A–B = 8 m.
3. Clique em **Encontrar melhor ligação**.
4. O grafo destaca A–B e Rack–A, totalizando **18 m e R$ 90**.

Aumente Rack–A para 30 m: a solução passa a usar Rack–B e A–B,
com **33 m e R$ 165** quando o preço é R$ 5/m.
Mudar apenas o preço por metro altera o custo, mas não as ligações escolhidas.

## Modelagem

- Vértices: rack e blocos A e B.
- Arestas: trajetos permitidos para passar cabo.
- Peso: comprimento do trajeto, em metros (não a distância visual no desenho).
- Kruskal escolhe as menores arestas sem formar ciclos até conectar todos os pontos.
- Resultado: árvore geradora mínima, com duas arestas para três vértices.
- Custo do cabo: soma das distâncias escolhidas × preço uniforme por metro.

A demonstração considera apenas o custo do cabo, sem equipamentos, mão de obra,
capacidade ou redundância. Não calcula uma rota entre dois pontos: conecta todos.

## Executar com Docker

Com o Docker Desktop iniciado em modo de contêineres Linux:

```bash
docker compose up --build
```

Abra http://localhost:8501. Para encerrar: `docker compose down`.
O primeiro build requer internet. A aplicação fica acessível apenas no computador local.

## Executar em Python (opcional)

Python 3.13, no PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m streamlit run app.py
```

## Código

- `app.py`: preço por metro, três distâncias, botão e resultado.
- `graph.py`: cenário e Kruskal com Union-Find, complexidade usual O(E log E).
- `visual.py`: desenho do grafo e formatação de valores.
- `Dockerfile` e `compose.yaml`: execução em contêiner.

Os passos internos do algoritmo continuam disponíveis para futuras melhorias.

## Testes

```bash
python -m unittest discover -s tests -v
```

O teste de interface requer as dependências instaladas; sem Streamlit é ignorado.
