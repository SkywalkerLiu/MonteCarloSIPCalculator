from __future__ import annotations

from PySide6.QtCore import QEvent, QPoint, QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMainWindow, QSizePolicy, QToolButton, QVBoxLayout, QWidget

from .theme import PALETTE, apply_paper_shadow


def _combined_edges(first: Qt.Edge, second: Qt.Edge) -> Qt.Edges:
    edges = Qt.Edges()
    edges |= first
    edges |= second
    return edges


class SealIcon(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedSize(28, 28)

    def sizeHint(self) -> QSize:
        return QSize(28, 28)

    def paintEvent(self, event) -> None:  # pragma: no cover - visual rendering
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        rect = QRectF(self.rect()).adjusted(2, 2, -2, -2)
        center = rect.center()

        painter.setBrush(QColor("#f5dfb2"))
        painter.setPen(QPen(QColor("#865227"), 1.4))
        painter.drawEllipse(rect)

        inner = rect.adjusted(4, 4, -4, -4)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor("#9e6c36"), 1.0))
        painter.drawEllipse(inner)

        painter.setPen(QPen(QColor("#7c3f1e"), 1.0))
        painter.drawLine(QPointF(center.x(), rect.top() + 5), QPointF(center.x(), rect.bottom() - 5))
        painter.drawLine(QPointF(rect.left() + 5, center.y()), QPointF(rect.right() - 5, center.y()))

        painter.setPen(QPen(QColor("#7c3f1e"), 1.2))
        painter.drawText(rect.adjusted(0, 1, 0, 0), Qt.AlignmentFlag.AlignCenter, "MC")


