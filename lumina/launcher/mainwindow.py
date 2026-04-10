"""
lumina/launcher/mainwindow.py
-----------------------------
Top-level QMainWindow — the Lumina dashboard.

Layout:
  - Left sidebar: category tree with simulation counts
  - Central area: card grid (browsing) or simulation widget (running)
  - Top toolbar: search, level filter, play/pause/reset/export, theme toggle
  - Status bar: current simulation info
"""

from __future__ import annotations

import logging
from typing import Any

from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QToolBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from lumina.core.config import (
    APP_NAME,
    APP_VERSION,
    CATEGORY_COLOURS,
    CATEGORY_ICONS,
    LEVEL_COLOURS,
    LEVEL_LABELS,
    PRESET_EXTENSION,
    THEME_DARK,
    THEME_HIGH_CONTRAST,
    THEME_LIGHT,
)
from lumina.core.engine import SimulationBase
from lumina.core.help_dialog import HelpDialog
from lumina.launcher.module_loader import discover_modules
from lumina.launcher.theme import (
    apply_theme,
    get_colourblind_pref,
    get_saved_theme,
    save_colourblind_pref,
    save_theme,
)

logger = logging.getLogger(__name__)

# Category display names
_CATEGORY_NAMES: dict[str, str] = {
    "mechanics": "Classical Mechanics",
    "waves": "Waves & Optics",
    "electromagnetism": "Electromagnetism",
    "thermodynamics": "Thermodynamics",
    "quantum": "Quantum Mechanics",
    "astrophysics": "Astrophysics & Gravity",
    "pure_maths": "Pure Mathematics",
    "applied_maths": "Applied Mathematics",
    "special_topics": "Special Topics",
}


