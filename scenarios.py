"""Três ambientes pequenos para comparar tamanho e orientação dos grafos."""

from dataclasses import dataclass
from graph import Edge, Vertex, sample_graph


@dataclass(frozen=True)
class Scenario:
    name: str
    vertices: list[Vertex]
    edges: list[Edge]
    directed: bool


def environments() -> list[Scenario]:
    vertices, edges = sample_graph()
    medium_vertices = [Vertex("Rack", 0, 2.5), Vertex("A", 3, 4),
                       Vertex("B", 3, 1), Vertex("C", 6, 4), Vertex("D", 6, 1)]
    medium_edges = [Edge("Rack", "A", 20), Edge("Rack", "B", 35),
                    Edge("A", "B", 12), Edge("B", "A", 16),
                    Edge("A", "C", 25), Edge("B", "C", 18),
                    Edge("B", "D", 30), Edge("C", "D", 10)]
    large_vertices = [Vertex("Rack", 0, 2.5), Vertex("A", 2, 4),
                      Vertex("B", 2, 1), Vertex("C", 4, 4), Vertex("D", 4, 1),
                      Vertex("E", 6, 4), Vertex("F", 6, 1)]
    large_edges = [Edge("Rack", "A", 40), Edge("Rack", "B", 60),
                   Edge("Rack", "C", 120), Edge("A", "B", 18),
                   Edge("B", "A", 22), Edge("A", "C", 30),
                   Edge("B", "D", 35), Edge("C", "D", 16),
                   Edge("D", "C", 20), Edge("C", "E", 28),
                   Edge("D", "F", 32), Edge("E", "F", 14),
                   Edge("F", "E", 19), Edge("B", "E", 90), Edge("A", "D", 65)]
    return [Scenario("1 — Condomínio pequeno", vertices, edges, False),
            Scenario("2 — Condomínio médio", medium_vertices, medium_edges, True),
            Scenario("3 — Condomínio grande", large_vertices, large_edges, True)]
