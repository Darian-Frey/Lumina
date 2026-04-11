"""E03 RC/RL/LC/RLC Circuits — UI module."""

from __future__ import annotations

from typing import Any

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QSplitter, QVBoxLayout, QWidget,
)

from lumina.core.config import BTN_STYLE_COMPUTE, BTN_STYLE_RESET
from lumina.core.plot import SimPlotWidget
from lumina.modules.electromagnetism.e03_rlc_circuits.physics import (
    damping_regime, lc_oscillation, quality_factor, rc_charging,
    rc_discharging, resonant_frequency, rl_building, rl_decaying,
    rlc_response,
)


def _spin_row(label: str, lo: float, hi: float, val: float, dec: int = 2) -> tuple[QHBoxLayout, QDoubleSpinBox]:
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


class CircuitsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._t = np.array([])
        self._y1 = np.array([])
        self._y2 = np.array([])
        self._build_ui()
        self._setup_tooltips()
        self._on_mode_changed()

    def _setup_tooltips(self) -> None:
        self._combo.setToolTip("Choose the circuit topology")
        self._spin_R.setToolTip("Resistance in ohms")
        self._spin_L.setToolTip("Inductance in henries")
        self._spin_C.setToolTip("Capacitance in farads")
        self._spin_V.setToolTip("Source voltage / initial energy storage")
        self._spin_t_max.setToolTip("Total simulation time")
        self._btn_compute.setToolTip("Recompute with current values")
        self._btn_reset_view.setToolTip("Auto-range the plots")

    def _build_ui(self) -> None:
        main = QHBoxLayout(self)
        main.setContentsMargins(8, 8, 8, 8)

        ctrl_w = QWidget()
        ctrl_w.setFixedWidth(240)
        ctrl = QVBoxLayout(ctrl_w)
        ctrl.setContentsMargins(4, 4, 4, 4)

        # Mode
        mode_grp = QGroupBox("Circuit")
        ml = QVBoxLayout(mode_grp)
        self._combo = QComboBox()
        self._combo.addItems([
            "RC charging", "RC discharging",
            "RL building", "RL decaying",
            "LC oscillation", "RLC damped",
        ])
        self._combo.setCurrentText("RC charging")
        self._combo.currentTextChanged.connect(self._on_mode_changed)
        ml.addWidget(self._combo)
        ctrl.addWidget(mode_grp)

        # Components
        comp_grp = QGroupBox("Components")
        cl = QVBoxLayout(comp_grp)
        r, self._spin_R = _spin_row("Resistance R (\u03a9):", 0.01, 1000.0, 100.0, 2)
        cl.addLayout(r)
        r, self._spin_L = _spin_row("Inductance L (H):", 0.001, 100.0, 1.0, 3)
        cl.addLayout(r)
        r, self._spin_C = _spin_row("Capacitance C (F):", 1e-6, 1.0, 1e-3, 6)
        cl.addLayout(r)
        ctrl.addWidget(comp_grp)

        # Source / IC
        src = QGroupBox("Source / IC")
        sl = QVBoxLayout(src)
        r, self._spin_V = _spin_row("Source V / Q\u2080:", 0.01, 100.0, 5.0, 2)
        sl.addLayout(r)
        r, self._spin_t_max = _spin_row("Duration (s):", 0.001, 100.0, 1.0, 3)
        sl.addLayout(r)
        ctrl.addWidget(src)

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

        # Plots
        plot_split = QSplitter(Qt.Orientation.Vertical)

        self._plot_y1 = SimPlotWidget(title="", x_label="t (s)", y_label="")
        self._line_y1 = self._plot_y1.add_line(width=2)
        plot_split.addWidget(self._plot_y1)

        self._plot_y2 = SimPlotWidget(title="", x_label="t (s)", y_label="")
        self._line_y2 = self._plot_y2.add_line(width=2)
        plot_split.addWidget(self._plot_y2)

        plot_split.setSizes([250, 250])
        main.addWidget(plot_split, 1)

    def _on_mode_changed(self) -> None:
        mode = self._combo.currentText()
        # Suggest sensible defaults per mode
        if "RC" in mode:
            self._spin_R.setValue(100.0)
            self._spin_C.setValue(1e-3)
            self._spin_t_max.setValue(0.5)
            self._spin_V.setValue(5.0)
            self._plot_y1.plot_item.setTitle("Charge q(t)", color="k", size="11pt")
            self._plot_y2.plot_item.setTitle("Current i(t)", color="k", size="11pt")
            self._plot_y1.plot_item.setLabel("left", "q (C)")
            self._plot_y2.plot_item.setLabel("left", "i (A)")
        elif "RL" in mode:
            self._spin_R.setValue(50.0)
            self._spin_L.setValue(1.0)
            self._spin_t_max.setValue(0.2)
            self._spin_V.setValue(10.0)
            self._plot_y1.plot_item.setTitle("Current i(t)", color="k", size="11pt")
            self._plot_y2.plot_item.setTitle("Inductor voltage v_L(t)", color="k", size="11pt")
            self._plot_y1.plot_item.setLabel("left", "i (A)")
            self._plot_y2.plot_item.setLabel("left", "v_L (V)")
        elif mode == "LC oscillation":
            self._spin_R.setValue(0.0)
            self._spin_L.setValue(1.0)
            self._spin_C.setValue(1e-3)
            self._spin_t_max.setValue(0.5)
            self._spin_V.setValue(5.0)
            self._plot_y1.plot_item.setTitle("Charge q(t)", color="k", size="11pt")
            self._plot_y2.plot_item.setTitle("Current i(t)", color="k", size="11pt")
            self._plot_y1.plot_item.setLabel("left", "q (C)")
            self._plot_y2.plot_item.setLabel("left", "i (A)")
        else:  # RLC
            self._spin_R.setValue(20.0)
            self._spin_L.setValue(1.0)
            self._spin_C.setValue(1e-3)
            self._spin_t_max.setValue(1.0)
            self._spin_V.setValue(5.0)
            self._plot_y1.plot_item.setTitle("Charge q(t)", color="k", size="11pt")
            self._plot_y2.plot_item.setTitle("Current i(t)", color="k", size="11pt")
            self._plot_y1.plot_item.setLabel("left", "q (C)")
            self._plot_y2.plot_item.setLabel("left", "i (A)")
        self._compute()

    def _compute(self) -> None:
        mode = self._combo.currentText()
        R = self._spin_R.value()
        L = self._spin_L.value()
        C = self._spin_C.value()
        V = self._spin_V.value()
        t_max = self._spin_t_max.value()

        n = 800
        t = np.linspace(0, t_max, n)

        if mode == "RC charging":
            y1, y2 = rc_charging(t, V, R, C)
            tau = R * C
            self._readout.setText(f"\u03c4 = R\u00b7C = {tau:.4f} s\nq_inf = C\u00b7V = {C * V:.4f} C")
        elif mode == "RC discharging":
            y1, y2 = rc_discharging(t, V, R, C)
            tau = R * C
            self._readout.setText(f"\u03c4 = R\u00b7C = {tau:.4f} s\nQ\u2080 = {V:.3f} C")
        elif mode == "RL building":
            y1, y2 = rl_building(t, V, R, L)
            tau = L / R
            self._readout.setText(f"\u03c4 = L/R = {tau:.4f} s\ni_inf = V/R = {V / R:.4f} A")
        elif mode == "RL decaying":
            y1, y2 = rl_decaying(t, V, R, L)
            tau = L / R
            self._readout.setText(f"\u03c4 = L/R = {tau:.4f} s\nI\u2080 = {V:.3f} A")
        elif mode == "LC oscillation":
            y1, y2 = lc_oscillation(t, V, L, C)
            omega = resonant_frequency(L, C)
            f = omega / (2 * np.pi)
            self._readout.setText(
                f"\u03c9\u2080 = {omega:.3f} rad/s\nf\u2080 = {f:.3f} Hz\nT = {1/f:.4f} s"
            )
        else:  # RLC damped
            y1, y2 = rlc_response(t, V, R, L, C)
            regime = damping_regime(R, L, C)
            omega0 = resonant_frequency(L, C)
            Q = quality_factor(R, L, C)
            self._readout.setText(
                f"\u03c9\u2080 = {omega0:.3f} rad/s\n"
                f"Q = {Q:.3f}\n"
                f"Regime: {regime}"
            )

        self._t = t
        self._y1 = y1
        self._y2 = y2
        self._line_y1.setData(t, y1)
        self._line_y2.setData(t, y2)

        # Lock view ranges
        for plot, y in ((self._plot_y1, y1), (self._plot_y2, y2)):
            y_max = float(np.abs(y).max())
            if y_max == 0:
                y_max = 1.0
            plot.plot_item.setLimits(
                xMin=-0.05 * t_max, xMax=1.1 * t_max,
                yMin=-y_max * 1.5, yMax=y_max * 1.5,
            )
            plot.plot_item.setXRange(0, t_max)
            plot.plot_item.setYRange(-y_max * 1.2, y_max * 1.2)

    def _reset_view(self) -> None:
        self._compute()

    def get_params(self) -> dict[str, Any]:
        return {
            "mode": self._combo.currentText(),
            "R": self._spin_R.value(),
            "L": self._spin_L.value(),
            "C": self._spin_C.value(),
            "V": self._spin_V.value(),
            "t_max": self._spin_t_max.value(),
        }

    def set_params(self, p: dict[str, Any]) -> None:
        if "mode" in p:
            idx = self._combo.findText(p["mode"])
            if idx >= 0:
                self._combo.setCurrentIndex(idx)
        for k, s in [
            ("R", self._spin_R), ("L", self._spin_L), ("C", self._spin_C),
            ("V", self._spin_V), ("t_max", self._spin_t_max),
        ]:
            if k in p:
                s.setValue(p[k])
        self._compute()

    def get_data(self) -> dict[str, np.ndarray]:
        return {"t": self._t, "y1": self._y1, "y2": self._y2}

    def stop(self) -> None:
        pass
