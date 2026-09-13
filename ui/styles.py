"""QSS styles for FloatNote v2 glossy deep-blue glass theme."""

FONT_FAMILY = '"Segoe UI Variable", "Segoe UI", sans-serif'
MONO_FONT_FAMILY = '"Cascadia Code", "Consolas", monospace'

CORNER_RADIUS = 15

# Base widget — rich translucent deep-blue glass for native acrylic/mica
BASE_STYLE = f"""
QWidget#glassRoot {{
    background: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 rgba(18, 34, 75, 125),
        stop: 0.5 rgba(11, 22, 54, 115),
        stop: 1 rgba(7, 14, 38, 135)
    );
    border: 1px solid rgba(135, 185, 255, 45);
    border-top: 1px solid rgba(190, 225, 255, 90);
    border-left: 1px solid rgba(170, 210, 255, 75);
    border-radius: {CORNER_RADIUS}px;
    font-family: {FONT_FAMILY};
    color: #FFFFFF;
}}
"""

# Fallback when native acrylic is unavailable
FALLBACK_STYLE = f"""
QWidget#glassRoot {{
    background: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 rgba(18, 34, 75, 220),
        stop: 0.5 rgba(11, 22, 54, 230),
        stop: 1 rgba(7, 14, 38, 240)
    );
    border: 1px solid rgba(135, 185, 255, 55);
    border-top: 1px solid rgba(190, 225, 255, 95);
    border-left: 1px solid rgba(170, 210, 255, 80);
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
    color: rgba(235, 245, 255, 225);
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
    color: rgba(215, 235, 255, 180);
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
    color: rgba(215, 235, 255, 180);
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
    background: rgba(120, 175, 255, 40);
    color: #FFFFFF;
}}
QPushButton#headerBtn:pressed, QPushButton#menuBtn:pressed, QPushButton#previewBtn:pressed {{
    background: rgba(120, 175, 255, 65);
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
    selection-background-color: rgba(80, 140, 245, 90);
    selection-color: #FFFFFF;
}}
QPlainTextEdit#noteEditor QScrollBar:vertical, QTextBrowser#notePreview QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 2px 2px 2px 0;
}}
QPlainTextEdit#noteEditor QScrollBar::handle:vertical, QTextBrowser#notePreview QScrollBar::handle:vertical {{
    background: rgba(150, 195, 255, 60);
    border-radius: 3px;
    min-height: 24px;
}}
QPlainTextEdit#noteEditor QScrollBar::handle:vertical:hover, QTextBrowser#notePreview QScrollBar::handle:vertical:hover {{
    background: rgba(180, 215, 255, 100);
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
    selection-background-color: rgba(80, 140, 245, 90);
    selection-color: #FFFFFF;
}}
"""

MARKDOWN_DOC_CSS = f"""
h1 {{
    font-size: 15px;
    font-weight: 700;
    color: #9eccff;
    margin-top: 6px;
    margin-bottom: 4px;
}}
h2 {{
    font-size: 14px;
    font-weight: 600;
    color: #b8dbff;
    margin-top: 5px;
    margin-bottom: 3px;
}}
h3, h4, h5, h6 {{
    font-size: 13px;
    font-weight: 600;
    color: #d6e8ff;
    margin-top: 4px;
    margin-bottom: 2px;
}}
p, li {{
    font-size: 12px;
    color: #f0f6ff;
    line-height: 1.4;
    margin-top: 2px;
    margin-bottom: 3px;
}}
code {{
    font-family: {MONO_FONT_FAMILY};
    font-size: 11px;
    background-color: rgba(255, 255, 255, 30);
    color: #aed8ff;
    border-radius: 3px;
    padding: 1px 3px;
}}
pre {{
    font-family: {MONO_FONT_FAMILY};
    font-size: 11px;
    background-color: rgba(8, 16, 38, 175);
    color: #cde4ff;
    border: 1px solid rgba(135, 185, 255, 45);
    border-radius: 5px;
    padding: 6px;
    margin: 4px 0;
}}
blockquote {{
    border-left: 3px solid #589bff;
    padding-left: 8px;
    margin-left: 0;
    color: rgba(220, 235, 255, 190);
    font-style: italic;
}}
a {{
    color: #6cb8ff;
    text-decoration: none;
}}
hr {{
    height: 1px;
    border: none;
    background-color: rgba(135, 185, 255, 45);
    margin: 6px 0;
}}
"""

RESIZE_HANDLE_STYLE = """
QWidget#resizeHandle {{
    background: transparent;
    min-height: 6px;
    max-height: 6px;
    border: none;
}}
QWidget#resizeHandle:hover {{
    background: rgba(120, 175, 255, 30);
}}
"""

