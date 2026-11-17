"""Compara projetos de cabeamento sob o rompimento de um cabo por vez."""

from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import combinations
from math import fsum, isfinite

from graph import Edge, kruskal
from directed import minimum_arborescence


@dataclass(frozen=True)
class Plan:
    edges: tuple[Edge, ...]
    meters: float
    worst_loss: int
    safe_failures: int
    total_loss: int = 0


def edge_id(edge: Edge, directed: bool) -> tuple[str, str]:
    return (edge.source, edge.target) if directed else edge.key


def _adjacency(edges, directed):
    adjacency = {}
    for edge in edges:
        adjacency.setdefault(edge.source, []).append((edge.target, edge))
        if not directed:
            adjacency.setdefault(edge.target, []).append((edge.source, edge))
    return adjacency


def _reachable(adjacency, root, failed=None):
    seen, pending = {root}, [root]
    while pending:
        for neighbor, edge in adjacency.get(pending.pop(), ()):
            if edge != failed and neighbor not in seen:
                seen.add(neighbor)
                pending.append(neighbor)
    return seen


def reachable(edges, directed, root="Rack", failed=None):
    return _reachable(_adjacency(edges, directed), root, failed)


def shortest_route(edges, directed, target, root="Rack", failed=None):
    """Dijkstra: retorna os pontos e cabos do trajeto ativo, ou None."""
    adjacency = _adjacency(edges, directed)
    best, parent, pending = {root: 0}, {}, [(0, root)]
    while pending:
        distance, vertex = heappop(pending)
        if distance != best[vertex]:
            continue
        if vertex == target:
            path, cables = [target], []
            while path[-1] != root:
                previous, edge = parent[path[-1]]
                cables.append(edge)
                path.append(previous)
            return tuple(reversed(path)), tuple(reversed(cables))
        for neighbor, edge in adjacency.get(vertex, ()):
            candidate = distance + edge.weight
            if edge != failed and candidate < best.get(neighbor, float("inf")):
                best[neighbor] = candidate
                parent[neighbor] = (vertex, edge)
                heappush(pending, (candidate, neighbor))
    return None


def _evaluate(vertices, edges, directed, root):
    """DFS testa o alcance antes e após a remoção de cada aresta."""
    adjacency = _adjacency(edges, directed)
    if _reachable(adjacency, root) != set(vertices):
        return None
    losses = [len(vertices) - len(_reachable(adjacency, root, edge)) for edge in edges]
    return Plan(tuple(edges), fsum(e.weight for e in edges), max(losses, default=0),
                losses.count(0), sum(losses))


def compare_plans(vertices, edges, directed, root="Rack"):
    """Base mínima e até duas alternativas por adição gulosa de reservas.

    A cada etapa, testa cada aresta ainda não instalada e escolhe a maior
    redução da soma de perdas por metro adicional. O pior impacto também
    não pode aumentar. Não garante custo mínimo para a redundância.
    """
    # Validações de pesos, pontos e duplicatas são compartilhadas com as bases.
    base = minimum_arborescence(vertices, edges, root) if directed else kruskal(vertices, edges)
    if not directed and root not in vertices:
        raise ValueError("Informe um rack cadastrado.")
    if not base.connected:
        return [], []
    current = _evaluate(vertices, base.selected, directed, root)
    history = [current]
    remaining = [e for e in edges if e not in current.edges]
    while remaining and current.worst_loss:
        candidates = []
        for edge in remaining:
            candidate = _evaluate(vertices, (*current.edges, edge), directed, root)
            gain = current.total_loss - candidate.total_loss
            if gain > 0 and candidate.worst_loss <= current.worst_loss:
                candidates.append((gain / edge.weight, -edge.weight, edge, candidate))
        if not candidates:
            break
        # Empates mantêm a ordem cadastrada dos trajetos.
        _, _, edge, current = max(candidates, key=lambda item: item[:2])
        history.append(current)
        remaining.remove(edge)
    # Base, primeira reserva e última melhoria; evita repetir projetos.
    alternatives = list(dict.fromkeys([history[0], history[min(1, len(history) - 1)], history[-1]]))
    return [history[0]], alternatives


def compare_plans_exact(vertices, edges, directed, root="Rack"):
    """Retorna até três alternativas econômicas e a fronteira custo × pior perda.

    Examina todos os subconjuntos com pelo menos V−1 cabos. Para cada rede
    conectada, remove cada cabo instalado e mede o alcance a partir do rack.
    A enumeração é exata e limitada aos cenários pequenos da demonstração.
    """
    ids = set(vertices)
    if not ids or len(ids) != len(vertices) or root not in ids:
        raise ValueError("Informe pontos únicos e um rack cadastrado.")
    if len(edges) > 16:
        raise ValueError("A comparação exata desta demonstração aceita até 16 cabos.")
    keys = set()
    for edge in edges:
        key = edge_id(edge, directed)
        if (edge.source not in ids or edge.target not in ids or edge.source == edge.target
                or key in keys or not isfinite(edge.weight) or edge.weight <= 0):
            raise ValueError("Use ligações válidas, sem duplicatas e com distâncias positivas.")
        keys.add(key)

    def rank(plan):
        return plan.meters, plan.worst_loss, -plan.safe_failures

    cheapest, by_loss = [], {}
    for size in range(len(ids) - 1, len(edges) + 1):
        for subset in combinations(edges, size):
            adjacency = _adjacency(subset, directed)
            if _reachable(adjacency, root) != ids:
                continue
            losses = [len(ids) - len(_reachable(adjacency, root, edge)) for edge in subset]
            plan = Plan(subset, fsum(e.weight for e in subset), max(losses, default=0), losses.count(0), sum(losses))
            if len(cheapest) < 3 or rank(plan) < rank(cheapest[-1]):
                cheapest = sorted([*cheapest, plan], key=rank)[:3]
            incumbent = by_loss.get(plan.worst_loss)
            if incumbent is None or rank(plan) < rank(incumbent):
                by_loss[plan.worst_loss] = plan

    frontier, lowest_loss = [], float("inf")
    for plan in sorted(by_loss.values(), key=rank):
        if plan.worst_loss < lowest_loss:
            frontier.append(plan)
            lowest_loss = plan.worst_loss
    return cheapest, frontier
