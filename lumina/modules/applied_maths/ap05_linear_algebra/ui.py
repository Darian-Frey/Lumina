"""AP05 Linear Algebra Visualiser — UI module."""

from __future__ import annotations

from typing import Any

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QVBoxLayout, QWidget,
)

from lumina.core.config import BTN_STYLE_COMPUTE, BTN_STYLE_RESET
from lumina.core.plot import SimPlotWidget
from lumina.modules.applied_maths.ap05_linear_algebra.physics import (
    PRESET_MATRICES, determinant, eigenvectors_2x2, transform_points,
    unit_circle, unit_grid, unit_square,
)


class LinearAlgebraWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._setup_tooltips()
        self._on_preset_changed()

    def _setup_tooltips(self) -> None:
        self._combo.setToolTip("Choose a preset 2x2 matrix")
        for spin in (self._spin_a, self._spin_b, self._spin_c, self._spin_d):
            spin.setToolTip("Matrix entry")
        self._btn_compute.setToolTip("Apply the matrix and recompute")
        self._btn_reset_view.setToolTip("Reset to identity matrix and default view")

    def _build_ui(self) -> None:
        main = QHBoxLayout(self)
        main.setContentsMargins(8, 8, 8, 8)

        ctrl_w = QWidget()
        ctrl_w.setFixedWidth(240)
        ctrl = QVBoxLayout(ctrl_w)
        ctrl.setContentsMargins(4, 4, 4, 4)

        # Preset selector
        preset_grp = QGroupBox("Preset")
        pl = QVBoxLayout(preset_grp)
        self._combo = QComboBox()
        for name in PRESET_MATRICES:
            self._combo.addItem(name)
        self._combo.setCurrentText("Shear x")
        self._combo.currentTextChanged.connect(self._on_preset_changed)
        pl.addWidget(self._combo)
        ctrl.addWidget(preset_grp)

        # Matrix entries
        mat_grp = QGroupBox("Matrix M")
        ml = QVBoxLayout(mat_grp)

        row1 = QHBoxLayout()
        self._spin_a = QDoubleSpinBox()
        self._spin_a.setRange(-10, 10)
        self._spin_a.setValue(1)
        self._spin_a.setDecimals(2)
        self._spin_a.setSingleStep(0.1)
        self._spin_a.setFixedWidth(75)
        row1.addWidget(self._spin_a)
        self._spin_b = QDoubleSpinBox()
        self._spin_b.setRange(-10, 10)
        self._spin_b.setValue(1)
        self._spin_b.setDecimals(2)
        self._spin_b.setSingleStep(0.1)
        self._spin_b.setFixedWidth(75)
        row1.addWidget(self._spin_b)
        ml.addLayout(row1)

        row2 = QHBoxLayout()
        self._spin_c = QDoubleSpinBox()
        self._spin_c.setRange(-10, 10)
        self._spin_c.setValue(0)
        self._spin_c.setDecimals(2)
        self._spin_c.setSingleStep(0.1)
        self._spin_c.setFixedWidth(75)
        row2.addWidget(self._spin_c)
        self._spin_d = QDoubleSpinBox()
        self._spin_d.setRange(-10, 10)
        self._spin_d.setValue(1)
        self._spin_d.setDecimals(2)
        self._spin_d.setSingleStep(0.1)
        self._spin_d.setFixedWidth(75)
        row2.addWidget(self._spin_d)
        ml.addLayout(row2)
        ctrl.addWidget(mat_grp)

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

        # Plot
        self._plot = SimPlotWidget(
            title="Linear Transformation", x_label="x", y_label="y",
        )
        self._plot.plot_item.setAspectLocked(True)
        self._plot.plot_item.addLegend(offset=(10, 10))
        self._plot.plot_item.getAxis("left").enableAutoSIPrefix(False)
        self._plot.plot_item.getAxis("bottom").enableAutoSIPrefix(False)
        # Background grid (transformed)
        self._line_grid_h = self._plot.plot_item.plot(
            [], [], pen=pg.mkPen("#cccccc", width=1), connect="pairs",
        )
        self._line_grid_v = self._plot.plot_item.plot(
            [], [], pen=pg.mkPen("#cccccc", width=1), connect="pairs",
        )
        # Original square
        self._line_orig_sq = self._plot.plot_item.plot(
            [], [], pen=pg.mkPen("#aaaaaa", width=2, style=Qt.PenStyle.DashLine),
            name="original",
        )
        # Transformed square
        self._line_xform_sq = self._plot.plot_item.plot(
            [], [], pen=pg.mkPen("#1f77b4", width=3),
            name="transformed square",
        )
        # Original unit circle
        self._line_orig_circle = self._plot.plot_item.plot(
            [], [], pen=pg.mkPen("#aaaaaa", width=1, style=Qt.PenStyle.DashLine),
        )
        # Transformed unit circle (becomes ellipse)
        self._line_xform_circle = self._plot.plot_item.plot(
            [], [], pen=pg.mkPen("#2ca02c", width=2),
            name="transformed circle",
        )
        # Eigenvectors (axes)
        self._line_eigvec1 = self._plot.plot_item.plot(
            [], [], pen=pg.mkPen("#d62728", width=3),
            name="eigenvector 1",
        )
        self._line_eigvec2 = self._plot.plot_item.plot(
            [], [], pen=pg.mkPen("#ff7f0e", width=3),
            name="eigenvector 2",
        )

        self._plot.plot_item.setLimits(xMin=-8, xMax=8, yMin=-8, yMax=8)
        self._plot.plot_item.setXRange(-4, 4)
        self._plot.plot_item.setYRange(-4, 4)

        main.addWidget(self._plot, 1)

    def _on_preset_changed(self) -> None:
        name = self._combo.currentText()
        M = PRESET_MATRICES[name]
        # Block signals while updating spinboxes
        for spin in (self._spin_a, self._spin_b, self._spin_c, self._spin_d):
            spin.blockSignals(True)
        self._spin_a.setValue(M[0, 0])
        self._spin_b.setValue(M[0, 1])
        self._spin_c.setValue(M[1, 0])
        self._spin_d.setValue(M[1, 1])
        for spin in (self._spin_a, self._spin_b, self._spin_c, self._spin_d):
            spin.blockSignals(False)
        self._compute()

    def _compute(self) -> None:
        M = np.array([
            [self._spin_a.value(), self._spin_b.value()],
            [self._spin_c.value(), self._spin_d.value()],
        ])

        # Original shapes
        sq = unit_square()
        circle = unit_circle()
        self._line_orig_sq.setData(sq[0], sq[1])
        self._line_orig_circle.setData(circle[0], circle[1])

        # Transformed shapes
        sq_xform = transform_points(sq, M)
        circle_xform = transform_points(circle, M)
        self._line_xform_sq.setData(sq_xform[0], sq_xform[1])
        self._line_xform_circle.setData(circle_xform[0], circle_xform[1])

        # Transformed grid
        n = 9
        grid_x = []
        grid_y = []
        for i in range(n):
            t = -2 + 4 * i / (n - 1)
            # Vertical line at x = t
            p1 = M @ np.array([t, -2])
            p2 = M @ np.array([t, 2])
            grid_x.extend([p1[0], p2[0]])
            grid_y.extend([p1[1], p2[1]])
            # Horizontal line at y = t
            p3 = M @ np.array([-2, t])
            p4 = M @ np.array([2, t])
            grid_x.extend([p3[0], p4[0]])
            grid_y.extend([p3[1], p4[1]])
        self._line_grid_h.setData(np.array(grid_x), np.array(grid_y))
        self._line_grid_v.setData([], [])

        # Eigenvectors
        eigvals, eigvecs = eigenvectors_2x2(M)
        # Only show real eigenvectors
        if np.all(np.abs(eigvals.imag) < 1e-10):
            v1 = eigvecs[:, 0].real
            v2 = eigvecs[:, 1].real
            # Scale by eigenvalue (or +1/-1 if zero)
            l1 = float(eigvals[0].real)
            l2 = float(eigvals[1].real)
            scale1 = max(abs(l1), 0.5) * np.sign(l1) if l1 != 0 else 1
            scale2 = max(abs(l2), 0.5) * np.sign(l2) if l2 != 0 else 1
            self._line_eigvec1.setData(
                [-v1[0] * abs(scale1) * 2, v1[0] * abs(scale1) * 2],
                [-v1[1] * abs(scale1) * 2, v1[1] * abs(scale1) * 2],
            )
            self._line_eigvec2.setData(
                [-v2[0] * abs(scale2) * 2, v2[0] * abs(scale2) * 2],
                [-v2[1] * abs(scale2) * 2, v2[1] * abs(scale2) * 2],
            )
        else:
            self._line_eigvec1.setData([], [])
            self._line_eigvec2.setData([], [])

        # Readout
        det = determinant(M)
        if np.all(np.abs(eigvals.imag) < 1e-10):
            eig_str = f"\u03bb\u2081 = {eigvals[0].real:+.3f}\n\u03bb\u2082 = {eigvals[1].real:+.3f}"
        else:
            eig_str = (
                f"\u03bb\u2081 = {eigvals[0].real:+.2f}{eigvals[0].imag:+.2f}i\n"
                f"\u03bb\u2082 = {eigvals[1].real:+.2f}{eigvals[1].imag:+.2f}i"
            )
        self._readout.setText(
            f"det(M) = {det:+.3f}\n"
            f"trace = {M[0,0] + M[1,1]:+.3f}\n\n"
            f"{eig_str}"
        )
        self._M = M

    def _reset_view(self) -> None:
        self._combo.setCurrentText("Identity")
        self._plot.plot_item.setXRange(-4, 4)
        self._plot.plot_item.setYRange(-4, 4)

    def get_params(self) -> dict[str, Any]:
        return {
            "preset": self._combo.currentText(),
            "a": self._spin_a.value(), "b": self._spin_b.value(),
            "c": self._spin_c.value(), "d": self._spin_d.value(),
        }

    def set_params(self, p: dict[str, Any]) -> None:
        if "preset" in p:
            idx = self._combo.findText(p["preset"])
            if idx >= 0:
                self._combo.setCurrentIndex(idx)
        for k, s in [
            ("a", self._spin_a), ("b", self._spin_b),
            ("c", self._spin_c), ("d", self._spin_d),
        ]:
            if k in p:
                s.setValue(p[k])
        self._compute()

    def get_data(self) -> dict[str, np.ndarray]:
        return {"M": self._M}

    def stop(self) -> None:
        pass
