"""QSS styles for FloatNote neutral charcoal/gray translucent glass theme."""

FONT_FAMILY = '"Segoe UI Variable", "Segoe UI", sans-serif'
MONO_FONT_FAMILY = '"Cascadia Code", "Consolas", monospace'

CORNER_RADIUS = 15

# Base widget — neutral dark translucent glass for native acrylic/mica
BASE_STYLE = f"""
QWidget#glassRoot {{
    background: rgba(32, 36, 44, 115);
    border: 1px solid rgba(255, 255, 255, 22);
    border-top: 1px solid rgba(255, 255, 255, 45);
    border-left: 1px solid rgba(255, 255, 255, 32);
    border-radius: {CORNER_RADIUS}px;
    font-family: {FONT_FAMILY};
    color: #FFFFFF;
}}
"""

# Fallback when native acrylic is unavailable
FALLBACK_STYLE = f"""
QWidget#glassRoot {{
    background: rgba(32, 36, 44, 230);
    border: 1px solid rgba(255, 255, 255, 25);
    border-top: 1px solid rgba(255, 255, 255, 50);
    border-left: 1px solid rgba(255, 255, 255, 35);
    border-radius: {CORNER_RADIUS}px;
    font-family: {FONT_FAMILY};
    color: #FFFFFF;
}}
"""

HEADER_STYLE = f"""
QWidget#headerBar {{
    background: transparent;
    border: none;
    min-height: 32px;
    max-height: 32px;
}}
QLabel#titleLabel {{
    color: rgba(245, 245, 245, 225);
    font-size: 11px;
    font-weight: 600;
    padding-left: 2px;
    padding-right: 4px;
    background: transparent;
    border: none;
}}
QPushButton#headerBtn, QPushButton#menuBtn, QPushButton#previewBtn {{
    background: transparent;
    border: none;
    border-radius: 6px;
    color: rgba(230, 230, 230, 180);
    font-size: 13px;
    min-width: 26px;
    max-width: 26px;
    min-height: 26px;
    max-height: 26px;
    padding: 0;
}}
QPushButton#closeBtn {{
    background: transparent;
    border: none;
    border-radius: 6px;
    color: rgba(230, 230, 230, 180);
    font-size: 14px;
    min-width: 26px;
    max-width: 26px;
    min-height: 26px;
    max-height: 26px;
    padding: 0;
}}
QPushButton#closeBtn:hover {{
    background: rgba(232, 17, 35, 200);
    color: white;
}}
QPushButton#headerBtn:hover, QPushButton#menuBtn:hover, QPushButton#previewBtn:hover {{
    background: rgba(255, 255, 255, 30);
    color: #FFFFFF;
}}
QPushButton#headerBtn:pressed, QPushButton#menuBtn:pressed, QPushButton#previewBtn:pressed {{
    background: rgba(255, 255, 255, 18);
}}
"""

EDITOR_STYLE = f"""
QPlainTextEdit#noteEditor {{
    background: transparent;
    border: none;
    color: #FFFFFF;
    font-family: {FONT_FAMILY};
    font-size: 13px;
    line-height: 1.45;
    padding: 4px 10px 8px 10px;
    selection-background-color: rgba(255, 255, 255, 50);
    selection-color: #FFFFFF;
}}
QPlainTextEdit#noteEditor QScrollBar:vertical, QTextBrowser#notePreview QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 2px 2px 2px 0;
}}
QPlainTextEdit#noteEditor QScrollBar::handle:vertical, QTextBrowser#notePreview QScrollBar::handle:vertical {{
    background: rgba(255, 255, 255, 60);
    border-radius: 3px;
    min-height: 24px;
}}
QPlainTextEdit#noteEditor QScrollBar::handle:vertical:hover, QTextBrowser#notePreview QScrollBar::handle:vertical:hover {{
    background: rgba(255, 255, 255, 100);
}}
QPlainTextEdit#noteEditor QScrollBar::add-line:vertical,
QPlainTextEdit#noteEditor QScrollBar::sub-line:vertical,
QPlainTextEdit#noteEditor QScrollBar::add-page:vertical,
QPlainTextEdit#noteEditor QScrollBar::sub-page:vertical,
QTextBrowser#notePreview QScrollBar::add-line:vertical,
QTextBrowser#notePreview QScrollBar::sub-line:vertical,
QTextBrowser#notePreview QScrollBar::add-page:vertical,
QTextBrowser#notePreview QScrollBar::sub-page:vertical {{
    background: transparent;
    height: 0;
    border: none;
}}
QPlainTextEdit#noteEditor QScrollBar:horizontal, QTextBrowser#notePreview QScrollBar:horizontal {{
    height: 0;
}}
"""

