"""Q01 Particle in a Box — UI module."""

from __future__ import annotations

from typing import Any

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox, QDoubleSpinBox, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QSplitter, QVBoxLayout, QWidget,
)

from lumina.core.config import (
    BTN_STYLE_COMPUTE, BTN_STYLE_RESET, DEFAULT_TIMER_MS,
)
from lumina.core.plot import SimPlotWidget
from lumina.modules.quantum.q01_particle_in_box.physics import (
    energy_level, normalise_coefficients, probability_density,
    time_evolved_state, wavefunction,
)
# Note: wavefunction/probability_density are kept for get_data() export

DEFAULT_L: float = 1.0
DEFAULT_N_MAX: int = 5
DEFAULT_N_POINTS: int = 500


class ParticleInBoxWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._t: float = 0.0
        self._x = np.linspace(0, DEFAULT_L, DEFAULT_N_POINTS)
        self._build_ui()
        self._setup_tooltips()
        self._compute()

    def _setup_tooltips(self) -> None:
        self._spin_L.setToolTip("Width of the infinite square well")
        self._spin_n.setToolTip("Quantum number n (1 = ground state)")
        self._spin_n_max.setToolTip("How many energy levels to display")
        self._chk_super.setToolTip("Show a superposition of states 1+2+3 with time evolution")
        self._spin_speed.setToolTip("Time evolution speed multiplier")
        self._btn_play.setToolTip("Animate time evolution of the superposition")
        self._btn_compute.setToolTip("Recompute with current parameters")
        self._btn_reset_view.setToolTip("Reset time and recompute")

    def _build_ui(self) -> None:
        main = QHBoxLayout(self)
        main.setContentsMargins(8, 8, 8, 8)

        ctrl_w = QWidget()
        ctrl_w.setFixedWidth(240)
        ctrl = QVBoxLayout(ctrl_w)
        ctrl.setContentsMargins(4, 4, 4, 4)

        # Box parameters
        box_grp = QGroupBox("Box")
        bl = QVBoxLayout(box_grp)
        r = QHBoxLayout()
        lbl = QLabel("Width L:")
        lbl.setFixedWidth(90)
        r.addWidget(lbl)
        self._spin_L = QDoubleSpinBox()
        self._spin_L.setRange(0.1, 10.0)
        self._spin_L.setValue(DEFAULT_L)
        self._spin_L.setDecimals(2)
        self._spin_L.setSingleStep(0.1)
        r.addWidget(self._spin_L)
        bl.addLayout(r)
        ctrl.addWidget(box_grp)

        # State selection
        state_grp = QGroupBox("Eigenstate")
        sl = QVBoxLayout(state_grp)
        r = QHBoxLayout()
        lbl = QLabel("Quantum n:")
        lbl.setFixedWidth(90)
        r.addWidget(lbl)
        self._spin_n = QSpinBox()
        self._spin_n.setRange(1, 20)
        self._spin_n.setValue(1)
        self._spin_n.valueChanged.connect(self._compute)
        r.addWidget(self._spin_n)
        sl.addLayout(r)

        r = QHBoxLayout()
        lbl = QLabel("Levels:")
        lbl.setFixedWidth(90)
        r.addWidget(lbl)
        self._spin_n_max = QSpinBox()
        self._spin_n_max.setRange(1, 15)
        self._spin_n_max.setValue(DEFAULT_N_MAX)
        self._spin_n_max.valueChanged.connect(self._compute)
        r.addWidget(self._spin_n_max)
        sl.addLayout(r)
        ctrl.addWidget(state_grp)

        # Superposition mode
        super_grp = QGroupBox("Time Evolution")
        spl = QVBoxLayout(super_grp)
        self._chk_super = QCheckBox("Superposition (|1>+|2>+|3>)")
        self._chk_super.stateChanged.connect(self._compute)
        spl.addWidget(self._chk_super)

        r = QHBoxLayout()
        lbl = QLabel("Speed:")
        lbl.setFixedWidth(90)
        r.addWidget(lbl)
        self._spin_speed = QDoubleSpinBox()
        self._spin_speed.setRange(0.01, 10.0)
        self._spin_speed.setValue(1.0)
        self._spin_speed.setDecimals(2)
        self._spin_speed.setSingleStep(0.1)
        r.addWidget(self._spin_speed)
        spl.addLayout(r)
        ctrl.addWidget(super_grp)

        # Buttons
        self._btn_play = QPushButton("Play")
        self._btn_play.setCheckable(True)
        self._btn_play.clicked.connect(self._toggle_play)
        ctrl.addWidget(self._btn_play)

        self._btn_compute = QPushButton("Compute")
        self._btn_compute.setStyleSheet(BTN_STYLE_COMPUTE)
        self._btn_compute.clicked.connect(self._compute)
        ctrl.addWidget(self._btn_compute)

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

        # Plots
        plot_split = QSplitter(Qt.Orientation.Vertical)

        # Top: energy levels
        self._plot_energy = SimPlotWidget(
            title="Energy Levels", x_label="quantum number n", y_label="energy E\u2099",
        )
        self._scatter_energy = self._plot_energy.add_scatter(size=12)
        self._plot_energy.plot_item.getAxis("left").enableAutoSIPrefix(False)
        self._plot_energy.plot_item.getAxis("bottom").enableAutoSIPrefix(False)
        plot_split.addWidget(self._plot_energy)

        # Middle: wavefunction
        self._plot_wf = SimPlotWidget(
            title="Wavefunction \u03c8(x, t)",
            x_label="position x", y_label="\u03c8",
        )
        self._plot_wf.plot_item.addLegend(offset=(10, 10))
        self._line_wf_real = self._plot_wf.plot_item.plot(
            [], [], pen=pg.mkPen("#1f77b4", width=2), name="Re[\u03c8]",
        )
        self._line_wf_imag = self._plot_wf.plot_item.plot(
            [], [], pen=pg.mkPen("#ff7f0e", width=2), name="Im[\u03c8]",
        )
        self._plot_wf.plot_item.getAxis("left").enableAutoSIPrefix(False)
        self._plot_wf.plot_item.getAxis("bottom").enableAutoSIPrefix(False)
        self._plot_wf.plot_item.addLine(
            x=0, pen=pg.mkPen("#666666", style=Qt.PenStyle.DashLine),
        )
        self._wall_right = self._plot_wf.plot_item.addLine(
            x=DEFAULT_L, pen=pg.mkPen("#666666", style=Qt.PenStyle.DashLine),
        )
        plot_split.addWidget(self._plot_wf)

        # Bottom: probability density
        self._plot_prob = SimPlotWidget(
            title="Probability Density |\u03c8(x, t)|\u00b2",
            x_label="position x", y_label="|\u03c8|\u00b2",
        )
        self._line_prob = self._plot_prob.add_line(width=2)
        self._plot_prob.plot_item.getAxis("left").enableAutoSIPrefix(False)
        self._plot_prob.plot_item.getAxis("bottom").enableAutoSIPrefix(False)
        self._plot_prob.plot_item.addLine(
            x=0, pen=pg.mkPen("#666666", style=Qt.PenStyle.DashLine),
        )
        self._wall_right_prob = self._plot_prob.plot_item.addLine(
            x=DEFAULT_L, pen=pg.mkPen("#666666", style=Qt.PenStyle.DashLine),
        )
        plot_split.addWidget(self._plot_prob)

        plot_split.setSizes([200, 250, 200])
        main.addWidget(plot_split, 1)

        # Animation timer
        self._timer = QTimer()
        self._timer.setInterval(DEFAULT_TIMER_MS)
        self._timer.timeout.connect(self._advance)

    def _compute(self) -> None:
        L = self._spin_L.value()
        n = self._spin_n.value()
        n_max = self._spin_n_max.value()

        self._x = np.linspace(0, L, DEFAULT_N_POINTS)

        # Energy levels
        ns = np.arange(1, n_max + 1)
        energies = np.array([energy_level(int(nn), L) for nn in ns])
        self._scatter_energy.setData(ns, energies)
        e_max = float(energies.max())
        self._plot_energy.plot_item.setLimits(
            xMin=0, xMax=n_max + 1, yMin=0, yMax=e_max * 1.5,
        )
        self._plot_energy.plot_item.setXRange(0.5, n_max + 0.5)
        self._plot_energy.plot_item.setYRange(0, e_max * 1.1)

        # Wavefunction (or superposition) — always time-evolve so Play is meaningful
        if self._chk_super.isChecked():
            coeffs = normalise_coefficients([(1, 1+0j), (2, 1+0j), (3, 1+0j)])
            psi = time_evolved_state(self._x, coeffs, self._t, L)
        else:
            # Single eigenstate with time-dependent phase exp(-i E_n t)
            psi = time_evolved_state(self._x, [(n, 1.0 + 0j)], self._t, L)

        self._line_wf_real.setData(self._x, psi.real)
        self._line_wf_imag.setData(self._x, psi.imag)
        prob = (np.abs(psi) ** 2).astype(np.float64)
        max_psi = max(
            float(np.abs(psi.real).max()),
            float(np.abs(psi.imag).max()),
            1e-10,
        )

        self._line_prob.setData(self._x, prob)

        # Update box wall positions
        self._wall_right.setValue(L)
        self._wall_right_prob.setValue(L)

        if max_psi <= 0:
            max_psi = 1.0
        self._plot_wf.plot_item.setLimits(
            xMin=-0.2 * L, xMax=1.2 * L,
            yMin=-max_psi * 1.5, yMax=max_psi * 1.5,
        )
        self._plot_wf.plot_item.setXRange(-0.05 * L, 1.05 * L)
        self._plot_wf.plot_item.setYRange(-max_psi * 1.2, max_psi * 1.2)

        max_prob = float(prob.max()) if prob.size else 1.0
        if max_prob <= 0:
            max_prob = 1.0
        self._plot_prob.plot_item.setLimits(
            xMin=-0.2 * L, xMax=1.2 * L,
            yMin=-0.1 * max_prob, yMax=max_prob * 1.5,
        )
        self._plot_prob.plot_item.setXRange(-0.05 * L, 1.05 * L)
        self._plot_prob.plot_item.setYRange(0, max_prob * 1.2)

        # Readout
        if self._chk_super.isChecked():
            E1 = energy_level(1, L)
            E2 = energy_level(2, L)
            E3 = energy_level(3, L)
            self._readout.setText(
                f"L = {L:.2f}\n"
                f"E\u2081 = {E1:.3f}\n"
                f"E\u2082 = {E2:.3f}\n"
                f"E\u2083 = {E3:.3f}\n"
                f"t = {self._t:.2f}"
            )
        else:
            E_n = energy_level(n, L)
            T_n = 2 * np.pi / E_n if E_n > 0 else 0.0
            self._readout.setText(
                f"L = {L:.2f}\n"
                f"n = {n}\n"
                f"E\u2099 = {E_n:.3f}\n"
                f"period = {T_n:.3f}\n"
                f"nodes = {n - 1}\n"
                f"t = {self._t:.2f}"
            )

    def _toggle_play(self) -> None:
        if self._btn_play.isChecked():
            self._btn_play.setText("Pause")
            self._timer.start()
        else:
            self._btn_play.setText("Play")
            self._timer.stop()

    def _advance(self) -> None:
        dt = (DEFAULT_TIMER_MS / 1000.0) * self._spin_speed.value()
        self._t += dt
        self._compute()

    def _reset_view(self) -> None:
        self._t = 0.0
        self._compute()

    def get_params(self) -> dict[str, Any]:
        return {
            "L": self._spin_L.value(),
            "n": self._spin_n.value(),
            "n_max": self._spin_n_max.value(),
            "superposition": self._chk_super.isChecked(),
            "speed": self._spin_speed.value(),
        }

    def set_params(self, p: dict[str, Any]) -> None:
        if "L" in p: self._spin_L.setValue(p["L"])
        if "n" in p: self._spin_n.setValue(p["n"])
        if "n_max" in p: self._spin_n_max.setValue(p["n_max"])
        if "superposition" in p: self._chk_super.setChecked(p["superposition"])
        if "speed" in p: self._spin_speed.setValue(p["speed"])
        self._compute()

    def get_data(self) -> dict[str, np.ndarray]:
        L = self._spin_L.value()
        n = self._spin_n.value()
        return {
            "x": self._x,
            "psi": wavefunction(self._x, n, L),
            "prob": probability_density(self._x, n, L),
        }

    def stop(self) -> None:
        self._timer.stop()
        self._btn_play.setChecked(False)
        self._btn_play.setText("Play")
