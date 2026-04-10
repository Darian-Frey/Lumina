"""
lumina/launcher/main.py
-----------------------
Application entry point.

Run with:
    python -m lumina
    or
    lumina  (if installed via pip install -e .)
"""

from __future__ import annotations

import logging
import sys

from PyQt6.QtWidgets import QApplication

from lumina.core.config import APP_NAME, APP_ORG, APP_VERSION
from lumina.launcher.mainwindow import MainWindow
from lumina.launcher.theme import apply_theme, get_saved_theme


def main() -> None:
    """Launch the Lumina application."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting %s v%s", APP_NAME, APP_VERSION)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(APP_ORG)

    # Apply saved theme
    theme = get_saved_theme()
    apply_theme(app, theme)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
