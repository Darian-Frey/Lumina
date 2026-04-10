"""
lumina/launcher/theme.py
------------------------
Qt stylesheet loader for dark / light / high-contrast themes.

Theme preference is persisted in QSettings so it survives restarts.
"""

from __future__ import annotations

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QApplication

from lumina.core.config import (
    APP_NAME,
    APP_ORG,
    DEFAULT_THEME,
    THEME_DARK,
    THEME_HIGH_CONTRAST,
    THEME_LIGHT,
)

# ---------------------------------------------------------------------------
# Stylesheets
# ---------------------------------------------------------------------------

_STYLESHEET_LIGHT = """
QMainWindow, QWidget {
    background-color: #f5f5f5;
    color: #1e1e1e;
}
QGroupBox {
    font-weight: bold;
    border: 1px solid #cccccc;
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 12px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}
QPushButton {
    background-color: #e0e0e0;
    border: 1px solid #bbbbbb;
    border-radius: 4px;
    padding: 6px 14px;
    min-height: 20px;
}
QPushButton:hover {
    background-color: #d0d0d0;
}
QPushButton:pressed {
    background-color: #c0c0c0;
}
QSlider::groove:horizontal {
    height: 6px;
    background: #cccccc;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #1f77b4;
    width: 16px;
    margin: -5px 0;
    border-radius: 8px;
}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #ffffff;
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 4px 8px;
}
QTreeWidget {
    background-color: #ffffff;
    border: 1px solid #cccccc;
    border-radius: 4px;
}
QTreeWidget::item:selected {
    background-color: #1f77b4;
    color: #ffffff;
}
QToolBar {
    background-color: #e8e8e8;
    border-bottom: 1px solid #cccccc;
    spacing: 6px;
    padding: 4px;
}
QStatusBar {
    background-color: #e8e8e8;
    border-top: 1px solid #cccccc;
}
"""

_STYLESHEET_DARK = """
QMainWindow, QWidget {
    background-color: #1e1e1e;
    color: #d4d4d4;
}
QGroupBox {
    font-weight: bold;
    border: 1px solid #444444;
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 12px;
    color: #d4d4d4;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}
QPushButton {
    background-color: #333333;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 6px 14px;
    min-height: 20px;
    color: #d4d4d4;
}
QPushButton:hover {
    background-color: #444444;
}
QPushButton:pressed {
    background-color: #555555;
}
QSlider::groove:horizontal {
    height: 6px;
    background: #444444;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #569cd6;
    width: 16px;
    margin: -5px 0;
    border-radius: 8px;
}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #2d2d2d;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 4px 8px;
    color: #d4d4d4;
}
QTreeWidget {
    background-color: #252526;
    border: 1px solid #444444;
    border-radius: 4px;
    color: #d4d4d4;
}
QTreeWidget::item:selected {
    background-color: #264f78;
    color: #ffffff;
}
QToolBar {
    background-color: #252526;
    border-bottom: 1px solid #444444;
    spacing: 6px;
    padding: 4px;
}
QStatusBar {
    background-color: #252526;
    border-top: 1px solid #444444;
    color: #d4d4d4;
}
"""

_STYLESHEET_HIGH_CONTRAST = """
QMainWindow, QWidget {
    background-color: #000000;
    color: #ffffff;
}
QGroupBox {
    font-weight: bold;
    border: 2px solid #ffffff;
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 12px;
    color: #ffffff;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}
QPushButton {
    background-color: #000000;
    border: 2px solid #ffffff;
    border-radius: 4px;
    padding: 6px 14px;
    min-height: 20px;
    color: #ffffff;
}
QPushButton:hover {
    background-color: #333333;
}
QPushButton:pressed {
    background-color: #555555;
}
QSlider::groove:horizontal {
    height: 6px;
    background: #ffffff;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #ffff00;
    width: 16px;
    margin: -5px 0;
    border-radius: 8px;
}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #000000;
    border: 2px solid #ffffff;
    border-radius: 4px;
    padding: 4px 8px;
    color: #ffffff;
}
QTreeWidget {
    background-color: #000000;
    border: 2px solid #ffffff;
    border-radius: 4px;
    color: #ffffff;
}
QTreeWidget::item:selected {
    background-color: #ffff00;
    color: #000000;
}
QToolBar {
    background-color: #000000;
    border-bottom: 2px solid #ffffff;
    spacing: 6px;
    padding: 4px;
}
QStatusBar {
    background-color: #000000;
    border-top: 2px solid #ffffff;
    color: #ffffff;
}
"""

_STYLESHEETS: dict[str, str] = {
    THEME_LIGHT: _STYLESHEET_LIGHT,
    THEME_DARK: _STYLESHEET_DARK,
    THEME_HIGH_CONTRAST: _STYLESHEET_HIGH_CONTRAST,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_saved_theme() -> str:
    """Read the persisted theme preference from QSettings.

    Returns:
        The theme name string.
    """
    settings = QSettings(APP_ORG, APP_NAME)
    return str(settings.value("theme", DEFAULT_THEME))


def save_theme(theme: str) -> None:
    """Persist the theme preference to QSettings.

    Args:
        theme: One of "light", "dark", "high_contrast".
    """
    settings = QSettings(APP_ORG, APP_NAME)
    settings.setValue("theme", theme)


def get_colourblind_pref() -> bool:
    """Read the persisted colourblind palette preference.

    Returns:
        True if colourblind palette is enabled.
    """
    settings = QSettings(APP_ORG, APP_NAME)
    return settings.value("colourblind", False, type=bool)


def save_colourblind_pref(enabled: bool) -> None:
    """Persist the colourblind palette preference.

    Args:
        enabled: True to enable colourblind-safe palette.
    """
    settings = QSettings(APP_ORG, APP_NAME)
    settings.setValue("colourblind", enabled)


_current_theme: str = DEFAULT_THEME


def current_theme() -> str:
    """Return the currently active theme name."""
    return _current_theme


def apply_theme(app: QApplication, theme: str) -> None:
    """Apply a theme stylesheet to the entire application.

    Args:
        app: The QApplication instance.
        theme: One of "light", "dark", "high_contrast".
    """
    global _current_theme
    _current_theme = theme
    stylesheet = _STYLESHEETS.get(theme, _STYLESHEETS[DEFAULT_THEME])
    app.setStyleSheet(stylesheet)
