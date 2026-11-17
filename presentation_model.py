"""Prim e árvore de caminhos mínimos: comparação do mesmo grafo dos slides."""

from dataclasses import dataclass
from heapq import heappop, heappush
from math import fsum, isfinite

from graph import Edge


@dataclass(frozen=True)
class Tree:
    selected: tuple[Edge, ...]
    total: float
    connected: bool


@dataclass(frozen=True)
class ShortestTree:
    selected: tuple[Edge, ...]
    total: float
    distances: dict[str, float]
    settled: tuple[str, ...]


def _adjacency(vertices, edges, root):
    ids = set(vertices)
    if not ids or len(ids) != len(vertices) or root not in ids:
        raise ValueError("Informe vértices únicos e um rack cadastrado.")
    adjacency, seen = {v: [] for v in vertices}, set()
    for edge in edges:
        if (edge.source not in ids or edge.target not in ids or edge.source == edge.target
                or edge.key in seen or not isfinite(edge.weight) or edge.weight <= 0):
            raise ValueError("Use arestas válidas, sem duplicatas e com pesos positivos.")
        seen.add(edge.key)
        adjacency[edge.source].append((edge.target, edge))
        adjacency[edge.target].append((edge.source, edge))
    return adjacency


def dijkstra_tree(vertices: list[str], edges: list[Edge], root: str = "R") -> ShortestTree:
    """Uma execução de Dijkstra gera a árvore de predecessores desde o rack.

    Soma apenas os cabos distintos da árvore, não as distâncias de todos os
    caminhos. Trechos compartilhados são instalados uma única vez.
    """
    adjacency = _adjacency(vertices, edges, root)
    distances, parents, settled, queue = {root: 0.0}, {}, [], [(0.0, root)]
    while queue:
        distance, vertex = heappop(queue)
        if distance != distances[vertex]:
            continue
        settled.append(vertex)
        for neighbor, edge in adjacency[vertex]:
            candidate = distance + edge.weight
            if candidate < distances.get(neighbor, float("inf")):
                distances[neighbor] = candidate
                parents[neighbor] = edge
                heappush(queue, (candidate, neighbor))
    selected = tuple(parents[v] for v in vertices if v in parents)
    return ShortestTree(selected, fsum(e.weight for e in selected), distances, tuple(settled))


def prim(vertices: list[str], edges: list[Edge], root: str = "R") -> Tree:
    """Prim com lista de adjacência e heap, O(E log V) em grafo simples conectado."""
    adjacency = _adjacency(vertices, edges, root)
    by_key = {e.key: e for e in edges}
    visited, selected, queue = {root}, [], []

    def expand(vertex):
        for neighbor, edge in adjacency[vertex]:
            if neighbor not in visited:
                heappush(queue, (edge.weight, vertex, neighbor))

    expand(root)
    while queue and len(visited) < len(vertices):
        _, source, target = heappop(queue)
        if target in visited:
            continue
        selected.append(by_key[tuple(sorted((source, target)))])
        visited.add(target)
        expand(target)
    return Tree(tuple(selected), fsum(e.weight for e in selected), len(visited) == len(vertices))
