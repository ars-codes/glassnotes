"""QSS styles for FloatNote dark glass theme."""

FONT_FAMILY = '"Segoe UI Variable", "Segoe UI", sans-serif'

CORNER_RADIUS = 15

# Base widget — dark translucent glass background for native acrylic/mica
BASE_STYLE = f"""
QWidget#glassRoot {{
    background: rgba(32, 36, 44, 77); /* 30% opacity */
    border: 1px solid rgba(255, 255, 255, 15); /* Very subtle rim */
    border-radius: {CORNER_RADIUS}px;
    font-family: {FONT_FAMILY};
    color: #FFFFFF;
}}
"""

# Fallback when native acrylic is unavailable
FALLBACK_STYLE = f"""
QWidget#glassRoot {{
    /* Sleek dark fallback matching Thick dark 2, but translucent */
    background: rgba(32, 36, 44, 77);
    border: 1px solid rgba(255, 255, 255, 15);
    border-radius: {CORNER_RADIUS}px;
    font-family: {FONT_FAMILY};
    color: #FFFFFF;
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
    color: rgba(255, 255, 255, 210);
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
    color: rgba(255, 255, 255, 160);
    font-size: 14px;
    min-width: 28px;
    max-width: 28px;
    min-height: 28px;
    max-height: 28px;
    padding: 0;
}
QPushButton#closeBtn {
    background: transparent;
    border: none;
    border-radius: 6px;
    color: rgba(255, 255, 255, 160);
    font-size: 14px;
    min-width: 28px;
    max-width: 28px;
    min-height: 28px;
    max-height: 28px;
    padding: 0;
}
QPushButton#closeBtn:hover {
    background: rgba(232, 17, 35, 190);
    color: white;
}
QPushButton#headerBtn:hover {
    background: rgba(255, 255, 255, 30);
    color: #FFFFFF;
}
QPushButton#headerBtn:pressed {
    background: rgba(255, 255, 255, 15);
}
"""

EDITOR_STYLE = """
QPlainTextEdit#noteEditor {
    background: transparent;
    border: none;
    color: #FFFFFF;
    font-family: """ + FONT_FAMILY + """;
    font-size: 13px;
    line-height: 1.45;
    padding: 4px 10px 8px 10px;
    selection-background-color: rgba(255, 255, 255, 50);
    selection-color: #FFFFFF;
}
QPlainTextEdit#noteEditor QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 2px 2px 2px 0;
}
QPlainTextEdit#noteEditor QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 60);
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
    background: rgba(255, 255, 255, 20);
}
"""

COLLAPSED_STYLE = """
QPushButton#collapsedIcon {
    background: rgba(32, 36, 44, 77);
    border: 1px solid rgba(255, 255, 255, 15);
    border-radius: 32px;
    color: #FFFFFF;
    font-size: 18px;
    font-weight: 600;
    min-width: 64px;
    max-width: 64px;
    min-height: 64px;
    max-height: 64px;
    padding: 0;
    qproperty-iconSize: 64px 64px;
}
QPushButton#collapsedIcon:hover {
    border-color: rgba(255, 255, 255, 80);
    background: rgba(35, 35, 35, 160);
}
"""

COLLAPSED_FALLBACK_STYLE = """
QPushButton#collapsedIcon {
    background: rgba(32, 36, 44, 77);
    border: 1px solid rgba(255, 255, 255, 15);
    border-radius: 32px;
    color: #FFFFFF;
    font-size: 18px;
    font-weight: 600;
    min-width: 64px;
    max-width: 64px;
    min-height: 64px;
    max-height: 64px;
    padding: 0;
    qproperty-iconSize: 64px 64px;
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
