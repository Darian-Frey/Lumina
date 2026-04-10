"""
lumina/core/help_dialog.py
--------------------------
Shared help dialog for simulation modules.

Displays the module's HELP_TEXT in a scrollable, formatted dialog.
Launched from the toolbar "?" button.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class HelpDialog(QDialog):
    """A modal help dialog displaying formatted help text for a simulation.

    Args:
        title: Dialog window title (e.g. "AP01 — ODE Phase Portrait").
        help_text: The help content string. Supports basic formatting:
            - Lines starting with # are rendered as bold headings.
            - Lines starting with - are rendered as bullet points.
            - Blank lines create paragraph breaks.
            - All other lines are rendered as body text.
        parent: Parent widget.
    """

    def __init__(
        self,
        title: str,
        help_text: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(520, 400)
        self.resize(600, 500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(8, 8, 8, 8)
        content_layout.setSpacing(4)

        # Parse and render the help text
        for line in help_text.strip().split("\n"):
            stripped = line.strip()

            if not stripped:
                # Blank line — spacer
                spacer = QLabel("")
                spacer.setFixedHeight(8)
                content_layout.addWidget(spacer)
            elif stripped.startswith("# "):
                # Heading
                heading = QLabel(stripped[2:])
                heading.setFont(QFont("sans-serif", 13, QFont.Weight.Bold))
                heading.setStyleSheet("color: #1f77b4; margin-top: 8px;")
                heading.setWordWrap(True)
                content_layout.addWidget(heading)
            elif stripped.startswith("## "):
                # Sub-heading
                heading = QLabel(stripped[3:])
                heading.setFont(QFont("sans-serif", 11, QFont.Weight.Bold))
                heading.setStyleSheet("color: #333333; margin-top: 4px;")
                heading.setWordWrap(True)
                content_layout.addWidget(heading)
            elif stripped.startswith("- "):
                # Bullet point
                bullet = QLabel(f"  \u2022  {stripped[2:]}")
                bullet.setFont(QFont("sans-serif", 10))
                bullet.setWordWrap(True)
                bullet.setStyleSheet("margin-left: 12px;")
                content_layout.addWidget(bullet)
            else:
                # Body text
                body = QLabel(stripped)
                body.setFont(QFont("sans-serif", 10))
                body.setWordWrap(True)
                body.setStyleSheet("color: #333333;")
                content_layout.addWidget(body)

        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        # Close button
        btn_close = QPushButton("Close")
        btn_close.setFixedWidth(100)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)
