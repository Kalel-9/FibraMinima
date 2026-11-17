"""Gera um prédio de simulação com pesos sorteados e reservas automáticas."""

from math import isfinite
from random import Random

from graph import Edge, Vertex
from scenarios import BuildingScenario, Floor


MIN_FLOORS = 2
MAX_FLOORS = 8
MIN_RACKS = 2
MAX_RACKS = 10
MIN_DISTANCE = 1
MAX_DISTANCE = 1000
DEFAULT_DISTANCE_RANGE = (8, 16)


def _validate_configuration(counts: dict[int, int], minimum: int, maximum: int) -> None:
    if not MIN_FLOORS <= len(counts) <= MAX_FLOORS:
        raise ValueError("Use de 2 a 8 andares para manter as duas prumadas.")
    if any(
        type(level) is not int
        or not 1 <= level <= MAX_FLOORS
        or type(count) is not int
        or not MIN_RACKS <= count <= MAX_RACKS
        for level, count in counts.items()
    ):
        raise ValueError("Informe andares de 1 a 8 e de 2 a 10 racks em cada andar.")
    if set(counts) != set(range(1, len(counts) + 1)):
        raise ValueError("Os andares devem ser consecutivos, começando pelo 1º, sem pular nenhum.")
    if (
        type(minimum) is not int
        or type(maximum) is not int
        or not MIN_DISTANCE <= minimum <= maximum <= MAX_DISTANCE
    ):
        raise ValueError("Use uma faixa inteira de 1 a 1000 metros, com mínimo ≤ máximo.")


def build_custom_building(
    counts: dict[int, int],
    minimum: int = DEFAULT_DISTANCE_RANGE[0],
    maximum: int = DEFAULT_DISTANCE_RANGE[1],
    previous: dict[tuple[str, str], float] | None = None,
    rng: Random | None = None,
) -> BuildingScenario:
    """Mantém os pesos existentes; sorteia apenas novos trechos comuns.

    Liga racks vizinhos, fecha um anel quando há três ou mais racks no andar,
    e conecta os extremos de andares sucessivos por duas prumadas. O cabo de
    fechamento é estimado pela soma dos trechos vizinhos, em rota independente.
    """
    _validate_configuration(counts, minimum, maximum)
    previous = previous or {}
    rng = rng or Random()
    floors = tuple(
        Floor(level, tuple(f"{level}{chr(65 + index)}" for index in range(counts[level])))
        for level in sorted(counts)
    )
    vertices = [
        Vertex(rack, 2 + 8 * index / (len(floor.racks) - 1), position * 2.4)
        for position, floor in enumerate(floors)
        for index, rack in enumerate(floor.racks)
    ]
    edges: list[Edge] = []

    def cable(source: str, target: str) -> Edge:
        key = tuple(sorted((source, target)))
        stored_length = previous.get(key)
        if stored_length is not None and isfinite(stored_length) and minimum <= stored_length <= maximum:
            weight = stored_length
        else:
            weight = rng.randint(minimum, maximum)
        return Edge(source, target, weight)

    for floor in floors:
        adjacent = [cable(a, b) for a, b in zip(floor.racks, floor.racks[1:])]
        edges.extend(adjacent)
        if len(floor.racks) >= 3:
            edges.append(Edge(floor.racks[-1], floor.racks[0], sum(e.weight for e in adjacent)))
    for lower, upper in zip(floors, floors[1:]):
        edges.append(cable(lower.racks[0], upper.racks[0]))
        edges.append(cable(lower.racks[-1], upper.racks[-1]))
    return BuildingScenario("Meu prédio", vertices, edges, False, floors, floors[0].racks[0])
