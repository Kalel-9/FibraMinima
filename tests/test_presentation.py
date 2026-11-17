import importlib.util
import itertools
from pathlib import Path
import unittest

from graph import Edge, kruskal
from presentation_model import dijkstra_tree, prim
from resilience import shortest_route
from scenarios import presentation_scenario


class PresentationAlgorithmsTests(unittest.TestCase):
    def setUp(self):
        self.scenario = presentation_scenario()
        self.ids = [v.id for v in self.scenario.vertices]
        self.edges = self.scenario.edges

    def test_slide_totals_and_routes(self):
        mst = kruskal(self.ids, self.edges)
        shortest = dijkstra_tree(self.ids, self.edges)
        self.assertEqual(sum(e.weight for e in self.edges), 490)
        self.assertEqual(shortest.total, 340)
        self.assertEqual(mst.total, 240)
        self.assertEqual(len(mst.selected), 6)
        self.assertEqual(len(mst.steps), 6)
        self.assertEqual({e.key for e in self.edges if e not in mst.selected},
                         {("B", "R"), ("C", "R"), ("A", "D"), ("C", "F")})
        self.assertEqual(shortest.distances["D"], 105)
        route = shortest_route(mst.selected, False, "D", root="R")
        self.assertEqual(route[0], ("R", "A", "B", "E", "D"))
        self.assertEqual(sum(e.weight for e in route[1]), 155)
        self.assertAlmostEqual((490 - mst.total) / 490 * 100, 51.02040816)
        self.assertAlmostEqual((340 - mst.total) / 340 * 100, 29.41176470)

    def test_prim_against_exhaustive_spanning_tree_oracle(self):
        nodes = ["R", "A", "B", "C"]
        edges = [Edge("R", "A", 5), Edge("R", "B", 2), Edge("A", "B", 1),
                 Edge("A", "C", 3), Edge("B", "C", 3)]
        totals = []
        for candidate in itertools.combinations(edges, len(nodes) - 1):
            if all(shortest_route(candidate, False, v, root="R") for v in nodes):
                totals.append(sum(e.weight for e in candidate))
        self.assertEqual(prim(nodes, edges).total, min(totals))
        self.assertEqual(prim(self.ids, self.edges).total, 240)

    def test_dijkstra_tree_counts_shared_edges_once(self):
        edges = [Edge("R", "A", 1), Edge("A", "B", 1), Edge("A", "C", 1), Edge("R", "C", 9)]
        tree = dijkstra_tree(["R", "A", "B", "C"], edges)
        self.assertEqual(tree.total, 3)
        self.assertEqual(sum(tree.distances.values()), 5)
        for node in tree.distances:
            expected = shortest_route(edges, False, node, root="R")
            self.assertEqual(sum(e.weight for e in expected[1]), tree.distances[node])

    def test_disconnected_and_invalid_graph(self):
        self.assertFalse(prim(["R", "A", "B"], [Edge("R", "A", 1)]).connected)
        self.assertNotIn("B", dijkstra_tree(["R", "A", "B"], [Edge("R", "A", 1)]).distances)
        for algorithm in (prim, dijkstra_tree):
            with self.assertRaises(ValueError):
                algorithm(["R", "A"], [Edge("R", "A", -1)])


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "Streamlit não instalado")
class PresentationInterfaceTests(unittest.TestCase):
    def app(self):
        from streamlit.testing.v1 import AppTest
        return AppTest.from_file(str(Path(__file__).resolve().parents[1] / "academic_app.py"), default_timeout=30).run()

    def test_default_view_and_three_alternatives(self):
        app = self.app()
        self.assertFalse(app.exception)
        self.assertEqual(app.radio(key="app_route").value, "Apresentação: MST e caminhos")
        self.assertEqual(app.metric[0].value, "240 m")
        app.button(key="slides_choose_Cabear tudo").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "490 m")
        app.button(key="slides_choose_Caminhos mínimos (Dijkstra)").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "340 m")

    def test_walkthrough_edit_restore_and_extension(self):
        app = self.app()
        app.toggle(key="slides_walk").set_value(True).run()
        self.assertFalse(app.exception)
        app.button(key="slides_next").click().run()
        self.assertIn("A ↔ B", app.info[0].value)
        self.assertEqual(app.session_state["slides_step"], 1)
        app.button(key="slides_finish").click().run()
        self.assertEqual(app.session_state["slides_step"], 6)
        app.button(key="slides_choose_Caminhos mínimos (Dijkstra)").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "340 m")
        app.button(key="slides_choose_Árvore mínima (Kruskal)").click().run()
        app.number_input(key="slides_distance_R_A").set_value(140.0)
        next(b for b in app.button if b.label == "Aplicar valores").click().run()
        self.assertFalse(app.exception)
        self.assertNotEqual(app.metric[0].value, "240 m")
        app.button(key="slides_reset").click().run()
        self.assertEqual(app.metric[0].value, "240 m")
        app.button(key="slides_open_extension").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.radio(key="app_route").value, "Extensão: falhas e redundância")
