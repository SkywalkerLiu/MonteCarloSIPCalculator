from __future__ import annotations

import math

import numpy as np

from .models import SimulationConfig, SimulationResult, SimulationSummary


def _monthly_distribution_parameters(config: SimulationConfig) -> tuple[float, float]:
    monthly_target_gross = math.pow(1.0 + config.expected_annual_return, 1.0 / 12.0)
    sigma_monthly = config.annual_volatility / math.sqrt(12.0)
    mu_monthly = math.log(monthly_target_gross) - 0.5 * sigma_monthly * sigma_monthly
    return mu_monthly, sigma_monthly


def run_monte_carlo(config: SimulationConfig, seed: int | None = None) -> SimulationResult:
    config.validate()

    simulation_count = config.simulation_count
    months = config.months
    rng = np.random.default_rng(seed)

    mu_monthly, sigma_monthly = _monthly_distribution_parameters(config)
    log_returns = rng.normal(mu_monthly, sigma_monthly, size=(simulation_count, months))
    monthly_growth = np.exp(log_returns)
    monthly_crash_probability = 1.0 - math.exp(-1.0 / (12.0 * config.crash_interval_years))
    crash_events = rng.random((simulation_count, months)) < monthly_crash_probability
    crash_counts = crash_events.sum(axis=1, dtype=np.int32)

    values = np.empty((simulation_count, months + 1), dtype=np.float64)
    values[:, 0] = config.current_holding

    for month_index in range(months):
        next_values = values[:, month_index] * monthly_growth[:, month_index]
        crash_mask = crash_events[:, month_index]
        if np.any(crash_mask):
            next_values[crash_mask] *= 1.0 - config.crash_drawdown
        next_values += config.monthly_investment
        values[:, month_index + 1] = next_values

    terminal_values = values[:, -1]
    p10, p25, p50, p75, p90 = np.percentile(values, [10, 25, 50, 75, 90], axis=0)

    sample_size = min(40, simulation_count)
    sample_indices = np.linspace(0, simulation_count - 1, sample_size, dtype=int)
    sampled_paths = values[sample_indices]

    summary = SimulationSummary(
        total_principal=config.total_principal,
        median_final_value=float(np.median(terminal_values)),
        mean_final_value=float(np.mean(terminal_values)),
        percentile_10_final=float(np.percentile(terminal_values, 10)),
        percentile_90_final=float(np.percentile(terminal_values, 90)),
        worst_final_value=float(np.min(terminal_values)),
        best_final_value=float(np.max(terminal_values)),
        loss_probability=float(np.mean(terminal_values < config.total_principal)),
        crash_occurrence_rate=float(np.mean(crash_counts > 0)),
        average_crash_count=float(np.mean(crash_counts)),
        zero_crash_rate=float(np.mean(crash_counts == 0)),
        one_crash_rate=float(np.mean(crash_counts == 1)),
        two_crash_rate=float(np.mean(crash_counts == 2)),
        three_plus_crash_rate=float(np.mean(crash_counts >= 3)),
    )

    return SimulationResult(
        config=config,
        month_axis=np.arange(months + 1),
        values=values,
        terminal_values=terminal_values,
        percentile_10=p10,
        percentile_25=p25,
        percentile_50=p50,
        percentile_75=p75,
        percentile_90=p90,
        sampled_paths=sampled_paths,
        crash_events=crash_events,
        crash_counts=crash_counts,
        summary=summary,
    )
