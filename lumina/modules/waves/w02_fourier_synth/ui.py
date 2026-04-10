"""W02 Fourier Synthesiser — UI module."""

from __future__ import annotations

from typing import Any

import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox, QGroupBox, QHBoxLayout, QLabel, QPushButton,
    QSlider, QSpinBox, QSplitter, QVBoxLayout, QWidget,
)

from lumina.core.plot import SimPlotWidget
from lumina.modules.waves.w02_fourier_synth.physics import (
    fourier_partial_sum, gibbs_overshoot,
    sawtooth_wave_coefficients, square_wave_coefficients,
    target_waveform, triangle_wave_coefficients,
)

_COEFF_FNS = {
    "square": square_wave_coefficients,
    "triangle": triangle_wave_coefficients,
    "sawtooth": sawtooth_wave_coefficients,
}


class FourierSynthWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._x = np.linspace(-np.pi, np.pi, 1000)
        self._build_ui()
        self._update()

    def _build_ui(self) -> None:
        main = QHBoxLayout(self)
        main.setContentsMargins(8, 8, 8, 8)

        ctrl_w = QWidget()
        ctrl_w.setFixedWidth(220)
        ctrl = QVBoxLayout(ctrl_w)
        ctrl.setContentsMargins(4, 4, 4, 4)

        # Waveform selector
        wf = QGroupBox("Target Waveform")
        wfl = QVBoxLayout(wf)
        self._combo = QComboBox()
        self._combo.addItems(["square", "triangle", "sawtooth"])
        self._combo.currentTextChanged.connect(lambda: self._update())
        wfl.addWidget(self._combo)
        ctrl.addWidget(wf)

        # N harmonics
        nh = QGroupBox("Harmonics")
        nhl = QVBoxLayout(nh)
        row = QHBoxLayout()
        row.addWidget(QLabel("N:"))
        self._spin_n = QSpinBox()
        self._spin_n.setRange(1, 50)
        self._spin_n.setValue(5)
        self._spin_n.valueChanged.connect(self._update)
        row.addWidget(self._spin_n)
        nhl.addLayout(row)
        ctrl.addWidget(nh)

        self._btn_update = QPushButton("Update")
        self._btn_update.clicked.connect(self._update)
        ctrl.addWidget(self._btn_update)

        # Readout
        self._readout = QLabel()
        self._readout.setFont(QFont("monospace", 9))
        self._readout.setWordWrap(True)
        ctrl.addWidget(self._readout)

        # Equation
        eq = QGroupBox("Series")
        eql = QVBoxLayout(eq)
        self._eq_label = QLabel()
        self._eq_label.setFont(QFont("monospace", 9))
        self._eq_label.setWordWrap(True)
        eql.addWidget(self._eq_label)
        ctrl.addWidget(eq)

        ctrl.addStretch()
        main.addWidget(ctrl_w)

        sp = QSplitter(Qt.Orientation.Vertical)

        self._plot_harmonics = SimPlotWidget(
            title="Individual Harmonics", x_label="x", y_label="y"
        )
        self._harmonic_lines = [self._plot_harmonics.add_line() for _ in range(50)]
        sp.addWidget(self._plot_harmonics)

        self._plot_sum = SimPlotWidget(
            title="Partial Sum vs Target", x_label="x", y_label="y"
        )
        self._line_target = self._plot_sum.add_line(
            pen=self._plot_sum.plot_item.plot([], [], pen="r").opts.get("pen")
        )
        # Re-do properly
        self._plot_sum.clear()
        self._line_target = self._plot_sum.plot_item.plot(
            [], [], pen={"color": "#999999", "width": 1, "style": Qt.PenStyle.DashLine},
            name="target",
        )
        self._line_sum = self._plot_sum.add_line(name="partial sum", width=2)
        sp.addWidget(self._plot_sum)

        main.addWidget(sp, 1)

    def _update(self) -> None:
        kind = self._combo.currentText()
        n = self._spin_n.value()
        coeff_fn = _COEFF_FNS.get(kind, square_wave_coefficients)
        coeffs = coeff_fn(n)

        # Individual harmonics
        for i, line in enumerate(self._harmonic_lines):
            if i < len(coeffs):
                nn, bn = coeffs[i]
                line.setData(self._x, bn * np.sin(nn * self._x))
            else:
                line.setData([], [])

        # Partial sum
        y_sum = fourier_partial_sum(self._x, coeffs)
        self._line_sum.setData(self._x, y_sum)

        # Target
        y_target = target_waveform(self._x, kind)
        self._line_target.setData(self._x, y_target)

        # Readout
        overshoot = gibbs_overshoot(coeffs)
        self._readout.setText(
            f"N = {n} harmonics\n"
            f"Gibbs overshoot: {overshoot:.1f}%"
        )

        # Equation label
        terms = [f"{bn:+.3f}\u00b7sin({nn}x)" for nn, bn in coeffs[:5]]
        eq_str = " ".join(terms)
        if len(coeffs) > 5:
            eq_str += " + ..."
        self._eq_label.setText(f"f(x) \u2248 {eq_str}")

    def get_params(self) -> dict[str, Any]:
        return {"kind": self._combo.currentText(), "n": self._spin_n.value()}

    def set_params(self, p: dict[str, Any]) -> None:
        if "kind" in p:
            idx = self._combo.findText(p["kind"])
            if idx >= 0:
                self._combo.setCurrentIndex(idx)
        if "n" in p:
            self._spin_n.setValue(p["n"])
        self._update()

    def get_data(self) -> dict[str, np.ndarray]:
        kind = self._combo.currentText()
        n = self._spin_n.value()
        coeffs = _COEFF_FNS[kind](n)
        return {
            "x": self._x,
            "partial_sum": fourier_partial_sum(self._x, coeffs),
            "target": target_waveform(self._x, kind),
        }

    def stop(self) -> None:
        pass