class VintageTitleBar(QFrame):
    def __init__(self, window: QMainWindow, parent=None) -> None:
        super().__init__(parent)
        self._window = window
        self._drag_offset: QPoint | None = None

        self.setObjectName("TitleBarFrame")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(64)
        self.setMouseTracking(True)

        icon = SealIcon()

        self.title_label = QLabel("蒙特卡洛定投计算器")
        self.title_label.setObjectName("TitleBarTitle")
        self.subtitle_label = QLabel("Monte Carlo Reserve Ledger")
        self.subtitle_label.setObjectName("TitleBarSubtitle")

        text_column = QWidget()
        text_layout = QVBoxLayout(text_column)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(0)
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.subtitle_label)

        self.minimize_button = self._create_button("—", "WindowControlButton", "最小化")
        self.maximize_button = self._create_button("□", "WindowControlButton", "最大化")
        self.close_button = self._create_button("✕", "CloseWindowButton", "关闭")

        self.minimize_button.clicked.connect(self._window.showMinimized)
        self.maximize_button.clicked.connect(self.toggle_maximize)
        self.close_button.clicked.connect(self._window.close)

        controls = QWidget()
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(6)
        controls_layout.addWidget(self.minimize_button)
        controls_layout.addWidget(self.maximize_button)
        controls_layout.addWidget(self.close_button)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 10, 14, 10)
        layout.setSpacing(12)
        layout.addWidget(icon, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(text_column, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addStretch(1)
        layout.addWidget(controls, 0, Qt.AlignmentFlag.AlignVCenter)

        self.sync_window_state()

    def _create_button(self, text: str, object_name: str, tooltip: str) -> QToolButton:
        button = QToolButton(self)
        button.setObjectName(object_name)
        button.setText(text)
        button.setToolTip(tooltip)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setAutoRaise(True)
        button.setFixedSize(40, 32)
        return button

    def _click_hits_control(self, position: QPoint) -> bool:
        child = self.childAt(position)
        while child is not None and child is not self:
            if isinstance(child, QToolButton):
                return True
            child = child.parentWidget()
        return False

    def toggle_maximize(self) -> None:
        if self._window.isMaximized():
            self._window.showNormal()
        else:
            self._window.showMaximized()
        self.sync_window_state()

    def sync_window_state(self) -> None:
        is_maximized = self._window.isMaximized()
        self.maximize_button.setText("❐" if is_maximized else "□")
        self.maximize_button.setToolTip("还原" if is_maximized else "最大化")

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and not self._click_hits_control(event.position().toPoint()):
            self.toggle_maximize()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and not self._click_hits_control(event.position().toPoint()):
            self._drag_offset = event.globalPosition().toPoint() - self._window.frameGeometry().topLeft()
            handle = self._window.windowHandle()
            if handle is not None and not self._window.isMaximized() and handle.startSystemMove():
                self._drag_offset = None
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton and not self._window.isMaximized():
            self._window.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_offset = None
        super().mouseReleaseEvent(event)


class FramelessMainWindow(QMainWindow):
    resize_margin = 8

    def __init__(self) -> None:
        super().__init__()
        self._content_widget: QWidget | None = None

        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setMouseTracking(True)

        self._window_root = QWidget()
        self._window_root.setObjectName("WindowRoot")
        self._window_root.setMouseTracking(True)
        self._window_root.installEventFilter(self)

        self._window_root_layout = QVBoxLayout(self._window_root)
        self._window_root_layout.setContentsMargins(self.resize_margin, self.resize_margin, self.resize_margin, self.resize_margin)
        self._window_root_layout.setSpacing(0)

        self._window_shell = QFrame()
        self._window_shell.setObjectName("WindowShell")
        apply_paper_shadow(self._window_shell, blur_radius=36.0, y_offset=8.0)

        self._window_shell_layout = QVBoxLayout(self._window_shell)
        self._window_shell_layout.setContentsMargins(0, 0, 0, 0)
        self._window_shell_layout.setSpacing(0)

        self.title_bar = VintageTitleBar(self)
        self._window_shell_layout.addWidget(self.title_bar)
        self._window_root_layout.addWidget(self._window_shell, 1)
        super().setCentralWidget(self._window_root)

        self._sync_window_frame()

    def set_chrome_content(self, widget: QWidget) -> None:
        if self._content_widget is not None:
            self._content_widget.setParent(None)
        self._content_widget = widget
        self._window_shell_layout.addWidget(widget, 1)

    def changeEvent(self, event) -> None:
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            self._sync_window_frame()

    def eventFilter(self, watched, event) -> bool:
        if watched is self._window_root:
            if event.type() == QEvent.Type.MouseMove:
                if not self.isMaximized() and not (event.buttons() & Qt.MouseButton.LeftButton):
                    self._update_resize_cursor(event.position().toPoint())
            elif event.type() == QEvent.Type.Leave:
                self._window_root.unsetCursor()
            elif event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton and not self.isMaximized():
                edges = self._resize_edges_at(event.position().toPoint())
                if edges:
                    handle = self.windowHandle()
                    if handle is not None and handle.startSystemResize(edges):
                        return True
        return super().eventFilter(watched, event)

    def _sync_window_frame(self) -> None:
        margin = 0 if self.isMaximized() else self.resize_margin
        self._window_root_layout.setContentsMargins(margin, margin, margin, margin)
        effect = self._window_shell.graphicsEffect()
        if effect is not None:
            effect.setEnabled(not self.isMaximized())
        self.title_bar.sync_window_state()
        self._window_root.unsetCursor()

    def _resize_edges_at(self, position: QPoint) -> Qt.Edges:
        rect = self._window_root.rect()
        margin = self.resize_margin
        edges = Qt.Edges()

        if position.x() <= margin:
            edges |= Qt.Edge.LeftEdge
        elif position.x() >= rect.width() - margin:
            edges |= Qt.Edge.RightEdge

        if position.y() <= margin:
            edges |= Qt.Edge.TopEdge
        elif position.y() >= rect.height() - margin:
            edges |= Qt.Edge.BottomEdge

        return edges

    def _update_resize_cursor(self, position: QPoint) -> None:
        edges = self._resize_edges_at(position)
        if edges == _combined_edges(Qt.Edge.TopEdge, Qt.Edge.LeftEdge) or edges == _combined_edges(Qt.Edge.BottomEdge, Qt.Edge.RightEdge):
            self._window_root.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif edges == _combined_edges(Qt.Edge.TopEdge, Qt.Edge.RightEdge) or edges == _combined_edges(Qt.Edge.BottomEdge, Qt.Edge.LeftEdge):
            self._window_root.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif edges in (Qt.Edge.LeftEdge, Qt.Edge.RightEdge):
            self._window_root.setCursor(Qt.CursorShape.SizeHorCursor)
        elif edges in (Qt.Edge.TopEdge, Qt.Edge.BottomEdge):
            self._window_root.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            self._window_root.unsetCursor()
