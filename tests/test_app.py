"""Verifica distâncias, preço por metro e cálculo do custo."""

import importlib.util
from pathlib import Path
import unittest


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "Streamlit não instalado")
class InterfaceTests(unittest.TestCase):
    def test_cost_input_and_calculation(self):
        from streamlit.testing.v1 import AppTest

        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(len(app.number_input), 4)
        self.assertEqual(len(app.button), 1)
        self.assertFalse(app.success)
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "18 m")
        self.assertEqual(app.metric[1].value, "R$ 90,00")
        app.number_input[0].set_value(10.0)
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "18 m")
        self.assertEqual(app.metric[1].value, "R$ 180,00")
        app.number_input[1].set_value(30.0)
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "33 m")
        self.assertEqual(app.metric[1].value, "R$ 330,00")


if __name__ == "__main__":
    unittest.main()
