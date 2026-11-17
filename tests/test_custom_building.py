import importlib.util
from pathlib import Path
from random import Random
import unittest
from unittest.mock import patch

from custom_building import build_custom_building
from failure_demo import calculate_network


class CustomBuildingTests(unittest.TestCase):
    def test_random_range_and_estimated_reserve_lengths(self):
        building = build_custom_building({1: 2, 2: 4, 3: 3}, rng=Random(7))
        by_key = {edge.key: edge.weight for edge in building.edges}
        self.assertEqual(len(building.vertices), 9)
        for floor in building.floors:
            adjacent = [by_key[tuple(sorted((a, b)))] for a, b in zip(floor.racks, floor.racks[1:])]
            self.assertTrue(all(8 <= weight <= 16 for weight in adjacent))
            if len(floor.racks) >= 3:
                self.assertEqual(by_key[tuple(sorted((floor.racks[0], floor.racks[-1])))], sum(adjacent))
        for lower, upper in zip(building.floors, building.floors[1:]):
            for a, b in ((lower.racks[0], upper.racks[0]), (lower.racks[-1], upper.racks[-1])):
                self.assertTrue(8 <= by_key[tuple(sorted((a, b)))] <= 16)

    def test_weights_stay_fixed_and_existing_cables_survive_expansion(self):
        first = build_custom_building({1: 2, 2: 4}, rng=Random(1))
        cache = {edge.key: edge.weight for edge in first.edges}
        unchanged = build_custom_building({1: 2, 2: 4}, previous=cache, rng=Random(99))
        self.assertEqual(first.edges, unchanged.edges)
        expanded = build_custom_building({1: 2, 2: 5, 3: 3}, previous=cache, rng=Random(4))
        shared = [edge for edge in expanded.edges if edge.key in cache]
        self.assertTrue(shared)
        self.assertTrue(all(edge.weight == cache[edge.key] for edge in shared))

    def test_every_single_cable_failure_preserves_connectivity(self):
        for counts in ({1: 2, 2: 2}, {1: 2, 2: 4}, {1: 3, 2: 5, 3: 2},
                       {level: 10 for level in range(1, 9)}):
            building = build_custom_building(counts, rng=Random(3))
            ids = [vertex.id for vertex in building.vertices]
            for cable in building.edges:
                with self.subTest(counts=counts, cable=cable.key):
                    network = calculate_network(ids, building.edges, building.root, cable)
                    self.assertFalse(network.offline)
                    self.assertNotIn(cable, network.active)
                    self.assertEqual(len(network.active), len(ids) - 1)

    def test_invalid_inputs_are_rejected(self):
        for counts, low, high in (({1: 2}, 8, 16), ({1: 1, 2: 4}, 8, 16),
                                  ({0: 2, 2: 4}, 8, 16), ({1: 2, 2: 4}, 16, 8),
                                  ({1: 2, 3: 4}, 8, 16), ({2: 2, 3: 4}, 8, 16)):
            with self.subTest(counts=counts, low=low, high=high):
                with self.assertRaises(ValueError):
                    build_custom_building(counts, low, high)


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "Streamlit não instalado")
class CustomInterfaceTests(unittest.TestCase):
    def make_app(self):
        from streamlit.testing.v1 import AppTest
        return AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30).run()

    def test_break_and_price_changes_preserve_random_weights(self):
        app = self.make_app()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[5].value, "6 / 6")
        lengths = dict(app.session_state["custom_lengths"])
        with patch("failure_demo.random.choice", side_effect=lambda candidates: candidates[0]):
            app.button(key="custom_simple_break").click().run()
        self.assertFalse(app.exception)
        failure = app.session_state["custom_building4_failure"]
        self.assertEqual(app.metric[5].value, "6 / 6")
        app.number_input(key="custom_simple_price").set_value(10.0).run()
        app.selectbox(key="custom_building4_target_floor").select(1).run()
        self.assertFalse(app.exception)
        self.assertEqual(dict(app.session_state["custom_lengths"]), lengths)
        self.assertEqual(app.session_state["custom_building4_failure"], failure)
        self.assertEqual(app.metric[0].value, "129 m")
        self.assertEqual(app.metric[1].value, "R$ 645,00")
        app.button(key="custom_simple_restore").click().run()
        self.assertFalse(app.exception)
        self.assertTrue(app.button(key="custom_simple_restore").disabled)

    def test_floors_form_a_stack_without_changing_the_fixed_example(self):
        app = self.make_app()
        self.assertNotIn("custom_edit_floor", [element.key for element in app.number_input])
        self.assertEqual(app.selectbox(key="custom_new_racks").options, [str(n) for n in range(2, 11)])
        with patch("failure_demo.random.choice", side_effect=lambda candidates: candidates[0]):
            app.button(key="simple_break").click().run()
            app.button(key="custom_simple_break").click().run()
        fixed_failure = app.session_state["building4_failure"]
        lengths = dict(app.session_state["custom_lengths"])
        app.button(key="FormSubmitter:custom_floor_form-Salvar andar").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[5].value, "9 / 9")
        self.assertEqual(app.session_state["building4_failure"], fixed_failure)
        self.assertTrue(app.button(key="custom_simple_restore").disabled)
        self.assertEqual(app.selectbox(key="custom_building4_target_floor").options, ["3º andar", "2º andar", "1º andar"])
        self.assertEqual(app.selectbox(key="custom_building4_target_floor").value, 2)
        self.assertEqual(app.selectbox(key="custom_building4_target_2").value, "2D")
        self.assertTrue(all(app.session_state["custom_lengths"][key] == value for key, value in lengths.items()))
        self.assertEqual(dict(app.session_state["custom_floor_counts"]), {1: 2, 2: 4, 3: 3})
        app.selectbox(key="custom_new_racks").select(2)
        app.button(key="FormSubmitter:custom_floor_form-Salvar andar").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(dict(app.session_state["custom_floor_counts"]), {1: 2, 2: 4, 3: 3, 4: 2})
        self.assertEqual(app.metric[5].value, "11 / 11")
        app.selectbox(key="custom_building4_target_floor").select(4).run()
        app.button(key="custom_remove").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[5].value, "9 / 9")
        self.assertEqual(app.selectbox(key="custom_building4_target_floor").value, 3)
        self.assertEqual(app.selectbox(key="custom_building4_target_3").value, "3C")
        app.button(key="custom_remove").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[5].value, "6 / 6")
        self.assertEqual(app.selectbox(key="custom_building4_target_floor").value, 2)
        self.assertEqual(app.selectbox(key="custom_building4_target_2").value, "2D")
        self.assertTrue(app.button(key="custom_remove").disabled)
        self.assertEqual(app.session_state["building4_failure"], fixed_failure)
        app.selectbox(key="custom_new_racks").select(4)
        app.button(key="FormSubmitter:custom_floor_form-Salvar andar").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(dict(app.session_state["custom_floor_counts"]), {1: 2, 2: 4, 3: 4})
        self.assertEqual(app.metric[5].value, "10 / 10")

    def test_top_floor_limit_and_removal_keep_the_sequence(self):
        app = self.make_app()
        for level in range(3, 9):
            app.button(key="FormSubmitter:custom_floor_form-Salvar andar").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(sorted(app.session_state["custom_floor_counts"]), list(range(1, level + 1)))
        self.assertTrue(app.button(key="FormSubmitter:custom_floor_form-Salvar andar").disabled)
        app.button(key="custom_remove").click().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.button(key="FormSubmitter:custom_floor_form-Salvar andar").disabled)
        app.button(key="FormSubmitter:custom_floor_form-Salvar andar").click().run()
        self.assertEqual(sorted(app.session_state["custom_floor_counts"]), list(range(1, 9)))

    def test_old_sessions_with_gaps_are_renumbered(self):
        app = self.make_app()
        app.session_state["custom_floor_counts"] = {1: 2, 4: 4}
        app.run()
        self.assertFalse(app.exception)
        self.assertEqual(dict(app.session_state["custom_floor_counts"]), {1: 2, 2: 4})
        self.assertEqual(app.metric[5].value, "6 / 6")

    def test_applying_range_changes_only_custom_weights_and_validates_bounds(self):
        app = self.make_app()
        with patch("failure_demo.random.choice", side_effect=lambda candidates: candidates[0]):
            app.button(key="simple_break").click().run()
            app.button(key="custom_simple_break").click().run()
        fixed_failure = app.session_state["building4_failure"]
        app.number_input(key="custom_min").set_value(20)
        app.number_input(key="custom_max").set_value(20)
        app.button(key="FormSubmitter:custom_range_form-Aplicar faixa e sortear").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["custom_range"], (20, 20))
        self.assertEqual(set(app.session_state["custom_lengths"].values()), {20, 60})
        self.assertTrue(app.button(key="custom_simple_restore").disabled)
        self.assertEqual(app.session_state["building4_failure"], fixed_failure)
        lengths = dict(app.session_state["custom_lengths"])
        app.number_input(key="custom_min").set_value(30)
        app.button(key="FormSubmitter:custom_range_form-Aplicar faixa e sortear").click().run()
        self.assertFalse(app.exception)
        self.assertTrue(app.error)
        self.assertEqual(app.session_state["custom_range"], (20, 20))
        self.assertEqual(dict(app.session_state["custom_lengths"]), lengths)
