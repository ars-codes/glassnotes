"""QSS styles for GlassNotes dark glass theme."""

FONT_FAMILY = '"Segoe UI Variable", "Segoe UI", sans-serif'

CORNER_RADIUS = 12

# Base widget — dark translucent glass background for native acrylic/mica
BASE_STYLE = f"""
QWidget#glassRoot {{
    background: rgba(12, 18, 48, 180);
    border: 1px solid rgba(190, 210, 255, 90);
    border-radius: {CORNER_RADIUS}px;
    font-family: {FONT_FAMILY};
    color: #E8F4FF;
}}
"""

# Fallback when native acrylic is unavailable
FALLBACK_STYLE = f"""
QWidget#glassRoot {{
    /* deep navy / indigo vertical gradient with a subtle top gloss stop */
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(20, 30, 70, 224),      /* rich saturated navy at top */
        stop:0.06 rgba(60, 90, 200, 15),   /* thin glossy top inner highlight */
        stop:1 rgba(10, 14, 40, 235)       /* darker deep-blue at bottom */
    );
    /* rim-light: slightly cool, brighter thin border to read as rim */
    border: 1px solid rgba(190, 210, 255, 90);
    border-radius: {CORNER_RADIUS}px;
    font-family: {FONT_FAMILY};
    color: #E8F4FF; /* slightly cool white for legibility on blue */
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
    color: rgba(234, 244, 255, 184);
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
    color: rgba(255, 255, 255, 166);
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
    color: rgba(255, 255, 255, 166);
    font-size: 14px;
    min-width: 28px;
    max-width: 28px;
    min-height: 28px;
    max-height: 28px;
    padding: 0;
}
QPushButton#closeBtn:hover {
    background: rgba(232, 17, 35, 191);
    color: white;
}
QPushButton#headerBtn:hover {
    /* cool blue hover glow */
    background: rgba(100, 150, 255, 31);
    color: rgba(235, 246, 255, 250);
}
QPushButton#headerBtn:pressed {
    background: rgba(60, 110, 220, 26);
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
    /* slightly richer selection tint to match blue theme */
    selection-background-color: rgba(100, 150, 255, 128);
    selection-color: #FFFFFF;
}
QPlainTextEdit#noteEditor QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 2px 2px 2px 0;
}
QPlainTextEdit#noteEditor QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 56);
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
    /* jeweled radial: brighter center, deep outer rim */
    background: qradialgradient(
        cx:0.5, cy:0.5, radius:0.85,
        fx:0.5, fy:0.5,
        stop:0 rgba(70, 110, 230, 178),   /* jewel-blue center glow */
        stop:0.6 rgba(30, 60, 150, 128),
        stop:1 rgba(15, 20, 55, 242)     /* deep outer edge */
    );
    border: 1px solid rgba(190, 210, 255, 90);
    border-radius: 24px;
    color: #EAF4FF;
    font-size: 18px;
    font-weight: 600;
    min-width: 48px;
    max-width: 48px;
    min-height: 48px;
    max-height: 48px;
    padding: 0;
    qproperty-iconSize: 26px 26px;
}
QPushButton#collapsedIcon:hover {
    border-color: rgba(220, 235, 255, 128);
    background: qradialgradient(
        cx:0.5, cy:0.5, radius:0.85,
        fx:0.5, fy:0.5,
        stop:0 rgba(90, 130, 250, 199),
        stop:1 rgba(18, 26, 70, 250)
    );
}
"""

COLLAPSED_FALLBACK_STYLE = """
QPushButton#collapsedIcon {
    background: qradialgradient(
        cx:0.5, cy:0.5, radius:0.85,
        fx:0.5, fy:0.5,
        stop:0 rgba(70, 110, 230, 178),
        stop:1 rgba(15, 20, 55, 242)
    );
    border: 1px solid rgba(190, 210, 255, 90);
    border-radius: 24px;
    color: #EAF4FF;
    font-size: 18px;
    font-weight: 600;
    min-width: 48px;
    max-width: 48px;
    min-height: 48px;
    max-height: 48px;
    padding: 0;
    qproperty-iconSize: 26px 26px;
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
