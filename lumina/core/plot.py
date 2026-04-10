"""
lumina/core/plot.py
-------------------
Shared plot widget wrappers built on pyqtgraph.

Provides theme-aware, colourblind-safe plotting widgets that all
simulation modules should use instead of raw pyqtgraph calls.
"""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from lumina.core.config import (
    PALETTE_COLOURBLIND,
    PALETTE_STANDARD,
    THEME_LIGHT,
    THEME_PLOT_BACKGROUNDS,
    THEME_PLOT_FOREGROUNDS,
)


class SimPlotWidget(QWidget):
    """Theme-aware pyqtgraph plot widget for Lumina simulations.

    Wraps pg.PlotWidget with automatic theme colouring, palette management,
    and export helpers. All simulations should use this instead of creating
    raw PlotWidgets.

    Args:
        title: Plot title displayed above the axes.
        x_label: X-axis label.
        y_label: Y-axis label.
        theme: One of "light", "dark", "high_contrast".
        colourblind: If True, use the Okabe-Ito colourblind-safe palette.
        show_grid: If True, show grid lines.
        parent: Parent widget.
    """

    def __init__(
        self,
        title: str = "",
        x_label: str = "",
        y_label: str = "",
        theme: str = "",
        colourblind: bool = False,
        show_grid: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        # Auto-detect theme if not specified
        if not theme:
            try:
                from lumina.launcher.theme import current_theme
                theme = current_theme()
            except ImportError:
                theme = THEME_LIGHT

        self._theme = theme
        self._colourblind = colourblind
        self._palette = PALETTE_COLOURBLIND if colourblind else PALETTE_STANDARD
        self._pen_index = 0

        # Create the pyqtgraph widget
        bg = THEME_PLOT_BACKGROUNDS.get(theme, THEME_PLOT_BACKGROUNDS[THEME_LIGHT])
        self._plot_widget = pg.PlotWidget(background=bg)
        self._plot_item = self._plot_widget.getPlotItem()

        # Foreground colour for axes, labels, title
        fg = THEME_PLOT_FOREGROUNDS.get(theme, THEME_PLOT_FOREGROUNDS[THEME_LIGHT])
        axis_pen = pg.mkPen(fg)
        label_style = {"color": fg, "font-size": "11pt"}

        if title:
            self._plot_item.setTitle(title, color=fg, size="12pt")

        self._plot_item.setLabel("bottom", x_label, **label_style)
        self._plot_item.setLabel("left", y_label, **label_style)

        # Style axes
        for axis_name in ("bottom", "left", "top", "right"):
            axis = self._plot_item.getAxis(axis_name)
            axis.setPen(axis_pen)
            axis.setTextPen(axis_pen)

        if show_grid:
            self._plot_item.showGrid(x=True, y=True, alpha=0.3)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._plot_widget)

    @property
    def plot_item(self) -> pg.PlotItem:
        """Access the underlying PlotItem for advanced configuration."""
        return self._plot_item

    @property
    def plot_widget(self) -> pg.PlotWidget:
        """Access the underlying PlotWidget."""
        return self._plot_widget

    def next_pen(self, width: int = 2) -> pg.functions.mkPen:
        """Return the next pen from the active palette, cycling automatically.

        Args:
            width: Pen width in pixels.

        Returns:
            A pyqtgraph pen object.
        """
        colour = self._palette[self._pen_index % len(self._palette)]
        self._pen_index += 1
        return pg.mkPen(colour, width=width)

    def reset_pen_cycle(self) -> None:
        """Reset the pen colour cycle back to the first colour."""
        self._pen_index = 0

    def add_line(
        self,
        x: np.ndarray | None = None,
        y: np.ndarray | None = None,
        name: str = "",
        pen: object | None = None,
        width: int = 2,
    ) -> pg.PlotDataItem:
        """Add a line to the plot and return the PlotDataItem for later updates.

        Args:
            x: X data. If None, uses integer indices.
            y: Y data.
            name: Legend name for this line.
            pen: Custom pen. If None, uses next_pen().
            width: Pen width (only used if pen is None).

        Returns:
            The PlotDataItem — call .setData() on it to update.
        """
        if pen is None:
            pen = self.next_pen(width)
        if x is not None and y is not None:
            item = self._plot_item.plot(x, y, pen=pen, name=name or None)
        elif y is not None:
            item = self._plot_item.plot(y, pen=pen, name=name or None)
        else:
            item = self._plot_item.plot([], [], pen=pen, name=name or None)
        return item

    def add_scatter(
        self,
        x: np.ndarray | None = None,
        y: np.ndarray | None = None,
        name: str = "",
        size: int = 5,
        brush: object | None = None,
    ) -> pg.ScatterPlotItem:
        """Add a scatter plot and return the item for later updates.

        Args:
            x: X data.
            y: Y data.
            name: Legend name.
            size: Point size.
            brush: Custom brush. If None, uses next colour from palette.

        Returns:
            The ScatterPlotItem.
        """
        if brush is None:
            colour = self._palette[self._pen_index % len(self._palette)]
            self._pen_index += 1
            brush = pg.mkBrush(colour)

        scatter = pg.ScatterPlotItem(size=size, brush=brush, name=name or None)
        if x is not None and y is not None:
            scatter.setData(x, y)
        self._plot_item.addItem(scatter)
        return scatter

    def clear(self) -> None:
        """Remove all plot items and reset the pen cycle."""
        self._plot_item.clear()
        self._pen_index = 0

    def set_theme(self, theme: str, colourblind: bool | None = None) -> None:
        """Update the plot theme dynamically.

        Args:
            theme: One of "light", "dark", "high_contrast".
            colourblind: If provided, toggle colourblind palette.
        """
        self._theme = theme
        bg = THEME_PLOT_BACKGROUNDS.get(theme, THEME_PLOT_BACKGROUNDS[THEME_LIGHT])
        fg = THEME_PLOT_FOREGROUNDS.get(theme, THEME_PLOT_FOREGROUNDS[THEME_LIGHT])

        self._plot_widget.setBackground(bg)

        axis_pen = pg.mkPen(fg)
        for axis_name in ("bottom", "left", "top", "right"):
            axis = self._plot_item.getAxis(axis_name)
            axis.setPen(axis_pen)
            axis.setTextPen(axis_pen)

        if colourblind is not None:
            self._colourblind = colourblind
            self._palette = PALETTE_COLOURBLIND if colourblind else PALETTE_STANDARD

    def export_png(self, path: str | Path, width: int = 1200) -> None:
        """Export the current plot as a PNG image.

        Args:
            path: Output file path.
            width: Image width in pixels.
        """
        from pyqtgraph.exporters import ImageExporter

        exporter = ImageExporter(self._plot_item)
        exporter.parameters()["width"] = width
        exporter.export(str(path))

    def export_csv(self, path: str | Path, data: dict[str, np.ndarray]) -> None:
        """Export data columns as a CSV file.

        Args:
            path: Output file path.
            data: Mapping of column names to arrays. All arrays must
                have the same length.
        """
        path = Path(path)
        header = ",".join(data.keys())
        columns = np.column_stack(list(data.values()))
        np.savetxt(path, columns, delimiter=",", header=header, comments="")
