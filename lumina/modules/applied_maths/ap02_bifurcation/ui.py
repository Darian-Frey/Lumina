"""
AP02 Bifurcation Diagram — UI module.
--------------------------------------
Scatter plot of the logistic map bifurcation with zoom support.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from lumina.core.config import THEME_LIGHT
from lumina.core.plot import SimPlotWidget
from lumina.modules.applied_maths.ap02_bifurcation.physics import (
    DEFAULT_N_DISCARD,
    DEFAULT_N_ITER,
    DEFAULT_N_R,
    DEFAULT_R_MAX,
    DEFAULT_R_MIN,
    DEFAULT_X0,
    compute_bifurcation,
    lyapunov_exponent,
)


def _spin_row(label: str, spin: QDoubleSpinBox | QSpinBox) -> QHBoxLayout:
    row = QHBoxLayout()
    lbl = QLabel(label)
    lbl.setFixedWidth(80)
    lbl.setFont(QFont("sans-serif", 10))
    row.addWidget(lbl)
    spin.setFixedWidth(90)
    row.addWidget(spin)
    return row


class BifurcationWidget(QWidget):
    """Main widget for the Bifurcation Diagram simulation."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._r_data = np.array([])
        self._x_data = np.array([])
        self._build_ui()
        self._compute()

    def _build_ui(self) -> None:
        main = QHBoxLayout(self)
        main.setContentsMargins(8, 8, 8, 8)

        # --- Controls ---
        controls = QWidget()
        controls.setFixedWidth(240)
        ctrl = QVBoxLayout(controls)
        ctrl.setContentsMargins(4, 4, 4, 4)

        # Range
        rng = QGroupBox("Parameter Range")
        rl = QVBoxLayout(rng)

        self._spin_rmin = QDoubleSpinBox()
        self._spin_rmin.setRange(0.0, 4.0)
        self._spin_rmin.setValue(DEFAULT_R_MIN)
        self._spin_rmin.setDecimals(3)
        self._spin_rmin.setSingleStep(0.1)
        rl.addLayout(_spin_row("r min", self._spin_rmin))

        self._spin_rmax = QDoubleSpinBox()
        self._spin_rmax.setRange(0.0, 4.0)
        self._spin_rmax.setValue(DEFAULT_R_MAX)
        self._spin_rmax.setDecimals(3)
        self._spin_rmax.setSingleStep(0.1)
        rl.addLayout(_spin_row("r max", self._spin_rmax))

        ctrl.addWidget(rng)

        # Resolution
        res = QGroupBox("Resolution")
        resl = QVBoxLayout(res)

        self._spin_nr = QSpinBox()
        self._spin_nr.setRange(100, 5000)
        self._spin_nr.setValue(DEFAULT_N_R)
        self._spin_nr.setSingleStep(100)
        resl.addLayout(_spin_row("r samples", self._spin_nr))

        self._spin_niter = QSpinBox()
        self._spin_niter.setRange(100, 5000)
        self._spin_niter.setValue(DEFAULT_N_ITER)
        self._spin_niter.setSingleStep(100)
        resl.addLayout(_spin_row("iterations", self._spin_niter))

        self._spin_ndiscard = QSpinBox()
        self._spin_ndiscard.setRange(50, 4000)
        self._spin_ndiscard.setValue(DEFAULT_N_DISCARD)
        self._spin_ndiscard.setSingleStep(50)
        resl.addLayout(_spin_row("transient", self._spin_ndiscard))

        ctrl.addWidget(res)

        # IC
        ic = QGroupBox("Initial Condition")
        icl = QVBoxLayout(ic)
        self._spin_x0 = QDoubleSpinBox()
        self._spin_x0.setRange(0.001, 0.999)
        self._spin_x0.setValue(DEFAULT_X0)
        self._spin_x0.setDecimals(3)
        self._spin_x0.setSingleStep(0.05)
        icl.addLayout(_spin_row("x0", self._spin_x0))
        ctrl.addWidget(ic)

        # Buttons
        self._btn_compute = QPushButton("Compute")
        self._btn_compute.clicked.connect(self._compute)
        ctrl.addWidget(self._btn_compute)

        self._btn_reset_zoom = QPushButton("Reset Zoom")
        self._btn_reset_zoom.clicked.connect(self._reset_zoom)
        ctrl.addWidget(self._btn_reset_zoom)

        # Equation
        eq = QGroupBox("Map")
        eql = QVBoxLayout(eq)
        eql.addWidget(QLabel("x\u2099\u208A\u2081 = r \u00b7 x\u2099 \u00b7 (1 \u2212 x\u2099)"))
        self._readout = QLabel()
        self._readout.setFont(QFont("monospace", 9))
        eql.addWidget(self._readout)
        ctrl.addWidget(eq)

        ctrl.addStretch()
        main.addWidget(controls)

        # --- Plots ---
        plot_split = QSplitter(Qt.Orientation.Vertical)

        # Bifurcation scatter
        self._plot_bif = SimPlotWidget(
            title="Bifurcation Diagram", x_label="r", y_label="x*"
        )
        self._scatter = self._plot_bif.add_scatter(size=1)
        plot_split.addWidget(self._plot_bif)

        # Lyapunov exponent
        self._plot_lyap = SimPlotWidget(
            title="Lyapunov Exponent", x_label="r", y_label="\u03bb"
        )
        self._line_lyap = self._plot_lyap.add_line(name="\u03bb(r)")
        # Zero line
        self._plot_lyap.plot_item.addLine(y=0, pen=pg.mkPen("#999999", style=Qt.PenStyle.DashLine))
        plot_split.addWidget(self._plot_lyap)

        plot_split.setSizes([500, 200])
        main.addWidget(plot_split, 1)

    def _compute(self) -> None:
        r_min = self._spin_rmin.value()
        r_max = self._spin_rmax.value()
        n_r = self._spin_nr.value()
        n_iter = self._spin_niter.value()
        n_discard = self._spin_ndiscard.value()
        x0 = self._spin_x0.value()

        self._r_data, self._x_data = compute_bifurcation(
            r_min=r_min, r_max=r_max, n_r=n_r,
            n_iter=n_iter, n_discard=n_discard, x0=x0,
        )
        self._scatter.setData(self._r_data, self._x_data)

        # Lyapunov exponent curve
        r_vals = np.linspace(r_min, r_max, min(n_r, 500))
        lyap = np.array([lyapunov_exponent(r, x0=x0) for r in r_vals])
        self._line_lyap.setData(r_vals, lyap)

        self._readout.setText(
            f"r \u2208 [{r_min:.3f}, {r_max:.3f}]  |  "
            f"{len(self._r_data):,} points"
        )

    def _reset_zoom(self) -> None:
        self._plot_bif.plot_item.autoRange()
        self._plot_lyap.plot_item.autoRange()

    def get_params(self) -> dict[str, Any]:
        return {
            "r_min": self._spin_rmin.value(),
            "r_max": self._spin_rmax.value(),
            "n_r": self._spin_nr.value(),
            "n_iter": self._spin_niter.value(),
            "n_discard": self._spin_ndiscard.value(),
            "x0": self._spin_x0.value(),
        }

    def set_params(self, p: dict[str, Any]) -> None:
        for key, spin in [
            ("r_min", self._spin_rmin), ("r_max", self._spin_rmax),
            ("x0", self._spin_x0),
        ]:
            if key in p:
                spin.setValue(p[key])
        for key, spin in [
            ("n_r", self._spin_nr), ("n_iter", self._spin_niter),
            ("n_discard", self._spin_ndiscard),
        ]:
            if key in p:
                spin.setValue(p[key])
        self._compute()

    def get_data(self) -> dict[str, np.ndarray]:
        return {"r": self._r_data, "x": self._x_data}

    def stop(self) -> None:
        pass  # No animation to stop
