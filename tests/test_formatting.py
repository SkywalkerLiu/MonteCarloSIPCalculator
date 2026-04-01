from __future__ import annotations

import unittest

from app.ui.formatting import format_currency


class FormattingTests(unittest.TestCase):
    def test_compact_currency_thresholds(self) -> None:
        self.assertEqual(format_currency(850), "$850")
        self.assertEqual(format_currency(12_500), "$12.5K")
        self.assertEqual(format_currency(125_000), "$125K")
        self.assertEqual(format_currency(2_400_000), "$2.4M")
        self.assertEqual(format_currency(1_100_000_000), "$1.1B")

    def test_negative_currency_uses_leading_minus(self) -> None:
        self.assertEqual(format_currency(-2_500), "-$2.5K")


if __name__ == "__main__":
    unittest.main()
