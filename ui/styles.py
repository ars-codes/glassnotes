"""QSS styles for GlassNotes dark glass theme."""

FONT_FAMILY = '"Segoe UI Variable", "Segoe UI", sans-serif'

CORNER_RADIUS = 12

# Base widget — transparent when native acrylic is active
BASE_STYLE = f"""
QWidget#glassRoot {{
    background: transparent;
    border: none;
    font-family: {FONT_FAMILY};
    color: #E8E8E8;
}}
"""

# Fallback when native acrylic is unavailable
FALLBACK_STYLE = f"""
QWidget#glassRoot {{
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(40, 40, 44, 0.88),
        stop:1 rgba(24, 24, 28, 0.92)
    );
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: {CORNER_RADIUS}px;
    font-family: {FONT_FAMILY};
    color: #E8E8E8;
}}
"""

HEADER_STYLE = """
QWidget#headerBar {
    background: transparent;
    border: none;
    min-height: 32px;
    max-height: 32px;
}
QLabel#titleLabel {
    color: rgba(255, 255, 255, 0.55);
    font-size: 11px;
    font-weight: 500;
    padding-left: 4px;
    background: transparent;
    border: none;
}
QPushButton#headerBtn {
    background: transparent;
    border: none;
    border-radius: 6px;
    color: rgba(255, 255, 255, 0.65);
    font-size: 14px;
    min-width: 28px;
    max-width: 28px;
    min-height: 28px;
    max-height: 28px;
    padding: 0;
}
QPushButton#headerBtn:hover {
    background: rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.95);
}
QPushButton#headerBtn:pressed {
    background: rgba(255, 255, 255, 0.06);
}
QPushButton#closeBtn:hover {
    background: rgba(232, 17, 35, 0.75);
    color: white;
}
"""

EDITOR_STYLE = """
QPlainTextEdit#noteEditor {
    background: transparent;
    border: none;
    color: #F0F0F0;
    font-family: """ + FONT_FAMILY + """;
    font-size: 13px;
    line-height: 1.45;
    padding: 4px 10px 8px 10px;
    selection-background-color: rgba(100, 160, 255, 0.45);
    selection-color: #FFFFFF;
}
QPlainTextEdit#noteEditor QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 2px 2px 2px 0;
}
QPlainTextEdit#noteEditor QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.22);
    border-radius: 3px;
    min-height: 24px;
}
QPlainTextEdit#noteEditor QScrollBar::add-line:vertical,
QPlainTextEdit#noteEditor QScrollBar::sub-line:vertical,
QPlainTextEdit#noteEditor QScrollBar::add-page:vertical,
QPlainTextEdit#noteEditor QScrollBar::sub-page:vertical {
    background: transparent;
    height: 0;
    border: none;
}
QPlainTextEdit#noteEditor QScrollBar:horizontal {
    height: 0;
}
"""

RESIZE_HANDLE_STYLE = """
QWidget#resizeHandle {
    background: transparent;
    min-height: 6px;
    max-height: 6px;
    border: none;
}
QWidget#resizeHandle:hover {
    background: rgba(255, 255, 255, 0.08);
}
"""

COLLAPSED_STYLE = """
QPushButton#collapsedIcon {
    background: qradialgradient(
        cx:0.5, cy:0.5, radius:0.85,
        fx:0.5, fy:0.5,
        stop:0 rgba(60, 120, 220, 0.55),
        stop:1 rgba(30, 30, 36, 0.92)
    );
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 24px;
    color: white;
    font-size: 18px;
    font-weight: 600;
    min-width: 48px;
    max-width: 48px;
    min-height: 48px;
    max-height: 48px;
    padding: 0;
}
QPushButton#collapsedIcon:hover {
    border-color: rgba(255, 255, 255, 0.35);
    background: qradialgradient(
        cx:0.5, cy:0.5, radius:0.85,
        fx:0.5, fy:0.5,
        stop:0 rgba(80, 140, 240, 0.65),
        stop:1 rgba(36, 36, 42, 0.95)
    );
}
"""

COLLAPSED_FALLBACK_STYLE = """
QPushButton#collapsedIcon {
    background: qradialgradient(
        cx:0.5, cy:0.5, radius:0.85,
        fx:0.5, fy:0.5,
        stop:0 rgba(60, 120, 220, 0.65),
        stop:1 rgba(24, 24, 28, 0.96)
    );
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 24px;
    color: white;
    font-size: 18px;
    font-weight: 600;
    min-width: 48px;
    max-width: 48px;
    min-height: 48px;
    max-height: 48px;
    padding: 0;
}
"""


def expanded_styles(use_fallback: bool) -> str:
    """Return combined QSS for expanded widget state."""
    root = FALLBACK_STYLE if use_fallback else BASE_STYLE
    return root + HEADER_STYLE + EDITOR_STYLE + RESIZE_HANDLE_STYLE


def collapsed_styles(use_fallback: bool) -> str:
    """Return QSS for collapsed circular icon state."""
    icon = COLLAPSED_FALLBACK_STYLE if use_fallback else COLLAPSED_STYLE
    root = FALLBACK_STYLE if use_fallback else BASE_STYLE
    return root + icon
