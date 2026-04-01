from __future__ import annotations

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import QFrame, QLabel, QSizePolicy, QVBoxLayout

from app.core.models import SimulationResult
from .formatting import apply_currency_axis, apply_integer_axis, format_currency
from .theme import PALETTE, apply_paper_shadow


def format_year_label(year_value: float) -> str:
    rounded = round(year_value)
    if abs(year_value - rounded) < 0.05:
        return f"第 {int(rounded)} 年"
    return f"第 {year_value:.1f} 年"


class ChartCard(QFrame):
    def __init__(self, title: str, subtitle: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("ChartCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.result: SimulationResult | None = None
        self.axis = None
        self.hover_annotation = None
        self.hover_line = None
        self.hist_counts: np.ndarray | None = None
        self.hist_bins: np.ndarray | None = None
        self._hover_signature: object | None = None

        self.figure = Figure(figsize=(6.2, 4.2), dpi=100, facecolor="#fbf0db")
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.canvas.setMinimumHeight(460)
        self.canvas.setMouseTracking(True)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("CardTitle")
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("CardSubtitle")
        self.subtitle_label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(3)
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)
        layout.addWidget(self.canvas, 1)

        self.canvas.mpl_connect("motion_notify_event", self._handle_motion)
        self.canvas.mpl_connect("figure_leave_event", self._handle_leave)
        apply_paper_shadow(self, blur_radius=24.0, y_offset=5.0)

    def clear_axes(self):
        self.figure.clear()
        self.hist_counts = None
        self.hist_bins = None
        axis = self.figure.add_subplot(111)
        self.axis = axis
        axis.set_facecolor("#fbf0db")
        axis.tick_params(colors=PALETTE["muted"], labelsize=10)
        axis.set_axisbelow(True)
        for side in ("top", "right"):
            axis.spines[side].set_visible(False)
        axis.spines["left"].set_color(PALETTE["border"])
        axis.spines["bottom"].set_color(PALETTE["border"])
        axis.grid(color=PALETTE["accent_soft"], alpha=0.55, linewidth=0.8)
        axis.xaxis.label.set_color(PALETTE["muted"])
        axis.yaxis.label.set_color(PALETTE["muted"])
        self.hover_annotation = None
        self.hover_line = None
        self._hover_signature = None
        return axis

    def finalize_axes(self) -> None:
        if self.axis is None:
            return
        self.figure.subplots_adjust(left=0.075, right=0.992, top=0.985, bottom=0.15)
        self.hover_line = self.axis.axvline(
            0,
            color=PALETTE["accent"],
            linewidth=1.1,
            linestyle=(0, (4, 4)),
            alpha=0.78,
            visible=False,
            zorder=9,
        )
        self.hover_annotation = self.axis.annotate(
            "",
            xy=(0, 0),
            xytext=(14, 16),
            textcoords="offset points",
            fontsize=9.8,
            color=PALETTE["text"],
            bbox={
                "boxstyle": "round,pad=0.45,rounding_size=0.18",
                "fc": "#fffaf0",
                "ec": PALETTE["border"],
                "alpha": 0.96,
            },
            ha="left",
            va="bottom",
            visible=False,
            zorder=10,
            annotation_clip=False,
        )
        self.hover_annotation.set_clip_on(False)

    def _hover_style(self, anchor_x: float, anchor_y: float) -> dict[str, object]:
        if self.axis is None:
            return {"offset": (14, 16), "ha": "left", "va": "bottom"}

        display_x, display_y = self.axis.transData.transform((anchor_x, anchor_y))
        canvas_width = max(float(self.canvas.width()), 1.0)
        canvas_height = max(float(self.canvas.height()), 1.0)

        offset_x = -14 if display_x > canvas_width * 0.78 else 14
        offset_y = -14 if display_y > canvas_height * 0.76 else 16
        return {
            "offset": (offset_x, offset_y),
            "ha": "right" if offset_x < 0 else "left",
            "va": "top" if offset_y < 0 else "bottom",
        }

    def _handle_leave(self, event) -> None:
        self._hide_hover()

    def _hide_hover(self) -> None:
        changed = False
        if self.hover_annotation is not None and self.hover_annotation.get_visible():
            self.hover_annotation.set_visible(False)
            changed = True
        if self.hover_line is not None and self.hover_line.get_visible():
            self.hover_line.set_visible(False)
            changed = True
        self._hover_signature = None
        if changed:
            self.canvas.draw_idle()

    def _handle_motion(self, event) -> None:
        if (
            self.result is None
            or self.axis is None
            or event.inaxes != self.axis
            or event.xdata is None
            or self.hover_annotation is None
            or self.hover_line is None
        ):
            self._hide_hover()
            return

        payload = self.hover_payload(event)
        if payload is None:
            self._hide_hover()
            return

        x_line = payload["x_line"]
        anchor_x, anchor_y = payload["anchor"]
        hover_style = self._hover_style(anchor_x, anchor_y)
        signature = payload.get("signature", (x_line, anchor_x, anchor_y, hover_style["offset"]))

        if signature == self._hover_signature and self.hover_annotation.get_visible() and self.hover_line.get_visible():
            return
        self._hover_signature = signature

        self.hover_line.set_xdata([x_line, x_line])
        self.hover_line.set_visible(True)
        self.hover_annotation.xy = (anchor_x, anchor_y)
        self.hover_annotation.set_position(hover_style["offset"])
        self.hover_annotation.set_ha(str(hover_style["ha"]))
        self.hover_annotation.set_va(str(hover_style["va"]))
        self.hover_annotation.set_text(payload["text"])
        self.hover_annotation.set_visible(True)
        self.canvas.draw_idle()

    def hover_payload(self, event) -> dict[str, object] | None:
        return None


class FanChartCard(ChartCard):
    def update_result(self, result: SimulationResult) -> None:
        self.result = result
        axis = self.clear_axes()
        x_years = result.month_axis / 12.0
        axis.fill_between(x_years, result.percentile_10, result.percentile_90, color=PALETTE["chart_outer"], alpha=0.55)
        axis.fill_between(x_years, result.percentile_25, result.percentile_75, color=PALETTE["chart_inner"], alpha=0.28)
        axis.plot(x_years, result.percentile_50, color=PALETTE["chart_line"], linewidth=2.5)
        axis.set_xlabel("投资年份")
        axis.set_ylabel("资产规模")
        apply_currency_axis(axis, "y")
        axis.margins(x=0.02, y=0.08)
        self.finalize_axes()
        self.canvas.draw_idle()

    def hover_payload(self, event) -> dict[str, object] | None:
        assert self.result is not None
        x_years = self.result.month_axis / 12.0
        index = int(np.clip(round(event.xdata * 12.0), 0, len(x_years) - 1))
        year_value = float(x_years[index])
        p10 = float(self.result.percentile_10[index])
        p50 = float(self.result.percentile_50[index])
        p90 = float(self.result.percentile_90[index])
        return {
            "x_line": year_value,
            "anchor": (year_value, p90),
            "signature": ("fan", index),
            "text": (
                f"{format_year_label(year_value)}\n"
                f"P10: {format_currency(p10)}\n"
                f"P50: {format_currency(p50)}\n"
                f"P90: {format_currency(p90)}"
            ),
        }


class HistogramChartCard(ChartCard):
    def update_result(self, result: SimulationResult) -> None:
        self.result = result
        axis = self.clear_axes()
        terminal_values = result.terminal_values
        bins = min(30, max(18, int(len(terminal_values) ** 0.5)))
        counts, edges, _ = axis.hist(
            terminal_values,
            bins=bins,
            color="#b48748",
            edgecolor="#fff6e5",
            linewidth=0.8,
            alpha=0.82,
        )
        self.hist_counts = np.asarray(counts)
        self.hist_bins = np.asarray(edges)
        axis.axvline(result.summary.percentile_10_final, color=PALETTE["red"], linestyle="--", linewidth=1.5)
        axis.axvline(result.summary.median_final_value, color=PALETTE["chart_line"], linewidth=2.0)
        axis.axvline(result.summary.percentile_90_final, color=PALETTE["green"], linestyle="--", linewidth=1.5)
        axis.set_xlabel("组合终值")
        axis.set_ylabel("出现次数")
        apply_currency_axis(axis, "x")
        apply_integer_axis(axis, "y")
        axis.margins(x=0.02, y=0.08)
        self.finalize_axes()
        self.canvas.draw_idle()

    def hover_payload(self, event) -> dict[str, object] | None:
        if self.hist_counts is None or self.hist_bins is None:
            return None
        index = int(np.searchsorted(self.hist_bins, event.xdata, side="right") - 1)
        if index < 0 or index >= len(self.hist_counts):
            return None
        left_edge = float(self.hist_bins[index])
        right_edge = float(self.hist_bins[index + 1])
        count = float(self.hist_counts[index])
        center_x = (left_edge + right_edge) / 2.0
        return {
            "x_line": center_x,
            "anchor": (center_x, max(count, 0.0)),
            "signature": ("hist", index),
            "text": (
                f"终值区间\n"
                f"{format_currency(left_edge)} - {format_currency(right_edge)}\n"
                f"出现次数: {int(round(count)):,}"
            ),
        }


class SamplePathsChartCard(ChartCard):
    def update_result(self, result: SimulationResult) -> None:
        self.result = result
        axis = self.clear_axes()
        x_years = result.month_axis / 12.0
        for path in result.sampled_paths[:24]:
            axis.plot(x_years, path, color=PALETTE["chart_sample"], linewidth=0.95, alpha=0.26)
        axis.plot(x_years, result.percentile_50, color=PALETTE["chart_line"], linewidth=2.3)
        axis.set_xlabel("投资年份")
        axis.set_ylabel("资产规模")
        apply_currency_axis(axis, "y")
        axis.margins(x=0.02, y=0.08)
        self.finalize_axes()
        self.canvas.draw_idle()

    def hover_payload(self, event) -> dict[str, object] | None:
        assert self.result is not None
        x_years = self.result.month_axis / 12.0
        index = int(np.clip(round(event.xdata * 12.0), 0, len(x_years) - 1))
        year_value = float(x_years[index])
        p10 = float(self.result.percentile_10[index])
        p50 = float(self.result.percentile_50[index])
        p90 = float(self.result.percentile_90[index])
        return {
            "x_line": year_value,
            "anchor": (year_value, p90),
            "signature": ("paths", index),
            "text": (
                f"{format_year_label(year_value)}\n"
                f"P10: {format_currency(p10)}\n"
                f"P50: {format_currency(p50)}\n"
                f"P90: {format_currency(p90)}"
            ),
        }