class SimulationCard(QFrame):
    """A clickable card with category colour banner and icon."""

    clicked = pyqtSignal()

    def __init__(
        self,
        sim_class: type[SimulationBase],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.sim_class = sim_class
        self.setObjectName("simCard")

        cat_colour = CATEGORY_COLOURS.get(sim_class.CATEGORY, "#607D8B")
        cat_icon = CATEGORY_ICONS.get(sim_class.CATEGORY, "\u2022")
        level_colour = LEVEL_COLOURS.get(sim_class.LEVEL, "#999999")
        level_text = LEVEL_LABELS.get(sim_class.LEVEL, sim_class.LEVEL)

        self.setFixedSize(310, 150)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFrameShape(QFrame.Shape.StyledPanel)

        self._cat_colour = cat_colour

        # Theme-adaptive card styles — inherit bg/text from the app theme
        # Only category-specific colours are hardcoded
        self._normal_ss = (
            f"QFrame#simCard {{ border: 2px solid palette(mid);"
            f" border-radius: 8px; border-left: 5px solid {cat_colour}; }}"
            f"QFrame#simCard QLabel {{ background: transparent; border: none; }}"
        )
        self._hover_ss = (
            f"QFrame#simCard {{ border: 2px solid {cat_colour};"
            f" border-radius: 8px; border-left: 5px solid {cat_colour}; }}"
            f"QFrame#simCard QLabel {{ background: transparent; border: none; }}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 8)
        layout.setSpacing(4)

        # Row 1: category icon + ID badge + name
        header = QHBoxLayout()
        header.setSpacing(6)

        icon_label = QLabel(cat_icon)
        icon_label.setFont(QFont("sans-serif", 16))
        icon_label.setFixedWidth(24)
        icon_label.setStyleSheet(f"color: {cat_colour};")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(icon_label)

        id_label = QLabel(sim_class.ID)
        id_label.setFont(QFont("monospace", 8, QFont.Weight.Bold))
        id_label.setFixedWidth(42)
        id_label.setFixedHeight(20)
        id_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        id_label.setStyleSheet(
            f"background-color: {cat_colour} !important; color: #ffffff;"
            f" padding: 1px 4px; border-radius: 3px;"
        )
        header.addWidget(id_label)

        name_label = QLabel(sim_class.NAME)
        name_label.setFont(QFont("sans-serif", 11, QFont.Weight.Bold))
        name_label.setWordWrap(True)
        header.addWidget(name_label, 1)
        layout.addLayout(header)

        # Row 2: description
        desc = QLabel(sim_class.DESCRIPTION)
        desc.setWordWrap(True)
        desc.setFont(QFont("sans-serif", 9))
        layout.addWidget(desc, 1)

        # Row 3: level badge + category name
        footer = QHBoxLayout()
        footer.setSpacing(8)

        level_label = QLabel(level_text)
        level_label.setFont(QFont("sans-serif", 8, QFont.Weight.Bold))
        level_label.setStyleSheet(
            f"color: #ffffff; background-color: {level_colour} !important;"
            f" padding: 1px 6px; border-radius: 2px;"
        )
        footer.addWidget(level_label)

        cat_name = _CATEGORY_NAMES.get(sim_class.CATEGORY, sim_class.CATEGORY)
        cat_label = QLabel(cat_name)
        cat_label.setFont(QFont("sans-serif", 8))
        cat_label.setStyleSheet(f"color: {cat_colour};")
        footer.addWidget(cat_label)
        footer.addStretch()

        layout.addLayout(footer)

        self.setStyleSheet(self._normal_ss)

    def enterEvent(self, event: Any) -> None:
        self.setStyleSheet(self._hover_ss)
        super().enterEvent(event)

    def leaveEvent(self, event: Any) -> None:
        self.setStyleSheet(self._normal_ss)
        super().leaveEvent(event)

    def mousePressEvent(self, event: Any) -> None:
        self.clicked.emit()
        super().mousePressEvent(event)


class MainWindow(QMainWindow):
    """The Lumina launcher — dashboard + simulation host."""

    def __init__(self) -> None:
        super().__init__()

        self._current_theme = get_saved_theme()
        self._colourblind = get_colourblind_pref()
        self._sim_classes: list[type[SimulationBase]] = []
        self._active_sim: SimulationBase | None = None

        self._setup_window()
        self._build_toolbar()
        self._build_ui()
        self._build_status_bar()
        self._load_modules()

    def _setup_window(self) -> None:
        """Configure the main window properties."""
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)

    def _build_toolbar(self) -> None:
        """Build the top toolbar with search, filters, and controls.

        Qt toolbar visibility is controlled via QAction references, not
        widget.setVisible(). Each addWidget() call returns a QAction that
        must be toggled instead.
        """
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)

        # --- Dashboard controls (visible on dashboard) ---
        self._search_field = QLineEdit()
        self._search_field.setPlaceholderText("Search simulations...")
        self._search_field.setFixedWidth(220)
        self._search_field.textChanged.connect(self._filter_cards)
        self._act_search = toolbar.addWidget(self._search_field)

        self._level_filter = QComboBox()
        self._level_filter.addItem("All Levels", "")
        for key, label in LEVEL_LABELS.items():
            self._level_filter.addItem(label, key)
        self._level_filter.setFixedWidth(140)
        self._level_filter.currentIndexChanged.connect(self._filter_cards)
        self._act_level = toolbar.addWidget(self._level_filter)

        # --- Simulation controls (visible when a sim is active) ---
        self._btn_back = QPushButton("\u2190  Dashboard")
        self._btn_back.setStyleSheet(
            "QPushButton { font-weight: bold; padding: 6px 16px; "
            "background-color: #1f77b4; color: white; border-radius: 4px; }"
            "QPushButton:hover { background-color: #1a6aa5; }"
        )
        self._btn_back.clicked.connect(self._show_dashboard)
        self._act_back = toolbar.addWidget(self._btn_back)
        self._act_back.setVisible(False)

        self._sim_label = QLabel()
        self._sim_label.setFont(QFont("sans-serif", 10, QFont.Weight.Bold))
        self._act_sim_label = toolbar.addWidget(self._sim_label)
        self._act_sim_label.setVisible(False)

        self._act_sep = toolbar.addSeparator()
        self._act_sep.setVisible(False)

        self._btn_reset = QPushButton("\u21ba  Reset")
        self._btn_reset.setToolTip("Reset simulation to default parameters")
        self._btn_reset.clicked.connect(self._reset_sim)
        self._act_reset = toolbar.addWidget(self._btn_reset)
        self._act_reset.setVisible(False)

        self._btn_export = QPushButton("\u2913  Export")
        self._btn_export.setToolTip("Export plots as PNG and data as CSV")
        self._btn_export.clicked.connect(self._export_sim)
        self._act_export = toolbar.addWidget(self._btn_export)
        self._act_export.setVisible(False)

        self._btn_save = QPushButton("\u2b07  Save")
        self._btn_save.setToolTip("Save simulation state to a .lumina file")
        self._btn_save.clicked.connect(self._save_state)
        self._act_save = toolbar.addWidget(self._btn_save)
        self._act_save.setVisible(False)

        self._btn_load = QPushButton("\u2b06  Load")
        self._btn_load.setToolTip("Load simulation state from a .lumina file")
        self._btn_load.clicked.connect(self._load_state)
        self._act_load = toolbar.addWidget(self._btn_load)
        self._act_load.setVisible(False)

        self._btn_help = QPushButton("\u2753")
        self._btn_help.setFixedWidth(34)
        self._btn_help.setStyleSheet(
            "QPushButton { font-size: 14px; padding: 4px; "
            "background-color: #17becf; color: white; border-radius: 4px; }"
            "QPushButton:hover { background-color: #139bab; }"
        )
        self._btn_help.setToolTip("Show help for this simulation")
        self._btn_help.clicked.connect(self._show_help)
        self._act_help = toolbar.addWidget(self._btn_help)
        self._act_help.setVisible(False)

        # --- Right-aligned: theme controls (always visible) ---
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        self._theme_combo = QComboBox()
        self._theme_combo.addItem("Light", THEME_LIGHT)
        self._theme_combo.addItem("Dark", THEME_DARK)
        self._theme_combo.addItem("High Contrast", THEME_HIGH_CONTRAST)
        for i in range(self._theme_combo.count()):
            if self._theme_combo.itemData(i) == self._current_theme:
                self._theme_combo.setCurrentIndex(i)
                break
        self._theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        toolbar.addWidget(self._theme_combo)

        self._btn_colourblind = QPushButton("CB Palette")
        self._btn_colourblind.setCheckable(True)
        self._btn_colourblind.setChecked(self._colourblind)
        self._btn_colourblind.clicked.connect(self._on_colourblind_toggled)
        toolbar.addWidget(self._btn_colourblind)

    def _build_ui(self) -> None:
        """Build the main content area — sidebar + stacked widget."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Splitter: sidebar | content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # --- Sidebar: category tree ---
        self._category_tree = QTreeWidget()
        self._category_tree.setHeaderHidden(True)
        self._category_tree.setFixedWidth(220)
        self._category_tree.setIndentation(16)
        self._category_tree.itemClicked.connect(self._on_category_clicked)

        # "All" top-level item
        self._all_item = QTreeWidgetItem(["All Simulations"])
        self._all_item.setFont(0, QFont("sans-serif", 10, QFont.Weight.Bold))
        self._category_tree.addTopLevelItem(self._all_item)

        # Category items (populated when modules load)
        self._category_items: dict[str, QTreeWidgetItem] = {}
        for cat_key, cat_name in _CATEGORY_NAMES.items():
            item = QTreeWidgetItem([cat_name])
            item.setData(0, Qt.ItemDataRole.UserRole, cat_key)
            self._category_tree.addTopLevelItem(item)
            self._category_items[cat_key] = item

        splitter.addWidget(self._category_tree)

        # --- Content stack: dashboard or simulation ---
        self._stack = QStackedWidget()
        splitter.addWidget(self._stack)

        # Page 0: Dashboard (card grid)
        self._dashboard_page = QWidget()
        dash_layout = QVBoxLayout(self._dashboard_page)
        dash_layout.setContentsMargins(16, 16, 16, 16)

        self._dashboard_title = QLabel("All Simulations")
        self._dashboard_title.setFont(QFont("sans-serif", 16, QFont.Weight.Bold))
        dash_layout.addWidget(self._dashboard_title)

        # Scrollable card area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._card_container = QWidget()
        self._card_layout = QGridLayout(self._card_container)
        self._card_layout.setSpacing(12)
        self._card_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )
        scroll.setWidget(self._card_container)
        dash_layout.addWidget(scroll, 1)

        self._stack.addWidget(self._dashboard_page)

        # Page 1: Simulation host (populated when a sim is launched)
        self._sim_page = QWidget()
        self._sim_layout = QVBoxLayout(self._sim_page)
        self._sim_layout.setContentsMargins(0, 0, 0, 0)
        self._stack.addWidget(self._sim_page)

        # Set initial splitter proportions
        splitter.setSizes([220, 1060])

    def _build_status_bar(self) -> None:
        """Build the bottom status bar."""
        status = QStatusBar()
        self.setStatusBar(status)
        self._status_label = QLabel(f"{APP_NAME} v{APP_VERSION} — Ready")
        status.addPermanentWidget(self._status_label)

    # ------------------------------------------------------------------
    # Module loading
    # ------------------------------------------------------------------

    def _load_modules(self) -> None:
        """Discover simulation modules and populate the dashboard."""
        self._sim_classes = discover_modules()
        logger.info("Loaded %d simulation modules", len(self._sim_classes))

        # Update category counts in sidebar
        category_counts: dict[str, int] = {}
        for cls in self._sim_classes:
            cat = cls.CATEGORY
            category_counts[cat] = category_counts.get(cat, 0) + 1

        self._all_item.setText(0, f"All Simulations ({len(self._sim_classes)})")
        for cat_key, item in self._category_items.items():
            count = category_counts.get(cat_key, 0)
            name = _CATEGORY_NAMES.get(cat_key, cat_key)
            item.setText(0, f"{name} ({count})")

        self._populate_cards()

    def _populate_cards(
        self,
        category: str = "",
        search: str = "",
        level: str = "",
    ) -> None:
        """Fill the card grid with simulation cards matching the filters.

        Args:
            category: Category key to filter by, or "" for all.
            search: Search text to match against name, description, tags.
            level: Level key to filter by, or "" for all.
        """
        # Clear existing cards
        while self._card_layout.count():
            child = self._card_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        search_lower = search.lower()
        col_count = 3
        row, col = 0, 0

        for cls in self._sim_classes:
            # Category filter
            if category and cls.CATEGORY != category:
                continue
            # Level filter
            if level and cls.LEVEL != level:
                continue
            # Search filter
            if search_lower:
                searchable = (
                    f"{cls.ID} {cls.NAME} {cls.DESCRIPTION} "
                    f"{' '.join(cls.TAGS)}"
                ).lower()
                if search_lower not in searchable:
                    continue

            card = SimulationCard(cls)
            card.clicked.connect(lambda c=cls: self._launch_sim(c))
            self._card_layout.addWidget(card, row, col)
            col += 1
            if col >= col_count:
                col = 0
                row += 1

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def _get_current_filters(self) -> tuple[str, str, str]:
        """Return the current (category, search, level) filter state."""
        # Category from sidebar selection
        selected = self._category_tree.currentItem()
        category = ""
        if selected and selected is not self._all_item:
            category = selected.data(0, Qt.ItemDataRole.UserRole) or ""

        search = self._search_field.text().strip()
        level = self._level_filter.currentData() or ""
        return category, search, level

    def _filter_cards(self) -> None:
        """Re-filter the card grid based on current search/filter state."""
        category, search, level = self._get_current_filters()
        self._populate_cards(category, search, level)

    def _on_category_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """Handle a click on a category in the sidebar."""
        if item is self._all_item:
            cat_name = "All Simulations"
            self._dashboard_title.setText(cat_name)
        else:
            cat_key = item.data(0, Qt.ItemDataRole.UserRole)
            cat_name = _CATEGORY_NAMES.get(cat_key, cat_key)
            self._dashboard_title.setText(cat_name)

        self._filter_cards()

    # ------------------------------------------------------------------
    # Simulation lifecycle
    # ------------------------------------------------------------------

    def _launch_sim(self, sim_class: type[SimulationBase]) -> None:
        """Instantiate and display a simulation module.

        Args:
            sim_class: The SimulationBase subclass to launch.
        """
        # Clean up previous simulation
        if self._active_sim is not None:
            self._active_sim.on_hide()
            self._active_sim.on_close()

        # Clear the sim page
        while self._sim_layout.count():
            child = self._sim_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Instantiate and build UI
        sim = sim_class()
        self._active_sim = sim
        widget = sim.build_ui()
        self._sim_layout.addWidget(widget)

        # Show simulation page
        self._stack.setCurrentIndex(1)
        sim.on_show()

        # Update toolbar — hide search, show sim controls
        self._act_search.setVisible(False)
        self._act_level.setVisible(False)
        self._set_sim_controls_visible(True)
        self._sim_label.setText(f"  {sim.ID} \u2014 {sim.NAME}")

        # Update status bar
        self._status_label.setText(
            f"{sim.ID} — {sim.NAME} | {sim.LEVEL}"
        )
        logger.info("Launched simulation: %s (%s)", sim.ID, sim.NAME)

    def _show_dashboard(self) -> None:
        """Return to the dashboard view."""
        if self._active_sim is not None:
            self._active_sim.on_hide()
            self._active_sim.on_close()
            self._active_sim = None

        # Clear the sim page
        while self._sim_layout.count():
            child = self._sim_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self._stack.setCurrentIndex(0)

        # Update toolbar — show search, hide sim controls
        self._set_sim_controls_visible(False)
        self._act_search.setVisible(True)
        self._act_level.setVisible(True)

        self._status_label.setText(f"{APP_NAME} v{APP_VERSION} — Ready")

    def _set_sim_controls_visible(self, visible: bool) -> None:
        """Show/hide the simulation control buttons via QAction references."""
        self._act_back.setVisible(visible)
        self._act_sim_label.setVisible(visible)
        self._act_sep.setVisible(visible)
        self._act_reset.setVisible(visible)
        self._act_export.setVisible(visible)
        self._act_save.setVisible(visible)
        self._act_load.setVisible(visible)
        self._act_help.setVisible(visible)

    def _reset_sim(self) -> None:
        """Reset the active simulation."""
        if self._active_sim is not None:
            self._active_sim.reset()

    def _export_sim(self) -> None:
        """Export the active simulation's data and plot."""
        if self._active_sim is None:
            return
        directory = QFileDialog.getExistingDirectory(
            self, "Export Simulation", ""
        )
        if directory:
            self._active_sim.export(directory)
            self._status_label.setText(f"Exported to {directory}")

    def _save_state(self) -> None:
        """Save the active simulation's state to a file."""
        if self._active_sim is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save State",
            f"{self._active_sim.ID}_state{PRESET_EXTENSION}",
            f"Lumina Preset (*{PRESET_EXTENSION});;JSON (*.json)",
        )
        if path:
            self._active_sim.save_state(path)
            self._status_label.setText(f"State saved to {path}")

    def _load_state(self) -> None:
        """Load simulation state from a file."""
        if self._active_sim is None:
            return
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Load State",
            "",
            f"Lumina Preset (*{PRESET_EXTENSION});;JSON (*.json);;All (*)",
        )
        if path:
            self._active_sim.load_state(path)
            self._status_label.setText(f"State loaded from {path}")

    # ------------------------------------------------------------------
    # Theme controls
    # ------------------------------------------------------------------

    def _show_help(self) -> None:
        """Show the help dialog for the active simulation."""
        if self._active_sim is None:
            return
        title = f"{self._active_sim.ID} — {self._active_sim.NAME}"
        help_text = self._active_sim.HELP_TEXT
        if not help_text:
            help_text = (
                f"# {self._active_sim.NAME}\n\n"
                f"{self._active_sim.DESCRIPTION}\n\n"
                "No detailed help is available for this module yet."
            )
        dialog = HelpDialog(title, help_text, self)
        dialog.exec()

    def _on_theme_changed(self) -> None:
        """Handle theme selector change — re-launches active sim to apply new plot colours."""
        theme = self._theme_combo.currentData()
        if theme and theme != self._current_theme:
            self._current_theme = theme
            save_theme(theme)
            app = QApplication.instance()
            if app is not None:
                apply_theme(app, theme)

            # Update dashboard cards
            self._populate_cards(*self._get_current_filters())

            # Re-launch the active simulation so plots pick up new theme
            if self._active_sim is not None:
                sim_class = type(self._active_sim)
                self._launch_sim(sim_class)

    def _on_colourblind_toggled(self) -> None:
        """Handle colourblind palette toggle."""
        self._colourblind = self._btn_colourblind.isChecked()
        save_colourblind_pref(self._colourblind)

    # ------------------------------------------------------------------
    # Window events
    # ------------------------------------------------------------------

    def closeEvent(self, event: Any) -> None:
        """Clean up active simulation on window close."""
        if self._active_sim is not None:
            self._active_sim.on_hide()
            self._active_sim.on_close()
            self._active_sim = None
        super().closeEvent(event)
