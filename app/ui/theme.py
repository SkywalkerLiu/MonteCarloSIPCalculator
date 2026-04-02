from __future__ import annotations

from matplotlib import rcParams
from PySide6.QtGui import QColor, QFont, QFontDatabase
from PySide6.QtWidgets import QApplication, QGraphicsDropShadowEffect, QWidget

from app.resources import resource_path

PALETTE = {
    "bg": "#d2a066",
    "card": "rgba(252, 244, 228, 0.92)",
    "card_strong": "rgba(255, 247, 234, 0.96)",
    "panel_input": "rgba(255, 247, 232, 0.97)",
    "border": "#caa36f",
    "border_soft": "#ddc394",
    "rule": "#e6d2b0",
    "text": "#4d3217",
    "muted": "#77553a",
    "accent": "#7c3520",
    "accent_hover": "#662715",
    "accent_soft": "#ead7b5",
    "green": "#556b45",
    "red": "#8b4635",
    "chart_outer": "#d6b276",
    "chart_inner": "#aa7f47",
    "chart_line": "#6a341d",
    "chart_sample": "#8d714f",
}


def _load_available_font_families() -> set[str]:
    fonts_dir = resource_path("assets", "fonts")
    families: set[str] = set()
    for font_path in sorted(fonts_dir.glob("*.ttf")) + sorted(fonts_dir.glob("*.otf")):
        font_id = QFontDatabase.addApplicationFont(str(font_path))
        if font_id != -1:
            families.update(QFontDatabase.applicationFontFamilies(font_id))
    return families


def _first_available(available: set[str], *candidates: str) -> str:
    for family in candidates:
        if family in available:
            return family
    return candidates[-1]


def load_preferred_fonts() -> dict[str, str]:
    available = _load_available_font_families()
    text_family = _first_available(
        available,
        "Source Han Serif SC",
        "Noto Serif CJK SC",
        "Source Han Sans SC",
        "Microsoft YaHei",
    )
    display_family = _first_available(
        available,
        "Cormorant Garamond",
        "Cormorant",
        "Source Serif 4",
        text_family,
    )
    return {
        "text": text_family,
        "display": display_family,
    }


def configure_matplotlib_fonts(font_family: str) -> None:
    rcParams["font.family"] = "sans-serif"
    rcParams["font.sans-serif"] = [font_family, "Microsoft YaHei", "SimHei", "DejaVu Sans"]
    rcParams["axes.unicode_minus"] = False
    rcParams["axes.formatter.useoffset"] = False
    rcParams["axes.formatter.limits"] = (-99, 99)


def apply_paper_shadow(widget: QWidget, blur_radius: float = 28.0, y_offset: float = 6.0) -> None:
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur_radius)
    effect.setOffset(0.0, y_offset)
    effect.setColor(QColor(86, 50, 23, 44))
    widget.setGraphicsEffect(effect)


