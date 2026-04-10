"""T02 Maxwell-Boltzmann — UI module."""
from __future__ import annotations
from typing import Any
import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDoubleSpinBox, QGroupBox, QHBoxLayout, QLabel, QPushButton,
    QVBoxLayout, QWidget,
)
from lumina.core.plot import SimPlotWidget
from lumina.modules.thermodynamics.t02_maxwell_boltzmann.physics import (
    mb_pdf_3d, mean_speed, most_probable_speed, rms_speed,
)

DEFAULT_MASS: float = 4.65e-26  # N2

class MaxwellBoltzmannWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._update()

    def _build_ui(self) -> None:
        main = QHBoxLayout(self)
        main.setContentsMargins(8, 8, 8, 8)
        ctrl_w = QWidget()
        ctrl_w.setFixedWidth(220)
        ctrl = QVBoxLayout(ctrl_w)
        ctrl.setContentsMargins(4, 4, 4, 4)

        pg_grp = QGroupBox("Parameters")
        pl = QVBoxLayout(pg_grp)
        r = QHBoxLayout()
        r.addWidget(QLabel("T (K)"))
        self._spin_T = QDoubleSpinBox()
        self._spin_T.setRange(50, 5000)
        self._spin_T.setValue(300)
        self._spin_T.setDecimals(0)
        self._spin_T.valueChanged.connect(self._update)
        r.addWidget(self._spin_T)
        pl.addLayout(r)
        ctrl.addWidget(pg_grp)

        self._btn = QPushButton("Update")
        self._btn.clicked.connect(self._update)
        ctrl.addWidget(self._btn)

        self._readout = QLabel()
        self._readout.setFont(QFont("monospace", 9))
        self._readout.setWordWrap(True)
        ctrl.addWidget(self._readout)

        eq = QGroupBox("Distribution")
        eql = QVBoxLayout(eq)
        eql.addWidget(QLabel("f(v) = 4\u03c0(m/2\u03c0kT)^(3/2)\n"
                              "\u00b7 v\u00b2 \u00b7 exp(-mv\u00b2/2kT)"))
        ctrl.addWidget(eq)
        ctrl.addStretch()
        main.addWidget(ctrl_w)

        self._plot = SimPlotWidget(title="Maxwell-Boltzmann Distribution",
                                    x_label="v (m/s)", y_label="f(v)")
        self._line = self._plot.add_line(name="f(v)", width=2)
        # Vertical markers
        self._vmp_line = self._plot.plot_item.addLine(x=0, pen=pg.mkPen("#2ca02c", style=Qt.PenStyle.DashLine))
        self._vavg_line = self._plot.plot_item.addLine(x=0, pen=pg.mkPen("#ff7f0e", style=Qt.PenStyle.DashLine))
        self._vrms_line = self._plot.plot_item.addLine(x=0, pen=pg.mkPen("#d62728", style=Qt.PenStyle.DashLine))
        main.addWidget(self._plot, 1)

    def _update(self) -> None:
        T = self._spin_T.value()
        m = DEFAULT_MASS
        vmp = most_probable_speed(m, T)
        vavg = mean_speed(m, T)
        vrms = rms_speed(m, T)

        v = np.linspace(0, vrms * 3, 500)
        fv = mb_pdf_3d(v, m, T)
        self._line.setData(v, fv)
        self._vmp_line.setValue(vmp)
        self._vavg_line.setValue(vavg)
        self._vrms_line.setValue(vrms)

        self._readout.setText(
            f"v_mp  = {vmp:.1f} m/s\n"
            f"v_avg = {vavg:.1f} m/s\n"
            f"v_rms = {vrms:.1f} m/s"
        )

    def get_params(self) -> dict[str, Any]:
        return {"T": self._spin_T.value()}

    def set_params(self, p: dict[str, Any]) -> None:
        if "T" in p: self._spin_T.setValue(p["T"])
        self._update()

    def get_data(self) -> dict[str, np.ndarray]:
        T = self._spin_T.value()
        v = np.linspace(0, rms_speed(DEFAULT_MASS, T) * 3, 500)
        return {"v": v, "fv": mb_pdf_3d(v, DEFAULT_MASS, T)}

    def stop(self) -> None:
        pass
