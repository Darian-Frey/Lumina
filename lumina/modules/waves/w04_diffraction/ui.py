"""W04 Diffraction & Interference — UI module."""

from __future__ import annotations

from typing import Any

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QVBoxLayout, QWidget,
)

from lumina.core.config import BTN_STYLE_COMPUTE, BTN_STYLE_RESET
from lumina.core.plot import SimPlotWidget
from lumina.modules.waves.w04_diffraction.physics import (
    double_slit_intensity, first_minimum_angle, fringe_spacing,
    n_slit_intensity, single_slit_intensity,
)


def _spin_row(
    label: str, lo: float, hi: float, val: float, dec: int = 3,
) -> tuple[QHBoxLayout, QDoubleSpinBox]:
    r = QHBoxLayout()
    l = QLabel(label)
    l.setFixedWidth(110)
    l.setFont(QFont("sans-serif", 9))
    r.addWidget(l)
    s = QDoubleSpinBox()
    s.setRange(lo, hi)
    s.setValue(val)
    s.setDecimals(dec)
    s.setSingleStep(10 ** (-dec))
    s.setFixedWidth(80)
    r.addWidget(s)
    return r, s


class DiffractionWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._theta = np.array([])
        self._I = np.array([])
        self._build_ui()
        self._setup_tooltips()
        self._on_mode_changed()

    def _setup_tooltips(self) -> None:
        self._combo.setToolTip("Choose diffraction setup")
        self._spin_a.setToolTip("Slit width (in same units as wavelength)")
        self._spin_d.setToolTip("Slit separation (centre to centre)")
        self._spin_lambda.setToolTip("Light wavelength")
        self._spin_N.setToolTip("Number of slits in the grating")
        self._btn_compute.setToolTip("Recompute the pattern")
        self._btn_reset_view.setToolTip("Auto-range the plot")

    def _build_ui(self) -> None:
        main = QHBoxLayout(self)
        main.setContentsMargins(8, 8, 8, 8)

        ctrl_w = QWidget()
        ctrl_w.setFixedWidth(240)
        ctrl = QVBoxLayout(ctrl_w)
        ctrl.setContentsMargins(4, 4, 4, 4)

        # Mode
        mode_grp = QGroupBox("Setup")
        ml = QVBoxLayout(mode_grp)
        self._combo = QComboBox()
        self._combo.addItems([
            "Single slit", "Double slit (Young)", "N-slit grating",
        ])
        self._combo.currentTextChanged.connect(self._on_mode_changed)
        ml.addWidget(self._combo)
        ctrl.addWidget(mode_grp)

        # Parameters
        param_grp = QGroupBox("Parameters")
        pl = QVBoxLayout(param_grp)
        r, self._spin_a = _spin_row("Slit width a:", 0.001, 0.5, 0.05)
        pl.addLayout(r)
        r, self._spin_d = _spin_row("Slit sep d:", 0.01, 2.0, 0.2)
        pl.addLayout(r)
        r, self._spin_lambda = _spin_row("Wavelength \u03bb:", 0.001, 0.1, 0.01)
        pl.addLayout(r)

        r = QHBoxLayout()
        l = QLabel("Slit count N:")
        l.setFixedWidth(110)
        r.addWidget(l)
        self._spin_N = QSpinBox()
        self._spin_N.setRange(2, 100)
        self._spin_N.setValue(5)
        self._spin_N.setFixedWidth(80)
        r.addWidget(self._spin_N)
        pl.addLayout(r)
        ctrl.addWidget(param_grp)

        # Buttons
        self._btn_compute = QPushButton("Compute")
        self._btn_compute.setStyleSheet(BTN_STYLE_COMPUTE)
        self._btn_compute.clicked.connect(self._compute)
        ctrl.addWidget(self._btn_compute)

        self._btn_reset_view = QPushButton("Reset View")
        self._btn_reset_view.setStyleSheet(BTN_STYLE_RESET)
        self._btn_reset_view.clicked.connect(self._reset_view)
        ctrl.addWidget(self._btn_reset_view)

        # Readout
        self._readout = QLabel()
        self._readout.setFont(QFont("monospace", 9))
        self._readout.setWordWrap(True)
        ctrl.addWidget(self._readout)

        ctrl.addStretch()
        main.addWidget(ctrl_w)

        # Plot
        self._plot = SimPlotWidget(
            title="Diffraction Pattern",
            x_label="\u03b8 (degrees)", y_label="Intensity",
        )
        self._line = self._plot.add_line(width=2)
        main.addWidget(self._plot, 1)

    def _on_mode_changed(self) -> None:
        mode = self._combo.currentText()
        # Show/hide N spinner depending on mode
        self._spin_N.setEnabled("grating" in mode)
        self._spin_d.setEnabled("Single slit" not in mode)
        self._compute()

    def _compute(self) -> None:
        mode = self._combo.currentText()
        a = self._spin_a.value()
        d = self._spin_d.value()
        wavelength = self._spin_lambda.value()
        N = self._spin_N.value()

        # Choose theta range based on the slit width — first minimum at lambda/a
        max_theta = max(0.5, 5 * wavelength / a)
        if max_theta > np.pi / 2:
            max_theta = np.pi / 2
        theta = np.linspace(-max_theta, max_theta, 2000)

        if mode == "Single slit":
            I = single_slit_intensity(theta, a, wavelength)
        elif mode == "Double slit (Young)":
            I = double_slit_intensity(theta, a, d, wavelength)
        else:  # N-slit grating
            I = n_slit_intensity(theta, a, d, N, wavelength)

        self._theta = theta
        self._I = I
        self._line.setData(np.degrees(theta), I)

        # Lock view
        deg_max = float(np.degrees(max_theta))
        self._plot.plot_item.setLimits(
            xMin=-deg_max * 1.1, xMax=deg_max * 1.1,
            yMin=-0.05 * float(I.max()) if I.max() > 0 else -0.1,
            yMax=float(I.max()) * 1.2 if I.max() > 0 else 1.0,
        )
        self._plot.plot_item.setXRange(-deg_max, deg_max)
        self._plot.plot_item.setYRange(0, float(I.max()) * 1.1 if I.max() > 0 else 1.0)

        # Readout
        first_min_deg = np.degrees(first_minimum_angle(a, wavelength))
        info = f"\u03bb = {wavelength:.4f}\na = {a:.4f}\n\n"
        info += f"First min at \u00b1{first_min_deg:.2f}\u00b0\n"
        if mode != "Single slit":
            info += f"d = {d:.4f}\n"
            # Fringe spacing on a screen 1 m away
            spacing = fringe_spacing(d, wavelength, 1.0)
            info += f"Fringe spacing\n(D = 1): {spacing:.4f}"
        if "grating" in mode:
            info += f"\nN = {N} slits"
        self._readout.setText(info)

    def _reset_view(self) -> None:
        self._compute()

    def get_params(self) -> dict[str, Any]:
        return {
            "mode": self._combo.currentText(),
            "a": self._spin_a.value(),
            "d": self._spin_d.value(),
            "wavelength": self._spin_lambda.value(),
            "N": self._spin_N.value(),
        }

    def set_params(self, p: dict[str, Any]) -> None:
        if "mode" in p:
            idx = self._combo.findText(p["mode"])
            if idx >= 0:
                self._combo.setCurrentIndex(idx)
        if "a" in p: self._spin_a.setValue(p["a"])
        if "d" in p: self._spin_d.setValue(p["d"])
        if "wavelength" in p: self._spin_lambda.setValue(p["wavelength"])
        if "N" in p: self._spin_N.setValue(p["N"])
        self._compute()

    def get_data(self) -> dict[str, np.ndarray]:
        return {"theta": self._theta, "I": self._I}

    def stop(self) -> None:
        pass
