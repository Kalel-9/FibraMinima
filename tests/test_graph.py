import itertools
import unittest

from graph import Edge, kruskal, sample_graph


class KruskalTests(unittest.TestCase):
    def test_condominio(self):
        vertices, edges = sample_graph()
        result = kruskal([v.id for v in vertices], edges)
        self.assertTrue(result.connected)
        self.assertEqual(len(result.selected), 2)
        self.assertEqual(result.total, 18)

    def test_matches_exhaustive_search(self):
        # Oráculo independente: enumera árvores e verifica conectividade por busca.
        vertices = ["A", "B", "C", "D"]
        edges = [Edge("A", "B", 4), Edge("A", "C", 2), Edge("A", "D", 7),
                 Edge("B", "C", 1), Edge("B", "D", 3), Edge("C", "D", 3)]
        totals = []
        for candidate in itertools.combinations(edges, len(vertices) - 1):
            reached = {vertices[0]}
            for _ in vertices:
                for e in candidate:
                    if e.source in reached or e.target in reached:
                        reached.update((e.source, e.target))
            if reached == set(vertices):
                totals.append(sum(e.weight for e in candidate))
        self.assertEqual(kruskal(vertices, edges).total, min(totals))

    def test_disconnected(self):
        result = kruskal(["A", "B", "C"], [Edge("A", "B", 3)])
        self.assertFalse(result.connected)
        self.assertEqual(result.components, 2)
        self.assertEqual(result.total, 3)

    def test_single_vertex_and_no_edges(self):
        self.assertTrue(kruskal(["Rack"], []).connected)
        self.assertFalse(kruskal(["A", "B"], []).connected)

    def test_ties_are_deterministic(self):
        edges = [Edge("B", "C", 1), Edge("A", "C", 1), Edge("A", "B", 1)]
        self.assertEqual(kruskal(["A", "B", "C"], edges).selected,
                         kruskal(["A", "B", "C"], list(reversed(edges))).selected)

    def test_invalid_graphs(self):
        invalid = [([], []), (["A", "A"], []),
                   (["A", "B"], [Edge("A", "C", 1)]),
                   (["A"], [Edge("A", "A", 1)]),
                   (["A", "B"], [Edge("A", "B", float("nan"))]),
                   (["A", "B"], [Edge("A", "B", float("inf"))]),
                   (["A", "B"], [Edge("A", "B", 0)]),
                   (["A", "B"], [Edge("A", "B", -1)]),
                   (["A", "B"], [Edge("A", "B", 1), Edge("B", "A", 2)])]
        for vertices, edges in invalid:
            with self.subTest(vertices=vertices, edges=edges), self.assertRaises(ValueError):
                kruskal(vertices, edges)


if __name__ == "__main__":
    unittest.main()