PREVIEW_STYLE = f"""
QTextBrowser#notePreview {{
    background: transparent;
    border: none;
    color: #FFFFFF;
    font-family: {FONT_FAMILY};
    font-size: 13px;
    padding: 4px 10px 8px 10px;
    selection-background-color: rgba(255, 255, 255, 50);
    selection-color: #FFFFFF;
}}
"""

MARKDOWN_DOC_CSS = f"""
h1 {{
    font-size: 15px;
    font-weight: 700;
    color: #FFFFFF;
    margin-top: 6px;
    margin-bottom: 4px;
}}
h2 {{
    font-size: 14px;
    font-weight: 600;
    color: #EDEDED;
    margin-top: 5px;
    margin-bottom: 3px;
}}
h3, h4, h5, h6 {{
    font-size: 13px;
    font-weight: 600;
    color: #D6D6D6;
    margin-top: 4px;
    margin-bottom: 2px;
}}
p, li {{
    font-size: 12px;
    color: #F0F0F0;
    line-height: 1.4;
    margin-top: 2px;
    margin-bottom: 3px;
}}
code {{
    font-family: {MONO_FONT_FAMILY};
    font-size: 11px;
    background-color: rgba(255, 255, 255, 25);
    color: #E8E8E8;
    border-radius: 3px;
    padding: 1px 3px;
}}
pre {{
    font-family: {MONO_FONT_FAMILY};
    font-size: 11px;
    background-color: rgba(20, 22, 28, 200);
    color: #E0E0E0;
    border: 1px solid rgba(255, 255, 255, 30);
    border-radius: 5px;
    padding: 6px;
    margin: 4px 0;
}}
blockquote {{
    border-left: 3px solid rgba(255, 255, 255, 120);
    padding-left: 8px;
    margin-left: 0;
    color: rgba(230, 230, 230, 200);
    font-style: italic;
}}
a {{
    color: #8bbdff;
    text-decoration: none;
}}
hr {{
    height: 1px;
    border: none;
    background-color: rgba(255, 255, 255, 30);
    margin: 6px 0;
}}
"""

RESIZE_HANDLE_STYLE = """
QWidget#resizeHandle {
    background: transparent;
    min-height: 6px;
    max-height: 6px;
    border: none;
}
QWidget#resizeHandle:hover {
    background: rgba(255, 255, 255, 30);
}
"""

COLLAPSED_SIZE = 58
COLLAPSED_RADIUS = COLLAPSED_SIZE // 2

COLLAPSED_STYLE = f"""
QPushButton#collapsedIcon {{
    background: qradialgradient(
        cx: 0.35, cy: 0.35, radius: 0.75, fx: 0.25, fy: 0.25,
        stop: 0 rgba(62, 68, 78, 200),
        stop: 0.5 rgba(38, 42, 50, 215),
        stop: 1 rgba(22, 24, 30, 230)
    );
    border: 1px solid rgba(255, 255, 255, 25);
    border-top: 1px solid rgba(255, 255, 255, 60);
    border-left: 1px solid rgba(255, 255, 255, 45);
    border-radius: {COLLAPSED_RADIUS}px;
    color: #FFFFFF;
    font-size: 16px;
    font-weight: 600;
    min-width: {COLLAPSED_SIZE}px;
    max-width: {COLLAPSED_SIZE}px;
    min-height: {COLLAPSED_SIZE}px;
    max-height: {COLLAPSED_SIZE}px;
    padding: 0;
    qproperty-iconSize: {COLLAPSED_SIZE}px {COLLAPSED_SIZE}px;
}}
QPushButton#collapsedIcon:hover {{
    background: qradialgradient(
        cx: 0.35, cy: 0.35, radius: 0.75, fx: 0.25, fy: 0.25,
        stop: 0 rgba(80, 86, 98, 225),
        stop: 0.5 rgba(48, 54, 64, 230),
        stop: 1 rgba(28, 30, 38, 240)
    );
    border-color: rgba(255, 255, 255, 80);
}}
"""

COLLAPSED_FALLBACK_STYLE = f"""
QPushButton#collapsedIcon {{
    background: qradialgradient(
        cx: 0.35, cy: 0.35, radius: 0.75, fx: 0.25, fy: 0.25,
        stop: 0 rgba(55, 60, 70, 230),
        stop: 0.5 rgba(35, 38, 46, 240),
        stop: 1 rgba(20, 22, 28, 250)
    );
    border: 1px solid rgba(255, 255, 255, 30);
    border-top: 1px solid rgba(255, 255, 255, 65);
    border-left: 1px solid rgba(255, 255, 255, 50);
    border-radius: {COLLAPSED_RADIUS}px;
    color: #FFFFFF;
    font-size: 16px;
    font-weight: 600;
    min-width: {COLLAPSED_SIZE}px;
    max-width: {COLLAPSED_SIZE}px;
    min-height: {COLLAPSED_SIZE}px;
    max-height: {COLLAPSED_SIZE}px;
    padding: 0;
    qproperty-iconSize: {COLLAPSED_SIZE}px {COLLAPSED_SIZE}px;
}}
QPushButton#collapsedIcon:hover {{
    border-color: rgba(255, 255, 255, 85);
    background: qradialgradient(
        cx: 0.35, cy: 0.35, radius: 0.75, fx: 0.25, fy: 0.25,
        stop: 0 rgba(75, 82, 94, 240),
        stop: 0.5 rgba(45, 50, 60, 245),
        stop: 1 rgba(25, 28, 35, 255)
    );
}}
"""

