"""
AP02 Bifurcation Diagram — UI module.
--------------------------------------
Scatter plot of the logistic map bifurcation with zoom-aware recomputation.
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

from lumina.core.config import BTN_STYLE_COMPUTE, BTN_STYLE_RESET, current_mid_colour
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
    lbl.setFixedWidth(110)
    lbl.setFont(QFont("sans-serif", 9))
    row.addWidget(lbl)
    spin.setFixedWidth(80)
    row.addWidget(spin)
    return row


class BifurcationWidget(QWidget):
    """Main widget for the Bifurcation Diagram simulation."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._r_data = np.array([])
        self._x_data = np.array([])
        self._build_ui()
        self._setup_tooltips()
        self._compute()

    def _setup_tooltips(self) -> None:
        self._spin_nr.setToolTip("Number of r values to sample — more = denser plot")
        self._spin_niter.setToolTip("Total iterations per r value — more = better attractor")
        self._spin_ndiscard.setToolTip("Transient iterations to skip before recording")
        self._spin_x0.setToolTip("Initial condition for the iteration (0 < x0 < 1)")
        self._btn_compute.setToolTip("Recompute for the currently visible r range")
        self._btn_reset.setToolTip("Return to the default [2.5, 4.0] view")

    def _build_ui(self) -> None:
        main = QHBoxLayout(self)
        main.setContentsMargins(8, 8, 8, 8)

        # --- Controls ---
        controls = QWidget()
        controls.setFixedWidth(240)
        ctrl = QVBoxLayout(controls)
        ctrl.setContentsMargins(4, 4, 4, 4)

        # Resolution
        res = QGroupBox("Resolution")
        resl = QVBoxLayout(res)

        self._spin_nr = QSpinBox()
        self._spin_nr.setRange(100, 5000)
        self._spin_nr.setValue(DEFAULT_N_R)
        self._spin_nr.setSingleStep(100)
        resl.addLayout(_spin_row("r samples:", self._spin_nr))

        self._spin_niter = QSpinBox()
        self._spin_niter.setRange(100, 5000)
        self._spin_niter.setValue(DEFAULT_N_ITER)
        self._spin_niter.setSingleStep(100)
        resl.addLayout(_spin_row("Iterations:", self._spin_niter))

        self._spin_ndiscard = QSpinBox()
        self._spin_ndiscard.setRange(50, 4000)
        self._spin_ndiscard.setValue(DEFAULT_N_DISCARD)
        self._spin_ndiscard.setSingleStep(50)
        resl.addLayout(_spin_row("Transient:", self._spin_ndiscard))

        ctrl.addWidget(res)

        # IC
        ic = QGroupBox("Initial Condition")
        icl = QVBoxLayout(ic)
        self._spin_x0 = QDoubleSpinBox()
        self._spin_x0.setRange(0.001, 0.999)
        self._spin_x0.setValue(DEFAULT_X0)
        self._spin_x0.setDecimals(3)
        self._spin_x0.setSingleStep(0.05)
        icl.addLayout(_spin_row("Initial x\u2080:", self._spin_x0))
        ctrl.addWidget(ic)

        # Buttons — styled to match AP01
        self._btn_compute = QPushButton("Compute")
        self._btn_compute.setStyleSheet(BTN_STYLE_COMPUTE)
        self._btn_compute.clicked.connect(self._compute_from_view)
        ctrl.addWidget(self._btn_compute)

        self._btn_reset = QPushButton("Reset View")
        self._btn_reset.setStyleSheet(BTN_STYLE_RESET)
        self._btn_reset.clicked.connect(self._reset_view)
        ctrl.addWidget(self._btn_reset)

        # Hint
        hint = QLabel("Zoom into a region of interest,\n"
                       "then press Compute to refine.\n"
                       "Reset View to return to default.")
        hint.setFont(QFont("sans-serif", 8))
        hint.setStyleSheet("color: #888888;")
        hint.setWordWrap(True)
        ctrl.addWidget(hint)

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
        # Clamp zoom range: r in [0, 4], x* in [0, 1]
        self._plot_bif.plot_item.setLimits(
            xMin=0, xMax=4.0, yMin=-0.05, yMax=1.05,
        )
        # Disable auto-scaling notation on axes
        self._plot_bif.plot_item.getAxis("left").enableAutoSIPrefix(False)
        self._plot_bif.plot_item.getAxis("bottom").enableAutoSIPrefix(False)
        plot_split.addWidget(self._plot_bif)

        # Lyapunov exponent
        self._plot_lyap = SimPlotWidget(
            title="Lyapunov Exponent", x_label="r", y_label="\u03bb"
        )
        self._line_lyap = self._plot_lyap.add_line(name="\u03bb(r)")
        self._plot_lyap.plot_item.addLine(
            y=0, pen=pg.mkPen(current_mid_colour(), style=Qt.PenStyle.DashLine),
        )
        self._plot_lyap.plot_item.setLimits(xMin=0, xMax=4.0)
        self._plot_lyap.plot_item.getAxis("bottom").enableAutoSIPrefix(False)
        self._plot_lyap.plot_item.getAxis("left").enableAutoSIPrefix(False)
        plot_split.addWidget(self._plot_lyap)

        plot_split.setSizes([500, 200])
        main.addWidget(plot_split, 1)

    def _compute(self, r_min: float = DEFAULT_R_MIN, r_max: float = DEFAULT_R_MAX) -> None:
        """Compute bifurcation diagram for the given r range."""
        n_r = self._spin_nr.value()
        n_iter = self._spin_niter.value()
        n_discard = self._spin_ndiscard.value()
        x0 = self._spin_x0.value()

        self._r_data, self._x_data = compute_bifurcation(
            r_min=r_min, r_max=r_max, n_r=n_r,
            n_iter=n_iter, n_discard=n_discard, x0=x0,
        )
        self._scatter.setData(self._r_data, self._x_data)

        # Lyapunov exponent for same r range
        r_vals = np.linspace(r_min, r_max, min(n_r, 500))
        lyap = np.array([lyapunov_exponent(r, x0=x0) for r in r_vals])
        self._line_lyap.setData(r_vals, lyap)

        # Update Lyapunov plot range to match
        self._plot_lyap.plot_item.setXRange(r_min, r_max, padding=0.02)

        self._readout.setText(
            f"r \u2208 [{r_min:.4f}, {r_max:.4f}]\n"
            f"{len(self._r_data):,} points"
        )

    def _compute_from_view(self) -> None:
        """Recompute for the currently visible r range — zoom then compute."""
        vb = self._plot_bif.plot_item.vb
        xr = vb.viewRange()[0]
        r_min = max(0.0, xr[0])
        r_max = min(4.0, xr[1])
        if r_max <= r_min:
            r_min, r_max = DEFAULT_R_MIN, DEFAULT_R_MAX
        self._compute(r_min, r_max)

    def _reset_view(self) -> None:
        """Reset to the default [2.5, 4.0] range."""
        self._plot_bif.plot_item.setXRange(DEFAULT_R_MIN, DEFAULT_R_MAX, padding=0.02)
        self._plot_bif.plot_item.setYRange(-0.05, 1.05, padding=0.0)
        self._compute(DEFAULT_R_MIN, DEFAULT_R_MAX)

    def get_params(self) -> dict[str, Any]:
        return {
            "n_r": self._spin_nr.value(),
            "n_iter": self._spin_niter.value(),
            "n_discard": self._spin_ndiscard.value(),
            "x0": self._spin_x0.value(),
        }

    def set_params(self, p: dict[str, Any]) -> None:
        for key, spin in [("x0", self._spin_x0)]:
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
        pass
