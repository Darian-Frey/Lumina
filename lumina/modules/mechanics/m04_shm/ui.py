"""M04 Simple Harmonic Motion — UI module."""

from __future__ import annotations

from typing import Any

import numpy as np
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QSplitter, QVBoxLayout, QWidget,
)

from lumina.core.config import BTN_STYLE_COMPUTE, BTN_STYLE_RESET, DEFAULT_TIMER_MS
from lumina.core.plot import SimPlotWidget
from lumina.modules.mechanics.m04_shm.physics import (
    classify_damping, damped_shm, kinetic_energy, phase_space_ellipse,
    potential_energy, shm_solution, spring_omega,
)


def _row(label: str, lo: float, hi: float, val: float, dec: int = 2) -> tuple[QHBoxLayout, QDoubleSpinBox]:
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


class SHMWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._t_anim: float = 0.0
        self._build_ui()
        self._setup_tooltips()
        self._compute()

    def _setup_tooltips(self) -> None:
        self._spin_k.setToolTip("Spring constant — stiffer spring = higher frequency")
        self._spin_m.setToolTip("Mass — heavier = lower frequency")
        self._spin_A.setToolTip("Amplitude — maximum displacement from equilibrium")
        self._spin_phi.setToolTip("Initial phase angle in radians")
        self._spin_gamma.setToolTip("Damping coefficient — 0 for undamped, increase for damping")
        self._btn_compute.setToolTip("Recompute with current parameters")
        self._btn_reset_view.setToolTip("Auto-range all plots to fit the data")

    def _build_ui(self) -> None:
        main = QHBoxLayout(self)
        main.setContentsMargins(8, 8, 8, 8)
        ctrl_w = QWidget()
        ctrl_w.setFixedWidth(240)
        ctrl = QVBoxLayout(ctrl_w)
        ctrl.setContentsMargins(4, 4, 4, 4)

        pg = QGroupBox("Parameters")
        pl = QVBoxLayout(pg)
        r, self._spin_k = _row("Spring k (N/m):", 0.1, 50.0, 5.0)
        pl.addLayout(r)
        r, self._spin_m = _row("Mass m (kg):", 0.1, 20.0, 1.0)
        pl.addLayout(r)
        r, self._spin_A = _row("Amplitude A (m):", 0.01, 5.0, 1.0)
        pl.addLayout(r)
        r, self._spin_phi = _row("Phase \u03c6 (rad):", -3.14, 3.14, 0.0)
        pl.addLayout(r)
        r, self._spin_gamma = _row("Damping \u03b3 (1/s):", 0.0, 10.0, 0.0)
        pl.addLayout(r)
        ctrl.addWidget(pg)

        btn_row = QHBoxLayout()
        self._btn_play = QPushButton("Play")
        self._btn_play.setCheckable(True)
        self._btn_play.clicked.connect(self._toggle)
        btn_row.addWidget(self._btn_play)
        self._btn_compute = QPushButton("Compute")
        self._btn_compute.setStyleSheet(BTN_STYLE_COMPUTE)
        self._btn_compute.clicked.connect(self._compute)
        btn_row.addWidget(self._btn_compute)
        ctrl.addLayout(btn_row)

        self._btn_reset_view = QPushButton("Reset View")
        self._btn_reset_view.setStyleSheet(BTN_STYLE_RESET)
        self._btn_reset_view.clicked.connect(self._reset_view)
        ctrl.addWidget(self._btn_reset_view)

        self._readout = QLabel()
        self._readout.setFont(QFont("monospace", 9))
        self._readout.setWordWrap(True)
        ctrl.addWidget(self._readout)
        ctrl.addStretch()
        main.addWidget(ctrl_w)

        sp = QSplitter(Qt.Orientation.Vertical)

        self._plot_xt = SimPlotWidget(title="Displacement x(t)", x_label="t (s)", y_label="x (m)")
        self._plot_xt.plot_item.addLegend(offset=(10, 10))
        self._plot_xt.plot_item.getAxis("left").enableAutoSIPrefix(False)
        self._plot_xt.plot_item.getAxis("bottom").enableAutoSIPrefix(False)
        self._line_xt = self._plot_xt.add_line(name="x(t)")
        self._line_env = self._plot_xt.plot_item.plot(
            [], [], pen={"color": "#999", "style": Qt.PenStyle.DashLine},
            name="envelope",
        )
        sp.addWidget(self._plot_xt)

        bottom = QSplitter(Qt.Orientation.Horizontal)
        self._plot_phase = SimPlotWidget(title="Phase Space", x_label="x (m)", y_label="v (m/s)")
        self._plot_phase.plot_item.getAxis("left").enableAutoSIPrefix(False)
        self._plot_phase.plot_item.getAxis("bottom").enableAutoSIPrefix(False)
        self._line_phase = self._plot_phase.add_line(name="(x,v)")
        self._dot_phase = self._plot_phase.add_scatter(size=10)
        bottom.addWidget(self._plot_phase)

        self._plot_energy = SimPlotWidget(title="Energy", x_label="t (s)", y_label="E (J)")
        self._plot_energy.plot_item.addLegend(offset=(10, 10))
        self._plot_energy.plot_item.getAxis("left").enableAutoSIPrefix(False)
        self._plot_energy.plot_item.getAxis("bottom").enableAutoSIPrefix(False)
        self._line_ke = self._plot_energy.add_line(name="Kinetic")
        self._line_pe = self._plot_energy.add_line(name="Potential")
        self._line_total = self._plot_energy.add_line(name="Total")
        bottom.addWidget(self._plot_energy)

        sp.addWidget(bottom)
        main.addWidget(sp, 1)

        self._timer = QTimer()
        self._timer.setInterval(DEFAULT_TIMER_MS)
        self._timer.timeout.connect(self._advance)

    def _compute(self) -> None:
        k = self._spin_k.value()
        m = self._spin_m.value()
        A = self._spin_A.value()
        phi = self._spin_phi.value()
        gamma = self._spin_gamma.value()
        omega0 = spring_omega(k, m)

        self._t = np.linspace(0, 20, 2000)
        if gamma < 1e-6:
            self._x, self._v = shm_solution(self._t, A, omega0, phi)
            self._env = np.full_like(self._t, A)
        else:
            self._x = damped_shm(self._t, A, omega0, gamma, phi)
            self._v = np.gradient(self._x, self._t)
            self._env = A * np.exp(-gamma * self._t)

        self._ke = kinetic_energy(m, self._v)
        self._pe = potential_energy(k, self._x)

        self._line_xt.setData(self._t, self._x)
        self._line_env.setData(self._t, self._env)
        px, pv = phase_space_ellipse(A, omega0)
        self._line_phase.setData(px, pv)
        self._line_ke.setData(self._t, self._ke)
        self._line_pe.setData(self._t, self._pe)
        self._line_total.setData(self._t, self._ke + self._pe)

        cls = classify_damping(omega0, gamma)
        self._readout.setText(
            f"\u03c9\u2080 = {omega0:.3f} rad/s\n"
            f"T = {2*np.pi/omega0:.3f} s\n"
            f"Damping: {cls}"
        )
        self._t_anim = 0.0

        # Clamp zoom to sensible ranges based on current data
        v_max = A * omega0
        e_max = float(np.max(self._ke + self._pe)) * 1.2
        pad = 0.1
        self._plot_xt.plot_item.setLimits(
            xMin=-1, xMax=22, yMin=-(A + pad), yMax=A + pad,
        )
        self._plot_phase.plot_item.setLimits(
            xMin=-(A + pad), xMax=A + pad,
            yMin=-(v_max + pad), yMax=v_max + pad,
        )
        self._plot_energy.plot_item.setLimits(
            xMin=-1, xMax=22, yMin=-e_max * 0.1, yMax=e_max,
        )

    def _advance(self) -> None:
        self._t_anim += DEFAULT_TIMER_MS / 1000.0
        idx = np.searchsorted(self._t, self._t_anim)
        if idx >= len(self._t):
            self._t_anim = 0.0
            idx = 0
        self._dot_phase.setData([self._x[idx]], [self._v[idx]])

    def _reset_view(self) -> None:
        """Reset all plot views to auto-range."""
        for plot in (self._plot_xt, self._plot_phase, self._plot_energy):
            plot.plot_item.autoRange()

    def _toggle(self) -> None:
        if self._btn_play.isChecked():
            self._btn_play.setText("Pause")
            self._timer.start()
        else:
            self._btn_play.setText("Play")
            self._timer.stop()

    def get_params(self) -> dict[str, Any]:
        return {
            "k": self._spin_k.value(), "m": self._spin_m.value(),
            "A": self._spin_A.value(), "phi": self._spin_phi.value(),
            "gamma": self._spin_gamma.value(),
        }

    def set_params(self, p: dict[str, Any]) -> None:
        for k, s in [("k", self._spin_k), ("m", self._spin_m),
                      ("A", self._spin_A), ("phi", self._spin_phi),
                      ("gamma", self._spin_gamma)]:
            if k in p:
                s.setValue(p[k])
        self._compute()

    def get_data(self) -> dict[str, np.ndarray]:
        return {"t": self._t, "x": self._x, "v": self._v, "KE": self._ke, "PE": self._pe}

    def stop(self) -> None:
        self._timer.stop()
        self._btn_play.setChecked(False)
        self._btn_play.setText("Play")
