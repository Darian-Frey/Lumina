"""
lumina/core/config.py
---------------------
Global constants, paths, theme definitions, and colour palettes.

All configurable settings live here. Modules should import from this file
rather than defining their own constants.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PACKAGE_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
PROJECT_ROOT: Final[Path] = PACKAGE_ROOT.parent
DATA_DIR: Final[Path] = PACKAGE_ROOT / "data"
SPARC_DIR: Final[Path] = DATA_DIR / "sparc"

# ---------------------------------------------------------------------------
# Application metadata
# ---------------------------------------------------------------------------

APP_NAME: Final[str] = "Lumina"
APP_VERSION: Final[str] = "0.1.0-dev"
APP_ORG: Final[str] = "Darian-Frey"

# ---------------------------------------------------------------------------
# Simulation defaults
# ---------------------------------------------------------------------------

DEFAULT_FPS: Final[int] = 30
DEFAULT_TIMER_MS: Final[int] = 1000 // DEFAULT_FPS  # ~33 ms
MAX_FPS: Final[int] = 60

DEFAULT_EXPORT_DPI: Final[int] = 300

# ---------------------------------------------------------------------------
# Physics constants (shared across modules)
# ---------------------------------------------------------------------------

# RotoCurve / CODA — do not change without discussion (see CLAUDE.md)
A0_CANONICAL: Final[float] = 1.2e-10       # m/s^2 — MOND canonical acceleration scale
A0_CODA: Final[float] = 1.264e-10          # m/s^2 — CODA zero-parameter prediction
F_Q_LIMIT: Final[float] = 2.0 / 3.0        # F(Q) ~ (2/3) Q^{3/2} limit
CAUSALITY_BOUND: Final[float] = 0.35        # lambda <= 0.35
SPARC_N_GALAXIES: Final[int] = 175

# ---------------------------------------------------------------------------
# Colour palettes
# ---------------------------------------------------------------------------

# Standard palette — vibrant, general use
PALETTE_STANDARD: Final[list[str]] = [
    "#1f77b4",  # blue
    "#ff7f0e",  # orange
    "#2ca02c",  # green
    "#d62728",  # red
    "#9467bd",  # purple
    "#8c564b",  # brown
    "#e377c2",  # pink
    "#7f7f7f",  # grey
    "#bcbd22",  # olive
    "#17becf",  # cyan
]

# Colourblind-safe palette — Okabe-Ito (2008)
PALETTE_COLOURBLIND: Final[list[str]] = [
    "#0072B2",  # blue
    "#E69F00",  # orange
    "#009E73",  # green
    "#D55E00",  # vermillion
    "#CC79A7",  # pink
    "#56B4E9",  # sky blue
    "#F0E442",  # yellow
    "#000000",  # black
]

# ---------------------------------------------------------------------------
# Theme definitions
# ---------------------------------------------------------------------------

THEME_LIGHT: Final[str] = "light"
THEME_DARK: Final[str] = "dark"
THEME_HIGH_CONTRAST: Final[str] = "high_contrast"
DEFAULT_THEME: Final[str] = THEME_LIGHT

THEME_PLOT_BACKGROUNDS: Final[dict[str, str]] = {
    THEME_LIGHT: "#ffffff",
    THEME_DARK: "#1e1e1e",
    THEME_HIGH_CONTRAST: "#000000",
}

THEME_PLOT_FOREGROUNDS: Final[dict[str, str]] = {
    THEME_LIGHT: "#000000",
    THEME_DARK: "#d4d4d4",
    THEME_HIGH_CONTRAST: "#ffffff",
}

# ---------------------------------------------------------------------------
# Level display labels (for the launcher UI)
# ---------------------------------------------------------------------------

LEVEL_LABELS: Final[dict[str, str]] = {
    "GCSE": "GCSE",
    "A-level": "A-level",
    "University": "University",
    "Research": "Research",
}

LEVEL_COLOURS: Final[dict[str, str]] = {
    "GCSE": "#4caf50",
    "A-level": "#ff9800",
    "University": "#f44336",
    "Research": "#9c27b0",
}

# ---------------------------------------------------------------------------
# Preset file extension
# ---------------------------------------------------------------------------

PRESET_EXTENSION: Final[str] = ".lumina"

# ---------------------------------------------------------------------------
# Category display colours and icons (for dashboard cards)
# ---------------------------------------------------------------------------

CATEGORY_COLOURS: Final[dict[str, str]] = {
    "mechanics": "#2196F3",
    "waves": "#00BCD4",
    "electromagnetism": "#FF9800",
    "thermodynamics": "#F44336",
    "quantum": "#9C27B0",
    "astrophysics": "#3F51B5",
    "pure_maths": "#4CAF50",
    "applied_maths": "#607D8B",
    "special_topics": "#795548",
}

CATEGORY_ICONS: Final[dict[str, str]] = {
    "mechanics": "\u2699",      # gear
    "waves": "\u223f",          # sine wave
    "electromagnetism": "\u26a1",  # lightning
    "thermodynamics": "\u2668",   # hot springs
    "quantum": "\u269b",         # atom
    "astrophysics": "\u2b50",    # star
    "pure_maths": "\u2261",      # triple bar
    "applied_maths": "\u222b",   # integral
    "special_topics": "\u2623",  # biohazard
}

# ---------------------------------------------------------------------------
# Standard control panel width
# ---------------------------------------------------------------------------

CONTROL_PANEL_WIDTH: Final[int] = 240


def current_fg_colour() -> str:
    """Return the foreground colour for the current theme.

    Use this for plot elements (rods, arrows, box borders) that need
    to contrast against the plot background.
    """
    try:
        from lumina.launcher.theme import current_theme
        theme = current_theme()
    except ImportError:
        theme = THEME_LIGHT
    return THEME_PLOT_FOREGROUNDS.get(theme, "#000000")


def current_mid_colour() -> str:
    """Return a mid-tone colour for the current theme.

    Use this for secondary plot elements (grid lines, arrow fields)
    that should be visible but not dominant.
    """
    try:
        from lumina.launcher.theme import current_theme
        theme = current_theme()
    except ImportError:
        theme = THEME_LIGHT

    mid_colours = {
        THEME_LIGHT: "#888888",
        THEME_DARK: "#999999",
        THEME_HIGH_CONTRAST: "#cccccc",
    }
    return mid_colours.get(theme, "#888888")

# ---------------------------------------------------------------------------
# Shared button styles
# ---------------------------------------------------------------------------

BTN_STYLE_COMPUTE: Final[str] = (
    "QPushButton { font-weight: bold; padding: 8px; "
    "background-color: #1f77b4; color: white; border-radius: 4px; }"
    "QPushButton:hover { background-color: #1a6aa5; }"
)

BTN_STYLE_RESET: Final[str] = (
    "QPushButton { font-weight: bold; padding: 6px; "
    "background-color: #ff7f0e; color: white; border-radius: 4px; }"
    "QPushButton:hover { background-color: #e06600; }"
)
