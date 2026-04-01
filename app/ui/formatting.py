from __future__ import annotations

from matplotlib.ticker import FuncFormatter, MaxNLocator


def _trim_trailing_zeros(value: float, decimals: int) -> str:
    text = f"{value:,.{decimals}f}"
    return text.rstrip("0").rstrip(".")


def format_compact_number(value: float) -> str:
    absolute = abs(value)
    if absolute >= 1_000_000_000:
        return f"{_trim_trailing_zeros(value / 1_000_000_000, 2)}B"
    if absolute >= 1_000_000:
        return f"{_trim_trailing_zeros(value / 1_000_000, 2)}M"
    if absolute >= 1_000:
        return f"{_trim_trailing_zeros(value / 1_000, 2)}K"
    return f"{value:,.0f}"


def format_currency(value: float) -> str:
    if value < 0:
        return f"-${format_compact_number(abs(value))}"
    return f"${format_compact_number(value)}"


def format_integer(value: float) -> str:
    return f"{value:,.0f}"


def currency_tick_formatter() -> FuncFormatter:
    return FuncFormatter(lambda value, _: format_currency(value))


def integer_tick_formatter() -> FuncFormatter:
    return FuncFormatter(lambda value, _: format_integer(value))


def apply_currency_axis(axis, axis_name: str) -> None:
    if axis_name in {"x", "both"}:
        axis.xaxis.set_major_locator(MaxNLocator(nbins=6, min_n_ticks=4))
        axis.xaxis.set_major_formatter(currency_tick_formatter())
    if axis_name in {"y", "both"}:
        axis.yaxis.set_major_locator(MaxNLocator(nbins=6, min_n_ticks=4))
        axis.yaxis.set_major_formatter(currency_tick_formatter())


def apply_integer_axis(axis, axis_name: str) -> None:
    if axis_name in {"x", "both"}:
        axis.xaxis.set_major_locator(MaxNLocator(nbins=6, min_n_ticks=4, integer=True))
        axis.xaxis.set_major_formatter(integer_tick_formatter())
    if axis_name in {"y", "both"}:
        axis.yaxis.set_major_locator(MaxNLocator(nbins=6, min_n_ticks=4, integer=True))
        axis.yaxis.set_major_formatter(integer_tick_formatter())