def apply_theme(app: QApplication) -> str:
    font_families = load_preferred_fonts()
    font_family = font_families["text"]
    display_family = font_families["display"]
    app.setFont(QFont(font_family, 10))
    configure_matplotlib_fonts(font_family)
    app.setStyleSheet(
        f"""
        QWidget {{
            background: transparent;
            color: {PALETTE["text"]};
            font-family: "{font_family}", "Microsoft YaHei";
        }}
        QMainWindow {{
            background: {PALETTE["bg"]};
        }}
        QWidget#WindowRoot {{
            background: transparent;
        }}
        QFrame#WindowShell {{
            background: transparent;
            border: 1px solid rgba(110, 64, 29, 0.28);
            border-radius: 22px;
        }}
        QFrame#TitleBarFrame {{
            background: qlineargradient(
                spread:pad,
                x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(255, 249, 238, 245),
                stop:0.55 rgba(243, 227, 195, 236),
                stop:1 rgba(218, 182, 123, 228)
            );
            border: none;
            border-top-left-radius: 22px;
            border-top-right-radius: 22px;
            border-bottom: 1px solid rgba(124, 53, 32, 0.20);
        }}
        QWidget#RootSurface {{
            background: transparent;
        }}
        QLabel {{
            background: transparent;
        }}
        QLabel#TitleBarTitle {{
            color: {PALETTE["text"]};
            font-size: 15px;
            font-weight: 700;
        }}
        QLabel#TitleBarSubtitle {{
            color: rgba(122, 53, 32, 0.78);
            font-family: "{display_family}", "{font_family}", "Times New Roman";
            font-size: 11px;
            font-style: italic;
            font-weight: 600;
            letter-spacing: 1px;
        }}
        QToolButton#WindowControlButton, QToolButton#CloseWindowButton {{
            background: rgba(255, 249, 238, 0.72);
            color: {PALETTE["text"]};
            border: 1px solid rgba(124, 53, 32, 0.14);
            border-radius: 10px;
            padding: 2px;
            font-size: 15px;
            font-weight: 700;
        }}
        QToolButton#WindowControlButton:hover {{
            background: rgba(244, 226, 189, 0.92);
            border-color: rgba(124, 53, 32, 0.22);
        }}
        QToolButton#WindowControlButton:pressed {{
            background: rgba(219, 193, 143, 0.96);
        }}
        QToolButton#CloseWindowButton:hover {{
            background: rgba(138, 70, 53, 0.94);
            color: #fff8ef;
            border-color: rgba(110, 44, 29, 0.42);
        }}
        QToolButton#CloseWindowButton:pressed {{
            background: rgba(107, 43, 31, 0.96);
            color: #fff8ef;
        }}
        QFrame#PanelFrame, QFrame#MetricCard, QFrame#ChartCard {{
            background: qlineargradient(
                spread:pad,
                x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(255, 251, 242, 244),
                stop:1 rgba(245, 233, 209, 238)
            );
            border: 2px solid {PALETTE["border"]};
            border-radius: 16px;
        }}
        QFrame#PanelFrame {{
            background: qlineargradient(
                spread:pad,
                x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(255, 252, 245, 248),
                stop:1 rgba(244, 232, 212, 244)
            );
        }}
        QLabel#SectionTitle {{
            color: {PALETTE["text"]};
            font-size: 20px;
            font-weight: 700;
        }}
        QLabel#FlourishLabel {{
            color: rgba(122, 53, 32, 0.82);
            font-family: "{display_family}", "{font_family}", "Times New Roman";
            font-size: 16px;
            font-style: italic;
            font-weight: 600;
            letter-spacing: 1px;
        }}
        QLabel#SectionHint {{
            color: {PALETTE["muted"]};
            font-size: 12px;
        }}
        QLabel#MetricTitle {{
            color: {PALETTE["muted"]};
            font-size: 11px;
            font-weight: 600;
        }}
        QLabel#MetricValue {{
            color: {PALETTE["text"]};
            font-size: 23px;
            font-weight: 700;
        }}
        QLabel#MetricCaption {{
            color: {PALETTE["muted"]};
            font-size: 10px;
        }}
        QLabel#DividerCaption {{
            color: {PALETTE["muted"]};
            font-size: 11px;
            padding-top: 4px;
            border-top: 1px solid {PALETTE["rule"]};
        }}
        QLabel#CardTitle {{
            color: {PALETTE["text"]};
            font-size: 14px;
            font-weight: 700;
        }}
        QLabel#CardSubtitle {{
            color: {PALETTE["muted"]};
            font-size: 12px;
        }}
        QLabel#HeroLabel {{
            color: {PALETTE["accent"]};
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
        }}
        QLabel#StatusLabel {{
            color: {PALETTE["muted"]};
            font-size: 12px;
        }}
        QLabel#ResultSummary {{
            color: {PALETTE["muted"]};
            font-size: 12px;
            line-height: 1.4;
        }}
        QLineEdit, QSpinBox, QDoubleSpinBox {{
            background: {PALETTE["panel_input"]};
            border: 1px solid {PALETTE["border_soft"]};
            border-radius: 12px;
            padding: 8px 12px;
            padding-right: 34px;
            min-height: 20px;
            selection-background-color: {PALETTE["accent"]};
            selection-color: #fff8ef;
        }}
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 1px solid {PALETTE["accent"]};
        }}
        QSpinBox::up-button, QDoubleSpinBox::up-button {{
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 28px;
            border-left: 1px solid {PALETTE["border_soft"]};
            border-bottom: 1px solid {PALETTE["border_soft"]};
            border-top-right-radius: 11px;
            background: rgba(235, 211, 171, 0.98);
        }}
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 28px;
            border-left: 1px solid {PALETTE["border_soft"]};
            border-bottom-right-radius: 11px;
            background: rgba(232, 206, 164, 0.98);
        }}
        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
            background: rgba(214, 182, 129, 0.98);
        }}
        QSpinBox::up-button:pressed, QDoubleSpinBox::up-button:pressed,
        QSpinBox::down-button:pressed, QDoubleSpinBox::down-button:pressed {{
            background: rgba(147, 72, 44, 0.94);
        }}
        QSpinBox::up-arrow, QDoubleSpinBox::up-arrow,
        QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
            width: 10px;
            height: 10px;
        }}
        QToolButton#DisclosureButton {{
            background: transparent;
            border: none;
            color: {PALETTE["text"]};
            font-weight: 700;
            padding: 6px 0;
            text-align: left;
        }}
        QPushButton {{
            background: {PALETTE["accent"]};
            color: #fff8ef;
            border: none;
            border-radius: 14px;
            padding: 10px 18px;
            font-size: 13px;
            font-weight: 700;
        }}
        QPushButton:enabled {{
            background: {PALETTE["accent"]};
            color: #fff8ef;
        }}
        QPushButton:hover:enabled {{
            background: {PALETTE["accent_hover"]};
        }}
        QPushButton:pressed {{
            background: #5a1f12;
        }}
        QPushButton:disabled {{
            background: #b89b80;
            color: rgba(255, 248, 239, 0.88);
        }}
        QPushButton#ChartSwitchButton {{
            background: rgba(255, 250, 242, 0.92);
            color: {PALETTE["muted"]};
            border: 1px solid {PALETTE["border_soft"]};
            border-radius: 14px;
            min-width: 112px;
            padding: 10px 18px;
            font-size: 12px;
            font-weight: 700;
        }}
        QPushButton#ChartSwitchButton:hover:enabled {{
            background: rgba(244, 226, 189, 0.96);
            color: {PALETTE["text"]};
            border-color: rgba(124, 53, 32, 0.22);
        }}
        QPushButton#ChartSwitchButton:checked {{
            background: qlineargradient(
                spread:pad,
                x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(139, 64, 37, 0.96),
                stop:1 rgba(109, 44, 23, 0.98)
            );
            color: #fff8ef;
            border: 1px solid {PALETTE["accent"]};
        }}
        QScrollArea {{
            border: none;
            background: transparent;
        }}
        QScrollArea QWidget {{
            background: transparent;
        }}
        QScrollBar:vertical {{
            width: 10px;
            background: transparent;
            margin: 4px;
        }}
        QScrollBar::handle:vertical {{
            background: {PALETTE["border"]};
            border-radius: 5px;
            min-height: 24px;
        }}
        """
    )
    return font_family
