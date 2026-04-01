from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class SimulationConfig:
    current_holding: float
    monthly_investment: float
    expected_annual_return: float
    investment_years: int
    crash_drawdown: float
    crash_interval_years: float = 70.0
    annual_volatility: float = 0.18
    simulation_count: int = 5000

    @property
    def months(self) -> int:
        return self.investment_years * 12

    @property
    def total_principal(self) -> float:
        return self.current_holding + self.monthly_investment * self.months

    def validate(self) -> None:
        if self.current_holding < 0:
            raise ValueError("目前持仓市值不能为负数。")
        if self.monthly_investment < 0:
            raise ValueError("每月定投额不能为负数。")
        if self.expected_annual_return <= -1:
            raise ValueError("预期年化收益率必须大于 -100%。")
        if not 1 <= self.investment_years <= 50:
            raise ValueError("投资期限必须在 1 到 50 年之间。")
        if not 0 <= self.crash_drawdown < 1:
            raise ValueError("极端回撤幅度必须在 0% 到 100% 之间。")
        if not 0.5 <= self.crash_interval_years <= 200:
            raise ValueError("极端情况平均发生间隔必须在 0.5 年到 200 年之间。")
        if not 0 <= self.annual_volatility <= 1:
            raise ValueError("年化波动率必须在 0% 到 100% 之间。")
        if self.simulation_count < 1000 or self.simulation_count > 10000 or self.simulation_count % 1000 != 0:
            raise ValueError("模拟次数必须为 1000 到 10000 之间，且步进为 1000。")


@dataclass(slots=True)
class SimulationSummary:
    total_principal: float
    median_final_value: float
    mean_final_value: float
    percentile_10_final: float
    percentile_90_final: float
    worst_final_value: float
    best_final_value: float
    loss_probability: float
    crash_occurrence_rate: float
    average_crash_count: float
    zero_crash_rate: float
    one_crash_rate: float
    two_crash_rate: float
    three_plus_crash_rate: float


@dataclass(slots=True)
class SimulationResult:
    config: SimulationConfig
    month_axis: np.ndarray
    values: np.ndarray
    terminal_values: np.ndarray
    percentile_10: np.ndarray
    percentile_25: np.ndarray
    percentile_50: np.ndarray
    percentile_75: np.ndarray
    percentile_90: np.ndarray
    sampled_paths: np.ndarray
    crash_events: np.ndarray
    crash_counts: np.ndarray
    summary: SimulationSummary
