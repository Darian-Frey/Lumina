"""
M10 Double Pendulum — UI module.
---------------------------------
Real-time pendulum animation with trajectory tracing and energy plot.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from lumina.core.config import BTN_STYLE_COMPUTE, BTN_STYLE_RESET, DEFAULT_TIMER_MS
from lumina.core.plot import SimPlotWidget
from lumina.modules.mechanics.m10_double_pendulum.physics import (
    DEFAULT_G,
    DEFAULT_L1,
    DEFAULT_L2,
    DEFAULT_M1,
    DEFAULT_M2,
    DEFAULT_OMEGA1,
    DEFAULT_OMEGA2,
    DEFAULT_THETA1,
    DEFAULT_THETA2,
    pendulum_cartesian,
    solve_double_pendulum,
    total_energy,
)


def _spin_row(
    label: str, min_v: float, max_v: float, default: float, decimals: int = 2,
) -> tuple[QHBoxLayout, QDoubleSpinBox]:
    row = QHBoxLayout()
    lbl = QLabel(label)
    lbl.setFixedWidth(55)
    lbl.setFont(QFont("sans-serif", 10))
    row.addWidget(lbl)

    spin = QDoubleSpinBox()
    spin.setRange(min_v, max_v)
    spin.setValue(default)
    spin.setDecimals(decimals)
    spin.setSingleStep(10 ** (-decimals))
    spin.setFixedWidth(80)
    row.addWidget(spin)
    return row, spin


class DoublePendulumWidget(QWidget):
    """Main widget for the Double Pendulum simulation."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # State arrays
        self._t = np.array([])
        self._th1 = np.array([])
        self._w1 = np.array([])
        self._th2 = np.array([])
        self._w2 = np.array([])
        self._x1 = np.array([])
        self._y1 = np.array([])
        self._x2 = np.array([])
        self._y2 = np.array([])
        self._energy = np.array([])
        self._frame: int = 0
        self._trail_length: int = 600

        self._build_ui()
        self._setup_tooltips()
        self._compute()

    def _setup_tooltips(self) -> None:
        self._spin_m1.setToolTip("Mass of the first (upper) bob in kg")
        self._spin_m2.setToolTip("Mass of the second (lower) bob in kg")
        self._spin_L1.setToolTip("Length of the first (upper) rod in metres")
        self._spin_L2.setToolTip("Length of the second (lower) rod in metres")
        self._spin_g.setToolTip("Gravitational acceleration (9.81 m/s² on Earth)")
        self._spin_th1.setToolTip("Initial angle of first pendulum (0 = hanging down)")
        self._spin_th2.setToolTip("Initial angle of second pendulum (0 = hanging down)")
        self._spin_w1.setToolTip("Initial angular velocity of first pendulum")
        self._spin_w2.setToolTip("Initial angular velocity of second pendulum")
        self._spin_speed.setToolTip("Animation frames per tick")
        self._spin_trail.setToolTip("Number of points in the trajectory trail")
        self._btn_play.setToolTip("Start or pause the animation")
        self._btn_restart.setToolTip("Reset to initial conditions and recompute")
        self._btn_compute.setToolTip("Recompute trajectory with current parameters")
        self._btn_reset_view.setToolTip("Auto-range all plots to fit the data")

    def _build_ui(self) -> None:
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)

        # --- Left: controls ---
        controls = QWidget()
        controls.setFixedWidth(240)
        ctrl = QVBoxLayout(controls)
        ctrl.setContentsMargins(4, 4, 4, 4)

        # Masses and lengths
        phys = QGroupBox("Physical Parameters")
        pl = QVBoxLayout(phys)
        row, self._spin_m1 = _spin_row("m1 (kg)", 0.1, 10.0, DEFAULT_M1)
        pl.addLayout(row)
        row, self._spin_m2 = _spin_row("m2 (kg)", 0.1, 10.0, DEFAULT_M2)
        pl.addLayout(row)
        row, self._spin_L1 = _spin_row("L1 (m)", 0.1, 5.0, DEFAULT_L1)
        pl.addLayout(row)
        row, self._spin_L2 = _spin_row("L2 (m)", 0.1, 5.0, DEFAULT_L2)
        pl.addLayout(row)
        row, self._spin_g = _spin_row("g (m/s²)", 0.1, 20.0, DEFAULT_G)
        pl.addLayout(row)
        ctrl.addWidget(phys)

        # Initial angles
        ic = QGroupBox("Initial Conditions")
        il = QVBoxLayout(ic)
        row, self._spin_th1 = _spin_row("θ1 (rad)", -np.pi, np.pi, DEFAULT_THETA1)
        il.addLayout(row)
        row, self._spin_th2 = _spin_row("θ2 (rad)", -np.pi, np.pi, DEFAULT_THETA2)
        il.addLayout(row)
        row, self._spin_w1 = _spin_row("ω1", -10.0, 10.0, DEFAULT_OMEGA1)
        il.addLayout(row)
        row, self._spin_w2 = _spin_row("ω2", -10.0, 10.0, DEFAULT_OMEGA2)
        il.addLayout(row)
        ctrl.addWidget(ic)

        # Animation
        anim = QGroupBox("Animation")
        al = QVBoxLayout(anim)
        row, self._spin_speed = _spin_row("speed", 1, 50, 5, 0)
        al.addLayout(row)
        row, self._spin_trail = _spin_row("trail", 50, 3000, 600, 0)
        al.addLayout(row)

        btn_row = QHBoxLayout()
        self._btn_play = QPushButton("Play")
        self._btn_play.setCheckable(True)
        self._btn_play.clicked.connect(self._toggle_play)
        btn_row.addWidget(self._btn_play)
        self._btn_restart = QPushButton("Restart")
        self._btn_restart.clicked.connect(self._restart)
        btn_row.addWidget(self._btn_restart)
        al.addLayout(btn_row)
        ctrl.addWidget(anim)

        self._btn_compute = QPushButton("Recompute")
        self._btn_compute.setStyleSheet(BTN_STYLE_COMPUTE)
        self._btn_compute.clicked.connect(self._compute)
        ctrl.addWidget(self._btn_compute)

        self._btn_reset_view = QPushButton("Reset View")
        self._btn_reset_view.setStyleSheet(BTN_STYLE_RESET)
        self._btn_reset_view.clicked.connect(self._reset_view)
        ctrl.addWidget(self._btn_reset_view)

        ctrl.addStretch()
        main_layout.addWidget(controls)

        # --- Right: plots ---
        plot_split = QSplitter(Qt.Orientation.Vertical)

        # Top: pendulum animation
        self._plot_pend = SimPlotWidget(title="Double Pendulum")
        self._plot_pend.plot_item.setAspectLocked(True)
        self._plot_pend.plot_item.setXRange(-3, 3)
        self._plot_pend.plot_item.setYRange(-3, 1)
        self._line_rods = self._plot_pend.plot_item.plot(
            [], [], pen=pg.mkPen("#333333", width=3)
        )
        self._dot_bobs = pg.ScatterPlotItem(
            size=14, brush=pg.mkBrush("#d62728")
        )
        self._plot_pend.plot_item.addItem(self._dot_bobs)
        self._line_trail = self._plot_pend.add_line(name="trail")
        plot_split.addWidget(self._plot_pend)

        # Bottom row: trajectory + energy
        bottom = QSplitter(Qt.Orientation.Horizontal)

        self._plot_traj = SimPlotWidget(
            title="Tip Trajectory", x_label="x2", y_label="y2"
        )
        self._line_traj = self._plot_traj.add_line(name="trajectory")
        bottom.addWidget(self._plot_traj)

        self._plot_energy = SimPlotWidget(
            title="Total Energy", x_label="t", y_label="E (J)"
        )
        self._line_energy = self._plot_energy.add_line(name="energy")
        bottom.addWidget(self._plot_energy)

        plot_split.addWidget(bottom)
        plot_split.setSizes([400, 200])

        main_layout.addWidget(plot_split, 1)

        # Timer
        self._timer = QTimer()
        self._timer.setInterval(DEFAULT_TIMER_MS)
        self._timer.timeout.connect(self._advance_frame)

    def _compute(self) -> None:
        """Recompute the trajectory."""
        self._t, self._th1, self._w1, self._th2, self._w2 = solve_double_pendulum(
            m1=self._spin_m1.value(),
            m2=self._spin_m2.value(),
            L1=self._spin_L1.value(),
            L2=self._spin_L2.value(),
            g=self._spin_g.value(),
            theta1=self._spin_th1.value(),
            omega1=self._spin_w1.value(),
            theta2=self._spin_th2.value(),
            omega2=self._spin_w2.value(),
        )
        self._x1, self._y1, self._x2, self._y2 = pendulum_cartesian(
            self._th1, self._th2,
            L1=self._spin_L1.value(),
            L2=self._spin_L2.value(),
        )
        self._energy = total_energy(
            self._th1, self._w1, self._th2, self._w2,
            m1=self._spin_m1.value(),
            m2=self._spin_m2.value(),
            L1=self._spin_L1.value(),
            L2=self._spin_L2.value(),
            g=self._spin_g.value(),
        )
        self._frame = 0

        # Full trajectory plots
        self._line_traj.setData(self._x2, self._y2)
        self._line_energy.setData(self._t, self._energy)

        # Zoom limits based on rod lengths
        L = self._spin_L1.value() + self._spin_L2.value()
        self._plot_pend.plot_item.setLimits(
            xMin=-L - 1, xMax=L + 1, yMin=-L - 1, yMax=1.5,
        )
        self._plot_traj.plot_item.setLimits(
            xMin=-L - 1, xMax=L + 1, yMin=-L - 1, yMax=1.5,
        )
        t_max = float(self._t[-1]) if len(self._t) > 0 else 30
        self._plot_energy.plot_item.setLimits(xMin=-1, xMax=t_max + 1)

    def _toggle_play(self) -> None:
        if self._btn_play.isChecked():
            self._btn_play.setText("Pause")
            self._trail_length = int(self._spin_trail.value())
            self._timer.start()
        else:
            self._btn_play.setText("Play")
            self._timer.stop()

    def _restart(self) -> None:
        self._frame = 0
        self._compute()

    def _advance_frame(self) -> None:
        if len(self._t) == 0:
            return

        speed = int(self._spin_speed.value())
        self._frame += speed
        if self._frame >= len(self._t):
            self._frame = 0

        i = self._frame

        # Rod lines: pivot -> bob1 -> bob2
        rod_x = [0.0, self._x1[i], self._x2[i]]
        rod_y = [0.0, self._y1[i], self._y2[i]]
        self._line_rods.setData(rod_x, rod_y)

        # Bob positions
        self._dot_bobs.setData(
            [self._x1[i], self._x2[i]],
            [self._y1[i], self._y2[i]],
        )

        # Trail of second bob
        start = max(0, i - self._trail_length)
        self._line_trail.setData(self._x2[start:i], self._y2[start:i])

    # --- Public API ---

    def get_params(self) -> dict[str, Any]:
        return {
            "m1": self._spin_m1.value(),
            "m2": self._spin_m2.value(),
            "L1": self._spin_L1.value(),
            "L2": self._spin_L2.value(),
            "g": self._spin_g.value(),
            "theta1": self._spin_th1.value(),
            "theta2": self._spin_th2.value(),
            "omega1": self._spin_w1.value(),
            "omega2": self._spin_w2.value(),
            "speed": self._spin_speed.value(),
            "trail": self._spin_trail.value(),
        }

    def set_params(self, p: dict[str, Any]) -> None:
        for key, spin in [
            ("m1", self._spin_m1), ("m2", self._spin_m2),
            ("L1", self._spin_L1), ("L2", self._spin_L2),
            ("g", self._spin_g),
            ("theta1", self._spin_th1), ("theta2", self._spin_th2),
            ("omega1", self._spin_w1), ("omega2", self._spin_w2),
            ("speed", self._spin_speed), ("trail", self._spin_trail),
        ]:
            if key in p:
                spin.setValue(p[key])
        self._compute()

    def get_data(self) -> dict[str, np.ndarray]:
        return {
            "t": self._t, "theta1": self._th1, "omega1": self._w1,
            "theta2": self._th2, "omega2": self._w2,
            "x2": self._x2, "y2": self._y2, "energy": self._energy,
        }

    def _reset_view(self) -> None:
        """Reset all plot views to auto-range."""
        for plot in (self._plot_pend, self._plot_traj, self._plot_energy):
            plot.plot_item.autoRange()
        # Re-lock pendulum view
        L = self._spin_L1.value() + self._spin_L2.value()
        self._plot_pend.plot_item.setXRange(-L - 0.5, L + 0.5)
        self._plot_pend.plot_item.setYRange(-L - 0.5, 1)

    def stop(self) -> None:
        self._timer.stop()
        self._btn_play.setChecked(False)
        self._btn_play.setText("Play")
