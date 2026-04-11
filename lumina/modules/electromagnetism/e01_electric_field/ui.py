"""E01 Electric Field Lines — UI module."""

from __future__ import annotations

from typing import Any

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox, QComboBox, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QSplitter, QVBoxLayout, QWidget,
)

from lumina.core.config import BTN_STYLE_COMPUTE, BTN_STYLE_RESET
from lumina.core.plot import SimPlotWidget
from lumina.modules.electromagnetism.e01_electric_field.physics import (
    Charge, coulomb_field, field_magnitude, generate_field_lines,
)

DEFAULT_BOUNDS: tuple[float, float, float, float] = (-3.0, 3.0, -3.0, 3.0)

# Preset charge configurations
PRESETS: dict[str, list[Charge]] = {
    "Single positive": [(0.0, 0.0, 1.0)],
    "Single negative": [(0.0, 0.0, -1.0)],
    "Dipole": [(-1.0, 0.0, 1.0), (1.0, 0.0, -1.0)],
    "Two positive": [(-1.0, 0.0, 1.0), (1.0, 0.0, 1.0)],
    "Quadrupole": [
        (-1.0, 0.0, 1.0), (1.0, 0.0, 1.0),
        (0.0, -1.0, -1.0), (0.0, 1.0, -1.0),
    ],
    "Three charges": [
        (-1.5, 0.0, 1.0), (1.5, 0.0, 1.0), (0.0, 1.5, -2.0),
    ],
}


class ElectricFieldWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._charges: list[Charge] = list(PRESETS["Dipole"])
        self._build_ui()
        self._setup_tooltips()
        self._compute()

    def _setup_tooltips(self) -> None:
        self._combo.setToolTip("Choose a preset charge configuration")
        self._chk_field.setToolTip("Show vector field arrows")
        self._chk_lines.setToolTip("Show field lines")
        self._chk_potential.setToolTip("Colour the background by electric potential")
        self._btn_compute.setToolTip("Recompute the field")
        self._btn_reset_view.setToolTip("Reset view to default range")

    def _build_ui(self) -> None:
        main = QHBoxLayout(self)
        main.setContentsMargins(8, 8, 8, 8)

        ctrl_w = QWidget()
        ctrl_w.setFixedWidth(240)
        ctrl = QVBoxLayout(ctrl_w)
        ctrl.setContentsMargins(4, 4, 4, 4)

        # Preset selector
        preset_grp = QGroupBox("Configuration")
        pl = QVBoxLayout(preset_grp)
        self._combo = QComboBox()
        for name in PRESETS:
            self._combo.addItem(name)
        self._combo.setCurrentText("Dipole")
        self._combo.currentTextChanged.connect(self._on_preset_changed)
        pl.addWidget(self._combo)
        ctrl.addWidget(preset_grp)

        # Display options
        disp_grp = QGroupBox("Display")
        dl = QVBoxLayout(disp_grp)
        self._chk_lines = QCheckBox("Show field lines")
        self._chk_lines.setChecked(True)
        self._chk_lines.stateChanged.connect(self._compute)
        dl.addWidget(self._chk_lines)

        self._chk_field = QCheckBox("Show vector arrows")
        self._chk_field.setChecked(True)
        self._chk_field.stateChanged.connect(self._compute)
        dl.addWidget(self._chk_field)

        self._chk_potential = QCheckBox("Show potential")
        self._chk_potential.setChecked(False)
        self._chk_potential.stateChanged.connect(self._compute)
        dl.addWidget(self._chk_potential)
        ctrl.addWidget(disp_grp)

        # Buttons
        self._btn_compute = QPushButton("Compute")
        self._btn_compute.setStyleSheet(BTN_STYLE_COMPUTE)
        self._btn_compute.clicked.connect(self._compute)
        ctrl.addWidget(self._btn_compute)

        self._btn_reset_view = QPushButton("Reset View")
        self._btn_reset_view.setStyleSheet(BTN_STYLE_RESET)
        self._btn_reset_view.clicked.connect(self._reset_view)
        ctrl.addWidget(self._btn_reset_view)

        # Hint
        hint = QLabel(
            "Choose a charge configuration\n"
            "from the dropdown.\n"
            "Toggle layers with the checkboxes.\n"
            "Press Compute to refresh."
        )
        hint.setFont(QFont("sans-serif", 8))
        hint.setStyleSheet("color: #888888;")
        hint.setWordWrap(True)
        ctrl.addWidget(hint)

        # Readout
        self._readout = QLabel()
        self._readout.setFont(QFont("monospace", 9))
        self._readout.setWordWrap(True)
        ctrl.addWidget(self._readout)

        ctrl.addStretch()
        main.addWidget(ctrl_w)

        # Plot
        self._plot = SimPlotWidget(title="Electric Field", x_label="x", y_label="y")
        self._plot.plot_item.setAspectLocked(True)
        self._plot.plot_item.setXRange(*DEFAULT_BOUNDS[:2])
        self._plot.plot_item.setYRange(*DEFAULT_BOUNDS[2:])
        self._plot.plot_item.setLimits(
            xMin=DEFAULT_BOUNDS[0] - 1, xMax=DEFAULT_BOUNDS[1] + 1,
            yMin=DEFAULT_BOUNDS[2] - 1, yMax=DEFAULT_BOUNDS[3] + 1,
        )

        self._field_items: list[Any] = []
        self._line_items: list[Any] = []
        self._charge_items: list[Any] = []
        self._potential_image: pg.ImageItem | None = None

        main.addWidget(self._plot, 1)

    def _on_preset_changed(self) -> None:
        name = self._combo.currentText()
        self._charges = list(PRESETS.get(name, PRESETS["Dipole"]))
        self._compute()

    def _clear_layer(self, items: list) -> None:
        for item in items:
            self._plot.plot_item.removeItem(item)
        items.clear()

    def _compute(self) -> None:
        self._clear_layer(self._field_items)
        self._clear_layer(self._line_items)
        self._clear_layer(self._charge_items)
        if self._potential_image is not None:
            self._plot.plot_item.removeItem(self._potential_image)
            self._potential_image = None

        # Optional: potential as background image
        if self._chk_potential.isChecked():
            self._draw_potential()

        # Field lines
        if self._chk_lines.isChecked():
            self._draw_field_lines()

        # Vector field arrows
        if self._chk_field.isChecked():
            self._draw_quiver()

        # Charges (always on top)
        self._draw_charges()

        # Readout
        n_pos = sum(1 for _, _, q in self._charges if q > 0)
        n_neg = sum(1 for _, _, q in self._charges if q < 0)
        net_q = sum(q for _, _, q in self._charges)
        self._readout.setText(
            f"Charges: {len(self._charges)}\n"
            f"  + : {n_pos}\n"
            f"  - : {n_neg}\n"
            f"Net Q = {net_q:+.2f}"
        )

    def _draw_potential(self) -> None:
        from lumina.modules.electromagnetism.e01_electric_field.physics import potential

        n = 200
        x = np.linspace(DEFAULT_BOUNDS[0], DEFAULT_BOUNDS[1], n)
        y = np.linspace(DEFAULT_BOUNDS[2], DEFAULT_BOUNDS[3], n)
        X, Y = np.meshgrid(x, y)
        V = potential(X, Y, self._charges)

        # Clip extreme values for better contrast
        V_clip = np.clip(V, -5, 5)

        self._potential_image = pg.ImageItem()
        self._potential_image.setImage(V_clip.T, levels=(-5, 5))
        self._potential_image.setRect(
            DEFAULT_BOUNDS[0], DEFAULT_BOUNDS[2],
            DEFAULT_BOUNDS[1] - DEFAULT_BOUNDS[0],
            DEFAULT_BOUNDS[3] - DEFAULT_BOUNDS[2],
        )
        # Coolwarm-like colourmap
        cmap = pg.colormap.get("CET-D1A")
        if cmap is not None:
            self._potential_image.setLookupTable(cmap.getLookupTable())
        self._plot.plot_item.addItem(self._potential_image)
        self._potential_image.setZValue(-10)

    def _draw_quiver(self) -> None:
        n = 18
        x = np.linspace(DEFAULT_BOUNDS[0], DEFAULT_BOUNDS[1], n)
        y = np.linspace(DEFAULT_BOUNDS[2], DEFAULT_BOUNDS[3], n)
        X, Y = np.meshgrid(x, y)
        Ex, Ey = coulomb_field(X, Y, self._charges)

        mag = field_magnitude(Ex, Ey)
        mag_safe = np.maximum(mag, 1e-10)
        # Normalise to unit length, scale by grid spacing
        sx = (DEFAULT_BOUNDS[1] - DEFAULT_BOUNDS[0]) / n * 0.32
        sy = (DEFAULT_BOUNDS[3] - DEFAULT_BOUNDS[2]) / n * 0.32
        DX = Ex / mag_safe * sx
        DY = Ey / mag_safe * sy

        all_x: list[float] = []
        all_y: list[float] = []
        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                x0, y0 = X[i, j], Y[i, j]
                dx, dy = DX[i, j], DY[i, j]
                all_x.extend([x0, x0 + dx])
                all_y.extend([y0, y0 + dy])
                # Arrowhead
                angle = np.arctan2(dy, dx)
                head_len = np.sqrt(dx ** 2 + dy ** 2) * 0.3
                for da in [2.7, -2.7]:
                    hx = x0 + dx - head_len * np.cos(angle + da)
                    hy = y0 + dy - head_len * np.sin(angle + da)
                    all_x.extend([x0 + dx, hx])
                    all_y.extend([y0 + dy, hy])

        arrows = pg.PlotCurveItem(
            x=np.array(all_x), y=np.array(all_y),
            connect="pairs",
            pen=pg.mkPen("#888888", width=1.2),
        )
        self._plot.plot_item.addItem(arrows)
        self._field_items.append(arrows)

    def _draw_field_lines(self) -> None:
        lines = generate_field_lines(
            self._charges, n_lines_per_charge=14, bounds=DEFAULT_BOUNDS,
        )
        for xs, ys in lines:
            line = self._plot.plot_item.plot(
                xs, ys, pen=pg.mkPen("#1f77b4", width=1.5),
            )
            self._line_items.append(line)

    def _draw_charges(self) -> None:
        for cx, cy, q in self._charges:
            colour = "#d62728" if q > 0 else "#1f77b4"
            symbol = "+" if q > 0 else "o"
            scatter = pg.ScatterPlotItem(
                [cx], [cy], size=22, symbol=symbol,
                brush=pg.mkBrush(colour), pen=pg.mkPen("#000000", width=2),
            )
            self._plot.plot_item.addItem(scatter)
            self._charge_items.append(scatter)

            # Charge value label
            label = pg.TextItem(
                text=f" {q:+.1f}", color=colour, anchor=(0, 0),
            )
            label.setFont(QFont("sans-serif", 9, QFont.Weight.Bold))
            label.setPos(cx, cy)
            self._plot.plot_item.addItem(label)
            self._charge_items.append(label)

    def _reset_view(self) -> None:
        self._plot.plot_item.setXRange(*DEFAULT_BOUNDS[:2])
        self._plot.plot_item.setYRange(*DEFAULT_BOUNDS[2:])

    def get_params(self) -> dict[str, Any]:
        return {
            "preset": self._combo.currentText(),
            "show_lines": self._chk_lines.isChecked(),
            "show_field": self._chk_field.isChecked(),
            "show_potential": self._chk_potential.isChecked(),
        }

    def set_params(self, p: dict[str, Any]) -> None:
        if "preset" in p:
            idx = self._combo.findText(p["preset"])
            if idx >= 0:
                self._combo.setCurrentIndex(idx)
        if "show_lines" in p:
            self._chk_lines.setChecked(p["show_lines"])
        if "show_field" in p:
            self._chk_field.setChecked(p["show_field"])
        if "show_potential" in p:
            self._chk_potential.setChecked(p["show_potential"])
        self._compute()

    def get_data(self) -> dict[str, np.ndarray]:
        return {}

    def stop(self) -> None:
        pass
