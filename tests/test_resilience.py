import unittest

from graph import Edge
from resilience import compare_plans, compare_plans_exact, reachable, shortest_route
from scenarios import environments


class ResilienceTests(unittest.TestCase):
    def test_building_compares_partial_and_full_protection(self):
        building = environments()[-1]
        ids = [v.id for v in building.vertices]
        cheapest, frontier = compare_plans_exact(ids, building.edges, False)
        self.assertEqual([(p.meters, p.worst_loss) for p in frontier],
                         [(32, 5), (42, 4), (48, 3), (57, 2), (64, 1), (72, 0)])
        self.assertEqual(len({p.edges for p in cheapest}), 3)
        cut = building.edges[0]
        self.assertEqual(reachable(cheapest[0].edges, False, failed=cut), {"Rack"})
        self.assertIsNone(shortest_route(cheapest[0].edges, False, ids[-1], failed=cut))
        robust = frontier[-1]
        before = shortest_route(robust.edges, False, ids[-1])
        after = shortest_route(robust.edges, False, ids[-1], failed=cut)
        self.assertNotEqual(before[0], after[0])
        self.assertNotIn(cut, after[1])
        for cable in robust.edges:
            self.assertEqual(reachable(robust.edges, False, failed=cable), set(ids))

    def test_directed_reverse_cable_cannot_repair_incoming_failure(self):
        inbound = Edge("Rack", "A", 2)
        outbound = Edge("A", "Rack", 1)
        onward = Edge("A", "B", 1)
        alternate = Edge("Rack", "B", 4)
        ids = ["Rack", "A", "B"]
        _, frontier = compare_plans_exact(ids, [inbound, outbound, onward, alternate], True)
        self.assertEqual([(p.meters, p.worst_loss) for p in frontier], [(3, 2), (6, 1)])
        self.assertEqual(reachable(frontier[-1].edges, True, failed=inbound), {"Rack", "B"})
        self.assertIsNone(shortest_route([outbound, alternate, onward], True, "A"))

    def test_rejects_unreachable_network(self):
        self.assertEqual(compare_plans(["Rack", "A"], [Edge("A", "Rack", 1)], True), ([], []))

    def test_greedy_alternatives_keep_base_and_reduce_losses(self):
        from graph import kruskal
        from directed import minimum_arborescence
        for scenario in environments():
            ids = [v.id for v in scenario.vertices]
            cheapest, plans = compare_plans(ids, scenario.edges, scenario.directed)
            base = (minimum_arborescence(ids, scenario.edges) if scenario.directed
                    else kruskal(ids, scenario.edges))
            self.assertEqual(set(cheapest[0].edges), set(base.selected))
            self.assertLessEqual(len(plans), 3)
            for first, second in zip(plans, plans[1:]):
                self.assertTrue(set(first.edges) < set(second.edges))
                self.assertLess(second.total_loss, first.total_loss)
                self.assertLessEqual(second.worst_loss, first.worst_loss)
            self.assertEqual(plans[-1].worst_loss, 0)
            for cable in plans[-1].edges:
                self.assertEqual(reachable(plans[-1].edges, scenario.directed, failed=cable), set(ids))
