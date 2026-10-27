import unittest
from graph import Edge
from directed import minimum_arborescence
from scenarios import environments


class DirectedTests(unittest.TestCase):
    def test_scenarios(self):
        for scenario, expected, count in zip(environments()[1:], (60, 146), (16, 216)):
            result = minimum_arborescence([v.id for v in scenario.vertices], scenario.edges)
            self.assertTrue(result.connected)
            self.assertEqual(result.total, expected)
            self.assertEqual(result.candidates, count)
            self.assertEqual(len(result.selected), len(scenario.vertices) - 1)

    def test_cycle_cannot_replace_connection_from_root(self):
        result = minimum_arborescence(["Rack", "A", "B"], [
            Edge("Rack", "A", 10), Edge("Rack", "B", 20),
            Edge("A", "B", 1), Edge("B", "A", 1)])
        self.assertTrue(result.connected)
        self.assertEqual(result.total, 11)
        self.assertIn(Edge("A", "B", 1), result.selected)
        self.assertNotIn(Edge("B", "A", 1), result.selected)

    def test_wrong_direction_and_disconnected_cycle(self):
        cases = [[Edge("A", "Rack", 1)],
                 [Edge("A", "B", 1), Edge("B", "A", 1)]]
        for edges in cases:
            result = minimum_arborescence(["Rack", "A", "B"], edges)
            self.assertFalse(result.connected)
            self.assertEqual(result.selected, ())

    def test_invalid(self):
        for edges in ([Edge("Rack", "A", -1)], [Edge("Rack", "X", 2)],
                      [Edge("Rack", "A", 1), Edge("Rack", "A", 2)]):
            with self.assertRaises(ValueError):
                minimum_arborescence(["Rack", "A"], edges)


if __name__ == "__main__":
    unittest.main()
