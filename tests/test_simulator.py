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
            crash_probability_horizon=0.2,
        )
        with self.assertRaises(ValueError):
            config.validate()

    def test_deterministic_path_when_no_volatility_and_no_crash(self) -> None:
        config = SimulationConfig(
            current_holding=100_000,
            monthly_investment=2_000,
            expected_annual_return=0.12,
            investment_years=1,
            crash_drawdown=0.0,
            crash_probability_horizon=0.0,
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
        self.assertTrue(np.all(result.crash_months == -1))

    def test_crash_probability_bounds(self) -> None:
        no_crash_config = SimulationConfig(
            current_holding=100_000,
            monthly_investment=1_000,
            expected_annual_return=0.0,
            investment_years=10,
            crash_drawdown=0.5,
            crash_probability_horizon=0.0,
            annual_volatility=0.0,
            simulation_count=1000,
        )
        all_crash_config = SimulationConfig(
            current_holding=100_000,
            monthly_investment=1_000,
            expected_annual_return=0.0,
            investment_years=10,
            crash_drawdown=0.5,
            crash_probability_horizon=1.0,
            annual_volatility=0.0,
            simulation_count=1000,
        )

        no_crash = run_monte_carlo(no_crash_config, seed=7)
        all_crash = run_monte_carlo(all_crash_config, seed=7)

        self.assertTrue(np.all(no_crash.crash_months == -1))
        self.assertTrue(np.all(all_crash.crash_months >= 0))
        self.assertAlmostEqual(no_crash.summary.crash_occurrence_rate, 0.0)
        self.assertAlmostEqual(all_crash.summary.crash_occurrence_rate, 1.0)

    def test_percentiles_are_monotonic(self) -> None:
        config = SimulationConfig(
            current_holding=50_000,
            monthly_investment=1_500,
            expected_annual_return=0.07,
            investment_years=15,
            crash_drawdown=0.3,
            crash_probability_horizon=0.3,
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
