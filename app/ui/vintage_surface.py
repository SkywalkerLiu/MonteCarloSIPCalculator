from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient
from PySide6.QtWidgets import QWidget


class VintageSurface(QWidget):
    def __init__(self, fallback_color: str, parent=None) -> None:
        super().__init__(parent)
        self._fallback_color = QColor(fallback_color)

    def paintEvent(self, event) -> None:  # pragma: no cover - visual rendering
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        rect = QRectF(self.rect())

        paper = QLinearGradient(rect.topLeft(), rect.bottomRight())
        paper.setColorAt(0.0, QColor("#b97a3d"))
        paper.setColorAt(0.28, QColor("#ddb375"))
        paper.setColorAt(0.62, QColor("#f6e7bf"))
        paper.setColorAt(1.0, QColor("#9a5a27"))
        painter.fillRect(rect, paper)

        glow = QRadialGradient(rect.width() * 0.38, rect.height() * 0.34, max(rect.width(), rect.height()) * 0.62)
        glow.setColorAt(0.0, QColor(255, 247, 225, 245))
        glow.setColorAt(0.55, QColor(244, 224, 177, 110))
        glow.setColorAt(1.0, QColor(119, 64, 28, 0))
        painter.fillRect(rect, glow)

        self._draw_quiet_band(painter, rect)
        self._draw_texture(painter, rect)
        self._draw_ledger_guides(painter, rect)
        self._draw_border_wash(painter, rect)
        self._draw_watermark(painter, rect)
        self._draw_filigree(painter, rect)

    def _draw_quiet_band(self, painter: QPainter, rect: QRectF) -> None:
        band_rect = QRectF(rect.left() + rect.width() * 0.24, rect.top() + 26, rect.width() * 0.68, 138)
        band = QLinearGradient(band_rect.topLeft(), band_rect.topRight())
        band.setColorAt(0.0, QColor(255, 247, 229, 0))
        band.setColorAt(0.18, QColor(255, 246, 223, 108))
        band.setColorAt(0.5, QColor(255, 248, 230, 165))
        band.setColorAt(0.82, QColor(255, 246, 223, 108))
        band.setColorAt(1.0, QColor(255, 247, 229, 0))
        painter.fillRect(band_rect, band)

    def _draw_texture(self, painter: QPainter, rect: QRectF) -> None:
        script_pen = QPen(QColor(122, 76, 36, 15))
        script_pen.setWidthF(1.0)
        painter.setPen(script_pen)

        row_height = rect.height() / 13.0
        for row in range(8):
            y = rect.top() + 148 + row * row_height
            path = QPainterPath(QPointF(rect.left() + 80, y))
            for step in range(1, 8):
                x = rect.left() + 80 + step * rect.width() / 9
                path.cubicTo(x - 70, y - 8, x - 28, y + 11, x, y)
            painter.drawPath(path)

        painter.setPen(QPen(QColor(154, 108, 57, 18), 1.7))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QRectF(rect.left() + 120, rect.top() + 170, 150, 150))
        painter.drawEllipse(QRectF(rect.right() - 310, rect.top() + 186, 170, 170))

    def _draw_ledger_guides(self, painter: QPainter, rect: QRectF) -> None:
        guide_pen = QPen(QColor(170, 128, 71, 22))
        guide_pen.setWidthF(0.9)
        painter.setPen(guide_pen)
        step = rect.height() / 6.0
        for index in range(1, 5):
            y = rect.top() + index * step
            painter.drawLine(rect.left() + 60, y, rect.right() - 120, y)

    def _draw_border_wash(self, painter: QPainter, rect: QRectF) -> None:
        edge_color = QColor(88, 43, 16, 34)
        painter.fillRect(QRectF(rect.left(), rect.top(), rect.width(), 26), edge_color)
        painter.fillRect(QRectF(rect.left(), rect.bottom() - 26, rect.width(), 26), edge_color)
        painter.fillRect(QRectF(rect.left(), rect.top(), 28, rect.height()), edge_color)
        painter.fillRect(QRectF(rect.right() - 28, rect.top(), 28, rect.height()), edge_color)

    def _draw_watermark(self, painter: QPainter, rect: QRectF) -> None:
        painter.save()
        painter.setOpacity(0.1)

        origin_x = rect.right() - min(rect.width() * 0.29, 390)
        origin_y = rect.bottom() - min(rect.height() * 0.31, 270)

        base_shadow = QColor("#6f3b19")
        painter.setBrush(base_shadow)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(origin_x + 18, origin_y + 198, 225, 38))

        bank_fill = QColor("#cb9954")
        bank_dark = QColor("#77421c")
        bank_light = QColor("#efd09a")

        painter.setBrush(bank_fill)
        painter.drawRect(QRectF(origin_x + 30, origin_y + 76, 190, 94))

        roof = QPainterPath()
        roof.moveTo(origin_x + 16, origin_y + 82)
        roof.lineTo(origin_x + 125, origin_y + 12)
        roof.lineTo(origin_x + 234, origin_y + 82)
        roof.closeSubpath()
        painter.setBrush(QColor("#8f5226"))
        painter.drawPath(roof)

        painter.setBrush(QColor("#bb8242"))
        painter.drawRect(QRectF(origin_x + 46, origin_y + 50, 158, 16))
        painter.setBrush(bank_light)
        painter.drawRect(QRectF(origin_x + 56, origin_y + 72, 138, 8))

        painter.setBrush(bank_dark)
        for column in range(5):
            painter.drawRect(QRectF(origin_x + 52 + column * 33, origin_y + 88, 20, 74))
        painter.drawRect(QRectF(origin_x + 22, origin_y + 168, 214, 12))

        self._draw_coin_stack(painter, origin_x + 212, origin_y + 114, 38, 3)
        self._draw_coin_stack(painter, origin_x + 268, origin_y + 128, 31, 2)
        self._draw_coin_stack(painter, origin_x + 164, origin_y + 142, 27, 2)

        painter.restore()

    def _draw_filigree(self, painter: QPainter, rect: QRectF) -> None:
        painter.save()
        painter.setOpacity(0.18)

        filigree_pen = QPen(QColor("#9d6c36"))
        filigree_pen.setWidthF(1.15)
        painter.setPen(filigree_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        top_right = QPainterPath(QPointF(rect.right() - 220, rect.top() + 126))
        top_right.cubicTo(rect.right() - 170, rect.top() + 88, rect.right() - 118, rect.top() + 88, rect.right() - 92, rect.top() + 134)
        top_right.cubicTo(rect.right() - 112, rect.top() + 156, rect.right() - 148, rect.top() + 162, rect.right() - 176, rect.top() + 150)
        painter.drawPath(top_right)

        bottom_left = QPainterPath(QPointF(rect.left() + 86, rect.bottom() - 126))
        bottom_left.cubicTo(rect.left() + 146, rect.bottom() - 164, rect.left() + 214, rect.bottom() - 164, rect.left() + 248, rect.bottom() - 120)
        bottom_left.cubicTo(rect.left() + 220, rect.bottom() - 102, rect.left() + 176, rect.bottom() - 100, rect.left() + 148, rect.bottom() - 114)
        painter.drawPath(bottom_left)

        seal_center = QPointF(rect.right() - 182, rect.top() + 136)
        painter.drawEllipse(QRectF(seal_center.x() - 28, seal_center.y() - 28, 56, 56))
        painter.drawEllipse(QRectF(seal_center.x() - 18, seal_center.y() - 18, 36, 36))
        for index in range(12):
            angle = index * 30.0
            outer = QPointF(
                seal_center.x() + 34 * math.cos(math.radians(angle)),
                seal_center.y() + 34 * math.sin(math.radians(angle)),
            )
            inner = QPointF(
                seal_center.x() + 24 * math.cos(math.radians(angle)),
                seal_center.y() + 24 * math.sin(math.radians(angle)),
            )
            painter.drawLine(inner, outer)

        script_font = QFont("Cormorant Garamond", 22)
        script_font.setItalic(True)
        painter.setFont(script_font)
        painter.setPen(QColor(120, 70, 29, 70))
        painter.drawText(QRectF(rect.left() + 86, rect.bottom() - 186, 320, 64), Qt.AlignmentFlag.AlignLeft, "Reserve Ledger")

        painter.restore()

    def _draw_coin_stack(self, painter: QPainter, x: float, y: float, radius: float, layers: int) -> None:
        gold = QColor("#e0b661")
        copper = QColor("#99602d")
        for layer in range(layers):
            top_y = y + layer * 16
            painter.setBrush(copper)
            painter.drawEllipse(QRectF(x - radius, top_y + 16, radius * 2, 12))
            painter.setBrush(gold)
            painter.drawRect(QRectF(x - radius, top_y, radius * 2, 20))
            painter.drawEllipse(QRectF(x - radius, top_y - 4, radius * 2, 12))
