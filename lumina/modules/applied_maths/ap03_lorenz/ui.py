"""
AP03 Lorenz Attractor — UI module.
-----------------------------------
Qt widget construction for the Lorenz attractor simulation.

Layout:
  Left panel: parameter controls (sigma, rho, beta, ICs, speed)
  Centre: 2D phase plots (XY, XZ) and time series
  Bottom-right: sensitivity divergence plot
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from lumina.core.config import BTN_STYLE_COMPUTE, BTN_STYLE_RESET, DEFAULT_TIMER_MS
from lumina.core.plot import SimPlotWidget
from lumina.modules.applied_maths.ap03_lorenz.physics import (
    DEFAULT_BETA,
    DEFAULT_IC,
    DEFAULT_RHO,
    DEFAULT_SIGMA,
    DEFAULT_T_MAX,
    solve_lorenz,
)


def _make_param_slider(
    label: str,
    min_val: float,
    max_val: float,
    default: float,
    decimals: int = 1,
    parent: QWidget | None = None,
) -> tuple[QHBoxLayout, QDoubleSpinBox]:
    """Create a labelled slider + spinbox row for a parameter.

    Args:
        label: Parameter name.
        min_val: Minimum value.
        max_val: Maximum value.
        default: Default value.
        decimals: Decimal places.
        parent: Parent widget.

    Returns:
        Tuple of (layout, spinbox).
    """
    row = QHBoxLayout()
    lbl = QLabel(label)
    lbl.setFixedWidth(110)
    lbl.setFont(QFont("sans-serif", 9))
    row.addWidget(lbl)

    spin = QDoubleSpinBox(parent)
    spin.setRange(min_val, max_val)
    spin.setValue(default)
    spin.setDecimals(decimals)
    spin.setSingleStep(10 ** (-decimals))
    spin.setFixedWidth(80)
    row.addWidget(spin)

    return row, spin


class LorenzWidget(QWidget):
    """Main widget for the Lorenz Attractor simulation.

    Provides:
      - Parameter controls for sigma, rho, beta
      - XZ and XY phase space plots
      - X(t) time series
      - Sensitivity divergence plot
      - Play/pause animation with trail drawing
    """

    params_changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._t = np.array([])
        self._x = np.array([])
        self._y = np.array([])
        self._z = np.array([])
        self._frame: int = 0
        self._playing: bool = False
        self._trail_length: int = 500

        self._build_ui()
        self._setup_tooltips()
        self._compute()

    def _setup_tooltips(self) -> None:
        self._spin_sigma.setToolTip("Prandtl number — controls rotation rate (default 10)")
        self._spin_rho.setToolTip("Rayleigh number — controls driving force (default 28)")
        self._spin_beta.setToolTip("Geometry factor — related to aspect ratio (default 8/3)")
        self._spin_x0.setToolTip("Initial x position")
        self._spin_y0.setToolTip("Initial y position")
        self._spin_z0.setToolTip("Initial z position")
        self._spin_speed.setToolTip("Animation frames per tick — higher = faster playback")
        self._spin_trail.setToolTip("Number of points in the animated trail")
        self._btn_play.setToolTip("Start or pause the trajectory animation")
        self._btn_restart.setToolTip("Reset animation to t=0")
        self._btn_compute.setToolTip("Recompute the trajectory with current parameters")
        self._btn_reset_view.setToolTip("Auto-range all four plots to fit the data")

    def _build_ui(self) -> None:
        """Construct the full UI layout."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)

        # --- Left panel: controls ---
        controls = QWidget()
        controls.setFixedWidth(240)
        ctrl_layout = QVBoxLayout(controls)
        ctrl_layout.setContentsMargins(4, 4, 4, 4)

        # Parameters group
        param_group = QGroupBox("Parameters")
        param_layout = QVBoxLayout(param_group)

        row, self._spin_sigma = _make_param_slider("Prandtl \u03c3:", 0.1, 50.0, DEFAULT_SIGMA)
        param_layout.addLayout(row)

        row, self._spin_rho = _make_param_slider("Rayleigh \u03c1:", 0.1, 100.0, DEFAULT_RHO)
        param_layout.addLayout(row)

        row, self._spin_beta = _make_param_slider("Geometry \u03b2:", 0.1, 20.0, DEFAULT_BETA, 2)
        param_layout.addLayout(row)

        ctrl_layout.addWidget(param_group)

        # Initial conditions group
        ic_group = QGroupBox("Initial Conditions")
        ic_layout = QVBoxLayout(ic_group)

        row, self._spin_x0 = _make_param_slider("Initial x\u2080:", -30.0, 30.0, DEFAULT_IC[0])
        ic_layout.addLayout(row)

        row, self._spin_y0 = _make_param_slider("Initial y\u2080:", -30.0, 30.0, DEFAULT_IC[1])
        ic_layout.addLayout(row)

        row, self._spin_z0 = _make_param_slider("Initial z\u2080:", -10.0, 60.0, DEFAULT_IC[2])
        ic_layout.addLayout(row)

        ctrl_layout.addWidget(ic_group)

        # Animation controls
        anim_group = QGroupBox("Animation")
        anim_layout = QVBoxLayout(anim_group)

        row, self._spin_speed = _make_param_slider("Speed:", 1, 50, 10, 0)
        anim_layout.addLayout(row)

        row, self._spin_trail = _make_param_slider("Trail length:", 50, 2000, 500, 0)
        anim_layout.addLayout(row)

        btn_row = QHBoxLayout()
        self._btn_play = QPushButton("Play")
        self._btn_play.setCheckable(True)
        self._btn_play.clicked.connect(self._toggle_play)
        btn_row.addWidget(self._btn_play)

        self._btn_restart = QPushButton("Restart")
        self._btn_restart.clicked.connect(self._restart)
        btn_row.addWidget(self._btn_restart)

        anim_layout.addLayout(btn_row)
        ctrl_layout.addWidget(anim_group)

        # Recompute button
        self._btn_compute = QPushButton("Recompute")
        self._btn_compute.setStyleSheet(BTN_STYLE_COMPUTE)
        self._btn_compute.clicked.connect(self._compute)
        ctrl_layout.addWidget(self._btn_compute)

        self._btn_reset_view = QPushButton("Reset View")
        self._btn_reset_view.setStyleSheet(BTN_STYLE_RESET)
        self._btn_reset_view.clicked.connect(self._reset_view)
        ctrl_layout.addWidget(self._btn_reset_view)

        # Equation display
        eq_group = QGroupBox("Equations")
        eq_layout = QVBoxLayout(eq_group)
        eq_text = QLabel(
            "dx/dt = \u03c3(y \u2212 x)\n"
            "dy/dt = x(\u03c1 \u2212 z) \u2212 y\n"
            "dz/dt = xy \u2212 \u03b2z"
        )
        eq_text.setFont(QFont("monospace", 10))
        eq_layout.addWidget(eq_text)

        # Live parameter readout
        self._param_readout = QLabel()
        self._param_readout.setFont(QFont("monospace", 9))
        eq_layout.addWidget(self._param_readout)
        self._update_readout()

        ctrl_layout.addWidget(eq_group)

        ctrl_layout.addStretch()
        main_layout.addWidget(controls)

        # --- Right panel: plots ---
        plot_splitter = QSplitter(Qt.Orientation.Vertical)

        # Top row: XZ and XY phase plots
        top_row = QSplitter(Qt.Orientation.Horizontal)

        self._plot_xz = SimPlotWidget(title="X-Z Phase Space", x_label="x", y_label="z")
        self._line_xz = self._plot_xz.add_line(name="trajectory")
        self._dot_xz = self._plot_xz.add_scatter(size=8)
        top_row.addWidget(self._plot_xz)

        self._plot_xy = SimPlotWidget(title="X-Y Phase Space", x_label="x", y_label="y")
        self._line_xy = self._plot_xy.add_line(name="trajectory")
        self._dot_xy = self._plot_xy.add_scatter(size=8)
        top_row.addWidget(self._plot_xy)

        plot_splitter.addWidget(top_row)

        # Bottom row: time series and divergence
        bottom_row = QSplitter(Qt.Orientation.Horizontal)

        self._plot_ts = SimPlotWidget(title="Time Series", x_label="t", y_label="x(t)")
        self._line_ts = self._plot_ts.add_line(name="x(t)")
        bottom_row.addWidget(self._plot_ts)

        self._plot_div = SimPlotWidget(
            title="Sensitivity to ICs", x_label="t", y_label="log10(|separation|)"
        )
        self._line_div = self._plot_div.add_line(name="divergence")
        bottom_row.addWidget(self._plot_div)

        plot_splitter.addWidget(bottom_row)

        main_layout.addWidget(plot_splitter, 1)

        # --- Animation timer ---
        self._timer = QTimer()
        self._timer.setInterval(DEFAULT_TIMER_MS)
        self._timer.timeout.connect(self._advance_frame)

        # Connect spinboxes to readout update
        for spin in (self._spin_sigma, self._spin_rho, self._spin_beta):
            spin.valueChanged.connect(self._update_readout)

    def _update_readout(self) -> None:
        """Update the live parameter readout label."""
        self._param_readout.setText(
            f"\u03c3 = {self._spin_sigma.value():.1f}   "
            f"\u03c1 = {self._spin_rho.value():.1f}   "
            f"\u03b2 = {self._spin_beta.value():.2f}"
        )

    def _compute(self) -> None:
        """Recompute the Lorenz trajectory with current parameters."""
        sigma = self._spin_sigma.value()
        rho = self._spin_rho.value()
        beta = self._spin_beta.value()
        ic = (self._spin_x0.value(), self._spin_y0.value(), self._spin_z0.value())

        self._t, self._x, self._y, self._z = solve_lorenz(
            sigma=sigma, rho=rho, beta=beta, ic=ic
        )
        self._frame = 0

        # Draw full trajectory on static plots
        self._line_xz.setData(self._x, self._z)
        self._line_xy.setData(self._x, self._y)
        self._line_ts.setData(self._t, self._x)

        # Compute divergence
        ic2 = (ic[0] + 1e-6, ic[1], ic[2])
        _, x2, y2, z2 = solve_lorenz(sigma=sigma, rho=rho, beta=beta, ic=ic2)
        dist = np.sqrt(
            (self._x - x2) ** 2 + (self._y - y2) ** 2 + (self._z - z2) ** 2
        )
        # Avoid log(0)
        dist = np.maximum(dist, 1e-20)
        self._line_div.setData(self._t, np.log10(dist))

        # Clear animation dots
        self._dot_xz.setData([], [])
        self._dot_xy.setData([], [])

    def _toggle_play(self) -> None:
        """Toggle animation playback."""
        if self._btn_play.isChecked():
            self._playing = True
            self._btn_play.setText("Pause")
            self._trail_length = int(self._spin_trail.value())
            self._timer.start()
        else:
            self._playing = False
            self._btn_play.setText("Play")
            self._timer.stop()

    def _restart(self) -> None:
        """Restart animation from the beginning."""
        self._frame = 0
        self._compute()

    def _reset_view(self) -> None:
        """Reset all plot views to auto-range."""
        for plot in (self._plot_xz, self._plot_xy, self._plot_ts, self._plot_div):
            plot.plot_item.autoRange()

    def _advance_frame(self) -> None:
        """Advance the animation by one step."""
        if len(self._t) == 0:
            return

        speed = int(self._spin_speed.value())
        self._frame += speed

        if self._frame >= len(self._t):
            self._frame = 0

        # Trail slice
        start = max(0, self._frame - self._trail_length)
        end = self._frame

        self._line_xz.setData(self._x[start:end], self._z[start:end])
        self._line_xy.setData(self._x[start:end], self._y[start:end])

        # Current position dot
        self._dot_xz.setData([self._x[self._frame]], [self._z[self._frame]])
        self._dot_xy.setData([self._x[self._frame]], [self._y[self._frame]])

    # ------------------------------------------------------------------
    # Public API for SimulationBase integration
    # ------------------------------------------------------------------

    def get_params(self) -> dict[str, Any]:
        """Return current parameter values for state save."""
        return {
            "sigma": self._spin_sigma.value(),
            "rho": self._spin_rho.value(),
            "beta": self._spin_beta.value(),
            "x0": self._spin_x0.value(),
            "y0": self._spin_y0.value(),
            "z0": self._spin_z0.value(),
            "speed": self._spin_speed.value(),
            "trail": self._spin_trail.value(),
        }

    def set_params(self, params: dict[str, Any]) -> None:
        """Restore parameter values from a state dict."""
        if "sigma" in params:
            self._spin_sigma.setValue(params["sigma"])
        if "rho" in params:
            self._spin_rho.setValue(params["rho"])
        if "beta" in params:
            self._spin_beta.setValue(params["beta"])
        if "x0" in params:
            self._spin_x0.setValue(params["x0"])
        if "y0" in params:
            self._spin_y0.setValue(params["y0"])
        if "z0" in params:
            self._spin_z0.setValue(params["z0"])
        if "speed" in params:
            self._spin_speed.setValue(params["speed"])
        if "trail" in params:
            self._spin_trail.setValue(params["trail"])
        self._compute()

    def get_data(self) -> dict[str, np.ndarray]:
        """Return current trajectory data for CSV export."""
        return {"t": self._t, "x": self._x, "y": self._y, "z": self._z}

    def stop(self) -> None:
        """Stop the animation timer."""
        self._timer.stop()
        self._playing = False
        self._btn_play.setChecked(False)
        self._btn_play.setText("Play")
