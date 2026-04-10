"""T01 Ideal Gas Simulation — UI module."""
from __future__ import annotations
from typing import Any
import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDoubleSpinBox, QGroupBox, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QSplitter, QVBoxLayout, QWidget,
)
from lumina.core.config import DEFAULT_TIMER_MS
from lumina.core.plot import SimPlotWidget
from lumina.modules.thermodynamics.t01_ideal_gas.physics import (
    DEFAULT_BOX, DEFAULT_MASS, DEFAULT_N, DEFAULT_RADIUS,
    compute_pressure, compute_speeds, compute_temperature,
    init_particles, step_particles,
)

class IdealGasWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._pos = np.zeros((0, 2))
        self._vel = np.zeros((0, 2))
        self._impulse_acc = 0.0
        self._steps = 0
        self._build_ui()
        self._init_sim()

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
        r.addWidget(QLabel("N particles"))
        self._spin_n = QSpinBox()
        self._spin_n.setRange(10, 500)
        self._spin_n.setValue(DEFAULT_N)
        r.addWidget(self._spin_n)
        pl.addLayout(r)
        r2 = QHBoxLayout()
        r2.addWidget(QLabel("T (K)"))
        self._spin_T = QDoubleSpinBox()
        self._spin_T.setRange(50, 2000)
        self._spin_T.setValue(300)
        self._spin_T.setDecimals(0)
        r2.addWidget(self._spin_T)
        pl.addLayout(r2)
        ctrl.addWidget(pg_grp)

        btn_row = QHBoxLayout()
        self._btn_play = QPushButton("Play")
        self._btn_play.setCheckable(True)
        self._btn_play.clicked.connect(self._toggle)
        btn_row.addWidget(self._btn_play)
        self._btn_reset = QPushButton("Reset")
        self._btn_reset.clicked.connect(self._init_sim)
        btn_row.addWidget(self._btn_reset)
        ctrl.addLayout(btn_row)

        self._readout = QLabel()
        self._readout.setFont(QFont("monospace", 9))
        self._readout.setWordWrap(True)
        ctrl.addWidget(self._readout)
        ctrl.addStretch()
        main.addWidget(ctrl_w)

        sp = QSplitter(Qt.Orientation.Vertical)
        self._plot_box = SimPlotWidget(title="Gas Box")
        self._plot_box.plot_item.setAspectLocked(True)
        self._plot_box.plot_item.setXRange(0, DEFAULT_BOX)
        self._plot_box.plot_item.setYRange(0, DEFAULT_BOX)
        self._scatter = pg.ScatterPlotItem(size=6, brush=pg.mkBrush("#1f77b4"))
        self._plot_box.plot_item.addItem(self._scatter)
        sp.addWidget(self._plot_box)

        self._plot_hist = SimPlotWidget(title="Speed Distribution", x_label="v", y_label="count")
        self._hist_bars = pg.BarGraphItem(x=[], height=[], width=0.1, brush="#1f77b4")
        self._plot_hist.plot_item.addItem(self._hist_bars)
        sp.addWidget(self._plot_hist)
        main.addWidget(sp, 1)

        self._timer = QTimer()
        self._timer.setInterval(DEFAULT_TIMER_MS)
        self._timer.timeout.connect(self._step)

    def _init_sim(self) -> None:
        n = self._spin_n.value()
        T = self._spin_T.value()
        self._pos, self._vel = init_particles(n, temperature=T)
        self._impulse_acc = 0.0
        self._steps = 0
        self._scatter.setData(self._pos[:, 0], self._pos[:, 1])
        self._update_readout()

    def _step(self) -> None:
        dt = 0.002
        self._pos, self._vel, imp = step_particles(
            self._pos, self._vel, DEFAULT_MASS, DEFAULT_BOX, DEFAULT_BOX, DEFAULT_RADIUS, dt,
        )
        self._impulse_acc += imp
        self._steps += 1
        self._scatter.setData(self._pos[:, 0], self._pos[:, 1])
        if self._steps % 10 == 0:
            self._update_readout()
            speeds = compute_speeds(self._vel)
            bins = np.linspace(0, speeds.max() * 1.2, 30)
            counts, edges = np.histogram(speeds, bins=bins)
            centres = (edges[:-1] + edges[1:]) / 2
            self._hist_bars.setOpts(x=centres, height=counts, width=(edges[1]-edges[0])*0.9)

    def _update_readout(self) -> None:
        T = compute_temperature(self._vel, DEFAULT_MASS)
        perim = 4 * DEFAULT_BOX
        dt = 0.002 * max(self._steps, 1)
        P = compute_pressure(self._impulse_acc, perim, dt)
        self._readout.setText(f"T = {T:.0f} K\nP = {P:.2e} Pa\nN = {len(self._pos)}")

    def _toggle(self) -> None:
        if self._btn_play.isChecked():
            self._btn_play.setText("Pause")
            self._timer.start()
        else:
            self._btn_play.setText("Play")
            self._timer.stop()

    def get_params(self) -> dict[str, Any]:
        return {"n": self._spin_n.value(), "T": self._spin_T.value()}

    def set_params(self, p: dict[str, Any]) -> None:
        if "n" in p: self._spin_n.setValue(p["n"])
        if "T" in p: self._spin_T.setValue(p["T"])
        self._init_sim()

    def get_data(self) -> dict[str, np.ndarray]:
        return {"speeds": compute_speeds(self._vel)}

    def stop(self) -> None:
        self._timer.stop()
        self._btn_play.setChecked(False)
        self._btn_play.setText("Play")
