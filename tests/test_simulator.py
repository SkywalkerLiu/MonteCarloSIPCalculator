from __future__ import annotations

import math
import unittest

import numpy as np

from app.core import SimulationConfig, run_monte_carlo


class SimulationTests(unittest.TestCase):
    def test_invalid_config_rejected(self) -> None:
        config = SimulationConfig(
            current_holding=-1,
            monthly_investment=1000,
            expected_annual_return=0.08,
            investment_years=20,
            crash_drawdown=0.35,
            crash_interval_years=70.0,
        )
        with self.assertRaises(ValueError):
            config.validate()

    def test_invalid_crash_interval_rejected(self) -> None:
        config = SimulationConfig(
            current_holding=100_000,
            monthly_investment=1_000,
            expected_annual_return=0.08,
            investment_years=20,
            crash_drawdown=0.35,
            crash_interval_years=0.4,
        )

        with self.assertRaises(ValueError):
            config.validate()

    def test_deterministic_path_when_no_volatility_and_zero_drawdown(self) -> None:
        config = SimulationConfig(
            current_holding=100_000,
            monthly_investment=2_000,
            expected_annual_return=0.12,
            investment_years=1,
            crash_drawdown=0.0,
            crash_interval_years=200.0,
            annual_volatility=0.0,
            simulation_count=1000,
        )
        result = run_monte_carlo(config, seed=123)

        monthly_growth = math.pow(1.0 + config.expected_annual_return, 1.0 / 12.0)
        expected = [config.current_holding]
        for _ in range(config.months):
            expected.append(expected[-1] * monthly_growth + config.monthly_investment)

        np.testing.assert_allclose(result.values[0], np.array(expected), rtol=1e-10, atol=1e-10)
        self.assertAlmostEqual(result.summary.loss_probability, 0.0)
        self.assertEqual(result.crash_events.shape, (config.simulation_count, config.months))
        self.assertEqual(result.crash_counts.shape, (config.simulation_count,))

    def test_long_crash_interval_rarely_triggers_events(self) -> None:
        config = SimulationConfig(
            current_holding=100_000,
            monthly_investment=1_000,
            expected_annual_return=0.0,
            investment_years=1,
            crash_drawdown=0.5,
            crash_interval_years=200.0,
            annual_volatility=0.0,
            simulation_count=10000,
        )

        result = run_monte_carlo(config, seed=7)

        self.assertLess(result.summary.crash_occurrence_rate, 0.02)
        self.assertLess(result.summary.average_crash_count, 0.02)
        self.assertGreater(result.summary.zero_crash_rate, 0.98)

    def test_high_frequency_config_allows_multiple_events(self) -> None:
        config = SimulationConfig(
            current_holding=100_000,
            monthly_investment=1_000,
            expected_annual_return=0.05,
            investment_years=10,
            crash_drawdown=0.35,
            crash_interval_years=0.5,
            annual_volatility=0.12,
            simulation_count=1000,
        )

        result = run_monte_carlo(config, seed=11)

        self.assertTrue(np.any(result.crash_counts >= 2))
        self.assertTrue(np.any(result.crash_events.any(axis=1)))
        self.assertGreater(result.summary.three_plus_crash_rate, 0.0)

    def test_crash_count_distribution_rates_are_consistent(self) -> None:
        config = SimulationConfig(
            current_holding=100_000,
            monthly_investment=1_000,
            expected_annual_return=0.03,
            investment_years=15,
            crash_drawdown=0.3,
            crash_interval_years=5.0,
            annual_volatility=0.15,
            simulation_count=4000,
        )

        result = run_monte_carlo(config, seed=5)
        summary = result.summary

        self.assertAlmostEqual(
            summary.zero_crash_rate + summary.one_crash_rate + summary.two_crash_rate + summary.three_plus_crash_rate,
            1.0,
            places=10,
        )
        self.assertAlmostEqual(summary.crash_occurrence_rate, 1.0 - summary.zero_crash_rate, places=10)
        self.assertAlmostEqual(
            summary.crash_occurrence_rate,
            summary.one_crash_rate + summary.two_crash_rate + summary.three_plus_crash_rate,
            places=10,
        )

    def test_percentiles_are_monotonic(self) -> None:
        config = SimulationConfig(
            current_holding=50_000,
            monthly_investment=1_500,
            expected_annual_return=0.07,
            investment_years=15,
            crash_drawdown=0.3,
            crash_interval_years=12.0,
            annual_volatility=0.18,
            simulation_count=2000,
        )

        result = run_monte_carlo(config, seed=42)

        self.assertEqual(result.terminal_values.shape[0], config.simulation_count)
        self.assertTrue(np.all(result.percentile_10 <= result.percentile_25))
        self.assertTrue(np.all(result.percentile_25 <= result.percentile_50))
        self.assertTrue(np.all(result.percentile_50 <= result.percentile_75))
        self.assertTrue(np.all(result.percentile_75 <= result.percentile_90))


if __name__ == "__main__":
    unittest.main()
