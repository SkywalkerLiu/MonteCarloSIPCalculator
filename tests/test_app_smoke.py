from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow
from app.ui.theme import apply_theme


class AppSmokeTests(unittest.TestCase):
    def test_main_window_constructs_offscreen(self) -> None:
        app = QApplication.instance() or QApplication([])
        apply_theme(app)

        window = MainWindow()
        try:
            window.show()
            app.processEvents()

            self.assertEqual(window.windowTitle(), "蒙特卡洛定投计算器")
            self.assertTrue(bool(window.windowFlags() & Qt.WindowType.FramelessWindowHint))
            self.assertIsNotNone(window.title_bar)
            self.assertEqual(window.title_bar.title_label.text(), "蒙特卡洛定投计算器")
            self.assertEqual(window.minimumWidth(), 1360)
            self.assertEqual(window.minimumHeight(), 920)
            self.assertEqual(window.still_life.minimumHeight(), window.still_life.maximumHeight())
            self.assertEqual(window.still_life.minimumHeight(), 180)
            self.assertEqual(window.chart_stack.minimumHeight(), 470)
            self.assertEqual(window.paths_chart.canvas.minimumHeight(), 390)
            self.assertEqual(window.current_holding_input.value(), 0.0)
            self.assertEqual(window.monthly_investment_input.value(), 1500.0)
            self.assertEqual(window.expected_return_input.value(), 15.0)
            self.assertEqual(window.investment_years_input.value(), 30)
            self.assertEqual(window.crash_drawdown_input.value(), 50.0)
            self.assertEqual(window.crash_interval_input.value(), 15.0)
            self.assertEqual(window.annual_volatility_input.value(), 20.0)

            window.advanced_section.toggle_button.setChecked(True)
            app.processEvents()

            self.assertEqual(window.control_scroll_area.verticalScrollBar().maximum(), 0)
        finally:
            window.close()
            app.processEvents()
