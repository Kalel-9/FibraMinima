"""Estado da rede preparada e recálculo após o rompimento de uma aresta."""

from dataclasses import dataclass
from math import fsum
import random

from graph import Edge, kruskal
from resilience import reachable


@dataclass(frozen=True)
class Network:
    active: tuple[Edge, ...]
    installed_meters: float
    active_meters: float
    offline: frozenset[str]
    failed: Edge | None


def calculate_network(vertices: list[str], installed: list[Edge], root: str,
                      failed: Edge | None = None) -> Network:
    """Recalcula a MST somente nos cabos já instalados que não romperam.

    O total instalado não muda: representa a infraestrutura paga antes da falha.
    O total ativo representa os trechos escolhidos para a árvore de distribuição.
    """
    if root not in vertices:
        raise ValueError("O rack de origem deve estar cadastrado.")
    if failed is not None and failed not in installed:
        raise ValueError("Só é possível romper um cabo instalado.")
    base = kruskal(vertices, installed)
    result = base if failed is None else kruskal(vertices, [e for e in installed if e != failed])
    offline = set(vertices) - reachable(result.selected, False, root=root)
    return Network(result.selected, fsum(e.weight for e in installed), result.total,
                   frozenset(offline), failed)


def random_break(active: tuple[Edge, ...]) -> Edge:
    """Sorteia um cabo em uso. O cabo da falha anterior não está na árvore ativa."""
    if not active:
        raise ValueError("Não há cabo ativo para romper.")
    return random.choice(active)
