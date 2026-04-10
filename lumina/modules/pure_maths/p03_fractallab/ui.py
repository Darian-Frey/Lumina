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
from lumina.core.config import BTN_STYLE_COMPUTE, BTN_STYLE_RESET
from lumina.core.plot import SimPlotWidget
from lumina.modules.pure_maths.p03_fractallab.physics import (
    DEFAULT_MAX_ITER, burning_ship, colour_map, julia_set,
    mandelbrot_set, multibrot, newton_fractal, tricorn,
)

# Default view bounds per fractal type
_DEFAULT_BOUNDS: dict[str, tuple[float, float, float, float]] = {
    "Mandelbrot": (-2.0, 1.0, -1.5, 1.5),
    "Julia": (-2.0, 2.0, -1.5, 1.5),
    "Burning Ship": (-2.5, 1.5, -2.0, 1.0),
    "Tricorn": (-2.5, 1.5, -2.0, 2.0),
    "Multibrot": (-2.0, 2.0, -2.0, 2.0),
    "Newton": (-2.0, 2.0, -2.0, 2.0),
}

class FractalLabWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._setup_tooltips()
        self._compute_default()

    def _setup_tooltips(self) -> None:
        self._combo.setToolTip("Choose the fractal type to render")
        self._spin_cr.setToolTip("Real part of c for Julia sets")
        self._spin_ci.setToolTip("Imaginary part of c for Julia sets")
        self._spin_power.setToolTip("Exponent N for the Multibrot set z^N + c")
        self._spin_iter.setToolTip("Maximum iterations — higher reveals more detail")
        self._btn_compute.setToolTip("Recompute at the current zoom level")
        self._btn_reset.setToolTip("Return to the default view for this fractal type")

    def _build_ui(self) -> None:
        main = QHBoxLayout(self)
        main.setContentsMargins(8, 8, 8, 8)
        ctrl_w = QWidget()
        ctrl_w.setFixedWidth(240)
        ctrl = QVBoxLayout(ctrl_w)
        ctrl.setContentsMargins(4, 4, 4, 4)

        fg = QGroupBox("Fractal Type")
        fl = QVBoxLayout(fg)
        self._combo = QComboBox()
        self._combo.addItems([
            "Mandelbrot", "Julia", "Burning Ship", "Tricorn", "Multibrot", "Newton",
        ])
        self._combo.currentIndexChanged.connect(self._on_type_changed)
        fl.addWidget(self._combo)
        ctrl.addWidget(fg)

        # Multibrot power
        mg = QGroupBox("Multibrot Power")
        ml = QVBoxLayout(mg)
        r = QHBoxLayout()
        r.addWidget(QLabel("N:"))
        self._spin_power = QSpinBox()
        self._spin_power.setRange(2, 12)
        self._spin_power.setValue(3)
        r.addWidget(self._spin_power)
        ml.addLayout(r)
        ctrl.addWidget(mg)
        self._power_group = mg
        self._power_group.setVisible(False)

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
        self._btn_compute.setStyleSheet(BTN_STYLE_COMPUTE)
        self._btn_compute.clicked.connect(self._compute)
        ctrl.addWidget(self._btn_compute)

        self._btn_reset = QPushButton("Reset View")
        self._btn_reset.setStyleSheet(BTN_STYLE_RESET)
        self._btn_reset.clicked.connect(self._reset_zoom)
        ctrl.addWidget(self._btn_reset)

        self._readout = QLabel()
        self._readout.setFont(QFont("monospace", 9))
        self._readout.setWordWrap(True)
        ctrl.addWidget(self._readout)

        hint = QLabel("Zoom in with scroll wheel,\nthen press Compute to refine.\nReset View to return to default.")
        hint.setFont(QFont("sans-serif", 8))
        hint.setStyleSheet("color: #888888;")
        hint.setWordWrap(True)
        ctrl.addWidget(hint)

        eq = QGroupBox("Iteration")
        eql = QVBoxLayout(eq)
        self._eq_label = QLabel("z\u2099\u208A\u2081 = z\u2099\u00b2 + c\nescape: |z| > 2")
        eql.addWidget(self._eq_label)
        ctrl.addWidget(eq)
        ctrl.addStretch()
        main.addWidget(ctrl_w)

        # Image display
        self._plot = SimPlotWidget(title="Fractal")
        self._plot.plot_item.setAspectLocked(True)
        self._img = pg.ImageItem()
        self._plot.plot_item.addItem(self._img)
        # Zoom limits — fractal is bounded in the complex plane
        self._plot.plot_item.setLimits(xMin=-3, xMax=3, yMin=-3, yMax=3)
        main.addWidget(self._plot, 1)

    def _get_visible_bounds(self) -> tuple[float, float, float, float]:
        """Read the current visible range from the plot viewbox."""
        vb = self._plot.plot_item.vb
        xr, yr = vb.viewRange()
        return xr[0], xr[1], yr[0], yr[1]

    def _on_type_changed(self) -> None:
        """Handle fractal type change — show/hide relevant controls, reset view."""
        ftype = self._combo.currentText()
        self._power_group.setVisible(ftype == "Multibrot")

        # Update equation display
        equations = {
            "Mandelbrot": "z\u2099\u208A\u2081 = z\u2099\u00b2 + c\nescape: |z| > 2",
            "Julia": "z\u2099\u208A\u2081 = z\u2099\u00b2 + c\nc fixed, z\u2080 varies",
            "Burning Ship": "z = (|Re(z)| + i|Im(z)|)\u00b2 + c",
            "Tricorn": "z\u2099\u208A\u2081 = conj(z\u2099)\u00b2 + c",
            "Multibrot": f"z\u2099\u208A\u2081 = z\u2099^N + c  (N={self._spin_power.value()})",
            "Newton": "Newton's method: z\u00b3 \u2212 1 = 0\nz \u2192 z \u2212 f(z)/f'(z)",
        }
        self._eq_label.setText(equations.get(ftype, ""))

        # Reset to default bounds for this fractal type
        self._reset_zoom()

    def _compute(self) -> None:
        """Recompute the fractal at the current visible zoom level."""
        xmin, xmax, ymin, ymax = self._get_visible_bounds()

        # Clamp to valid range
        xmin = max(xmin, -3.0)
        xmax = min(xmax, 3.0)
        ymin = max(ymin, -3.0)
        ymax = min(ymax, 3.0)
        if xmax <= xmin or ymax <= ymin:
            b = _DEFAULT_BOUNDS.get(self._combo.currentText(), (-2, 1, -1.5, 1.5))
            xmin, xmax, ymin, ymax = b

        max_iter = self._spin_iter.value()
        width, height = 800, 800
        ftype = self._combo.currentText()

        if ftype == "Mandelbrot":
            iters = mandelbrot_set(xmin, xmax, ymin, ymax, width, height, max_iter)
        elif ftype == "Julia":
            iters = julia_set(xmin, xmax, ymin, ymax, width, height,
                              self._spin_cr.value(), self._spin_ci.value(), max_iter)
        elif ftype == "Burning Ship":
            iters = burning_ship(xmin, xmax, ymin, ymax, width, height, max_iter)
        elif ftype == "Tricorn":
            iters = tricorn(xmin, xmax, ymin, ymax, width, height, max_iter)
        elif ftype == "Multibrot":
            iters = multibrot(xmin, xmax, ymin, ymax, width, height,
                              power=self._spin_power.value(), max_iter=max_iter)
        elif ftype == "Newton":
            iters = newton_fractal(xmin, xmax, ymin, ymax, width, height, max_iter)
        else:
            iters = mandelbrot_set(xmin, xmax, ymin, ymax, width, height, max_iter)

        rgb = colour_map(iters, max_iter)
        self._img.setImage(rgb.transpose(1, 0, 2))
        self._img.setRect(xmin, ymin, xmax - xmin, ymax - ymin)

        self._readout.setText(
            f"x: [{xmin:.6f}, {xmax:.6f}]\n"
            f"y: [{ymin:.6f}, {ymax:.6f}]\n"
            f"iter: {max_iter}  |  {width}x{height}px"
        )

    def _compute_default(self) -> None:
        """Compute at the default view — used on first load."""
        b = _DEFAULT_BOUNDS["Mandelbrot"]
        self._plot.plot_item.setXRange(b[0], b[1], padding=0.05)
        self._plot.plot_item.setYRange(b[2], b[3], padding=0.05)
        self._compute()

    def _reset_zoom(self) -> None:
        """Reset to default view for the current fractal type and recompute."""
        ftype = self._combo.currentText()
        b = _DEFAULT_BOUNDS.get(ftype, (-2, 1, -1.5, 1.5))
        self._plot.plot_item.setXRange(b[0], b[1], padding=0.05)
        self._plot.plot_item.setYRange(b[2], b[3], padding=0.05)
        self._compute()

    def get_params(self) -> dict[str, Any]:
        return {
            "type": self._combo.currentText(),
            "cr": self._spin_cr.value(), "ci": self._spin_ci.value(),
            "max_iter": self._spin_iter.value(),
            "power": self._spin_power.value(),
        }

    def set_params(self, p: dict[str, Any]) -> None:
        if "type" in p:
            idx = self._combo.findText(p["type"])
            if idx >= 0: self._combo.setCurrentIndex(idx)
        if "cr" in p: self._spin_cr.setValue(p["cr"])
        if "ci" in p: self._spin_ci.setValue(p["ci"])
        if "max_iter" in p: self._spin_iter.setValue(p["max_iter"])
        if "power" in p: self._spin_power.setValue(p["power"])
        self._compute()

    def get_data(self) -> dict[str, Any]:
        return {"bounds": self._get_visible_bounds()}

    def stop(self) -> None:
        pass
