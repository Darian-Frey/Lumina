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
