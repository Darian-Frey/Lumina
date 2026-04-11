"""A02 Orbital Mechanics — UI module."""

from __future__ import annotations

from typing import Any

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDoubleSpinBox, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QVBoxLayout, QWidget,
)

from lumina.core.config import (
    BTN_STYLE_COMPUTE, BTN_STYLE_RESET, DEFAULT_TIMER_MS,
)
from lumina.core.plot import SimPlotWidget
from lumina.modules.astrophysics.a02_orbital_mechanics.physics import (
    GM_DEFAULT, kepler_orbit, numerical_orbit, orbital_energy,
    orbital_period, vis_viva,
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


class OrbitalWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._t = np.array([])
        self._x = np.array([])
        self._y = np.array([])
        self._frame: int = 0
        self._build_ui()
        self._setup_tooltips()
        self._compute()

    def _setup_tooltips(self) -> None:
        self._spin_a.setToolTip("Semi-major axis")
        self._spin_e.setToolTip("Eccentricity (0 = circle, < 1 = ellipse)")
        self._spin_v_factor.setToolTip(
            "Velocity multiplier — 1.0 = circular, > 1.0 = elliptical/escape"
        )
        self._btn_play.setToolTip("Animate the orbit")
        self._btn_compute.setToolTip("Recompute with current parameters")
        self._btn_reset_view.setToolTip("Auto-range and reset animation")

    def _build_ui(self) -> None:
        main = QHBoxLayout(self)
        main.setContentsMargins(8, 8, 8, 8)

        ctrl_w = QWidget()
        ctrl_w.setFixedWidth(240)
        ctrl = QVBoxLayout(ctrl_w)
        ctrl.setContentsMargins(4, 4, 4, 4)

        # Orbit parameters
        orbit_grp = QGroupBox("Orbit")
        ol = QVBoxLayout(orbit_grp)
        r, self._spin_a = _spin_row("Semi-major a:", 0.1, 5.0, 1.5, 2)
        ol.addLayout(r)
        r, self._spin_e = _spin_row("Eccentricity e:", 0.0, 0.95, 0.5, 3)
        ol.addLayout(r)
        ctrl.addWidget(orbit_grp)

        # Numerical IC
        num_grp = QGroupBox("Numerical IC")
        nl = QVBoxLayout(num_grp)
        r, self._spin_v_factor = _spin_row("Speed factor:", 0.1, 1.5, 1.0, 3)
        nl.addLayout(r)
        ctrl.addWidget(num_grp)

        # Animation
        anim_grp = QGroupBox("Animation")
        al = QVBoxLayout(anim_grp)
        self._btn_play = QPushButton("Play")
        self._btn_play.setCheckable(True)
        self._btn_play.clicked.connect(self._toggle_play)
        al.addWidget(self._btn_play)
        ctrl.addWidget(anim_grp)

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
            title="Orbital Mechanics", x_label="x", y_label="y",
        )
        self._plot.plot_item.setAspectLocked(True)
        self._plot.plot_item.addLegend(offset=(10, 10))
        self._plot.plot_item.getAxis("left").enableAutoSIPrefix(False)
        self._plot.plot_item.getAxis("bottom").enableAutoSIPrefix(False)

        # Sun (centre)
        self._dot_sun = pg.ScatterPlotItem(
            [0], [0], size=20, brush=pg.mkBrush("#ffcc00"),
            pen=pg.mkPen("#000000", width=2),
        )
        self._plot.plot_item.addItem(self._dot_sun)

        # Closed-form ellipse
        self._line_ellipse = self._plot.plot_item.plot(
            [], [], pen=pg.mkPen("#aaaaaa", width=1, style=Qt.PenStyle.DashLine),
            name="Kepler ellipse",
        )
        # Numerical orbit
        self._line_orbit = self._plot.plot_item.plot(
            [], [], pen=pg.mkPen("#1f77b4", width=2),
            name="numerical orbit",
        )
        # Current planet position
        self._dot_planet = pg.ScatterPlotItem(
            [], [], size=14, brush=pg.mkBrush("#1f77b4"),
            pen=pg.mkPen("#000000", width=1),
        )
        self._plot.plot_item.addItem(self._dot_planet)

        main.addWidget(self._plot, 1)

        # Animation timer
        self._timer = QTimer()
        self._timer.setInterval(DEFAULT_TIMER_MS)
        self._timer.timeout.connect(self._advance)

    def _compute(self) -> None:
        a = self._spin_a.value()
        e = self._spin_e.value()
        v_factor = self._spin_v_factor.value()

        # Closed-form ellipse for reference
        x_ell, y_ell = kepler_orbit(a, e)
        self._line_ellipse.setData(x_ell, y_ell)

        # Numerical orbit starting from perihelion
        # At perihelion: r = a(1 - e), v = sqrt(GM (1+e)/(a(1-e)))
        r0 = a * (1 - e)
        v_circ = np.sqrt(GM_DEFAULT / r0)
        v0 = v_factor * v_circ * np.sqrt((1 + e) / (1 - e) * v_factor)
        # Simplify: just use vis-viva at r0 for given a, scaled by v_factor
        v0 = v_factor * vis_viva(r0, a, GM_DEFAULT)

        T = orbital_period(a, GM_DEFAULT)
        t_max = 1.5 * T
        dt = t_max / 1000

        self._t, self._x, self._y = numerical_orbit(
            r0=r0, v0=v0, theta0=0.0, t_max=t_max, dt=dt,
        )
        self._line_orbit.setData(self._x, self._y)
        self._frame = 0

        # Initial planet position
        if len(self._x) > 0:
            self._dot_planet.setData([self._x[0]], [self._y[0]])

        # Lock view
        max_r = float(max(np.abs(x_ell).max(), np.abs(y_ell).max())) * 1.4
        self._plot.plot_item.setLimits(
            xMin=-max_r * 1.5, xMax=max_r * 1.5,
            yMin=-max_r * 1.5, yMax=max_r * 1.5,
        )
        self._plot.plot_item.setXRange(-max_r, max_r)
        self._plot.plot_item.setYRange(-max_r, max_r)

        # Readout
        T_period = orbital_period(a)
        E = orbital_energy(r0, v0)
        v_peri = vis_viva(r0, a) if v_factor == 1.0 else v0
        r_apo = a * (1 + e)
        v_apo = vis_viva(r_apo, a) if e < 1 else 0
        self._readout.setText(
            f"a = {a:.3f}\n"
            f"e = {e:.3f}\n"
            f"T = {T_period:.3f}\n"
            f"\n"
            f"r_peri = {r0:.3f}\n"
            f"r_apo  = {r_apo:.3f}\n"
            f"v_peri = {v_peri:.3f}\n"
            f"v_apo  = {v_apo:.3f}\n"
            f"E = {E:.3f}"
        )

    def _toggle_play(self) -> None:
        if self._btn_play.isChecked():
            self._btn_play.setText("Pause")
            self._timer.start()
        else:
            self._btn_play.setText("Play")
            self._timer.stop()

    def _advance(self) -> None:
        if len(self._x) == 0:
            return
        self._frame = (self._frame + 5) % len(self._x)
        self._dot_planet.setData([self._x[self._frame]], [self._y[self._frame]])

    def _reset_view(self) -> None:
        self._frame = 0
        self._compute()

    def get_params(self) -> dict[str, Any]:
        return {
            "a": self._spin_a.value(),
            "e": self._spin_e.value(),
            "v_factor": self._spin_v_factor.value(),
        }

    def set_params(self, p: dict[str, Any]) -> None:
        if "a" in p: self._spin_a.setValue(p["a"])
        if "e" in p: self._spin_e.setValue(p["e"])
        if "v_factor" in p: self._spin_v_factor.setValue(p["v_factor"])
        self._compute()

    def get_data(self) -> dict[str, np.ndarray]:
        return {"t": self._t, "x": self._x, "y": self._y}

    def stop(self) -> None:
        self._timer.stop()
        self._btn_play.setChecked(False)
        self._btn_play.setText("Play")
