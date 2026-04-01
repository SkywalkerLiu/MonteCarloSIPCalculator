from __future__ import annotations

import math

from PySide6.QtCore import QObject, QPointF, QRectF, QRunnable, Qt, QThreadPool, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QStackedWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.core import SimulationConfig, SimulationResult, run_monte_carlo
from app.resources import resource_path
from .charts import FanChartCard, HistogramChartCard, SamplePathsChartCard
from .formatting import format_currency
from .theme import PALETTE, apply_paper_shadow, apply_theme
from .vintage_surface import VintageSurface
from .window_chrome import FramelessMainWindow


def format_percent(value: float) -> str:
    return f"{value * 100:.1f}%"


class WorkerSignals(QObject):
    finished = Signal(object)
    failed = Signal(str)


class SimulationTask(QRunnable):
    def __init__(self, config: SimulationConfig) -> None:
        super().__init__()
        self.config = config
        self.signals = WorkerSignals()

    def run(self) -> None:
        try:
            result = run_monte_carlo(self.config)
        except Exception as exc:  # pragma: no cover - surfaced to UI
            self.signals.failed.emit(str(exc))
        else:
            self.signals.finished.emit(result)


class MetricCard(QFrame):
    def __init__(self, title: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("MetricCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("MetricTitle")
        self.value_label = QLabel("--")
        self.value_label.setObjectName("MetricValue")
        self.caption_label = QLabel("等待模拟结果")
        self.caption_label.setObjectName("MetricCaption")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(6)
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.caption_label)

        apply_paper_shadow(self, blur_radius=22.0, y_offset=4.0)

    def update_text(self, value: str, caption: str) -> None:
        self.value_label.setText(value)
        self.caption_label.setText(caption)


class CollapsibleSection(QWidget):
    def __init__(self, title: str, parent=None) -> None:
        super().__init__(parent)
        self.toggle_button = QToolButton(text=title, checkable=True, checked=False)
        self.toggle_button.setObjectName("DisclosureButton")
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle_button.toggled.connect(self._handle_toggled)

        self.content = QWidget()
        self.content.setVisible(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content)

    def _handle_toggled(self, checked: bool) -> None:
        self.toggle_button.setArrowType(Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow)
        self.content.setVisible(checked)


class VintagePanelStillLife(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(180)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def paintEvent(self, event) -> None:  # pragma: no cover - visual rendering
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        rect = QRectF(self.rect())
        painter.fillRect(rect, Qt.GlobalColor.transparent)

        painter.save()
        painter.setOpacity(0.28)
        self._draw_signature(painter, rect)
        painter.setOpacity(0.34)
        self._draw_bank_seal(painter, rect)
        painter.setOpacity(0.42)
        self._draw_coin_stack_group(painter, rect)
        painter.restore()

    def _draw_signature(self, painter: QPainter, rect: QRectF) -> None:
        painter.save()
        painter.translate(rect.width() * 0.16, rect.height() * 0.62)
        script_font = painter.font()
        script_font.setFamily("Cormorant Garamond")
        script_font.setPointSize(22)
        script_font.setItalic(True)
        painter.setFont(script_font)
        painter.setPen(QPen(QColor(128, 77, 38, 72), 1.0))
        painter.drawText(QRectF(0, 0, rect.width() * 0.54, 48), Qt.AlignmentFlag.AlignLeft, "Private Reserve")
        painter.setPen(QPen(QColor(154, 109, 67, 54), 0.9))
        painter.drawText(QRectF(12, 28, rect.width() * 0.5, 42), Qt.AlignmentFlag.AlignLeft, "estate account")
        painter.restore()

    def _draw_bank_seal(self, painter: QPainter, rect: QRectF) -> None:
        painter.save()
        center = QPointF(rect.width() * 0.32, rect.height() * 0.74)
        outer = QRectF(center.x() - 42, center.y() - 42, 84, 84)
        inner = QRectF(center.x() - 28, center.y() - 28, 56, 56)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(138, 78, 41, 82), 1.5))
        painter.drawEllipse(outer)
        painter.setPen(QPen(QColor(163, 107, 64, 70), 1.1))
        painter.drawEllipse(inner)

        for index in range(16):
            angle = math.radians(index * 22.5)
            outer_point = QPointF(center.x() + 42 * math.cos(angle), center.y() + 42 * math.sin(angle))
            inner_point = QPointF(center.x() + 32 * math.cos(angle), center.y() + 32 * math.sin(angle))
            painter.drawLine(inner_point, outer_point)

        painter.setPen(QPen(QColor(131, 72, 36, 88), 1.2))
        painter.drawText(QRectF(center.x() - 22, center.y() - 12, 44, 24), Qt.AlignmentFlag.AlignCenter, "BANK")
        painter.restore()

    def _draw_coin_stack_group(self, painter: QPainter, rect: QRectF) -> None:
        painter.save()
        painter.translate(rect.width() * 0.59, rect.height() * 0.76)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(94, 55, 25, 34))
        painter.drawEllipse(QRectF(-22, 22, 132, 20))

        self._draw_coin_stack(painter, QPointF(20, -10), 24, 3, QColor(225, 184, 96, 168), QColor(135, 93, 36, 92))
        self._draw_coin_stack(painter, QPointF(58, -2), 20, 2, QColor(214, 171, 86, 156), QColor(124, 82, 30, 88))
        self._draw_coin_stack(painter, QPointF(84, 8), 18, 1, QColor(229, 191, 112, 162), QColor(145, 98, 40, 92))
        painter.restore()

    def _draw_coin_stack(self, painter: QPainter, origin: QPointF, radius: float, layers: int, fill: QColor, edge: QColor) -> None:
        for layer in range(layers):
            y = origin.y() - layer * 9
            painter.setBrush(edge)
            painter.drawEllipse(QRectF(origin.x() - radius, y + radius * 0.32, radius * 2, radius * 0.5))
            painter.setBrush(fill)
            painter.drawRect(QRectF(origin.x() - radius, y - radius * 0.12, radius * 2, radius * 0.58))
            painter.drawEllipse(QRectF(origin.x() - radius, y - radius * 0.42, radius * 2, radius * 0.6))

        top_rect = QRectF(origin.x() - radius, origin.y() - (layers - 1) * 9 - radius * 0.42, radius * 2, radius * 0.6)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(250, 230, 176, 108), 1.0))
        painter.drawEllipse(top_rect.adjusted(5, 3, -5, -3))
        painter.setPen(QPen(QColor(144, 98, 43, 88), 1.0))
        painter.drawLine(QPointF(top_rect.center().x(), top_rect.top() + 4), QPointF(top_rect.center().x(), top_rect.bottom() - 4))
        painter.drawLine(QPointF(top_rect.left() + 7, top_rect.center().y()), QPointF(top_rect.right() - 7, top_rect.center().y()))


