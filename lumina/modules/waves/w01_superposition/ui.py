"""W01 Wave Superposition — UI module."""

from __future__ import annotations

from typing import Any

import numpy as np
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDoubleSpinBox, QGroupBox, QHBoxLayout, QLabel, QPushButton,
    QSplitter, QVBoxLayout, QWidget,
)

from lumina.core.config import DEFAULT_TIMER_MS
from lumina.core.plot import SimPlotWidget
from lumina.modules.waves.w01_superposition.physics import (
    DEFAULT_N_POINTS, DEFAULT_X_MAX, beat_frequency,
    frequency_to_omega, sine_wave, superposition, wavelength_to_k,
)

MAX_WAVES = 5


class WaveControl(QGroupBox):
    def __init__(self, idx: int, parent: QWidget | None = None) -> None:
        super().__init__(f"Wave {idx + 1}", parent)
        self.setCheckable(True)
        self.setChecked(idx == 0)
        lay = QVBoxLayout(self)

        def row(lbl: str, lo: float, hi: float, val: float) -> QDoubleSpinBox:
            r = QHBoxLayout()
            l = QLabel(lbl)
            l.setFixedWidth(45)
            r.addWidget(l)
            s = QDoubleSpinBox()
            s.setRange(lo, hi)
            s.setValue(val)
            s.setDecimals(2)
            s.setSingleStep(0.1)
            s.setFixedWidth(70)
            r.addWidget(s)
            lay.addLayout(r)
            return s

        self.spin_A = row("A", 0.0, 5.0, 1.0 if idx == 0 else 0.0)
        self.spin_freq = row("f (Hz)", 0.1, 20.0, 1.0 + idx * 0.1)
        self.spin_phase = row("\u03c6", -3.14, 3.14, 0.0)


class WaveSuperpositionWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._t: float = 0.0
        self._x = np.linspace(0, DEFAULT_X_MAX, DEFAULT_N_POINTS)
        self._build_ui()
        self._update_plots()

    def _build_ui(self) -> None:
        main = QHBoxLayout(self)
        main.setContentsMargins(8, 8, 8, 8)
        ctrl_w = QWidget()
        ctrl_w.setFixedWidth(220)
        ctrl = QVBoxLayout(ctrl_w)
        ctrl.setContentsMargins(4, 4, 4, 4)

        self._wcs: list[WaveControl] = []
        for i in range(MAX_WAVES):
            wc = WaveControl(i)
            self._wcs.append(wc)
            ctrl.addWidget(wc)

        presets = QGroupBox("Presets")
        pl = QVBoxLayout(presets)
        b1 = QPushButton("Beats")
        b1.clicked.connect(self._preset_beats)
        pl.addWidget(b1)
        b2 = QPushButton("Standing Wave")
        b2.clicked.connect(self._preset_standing)
        pl.addWidget(b2)
        ctrl.addWidget(presets)

        btn_row = QHBoxLayout()
        self._btn_play = QPushButton("Play")
        self._btn_play.setCheckable(True)
        self._btn_play.clicked.connect(self._toggle)
        btn_row.addWidget(self._btn_play)
        ctrl.addLayout(btn_row)

        self._readout = QLabel()
        self._readout.setFont(QFont("monospace", 9))
        ctrl.addWidget(self._readout)
        ctrl.addStretch()
        main.addWidget(ctrl_w)

        sp = QSplitter(Qt.Orientation.Vertical)
        self._plot_ind = SimPlotWidget(title="Individual Waves", x_label="x", y_label="y")
        self._lines_ind = [self._plot_ind.add_line() for _ in range(MAX_WAVES)]
        sp.addWidget(self._plot_ind)

        self._plot_sum = SimPlotWidget(title="Superposition", x_label="x", y_label="y")
        self._line_sum = self._plot_sum.add_line(width=2)
        sp.addWidget(self._plot_sum)
        main.addWidget(sp, 1)

        self._timer = QTimer()
        self._timer.setInterval(DEFAULT_TIMER_MS)
        self._timer.timeout.connect(self._advance)

    def _get_waves(self) -> list[tuple[float, float, float, float]]:
        waves = []
        for wc in self._wcs:
            if wc.isChecked() and wc.spin_A.value() > 0:
                f = wc.spin_freq.value()
                waves.append((
                    wc.spin_A.value(), wavelength_to_k(1.0 / f) if f > 0 else 0.0,
                    frequency_to_omega(f), wc.spin_phase.value(),
                ))
        return waves

    def _update_plots(self) -> None:
        waves = self._get_waves()
        for i, line in enumerate(self._lines_ind):
            if i < len(waves):
                A, k, w, phi = waves[i]
                line.setData(self._x, sine_wave(self._x, self._t, A, k, w, phi))
            else:
                line.setData([], [])
        self._line_sum.setData(self._x, superposition(self._x, self._t, waves))
        freqs = [wc.spin_freq.value() for wc in self._wcs
                 if wc.isChecked() and wc.spin_A.value() > 0]
        info = f"t={self._t:.2f}s | {len(waves)} waves"
        if len(freqs) == 2:
            info += f" | beat={beat_frequency(freqs[0], freqs[1]):.2f}Hz"
        self._readout.setText(info)

    def _advance(self) -> None:
        self._t += DEFAULT_TIMER_MS / 1000.0
        self._update_plots()

    def _toggle(self) -> None:
        if self._btn_play.isChecked():
            self._btn_play.setText("Pause")
            self._timer.start()
        else:
            self._btn_play.setText("Play")
            self._timer.stop()

    def _preset_beats(self) -> None:
        for wc in self._wcs:
            wc.setChecked(False)
        self._wcs[0].setChecked(True)
        self._wcs[0].spin_A.setValue(1.0)
        self._wcs[0].spin_freq.setValue(5.0)
        self._wcs[0].spin_phase.setValue(0.0)
        self._wcs[1].setChecked(True)
        self._wcs[1].spin_A.setValue(1.0)
        self._wcs[1].spin_freq.setValue(5.5)
        self._wcs[1].spin_phase.setValue(0.0)
        self._update_plots()

    def _preset_standing(self) -> None:
        for wc in self._wcs:
            wc.setChecked(False)
        self._wcs[0].setChecked(True)
        self._wcs[0].spin_A.setValue(1.0)
        self._wcs[0].spin_freq.setValue(2.0)
        self._wcs[0].spin_phase.setValue(0.0)
        self._wcs[1].setChecked(True)
        self._wcs[1].spin_A.setValue(1.0)
        self._wcs[1].spin_freq.setValue(2.0)
        self._wcs[1].spin_phase.setValue(np.pi)
        self._update_plots()

    def get_params(self) -> dict[str, Any]:
        return {"waves": [
            {"A": w.spin_A.value(), "freq": w.spin_freq.value(),
             "phase": w.spin_phase.value(), "on": w.isChecked()}
            for w in self._wcs
        ]}

    def set_params(self, p: dict[str, Any]) -> None:
        for i, w in enumerate(p.get("waves", [])):
            if i < MAX_WAVES:
                self._wcs[i].setChecked(w.get("on", False))
                self._wcs[i].spin_A.setValue(w.get("A", 0.0))
                self._wcs[i].spin_freq.setValue(w.get("freq", 1.0))
                self._wcs[i].spin_phase.setValue(w.get("phase", 0.0))
        self._update_plots()

    def get_data(self) -> dict[str, np.ndarray]:
        waves = self._get_waves()
        return {"x": self._x, "y_sum": superposition(self._x, self._t, waves)}

    def stop(self) -> None:
        self._timer.stop()
        self._btn_play.setChecked(False)
        self._btn_play.setText("Play")
