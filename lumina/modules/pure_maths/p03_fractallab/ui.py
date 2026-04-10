"""P03 FractalLab — UI module."""
from __future__ import annotations
from typing import Any
import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QVBoxLayout, QWidget,
)
from lumina.core.plot import SimPlotWidget
from lumina.modules.pure_maths.p03_fractallab.physics import (
    DEFAULT_MAX_ITER, colour_map, julia_set, mandelbrot_set,
)

class FractalLabWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._zoom_stack: list[tuple[float, float, float, float]] = []
        self._build_ui()
        self._compute()

    def _build_ui(self) -> None:
        main = QHBoxLayout(self)
        main.setContentsMargins(8, 8, 8, 8)
        ctrl_w = QWidget()
        ctrl_w.setFixedWidth(220)
        ctrl = QVBoxLayout(ctrl_w)
        ctrl.setContentsMargins(4, 4, 4, 4)

        fg = QGroupBox("Fractal Type")
        fl = QVBoxLayout(fg)
        self._combo = QComboBox()
        self._combo.addItems(["Mandelbrot", "Julia"])
        self._combo.currentIndexChanged.connect(self._compute)
        fl.addWidget(self._combo)
        ctrl.addWidget(fg)

        jg = QGroupBox("Julia c")
        jl = QVBoxLayout(jg)
        r = QHBoxLayout()
        r.addWidget(QLabel("Re:"))
        self._spin_cr = QDoubleSpinBox()
        self._spin_cr.setRange(-2, 2)
        self._spin_cr.setValue(-0.7)
        self._spin_cr.setDecimals(4)
        self._spin_cr.setSingleStep(0.01)
        r.addWidget(self._spin_cr)
        jl.addLayout(r)
        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Im:"))
        self._spin_ci = QDoubleSpinBox()
        self._spin_ci.setRange(-2, 2)
        self._spin_ci.setValue(0.27015)
        self._spin_ci.setDecimals(4)
        self._spin_ci.setSingleStep(0.01)
        r2.addWidget(self._spin_ci)
        jl.addLayout(r2)
        ctrl.addWidget(jg)

        ig = QGroupBox("Resolution")
        il = QVBoxLayout(ig)
        r3 = QHBoxLayout()
        r3.addWidget(QLabel("max iter"))
        self._spin_iter = QSpinBox()
        self._spin_iter.setRange(32, 2000)
        self._spin_iter.setValue(DEFAULT_MAX_ITER)
        self._spin_iter.setSingleStep(32)
        r3.addWidget(self._spin_iter)
        il.addLayout(r3)
        ctrl.addWidget(ig)

        self._btn_compute = QPushButton("Compute")
        self._btn_compute.clicked.connect(self._compute)
        ctrl.addWidget(self._btn_compute)

        self._btn_reset = QPushButton("Reset Zoom")
        self._btn_reset.clicked.connect(self._reset_zoom)
        ctrl.addWidget(self._btn_reset)

        self._readout = QLabel()
        self._readout.setFont(QFont("monospace", 9))
        self._readout.setWordWrap(True)
        ctrl.addWidget(self._readout)

        eq = QGroupBox("Iteration")
        eql = QVBoxLayout(eq)
        eql.addWidget(QLabel("z\u2099\u208A\u2081 = z\u2099\u00b2 + c\nescape: |z| > 2"))
        ctrl.addWidget(eq)
        ctrl.addStretch()
        main.addWidget(ctrl_w)

        # Image display
        self._plot = SimPlotWidget(title="Fractal")
        self._plot.plot_item.setAspectLocked(True)
        self._img = pg.ImageItem()
        self._plot.plot_item.addItem(self._img)
        main.addWidget(self._plot, 1)

    def _get_bounds(self) -> tuple[float, float, float, float]:
        if self._zoom_stack:
            return self._zoom_stack[-1]
        return (-2.0, 1.0, -1.5, 1.5)

    def _compute(self) -> None:
        xmin, xmax, ymin, ymax = self._get_bounds()
        max_iter = self._spin_iter.value()
        width, height = 600, 600

        if self._combo.currentText() == "Mandelbrot":
            iters = mandelbrot_set(xmin, xmax, ymin, ymax, width, height, max_iter)
        else:
            iters = julia_set(xmin, xmax, ymin, ymax, width, height,
                              self._spin_cr.value(), self._spin_ci.value(), max_iter)

        rgb = colour_map(iters, max_iter)
        self._img.setImage(rgb.transpose(1, 0, 2))
        self._img.setRect(xmin, ymin, xmax - xmin, ymax - ymin)
        self._plot.plot_item.setXRange(xmin, xmax)
        self._plot.plot_item.setYRange(ymin, ymax)

        self._readout.setText(
            f"x: [{xmin:.4f}, {xmax:.4f}]\n"
            f"y: [{ymin:.4f}, {ymax:.4f}]\n"
            f"iter: {max_iter}"
        )

    def _reset_zoom(self) -> None:
        self._zoom_stack.clear()
        self._compute()

    def get_params(self) -> dict[str, Any]:
        return {
            "type": self._combo.currentText(),
            "cr": self._spin_cr.value(), "ci": self._spin_ci.value(),
            "max_iter": self._spin_iter.value(),
        }

    def set_params(self, p: dict[str, Any]) -> None:
        if "type" in p:
            idx = self._combo.findText(p["type"])
            if idx >= 0: self._combo.setCurrentIndex(idx)
        if "cr" in p: self._spin_cr.setValue(p["cr"])
        if "ci" in p: self._spin_ci.setValue(p["ci"])
        if "max_iter" in p: self._spin_iter.setValue(p["max_iter"])
        self._compute()

    def get_data(self) -> dict[str, Any]:
        return {"bounds": self._get_bounds()}

    def stop(self) -> None:
        pass