class MainWindow(FramelessMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.thread_pool = QThreadPool(self)
        self.active_task: SimulationTask | None = None
        self.result: SimulationResult | None = None
        self.chart_buttons: dict[str, QPushButton] = {}
        self.chart_cards: dict[str, QFrame] = {}
        self.chart_stack: QStackedWidget | None = None
        self.current_chart_key = "paths"

        self.setWindowTitle("蒙特卡洛定投计算器")
        self.resize(1540, 980)
        self.setMinimumSize(1280, 860)
        icon_path = resource_path("assets", "icons", "monte_carlo_reserve.png")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        central = VintageSurface(PALETTE["bg"])
        central.setObjectName("RootSurface")
        self.set_chrome_content(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(20, 14, 20, 20)
        root_layout.setSpacing(18)

        root_layout.addWidget(self._build_control_panel(), 0)
        root_layout.addWidget(self._build_results_panel(), 1)

    def _build_control_panel(self) -> QWidget:
        outer = QScrollArea()
        outer.setWidgetResizable(True)
        outer.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.setMinimumWidth(390)
        outer.setMaximumWidth(430)

        content = QWidget()
        outer.setWidget(content)

        panel = QFrame()
        panel.setObjectName("PanelFrame")
        apply_paper_shadow(panel, blur_radius=30.0, y_offset=6.0)

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(22, 14, 22, 22)
        panel_layout.setSpacing(12)

        title = QLabel("蒙特卡洛定投计算器")
        title.setObjectName("SectionTitle")
        title_note = QLabel("Monte Carlo Reserve Ledger")
        title_note.setObjectName("FlourishLabel")

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setFormAlignment(Qt.AlignmentFlag.AlignTop)

        self.current_holding_input = self._currency_input(100000)
        self.monthly_investment_input = self._currency_input(3000)
        self.expected_return_input = self._percent_input(8.0, minimum=-99.0, maximum=80.0)
        self.investment_years_input = QSpinBox()
        self.investment_years_input.setRange(1, 50)
        self.investment_years_input.setValue(20)
        self.crash_drawdown_input = self._percent_input(35.0, minimum=0.0, maximum=95.0)
        self.crash_probability_input = self._percent_input(25.0, minimum=0.0, maximum=100.0)

        form.addRow("当前持仓市值", self.current_holding_input)
        form.addRow("每月定投额", self.monthly_investment_input)
        form.addRow("预期年化收益率", self.expected_return_input)
        form.addRow("投资期限（年）", self.investment_years_input)
        form.addRow("极端回撤幅度", self.crash_drawdown_input)
        form.addRow("极端回撤发生概率", self.crash_probability_input)

        advanced = CollapsibleSection("高级设置")
        advanced_form = QFormLayout(advanced.content)
        advanced_form.setSpacing(12)

        self.annual_volatility_input = self._percent_input(18.0, minimum=0.0, maximum=100.0)
        self.simulation_count_input = QSpinBox()
        self.simulation_count_input.setRange(1000, 10000)
        self.simulation_count_input.setSingleStep(1000)
        self.simulation_count_input.setValue(5000)
        self.simulation_count_input.setWrapping(False)

        advanced_form.addRow("年化波动率", self.annual_volatility_input)
        advanced_form.addRow("模拟次数", self.simulation_count_input)

        button_row = QHBoxLayout()
        self.simulate_button = QPushButton("开始模拟")
        self.simulate_button.clicked.connect(self.start_simulation)
        button_row.addWidget(self.simulate_button)

        self.status_label = QLabel("正在加载默认参数。")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setWordWrap(True)
        self.still_life = VintagePanelStillLife()

        panel_layout.addWidget(title)
        panel_layout.addWidget(title_note)
        panel_layout.addLayout(form)
        panel_layout.addWidget(advanced)
        panel_layout.addSpacing(4)
        panel_layout.addLayout(button_row)
        panel_layout.addWidget(self.status_label)
        panel_layout.addWidget(self.still_life, 1)

        wrapper = QVBoxLayout(content)
        wrapper.setContentsMargins(0, 0, 0, 0)
        wrapper.addWidget(panel)
        return outer

    def _build_results_panel(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(12)

        heading = QLabel("结果概览")
        heading.setObjectName("SectionTitle")
        heading_ornament = QLabel("Savings Almanac")
        heading_ornament.setObjectName("FlourishLabel")

        heading_row = QHBoxLayout()
        heading_row.setContentsMargins(0, 0, 0, 0)
        heading_row.setSpacing(10)
        heading_row.addWidget(heading)
        heading_row.addStretch(1)
        heading_row.addWidget(heading_ornament, 0, Qt.AlignmentFlag.AlignBottom)

        metric_grid = QGridLayout()
        metric_grid.setHorizontalSpacing(14)
        metric_grid.setVerticalSpacing(14)
        self.metric_median = MetricCard("终值中位数")
        self.metric_range = MetricCard("10/90 分位区间")
        self.metric_principal = MetricCard("总投入")
        self.metric_loss = MetricCard("本金亏损概率")

        metric_grid.addWidget(self.metric_median, 0, 0)
        metric_grid.addWidget(self.metric_range, 0, 1)
        metric_grid.addWidget(self.metric_principal, 1, 0)
        metric_grid.addWidget(self.metric_loss, 1, 1)

        chart_switcher = self._build_chart_switcher()
        chart_stack = self._build_chart_stack()

        layout.addLayout(heading_row)
        layout.addLayout(metric_grid)
        layout.addLayout(chart_switcher)
        layout.addWidget(chart_stack, 1)
        return container

    def _build_chart_switcher(self) -> QHBoxLayout:
        switcher_layout = QHBoxLayout()
        switcher_layout.setContentsMargins(0, 0, 0, 0)
        switcher_layout.setSpacing(6)

        button_group = QButtonGroup(self)
        button_group.setExclusive(True)

        options = [
            ("paths", "样本路径图"),
            ("fan", "路径扇形图"),
            ("hist", "终值直方图"),
        ]
        for key, label in options:
            button = QPushButton(label)
            button.setObjectName("ChartSwitchButton")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setMinimumHeight(40)
            button.clicked.connect(lambda checked=False, chart_key=key: self.select_chart(chart_key))
            button_group.addButton(button)
            self.chart_buttons[key] = button
            switcher_layout.addWidget(button)

        switcher_layout.addStretch(1)
        return switcher_layout

    def _build_chart_stack(self) -> QStackedWidget:
        self.chart_stack = QStackedWidget()
        self.chart_stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.chart_stack.setMinimumHeight(560)

        self.fan_chart = FanChartCard("路径扇形图", "展示 P10 / P25 / P50 / P75 / P90 的资产区间")
        self.hist_chart = HistogramChartCard("终值直方图", "用终值分布观察结果偏态与上下沿")
        self.paths_chart = SamplePathsChartCard("样本路径图", "抽取少量路径展示真实波动和一次性回撤的影响")

        self.chart_cards = {
            "paths": self.paths_chart,
            "fan": self.fan_chart,
            "hist": self.hist_chart,
        }

        self.chart_stack.addWidget(self.paths_chart)
        self.chart_stack.addWidget(self.fan_chart)
        self.chart_stack.addWidget(self.hist_chart)

        self.select_chart(self.current_chart_key)
        return self.chart_stack

    def select_chart(self, chart_key: str) -> None:
        self.current_chart_key = chart_key
        if self.chart_stack is not None and chart_key in self.chart_cards:
            self.chart_stack.setCurrentWidget(self.chart_cards[chart_key])
        for key, button in self.chart_buttons.items():
            button.setChecked(key == chart_key)

    def _currency_input(self, value: float) -> QDoubleSpinBox:
        spinbox = QDoubleSpinBox()
        spinbox.setRange(0.0, 1_000_000_000.0)
        spinbox.setDecimals(0)
        spinbox.setSingleStep(1000.0)
        spinbox.setPrefix("$ ")
        spinbox.setValue(value)
        return spinbox

    def _percent_input(self, value: float, minimum: float, maximum: float) -> QDoubleSpinBox:
        spinbox = QDoubleSpinBox()
        spinbox.setRange(minimum, maximum)
        spinbox.setDecimals(1)
        spinbox.setSingleStep(0.5)
        spinbox.setSuffix(" %")
        spinbox.setValue(value)
        return spinbox

    def build_config(self) -> SimulationConfig:
        config = SimulationConfig(
            current_holding=self.current_holding_input.value(),
            monthly_investment=self.monthly_investment_input.value(),
            expected_annual_return=self.expected_return_input.value() / 100.0,
            investment_years=self.investment_years_input.value(),
            crash_drawdown=self.crash_drawdown_input.value() / 100.0,
            crash_probability_horizon=self.crash_probability_input.value() / 100.0,
            annual_volatility=self.annual_volatility_input.value() / 100.0,
            simulation_count=self.simulation_count_input.value(),
        )
        config.validate()
        return config

    def start_simulation(self) -> None:
        try:
            config = self.build_config()
        except ValueError as exc:
            QMessageBox.warning(self, "参数错误", str(exc))
            self.status_label.setText(str(exc))
            return

        self.simulate_button.setDisabled(True)
        self.status_label.setText(f"正在运行 {config.simulation_count:,} 次模拟，请稍候。")

        task = SimulationTask(config)
        task.signals.finished.connect(self.handle_result)
        task.signals.failed.connect(self.handle_failure)
        self.active_task = task
        self.thread_pool.start(task)

    def handle_failure(self, message: str) -> None:
        self.active_task = None
        self.simulate_button.setDisabled(False)
        self.status_label.setText("模拟失败，请检查参数或依赖环境。")
        QMessageBox.critical(self, "模拟失败", message)

    def handle_result(self, result: SimulationResult) -> None:
        self.active_task = None
        self.result = result
        self.simulate_button.setDisabled(False)
        self.status_label.setText(
            f"已完成 {result.config.simulation_count:,} 次模拟，投资期内黑天鹅实际触发率约为 {format_percent(result.summary.crash_occurrence_rate)}。"
        )

        summary = result.summary
        self.metric_median.update_text(format_currency(summary.median_final_value), "终值中位数更适合看中性结果")
        self.metric_range.update_text(
            f"{format_currency(summary.percentile_10_final)} - {format_currency(summary.percentile_90_final)}",
            "区间越宽，代表路径不确定性越高",
        )
        self.metric_principal.update_text(format_currency(summary.total_principal), "当前持仓加上未来全部定投金额")
        self.metric_loss.update_text(format_percent(summary.loss_probability), "终值低于总投入本金的概率")

        self.fan_chart.update_result(result)
        self.hist_chart.update_result(result)
        self.paths_chart.update_result(result)
        self.select_chart(self.current_chart_key)


def launch_app() -> int:
    app = QApplication.instance() or QApplication([])
    apply_theme(app)
    icon_path = resource_path("assets", "icons", "monte_carlo_reserve.png")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    window = MainWindow()
    window.show()
    return app.exec()
