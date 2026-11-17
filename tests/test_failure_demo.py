import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

from failure_demo import calculate_network, random_break
from graph import Edge
from resilience import shortest_route
from scenarios import environments, four_floor_building, presentation_scenario


class RandomFailureTests(unittest.TestCase):
    def test_every_single_failure_keeps_all_points_connected(self):
        for scenario in (environments()[-1], presentation_scenario(), four_floor_building()):
            ids = [v.id for v in scenario.vertices]
            root = ids[0]
            base = calculate_network(ids, scenario.edges, root)
            for cable in scenario.edges:
                with self.subTest(environment=scenario.name, cable=cable):
                    result = calculate_network(ids, scenario.edges, root, cable)
                    self.assertFalse(result.offline)
                    self.assertNotIn(cable, result.active)
                    self.assertEqual(len(result.active), len(ids) - 1)
                    self.assertEqual(result.installed_meters, base.installed_meters)
                    self.assertGreaterEqual(result.active_meters, base.active_meters)
                    for vertex in ids:
                        self.assertIsNotNone(shortest_route(result.active, False, vertex, root=root))

    def test_building_uses_installed_reserve_without_new_installation(self):
        scenario = environments()[-1]
        ids = [v.id for v in scenario.vertices]
        result = calculate_network(ids, scenario.edges, "Rack", scenario.edges[0])
        self.assertEqual(result.installed_meters, 197)
        self.assertEqual(result.active_meters, 40)
        route = shortest_route(result.active, False, "5º andar")
        self.assertEqual(route[0], ("Rack", "2º andar", "3º andar", "4º andar", "5º andar"))

    def test_random_choice_is_limited_to_active_cables(self):
        active = (Edge("Rack", "A", 1), Edge("A", "B", 2))
        with patch("failure_demo.random.choice", return_value=active[1]) as choose:
            self.assertEqual(random_break(active), active[1])
            choose.assert_called_once_with(active)
        with self.assertRaises(ValueError):
            random_break(())

    def test_four_floors_have_distinct_rack_and_cable_counts(self):
        building = four_floor_building()
        self.assertEqual([len(f.racks) for f in building.floors], [2, 3, 4, 5])
        self.assertEqual([sum(e.source in f.racks and e.target in f.racks for e in building.edges)
                          for f in building.floors], [1, 3, 4, 5])
        self.assertEqual(len(building.vertices), 14)
        self.assertEqual(len(building.edges), 19)
        floor_of = {rack: f.level for f in building.floors for rack in f.racks}
        inter_floor = [e for e in building.edges if floor_of[e.source] != floor_of[e.target]]
        self.assertEqual(len(inter_floor), 6)
        for level in (1, 2, 3):
            shafts = [e for e in inter_floor if floor_of[e.source] == level]
            self.assertEqual(len({e.source for e in shafts}), 2)
            self.assertEqual(len({e.target for e in shafts}), 2)
            self.assertTrue(all(floor_of[e.target] == level + 1 for e in shafts))

    def test_four_floor_backbone_failure_uses_prepared_other_shaft(self):
        building = four_floor_building()
        ids = [v.id for v in building.vertices]
        cable = next(e for e in building.edges if e.source == "1A" and e.target == "2A")
        before = calculate_network(ids, building.edges, building.root)
        after = calculate_network(ids, building.edges, building.root, cable)
        self.assertEqual(before.active_meters, 129)
        self.assertEqual(after.active_meters, 140)
        self.assertEqual(before.installed_meters, 283)
        self.assertEqual(after.installed_meters, 283)
        route = shortest_route(after.active, False, "4E", root=building.root)
        self.assertEqual(route[0][:3], ("1A", "1B", "2C"))
        self.assertFalse(after.offline)


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "Streamlit não instalado")
class SimpleInterfaceTests(unittest.TestCase):
    def test_break_again_and_restore_without_accumulating_failures(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30).run()
        self.assertFalse(app.exception)
        self.assertIsNotNone(app.button(key="simple_break"))
        self.assertIsNotNone(app.button(key="simple_restore"))
        self.assertFalse(app.dataframe)
        self.assertEqual([tab.label for tab in app.tabs], ["Prédio de exemplo", "Montar meu prédio"])
        self.assertFalse(app.sidebar.children)
        self.assertEqual(app.main.number_input(key="simple_price").value, 5.0)
        self.assertEqual(app.metric[0].value, "129 m")
        self.assertEqual(app.metric[1].value, "R$ 645,00")
        self.assertEqual(app.metric[2].value, "14 / 14")
        app.number_input(key="simple_price").set_value(10.0).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[1].value, "R$ 1.290,00")
        app.number_input(key="simple_price").set_value(5.0).run()
        with patch("failure_demo.random.choice", side_effect=lambda candidates: next(e for e in candidates if e.source == "1A" and e.target == "2A")):
            app.button(key="simple_break").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "140 m")
        self.assertEqual(app.metric[1].value, "R$ 700,00")
        self.assertEqual(app.metric[2].value, "14 / 14")
        first = app.session_state["building4_failure"]
        self.assertIsInstance(first, tuple)
        from types import SimpleNamespace
        app.session_state["building4_failure"] = SimpleNamespace(source="1A", target="2A", weight=9)
        app.run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "140 m")
        with patch("failure_demo.random.choice", side_effect=lambda candidates: candidates[0]):
            app.button(key="simple_break").click().run()
        self.assertFalse(app.exception)
        self.assertNotEqual(app.session_state["building4_failure"], first)
        self.assertEqual(app.metric[2].value, "14 / 14")
        app.button(key="simple_restore").click().run()
        self.assertEqual(app.metric[0].value, "129 m")
        self.assertTrue(app.button(key="simple_restore").disabled)
        app.selectbox(key="building4_target_floor").select(2).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.selectbox(key="building4_target_2").value, "2C")
        app.selectbox(key="building4_target_floor").select(1).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.selectbox(key="building4_target_1").value, "1B")
        self.assertEqual(app.metric[2].value, "14 / 14")
