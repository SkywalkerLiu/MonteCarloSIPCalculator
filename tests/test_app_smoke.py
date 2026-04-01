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
        finally:
            window.close()
            app.processEvents()
