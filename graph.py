"""Modelagem do condomínio e Kruskal, sem dependências de interface."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Vertex:
    id: str
    x: float
    y: float


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    weight: float

    @property
    def key(self) -> tuple[str, str]:
        # A–B e B–A representam o mesmo trajeto não direcionado.
        return tuple(sorted((self.source, self.target)))


@dataclass(frozen=True)
class Step:
    edge: Edge
    accepted: bool
    components: int
    total: float

    @property
    def explanation(self) -> str:
        route = f"{self.edge.source} ↔ {self.edge.target} (peso {self.edge.weight:g})"
        if self.accepted:
            return f"{route}: aceita, pois conecta componentes diferentes."
        return f"{route}: rejeitada, pois formaria um ciclo."


@dataclass(frozen=True)
class Result:
    selected: tuple[Edge, ...]
    steps: tuple[Step, ...]
    total: float
    connected: bool
    components: int


class UnionFind:
    """Conjuntos disjuntos com compressão de caminho e união por tamanho."""

    def __init__(self, vertices: list[str]):
        self.parent = {v: v for v in vertices}
        self.size = {v: 1 for v in vertices}

    def find(self, vertex: str) -> str:
        while vertex != self.parent[vertex]:
            self.parent[vertex] = self.parent[self.parent[vertex]]
            vertex = self.parent[vertex]
        return vertex

    def union(self, a: str, b: str) -> bool:
        a, b = self.find(a), self.find(b)
        if a == b:
            return False
        if self.size[a] < self.size[b]:
            a, b = b, a
        self.parent[b] = a
        self.size[a] += self.size[b]
        return True


def kruskal(vertices: list[str], edges: list[Edge]) -> Result:
    """Retorna MST ou floresta mínima se o grafo estiver desconectado.

    Ordenação: O(E log E). Union-Find: O(E α(V)).
    Os pesos representam distâncias e precisam ser finitos e positivos neste domínio.
    """
    vertex_ids = set(vertices)
    if not vertices or len(vertex_ids) != len(vertices):
        raise ValueError("Informe ao menos um vértice, sem identificadores repetidos.")
    seen = set()
    for edge in edges:
        if edge.source not in vertex_ids or edge.target not in vertex_ids:
            raise ValueError("Toda aresta precisa conectar vértices cadastrados.")
        if edge.source == edge.target:
            raise ValueError("Um trajeto não pode conectar um ponto a ele mesmo.")
        if not isfinite(edge.weight) or edge.weight <= 0:
            raise ValueError("As distâncias precisam ser finitas e maiores que zero.")
        if edge.key in seen:
            raise ValueError("Não cadastre o mesmo trajeto mais de uma vez.")
        seen.add(edge.key)

    sets = UnionFind(vertices)
    selected, steps = [], []
    total, components = 0.0, len(vertices)
    for edge in sorted(edges, key=lambda e: (e.weight, e.key)):
        if components == 1:
            break
        accepted = sets.union(edge.source, edge.target)
        if accepted:
            selected.append(edge)
            total += edge.weight
            components -= 1
        steps.append(Step(edge, accepted, components, total))
    return Result(tuple(selected), tuple(steps), total, components == 1, components)


def sample_graph() -> tuple[list[Vertex], list[Edge]]:
    vertices = [
        Vertex("Rack", 0, 2), Vertex("A", 6, 3.4), Vertex("B", 6, 0.6),
    ]
    edges = [
        Edge("Rack", "A", 10), Edge("Rack", "B", 25), Edge("A", "B", 8),
    ]
    return vertices, edges
