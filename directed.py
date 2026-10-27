"""Arborescência mínima saindo do rack por enumeração exata.

Não é Kruskal nem Dijkstra. Adequado apenas aos cenários pequenos da aula.
"""

from dataclasses import dataclass
from itertools import product
from math import isfinite
from graph import Edge


@dataclass(frozen=True)
class DirectedResult:
    selected: tuple[Edge, ...]
    total: float
    connected: bool
    candidates: int


def minimum_arborescence(vertices: list[str], edges: list[Edge], root: str = "Rack") -> DirectedResult:
    """Escolhe uma entrada por vértice não raiz e testa alcance desde a raiz.

    Cada arborescência tem exatamente uma entrada por vértice não raiz.
    Enumerar todas as escolhas e tomar a mais barata que alcança todos os
    vértices é exato, inclusive com ciclos e arcos de sentidos opostos.
    Custo: O(E + V * produto dos graus de entrada dos vértices não raiz).
    """
    ids = set(vertices)
    if not ids or len(ids) != len(vertices) or root not in ids:
        raise ValueError("Informe vértices únicos e um rack cadastrado.")
    incoming = {v: [] for v in vertices if v != root}
    seen = set()
    for edge in edges:
        key = (edge.source, edge.target)
        if edge.source not in ids or edge.target not in ids or edge.source == edge.target:
            raise ValueError("Arco inválido: confira os pontos de origem e destino.")
        if not isfinite(edge.weight) or edge.weight <= 0 or key in seen:
            raise ValueError("Use pesos positivos e finitos, sem arcos repetidos.")
        seen.add(key)
        if edge.target != root:
            incoming[edge.target].append(edge)
    if any(not options for options in incoming.values()):
        return DirectedResult((), 0, False, 0)

    best, best_total, count = (), float("inf"), 0
    for candidate in product(*incoming.values()):
        count += 1
        adjacency = {v: [] for v in vertices}
        for edge in candidate:
            adjacency[edge.source].append(edge.target)
        reached, pending = {root}, [root]
        while pending:
            for target in adjacency[pending.pop()]:
                if target not in reached:
                    reached.add(target)
                    pending.append(target)
        total = sum(edge.weight for edge in candidate)
        if reached == ids and total < best_total:
            best, best_total = candidate, total
    connected = best_total != float("inf")
    return DirectedResult(tuple(best), best_total if connected else 0, connected, count)
