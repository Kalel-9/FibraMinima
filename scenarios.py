"""Ambientes para comparar cabeamento, sentido das ligações e redundância."""

from dataclasses import dataclass
from graph import Edge, Vertex, sample_graph


@dataclass(frozen=True)
class Scenario:
    name: str
    vertices: list[Vertex]
    edges: list[Edge]
    directed: bool


@dataclass(frozen=True)
class Floor:
    level: int
    racks: tuple[str, ...]


@dataclass(frozen=True)
class BuildingScenario(Scenario):
    floors: tuple[Floor, ...]
    root: str


def four_floor_building() -> BuildingScenario:
    """Prédio com 2, 3, 4 e 5 racks, ligado por duas prumadas independentes.

    Anéis internos nos andares 2 a 4 e duas ligações entre andares
    permitem contornar qualquer rompimento individual dos 19 cabos.
    O rack principal 1A fica no primeiro andar.
    """
    floors = tuple(Floor(level, tuple(f"{level}{chr(65 + i)}" for i in range(level + 1)))
                   for level in range(1, 5))
    vertices = [Vertex(rack, 2 + 8 * i / (len(floor.racks) - 1), (floor.level - 1) * 2.4)
                for floor in floors for i, rack in enumerate(floor.racks)]
    edges = [
        Edge("1A", "1B", 20),
        Edge("2A", "2B", 10), Edge("2B", "2C", 12), Edge("2C", "2A", 28),
        Edge("3A", "3B", 8), Edge("3B", "3C", 11), Edge("3C", "3D", 9), Edge("3D", "3A", 35),
        Edge("4A", "4B", 7), Edge("4B", "4C", 10), Edge("4C", "4D", 8),
        Edge("4D", "4E", 12), Edge("4E", "4A", 44),
        # Prumada A (esquerda) e prumada B (direita).
        Edge("1A", "2A", 9), Edge("1B", "2C", 12),
        Edge("2A", "3A", 10), Edge("2C", "3D", 13),
        Edge("3A", "4A", 11), Edge("3D", "4E", 14),
    ]
    return BuildingScenario("Prédio de quatro andares", vertices, edges, False, floors, "1A")


def presentation_scenario() -> Scenario:
    """Grafo não direcionado dos slides 2 a 6, com os mesmos pesos."""
    vertices = [Vertex("R", 0, 2), Vertex("A", 2, 4), Vertex("B", 2, 2),
                Vertex("C", 2, 0), Vertex("D", 6, 4), Vertex("E", 6, 2), Vertex("F", 6, 0)]
    edges = [Edge("R", "A", 40), Edge("R", "B", 55), Edge("R", "C", 70),
             Edge("A", "B", 30), Edge("A", "D", 65), Edge("B", "C", 45),
             Edge("B", "E", 50), Edge("C", "F", 60), Edge("D", "E", 35), Edge("E", "F", 40)]
    return Scenario("Condomínio dos slides · Rack + 6 blocos", vertices, edges, False)


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
    floors = ["Rack", *[f"{i}º andar" for i in range(1, 6)]]
    building_vertices = [Vertex(name, 2.6, i) for i, name in enumerate(floors)]
    building_edges = [Edge(floors[i], floors[i + 1], 8 if i == 0 else 6) for i in range(5)]
    building_edges += [Edge(floors[0], floors[2], 16), Edge(floors[0], floors[3], 25),
                       Edge(floors[0], floors[4], 34), Edge(floors[0], floors[5], 44),
                       Edge(floors[1], floors[3], 15), Edge(floors[3], floors[5], 15),
                       Edge(floors[2], floors[4], 16)]
    return [Scenario("1 — Condomínio pequeno", vertices, edges, False),
            Scenario("2 — Condomínio médio", medium_vertices, medium_edges, True),
            Scenario("3 — Condomínio grande", large_vertices, large_edges, True),
            Scenario("4 — Prédio de cinco andares", building_vertices, building_edges, False)]