COLLAPSED_STYLE = """
QPushButton#collapsedIcon {{
    background: qradialgradient(
        cx: 0.35, cy: 0.35, radius: 0.75, fx: 0.25, fy: 0.25,
        stop: 0 rgba(50, 95, 210, 200),
        stop: 0.5 rgba(22, 44, 95, 215),
        stop: 1 rgba(10, 18, 45, 230)
    );
    border: 1px solid rgba(135, 185, 255, 60);
    border-top: 1px solid rgba(200, 235, 255, 120);
    border-left: 1px solid rgba(180, 220, 255, 95);
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
}}
QPushButton#collapsedIcon:hover {{
    background: qradialgradient(
        cx: 0.35, cy: 0.35, radius: 0.75, fx: 0.25, fy: 0.25,
        stop: 0 rgba(70, 120, 235, 225),
        stop: 0.5 rgba(30, 60, 125, 230),
        stop: 1 rgba(14, 26, 60, 240)
    );
    border-color: rgba(210, 240, 255, 160);
}}
"""

COLLAPSED_FALLBACK_STYLE = """
QPushButton#collapsedIcon {{
    background: qradialgradient(
        cx: 0.35, cy: 0.35, radius: 0.75, fx: 0.25, fy: 0.25,
        stop: 0 rgba(45, 90, 200, 230),
        stop: 0.5 rgba(20, 40, 90, 240),
        stop: 1 rgba(8, 16, 40, 250)
    );
    border: 1px solid rgba(135, 185, 255, 65);
    border-top: 1px solid rgba(200, 235, 255, 125);
    border-left: 1px solid rgba(180, 220, 255, 100);
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
}}
QPushButton#collapsedIcon:hover {{
    border-color: rgba(210, 240, 255, 170);
    background: qradialgradient(
        cx: 0.35, cy: 0.35, radius: 0.75, fx: 0.25, fy: 0.25,
        stop: 0 rgba(65, 115, 230, 240),
        stop: 0.5 rgba(28, 55, 120, 245),
        stop: 1 rgba(12, 22, 55, 255)
    );
}}
"""

MENU_STYLE = f"""
QMenu {{
    background-color: rgba(12, 22, 50, 245);
    border: 1px solid rgba(135, 185, 255, 60);
    border-radius: 8px;
    padding: 4px;
    color: #FFFFFF;
    font-family: {FONT_FAMILY};
    font-size: 12px;
}}
QMenu::item {{
    padding: 5px 22px 5px 12px;
    border-radius: 4px;
    color: rgba(240, 248, 255, 220);
}}
QMenu::item:selected {{
    background-color: rgba(60, 115, 225, 150);
    color: #FFFFFF;
}}
QMenu::item:disabled {{
    color: rgba(255, 255, 255, 70);
}}
QMenu::separator {{
    height: 1px;
    background: rgba(135, 185, 255, 40);
    margin: 4px 6px;
}}
"""

DIALOG_STYLE = f"""
QDialog {{
    background: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 rgba(16, 30, 68, 248),
        stop: 1 rgba(8, 16, 40, 252)
    );
    border: 1px solid rgba(135, 185, 255, 75);
    border-radius: 12px;
    font-family: {FONT_FAMILY};
    color: #FFFFFF;
}}
QLabel {{
    color: #FFFFFF;
    font-size: 12px;
}}
QLineEdit {{
    background: rgba(255, 255, 255, 20);
    border: 1px solid rgba(135, 185, 255, 55);
    border-radius: 6px;
    padding: 6px 10px;
    color: #FFFFFF;
    font-size: 13px;
    selection-background-color: rgba(80, 140, 245, 120);
}}
QLineEdit:focus {{
    border: 1px solid rgba(120, 185, 255, 180);
    background: rgba(255, 255, 255, 30);
}}
QComboBox {{
    background: rgba(255, 255, 255, 20);
    border: 1px solid rgba(135, 185, 255, 55);
    border-radius: 6px;
    padding: 5px 10px;
    color: #FFFFFF;
    font-size: 12px;
}}
QComboBox:hover {{
    background: rgba(255, 255, 255, 30);
}}
QComboBox QAbstractItemView {{
    background: rgba(14, 26, 56, 250);
    border: 1px solid rgba(135, 185, 255, 60);
    border-radius: 6px;
    color: #FFFFFF;
    selection-background-color: rgba(60, 115, 225, 150);
}}
QRadioButton {{
    color: rgba(235, 245, 255, 210);
    font-size: 12px;
}}
QRadioButton::indicator {{
    width: 14px;
    height: 14px;
}}
QPushButton#dialogBtn {{
    background: rgba(60, 115, 225, 140);
    border: 1px solid rgba(135, 185, 255, 80);
    border-radius: 6px;
    color: #FFFFFF;
    font-size: 12px;
    font-weight: 500;
    padding: 6px 16px;
}}
QPushButton#dialogBtn:hover {{
    background: rgba(75, 135, 245, 190);
    border-color: rgba(180, 220, 255, 140);
}}
QPushButton#dialogBtn:pressed {{
    background: rgba(50, 100, 205, 180);
}}
QPushButton#cancelBtn {{
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 35);
    border-radius: 6px;
    color: rgba(255, 255, 255, 180);
    font-size: 12px;
    padding: 6px 14px;
}}
QPushButton#cancelBtn:hover {{
    background: rgba(255, 255, 255, 25);
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

