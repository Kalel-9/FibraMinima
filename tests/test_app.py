"""Verifica controles de apresentação, entradas e comparação da mesma ruptura."""

import importlib.util
from pathlib import Path
import unittest


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "Streamlit não instalado")
class InterfaceTests(unittest.TestCase):
    def app(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "academic_app.py"), default_timeout=30).run()
        app.radio(key="app_route").set_value("Extensão: falhas e redundância").run()
        return app

    def apply_values(self, app):
        next(b for b in app.button if b.label == "Aplicar valores e recalcular").click().run()

    def test_cost_input_and_calculation(self):
        app = self.app()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "18 m")
        self.assertEqual(app.metric[1].value, "R$ 90,00")
        name = "1 — Condomínio pequeno"
        app.number_input(key=f"price_{name}").set_value(10.0)
        self.apply_values(app)
        self.assertEqual(app.metric[1].value, "R$ 180,00")
        app.number_input(key=f"distance_{name}_Rack_A").set_value(30.0)
        self.apply_values(app)
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "33 m")
        self.assertEqual(app.metric[1].value, "R$ 330,00")

    def test_directed_environments(self):
        app = self.app()
        for name, total in [("2 — Condomínio médio", "60 m"), ("3 — Condomínio grande", "146 m")]:
            app.selectbox(key="view_environment").select(name).run()
            self.assertFalse(app.exception)
            self.assertEqual(app.metric[0].value, total)
            app.button(key="break_critical").click().run()
            self.assertFalse(app.exception)
            app.button(key="preset_Mais protegida").click().run()
            self.assertFalse(app.exception)
            self.assertTrue(app.success)
            self.assertFalse(app.warning)

    def test_building_failure_and_backup_path(self):
        app = self.app()
        name = "4 — Prédio de cinco andares"
        app.button(key="demo_building").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[1].value, "R$ 160,00")
        app.button(key="break_critical").click().run()
        self.assertIn("5 ponto(s) perderam", app.warning[0].value)
        self.assertEqual(app.metric[2].value, "0 / 5")
        rupture = app.session_state[f"view_failure_{name}"]
        app.button(key="preset_Mais protegida").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[1].value, "R$ 395,00")
        self.assertEqual(app.metric[2].value, "5 / 5")
        self.assertEqual(app.session_state[f"view_failure_{name}"], rupture)
        self.assertTrue(app.success)
        self.assertFalse(app.warning)
        app.button(key="restore").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state[f"view_failure_{name}"], "intact")
        app.toggle(key="view_show_available").set_value(True).run()
        self.assertFalse(app.exception)
        app.toggle(key="view_presentation").set_value(False).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[1].value, "R$ 395,00")


if __name__ == "__main__":
    unittest.main()
