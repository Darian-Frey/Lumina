"""AP04 Fourier Series Builder — UI module."""

from __future__ import annotations

from typing import Any

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox, QGroupBox, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QSplitter, QVBoxLayout, QWidget,
)

from lumina.core.config import BTN_STYLE_COMPUTE, BTN_STYLE_RESET
from lumina.core.plot import SimPlotWidget
from lumina.modules.applied_maths.ap04_fourier_series.physics import (
    PRESETS, fourier_coefficients, fourier_partial_sum,
)


class FourierSeriesWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._x = np.linspace(-np.pi, np.pi, 1000)
        self._build_ui()
        self._setup_tooltips()
        self._compute()

    def _setup_tooltips(self) -> None:
        self._combo.setToolTip("Choose the target function to approximate")
        self._spin_n.setToolTip("Number of Fourier harmonics to include")
        self._btn_compute.setToolTip("Recompute with current settings")
        self._btn_reset_view.setToolTip("Auto-range the plots")

    def _build_ui(self) -> None:
        main = QHBoxLayout(self)
        main.setContentsMargins(8, 8, 8, 8)

        ctrl_w = QWidget()
        ctrl_w.setFixedWidth(240)
        ctrl = QVBoxLayout(ctrl_w)
        ctrl.setContentsMargins(4, 4, 4, 4)

        # Function selector
        fn_grp = QGroupBox("Target Function")
        fl = QVBoxLayout(fn_grp)
        self._combo = QComboBox()
        for name in PRESETS:
            self._combo.addItem(name)
        self._combo.currentTextChanged.connect(self._compute)
        fl.addWidget(self._combo)
        ctrl.addWidget(fn_grp)

        # Number of harmonics
        n_grp = QGroupBox("Harmonics")
        nl = QVBoxLayout(n_grp)
        r = QHBoxLayout()
        nl_lbl = QLabel("Harmonics N:")
        nl_lbl.setFixedWidth(110)
        nl_lbl.setFont(QFont("sans-serif", 9))
        r.addWidget(nl_lbl)
        self._spin_n = QSpinBox()
        self._spin_n.setRange(1, 100)
        self._spin_n.setValue(10)
        self._spin_n.setFixedWidth(80)
        self._spin_n.valueChanged.connect(self._compute)
        r.addWidget(self._spin_n)
        nl.addLayout(r)
        ctrl.addWidget(n_grp)

        # Buttons
        self._btn_compute = QPushButton("Compute")
        self._btn_compute.setStyleSheet(BTN_STYLE_COMPUTE)
        self._btn_compute.clicked.connect(self._compute)
        ctrl.addWidget(self._btn_compute)

        self._btn_reset_view = QPushButton("Reset View")
        self._btn_reset_view.setStyleSheet(BTN_STYLE_RESET)
        self._btn_reset_view.clicked.connect(self._reset_view)
        ctrl.addWidget(self._btn_reset_view)

        # Coefficient readout
        self._readout = QLabel()
        self._readout.setFont(QFont("monospace", 8))
        self._readout.setWordWrap(True)
        ctrl.addWidget(self._readout)

        ctrl.addStretch()
        main.addWidget(ctrl_w)

        # Plots
        sp = QSplitter(Qt.Orientation.Vertical)

        self._plot_fn = SimPlotWidget(
            title="Function & Approximation", x_label="x", y_label="f(x)",
        )
        self._plot_fn.plot_item.addLegend(offset=(10, 10))
        self._plot_fn.plot_item.getAxis("left").enableAutoSIPrefix(False)
        self._plot_fn.plot_item.getAxis("bottom").enableAutoSIPrefix(False)
        self._line_target = self._plot_fn.plot_item.plot(
            [], [], pen=pg.mkPen("#d62728", width=2, style=Qt.PenStyle.DashLine),
            name="target",
        )
        self._line_sum = self._plot_fn.add_line(name="approximation", width=2)
        sp.addWidget(self._plot_fn)

        self._plot_coeffs = SimPlotWidget(
            title="Fourier Coefficients", x_label="n", y_label="amplitude",
        )
        self._plot_coeffs.plot_item.addLegend(offset=(10, 10))
        self._plot_coeffs.plot_item.getAxis("left").enableAutoSIPrefix(False)
        self._bar_a = pg.BarGraphItem(
            x=[], height=[], width=0.4, brush="#1f77b4",
        )
        self._bar_b = pg.BarGraphItem(
            x=[], height=[], width=0.4, brush="#ff7f0e",
        )
        self._plot_coeffs.plot_item.addItem(self._bar_a)
        self._plot_coeffs.plot_item.addItem(self._bar_b)
        # Legend proxies (BarGraphItem doesn't render in legend)
        self._plot_coeffs.plot_item.plot(
            [], [], pen=pg.mkPen("#1f77b4", width=6), name="a\u2099 (cosine)",
        )
        self._plot_coeffs.plot_item.plot(
            [], [], pen=pg.mkPen("#ff7f0e", width=6), name="b\u2099 (sine)",
        )
        sp.addWidget(self._plot_coeffs)

        sp.setSizes([320, 200])
        main.addWidget(sp, 1)

    def _compute(self) -> None:
        name = self._combo.currentText()
        n_max = self._spin_n.value()
        f = PRESETS[name]
        target = f(self._x)
        a, b = fourier_coefficients(target, self._x, n_max)
        approximation = fourier_partial_sum(self._x, a, b)

        self._line_target.setData(self._x, target)
        self._line_sum.setData(self._x, approximation)

        # Coefficient bars
        ns = np.arange(0, n_max + 1)
        self._bar_a.setOpts(
            x=ns - 0.2, height=a, width=0.4, brush="#1f77b4",
        )
        self._bar_b.setOpts(
            x=ns + 0.2, height=b, width=0.4, brush="#ff7f0e",
        )

        # Lock plot ranges
        y_max = float(max(abs(target).max(), abs(approximation).max()))
        if y_max == 0:
            y_max = 1.0
        self._plot_fn.plot_item.setLimits(
            xMin=-np.pi - 0.5, xMax=np.pi + 0.5,
            yMin=-y_max * 1.5, yMax=y_max * 1.5,
        )
        self._plot_fn.plot_item.setXRange(-np.pi, np.pi)
        self._plot_fn.plot_item.setYRange(-y_max * 1.2, y_max * 1.2)

        coeff_max = float(max(abs(a).max(), abs(b).max())) if n_max > 0 else 1.0
        if coeff_max == 0:
            coeff_max = 1.0
        self._plot_coeffs.plot_item.setLimits(
            xMin=-1, xMax=n_max + 1,
            yMin=-coeff_max * 1.5, yMax=coeff_max * 1.5,
        )
        self._plot_coeffs.plot_item.setXRange(-0.5, n_max + 0.5)
        self._plot_coeffs.plot_item.setYRange(-coeff_max * 1.2, coeff_max * 1.2)

        # Readout: a_0 plus first few non-zero coefficients
        lines = [f"a\u2080 = {a[0]:+.3f}"]
        for n in range(1, min(6, n_max + 1)):
            lines.append(f"a{n} = {a[n]:+.3f}  b{n} = {b[n]:+.3f}")
        if n_max > 5:
            lines.append("...")
        self._readout.setText("\n".join(lines))
        self._a = a
        self._b = b

    def _reset_view(self) -> None:
        self._compute()

    def get_params(self) -> dict[str, Any]:
        return {
            "function": self._combo.currentText(),
            "n_max": self._spin_n.value(),
        }

    def set_params(self, p: dict[str, Any]) -> None:
        if "function" in p:
            idx = self._combo.findText(p["function"])
            if idx >= 0:
                self._combo.setCurrentIndex(idx)
        if "n_max" in p:
            self._spin_n.setValue(p["n_max"])
        self._compute()

    def get_data(self) -> dict[str, np.ndarray]:
        return {"x": self._x, "a": self._a, "b": self._b}

    def stop(self) -> None:
        pass