MENU_STYLE = f"""
QMenu {{
    background-color: rgba(28, 31, 38, 250);
    border: 1px solid rgba(255, 255, 255, 30);
    border-radius: 8px;
    padding: 4px;
    color: #FFFFFF;
    font-family: {FONT_FAMILY};
    font-size: 12px;
}}
QMenu::item {{
    padding: 5px 22px 5px 12px;
    border-radius: 4px;
    color: rgba(240, 240, 240, 220);
}}
QMenu::item:selected {{
    background-color: rgba(255, 255, 255, 35);
    color: #FFFFFF;
}}
QMenu::item:disabled {{
    color: rgba(255, 255, 255, 70);
}}
QMenu::separator {{
    height: 1px;
    background: rgba(255, 255, 255, 30);
    margin: 4px 6px;
}}
"""

DIALOG_STYLE = f"""
QDialog {{
    background: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 rgba(36, 40, 48, 252),
        stop: 1 rgba(24, 26, 32, 254)
    );
    border: 1px solid rgba(255, 255, 255, 55);
    border-top: 1.5px solid rgba(255, 255, 255, 120);
    border-bottom: 1.5px solid rgba(255, 255, 255, 95);
    border-radius: 12px;
    font-family: {FONT_FAMILY};
    color: #FFFFFF;
}}
QLabel {{
    color: #FFFFFF;
    font-size: 12px;
}}
QLineEdit {{
    background: rgba(18, 20, 24, 220);
    border: 1px solid rgba(255, 255, 255, 40);
    border-radius: 6px;
    padding: 6px 10px;
    color: #FFFFFF;
    font-size: 13px;
    selection-background-color: rgba(255, 255, 255, 50);
}}
QLineEdit:focus {{
    border: 1px solid rgba(255, 255, 255, 120);
    background: rgba(24, 28, 34, 240);
}}
QComboBox {{
    background: rgba(18, 20, 24, 220);
    border: 1px solid rgba(255, 255, 255, 40);
    border-radius: 6px;
    padding: 5px 10px;
    color: #FFFFFF;
    font-size: 12px;
}}
QComboBox:hover {{
    background: rgba(25, 28, 35, 240);
    border-color: rgba(255, 255, 255, 70);
}}
QComboBox QAbstractItemView {{
    background: rgba(24, 26, 32, 252);
    border: 1px solid rgba(255, 255, 255, 45);
    border-radius: 6px;
    color: #FFFFFF;
    selection-background-color: rgba(255, 255, 255, 35);
}}
QRadioButton {{
    color: rgba(240, 240, 240, 220);
    font-size: 12px;
}}
QRadioButton::indicator {{
    width: 14px;
    height: 14px;
}}
QPushButton#dialogBtn {{
    background: rgba(255, 255, 255, 30);
    border: 1px solid rgba(255, 255, 255, 60);
    border-radius: 6px;
    color: #FFFFFF;
    font-size: 12px;
    font-weight: 500;
    padding: 6px 16px;
}}
QPushButton#dialogBtn:hover {{
    background: rgba(255, 255, 255, 48);
    border-color: rgba(255, 255, 255, 90);
}}
QPushButton#dialogBtn:pressed {{
    background: rgba(255, 255, 255, 20);
}}
QPushButton#cancelBtn {{
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 30);
    border-radius: 6px;
    color: rgba(255, 255, 255, 180);
    font-size: 12px;
    padding: 6px 14px;
}}
QPushButton#cancelBtn:hover {{
    background: rgba(255, 255, 255, 20);
    color: #FFFFFF;
}}
"""


def expanded_styles(use_fallback: bool) -> str:
    """Return combined QSS for expanded widget state."""
    root = FALLBACK_STYLE if use_fallback else BASE_STYLE
    return root + HEADER_STYLE + EDITOR_STYLE + PREVIEW_STYLE + RESIZE_HANDLE_STYLE + MENU_STYLE


def collapsed_styles(use_fallback: bool) -> str:
    """Return QSS for collapsed circular icon state."""
    icon = COLLAPSED_FALLBACK_STYLE if use_fallback else COLLAPSED_STYLE
    root = FALLBACK_STYLE if use_fallback else BASE_STYLE
    return root + icon + MENU_STYLE
