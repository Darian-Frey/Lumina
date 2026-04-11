"""Q02 Quantum Tunnelling — UI module."""

from __future__ import annotations

from typing import Any

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDoubleSpinBox, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QSplitter, QVBoxLayout, QWidget,
)

from lumina.core.config import BTN_STYLE_COMPUTE, BTN_STYLE_RESET
from lumina.core.plot import SimPlotWidget
from lumina.modules.quantum.q02_tunnelling.physics import (
    potential_profile, stationary_state, transmission_coefficient,
    transmission_curve,
)


def _spin_row(
    label: str, lo: float, hi: float, val: float, dec: int = 2,
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


class TunnellingWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._setup_tooltips()
        self._compute()

    def _setup_tooltips(self) -> None:
        self._spin_E.setToolTip("Particle energy")
        self._spin_V0.setToolTip("Barrier height — tunnelling occurs when E < V0")
        self._spin_a.setToolTip("Barrier width — wider barriers reduce tunnelling exponentially")
        self._btn_compute.setToolTip("Recompute with current parameters")
        self._btn_reset_view.setToolTip("Auto-range the plots")

    def _build_ui(self) -> None:
        main = QHBoxLayout(self)
        main.setContentsMargins(8, 8, 8, 8)

        ctrl_w = QWidget()
        ctrl_w.setFixedWidth(240)
        ctrl = QVBoxLayout(ctrl_w)
        ctrl.setContentsMargins(4, 4, 4, 4)

        # Parameters
        param_grp = QGroupBox("Parameters")
        pl = QVBoxLayout(param_grp)
        r, self._spin_E = _spin_row("Energy E:", 0.01, 20.0, 2.0)
        pl.addLayout(r)
        r, self._spin_V0 = _spin_row("Barrier V\u2080:", 0.01, 20.0, 5.0)
        pl.addLayout(r)
        r, self._spin_a = _spin_row("Width a:", 0.1, 10.0, 1.5)
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

        # Equations — rendered as rich-text HTML for proper spacing
        eq = QGroupBox("Formulas")
        eql = QVBoxLayout(eq)
        eql.setContentsMargins(8, 12, 8, 8)
        eql.setSpacing(8)

        eq_label = QLabel(
            "<div style='line-height: 145%;'>"
            "<b>Tunnelling (E &lt; V&#8320;):</b><br>"
            "&nbsp;&nbsp;T = 1 / (1 + F&#x00b2;)<br>"
            "&nbsp;&nbsp;F = V&#8320; sinh(&#x03ba;a) /<br>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2&#x221a;(E(V&#8320;&#x2212;E))<br>"
            "&nbsp;&nbsp;&#x03ba; = &#x221a;(2m(V&#8320;&#x2212;E)) / &#x0127;<br>"
            "<br>"
            "<b>Above (E &gt; V&#8320;):</b><br>"
            "&nbsp;&nbsp;T oscillates with E"
            "</div>"
        )
        eq_label.setTextFormat(Qt.TextFormat.RichText)
        eq_label.setFont(QFont("sans-serif", 9))
        eq_label.setWordWrap(True)
        eql.addWidget(eq_label)
        ctrl.addWidget(eq)

        ctrl.addStretch()
        main.addWidget(ctrl_w)

        # Plots
        plot_split = QSplitter(Qt.Orientation.Vertical)

        # Top: barrier + wavefunction
        self._plot_wf = SimPlotWidget(
            title="Wavefunction & Barrier",
            x_label="position x", y_label="amplitude",
        )
        self._plot_wf.plot_item.addLegend(offset=(10, 10))
        self._plot_wf.plot_item.getAxis("left").enableAutoSIPrefix(False)
        self._plot_wf.plot_item.getAxis("bottom").enableAutoSIPrefix(False)

        self._line_potential = self._plot_wf.plot_item.plot(
            [], [], pen=pg.mkPen("#666666", width=2), name="V(x) barrier",
        )
        self._fill_potential = pg.FillBetweenItem(
            self._line_potential,
            self._plot_wf.plot_item.plot([], [], pen=None),
            brush=pg.mkBrush(102, 102, 102, 60),
        )
        self._plot_wf.plot_item.addItem(self._fill_potential)
        self._line_psi_real = self._plot_wf.plot_item.plot(
            [], [], pen=pg.mkPen("#1f77b4", width=2), name="Re[\u03c8]",
        )
        self._line_psi_imag = self._plot_wf.plot_item.plot(
            [], [], pen=pg.mkPen("#ff7f0e", width=2), name="Im[\u03c8]",
        )
        self._line_E = self._plot_wf.plot_item.addLine(
            y=0, pen=pg.mkPen("#d62728", width=2, style=Qt.PenStyle.DashLine),
        )
        plot_split.addWidget(self._plot_wf)

        # Bottom: T(E) curve
        self._plot_T = SimPlotWidget(
            title="Transmission T(E)",
            x_label="energy E", y_label="transmission T",
        )
        self._plot_T.plot_item.getAxis("left").enableAutoSIPrefix(False)
        self._plot_T.plot_item.getAxis("bottom").enableAutoSIPrefix(False)
        self._line_T = self._plot_T.add_line(name="T(E)", width=2)
        self._dot_E = self._plot_T.add_scatter(size=12)
        self._line_V0 = self._plot_T.plot_item.addLine(
            x=0, pen=pg.mkPen("#666666", width=1, style=Qt.PenStyle.DashLine),
        )
        self._plot_T.plot_item.setLimits(yMin=-0.05, yMax=1.1)
        plot_split.addWidget(self._plot_T)

        plot_split.setSizes([300, 250])
        main.addWidget(plot_split, 1)

    def _compute(self) -> None:
        E = self._spin_E.value()
        V0 = self._spin_V0.value()
        a = self._spin_a.value()

        # Wavefunction view
        x_min = -3.0
        x_max = a + 3.0
        x = np.linspace(x_min, x_max, 800)

        # Barrier
        V = potential_profile(x, V0, a, x0=0.0)
        # Scale potential for display: maximum drawn at top of plot
        V_disp = V / V0 * 2.0  # Display height = 2 units
        self._line_potential.setData(x, V_disp)

        # Update fill
        baseline = np.zeros_like(x)
        self._fill_potential.curves[1].setData(x, baseline)

        # Wavefunction
        psi = stationary_state(x, E, V0, a)
        self._line_psi_real.setData(x, psi.real)
        self._line_psi_imag.setData(x, psi.imag)

        # Energy line at scaled height
        self._line_E.setValue(E / V0 * 2.0)

        # T(E) curve
        E_max = max(V0 * 2, E * 2)
        E_arr, T_arr = transmission_curve(0.01, E_max, V0, a)
        self._line_T.setData(E_arr, T_arr)

        # Marker at current E
        T = transmission_coefficient(E, V0, a)
        self._dot_E.setData([E], [T])

        # V0 marker on T(E)
        self._line_V0.setValue(V0)

        # Lock plot ranges
        self._plot_wf.plot_item.setLimits(
            xMin=x_min - 1, xMax=x_max + 1,
            yMin=-2.5, yMax=3.0,
        )
        self._plot_wf.plot_item.setXRange(x_min, x_max)
        self._plot_wf.plot_item.setYRange(-2.0, 2.5)

        self._plot_T.plot_item.setLimits(
            xMin=0, xMax=E_max * 1.1, yMin=-0.05, yMax=1.1,
        )
        self._plot_T.plot_item.setXRange(0, E_max)
        self._plot_T.plot_item.setYRange(0, 1.05)

        # Readout
        regime = "tunnelling (E < V\u2080)" if E < V0 else (
            "above barrier (E > V\u2080)" if E > V0 else "at barrier (E = V\u2080)"
        )
        self._readout.setText(
            f"E = {E:.3f}\n"
            f"V\u2080 = {V0:.3f}\n"
            f"a = {a:.3f}\n"
            f"\n"
            f"Regime: {regime}\n"
            f"T = {T:.4f}\n"
            f"R = {1 - T:.4f}"
        )

    def _reset_view(self) -> None:
        self._compute()

    def get_params(self) -> dict[str, Any]:
        return {
            "E": self._spin_E.value(),
            "V0": self._spin_V0.value(),
            "a": self._spin_a.value(),
        }

    def set_params(self, p: dict[str, Any]) -> None:
        if "E" in p: self._spin_E.setValue(p["E"])
        if "V0" in p: self._spin_V0.setValue(p["V0"])
        if "a" in p: self._spin_a.setValue(p["a"])
        self._compute()

    def get_data(self) -> dict[str, np.ndarray]:
        E = self._spin_E.value()
        V0 = self._spin_V0.value()
        a = self._spin_a.value()
        E_arr, T_arr = transmission_curve(0.01, max(V0 * 2, E * 2), V0, a)
        return {"E": E_arr, "T": T_arr}

    def stop(self) -> None:
        pass
