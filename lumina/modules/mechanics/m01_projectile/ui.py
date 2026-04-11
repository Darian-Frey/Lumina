"""M01 Projectile Motion — UI module."""

from __future__ import annotations

from typing import Any

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QGroupBox, QHBoxLayout,
    QLabel, QPushButton, QVBoxLayout, QWidget,
)

from lumina.core.config import BTN_STYLE_COMPUTE, BTN_STYLE_RESET
from lumina.core.plot import SimPlotWidget
from lumina.modules.mechanics.m01_projectile.physics import (
    DEFAULT_G, analytic_trajectory, numerical_trajectory, trajectory_metrics,
)


def _spin_row(
    label: str, lo: float, hi: float, val: float, dec: int = 1,
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


class ProjectileWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._t = np.array([])
        self._x = np.array([])
        self._y = np.array([])
        self._build_ui()
        self._setup_tooltips()
        self._compute()

    def _setup_tooltips(self) -> None:
        self._spin_v0.setToolTip("Initial launch speed (m/s)")
        self._spin_theta.setToolTip("Launch angle from horizontal (degrees)")
        self._spin_h0.setToolTip("Initial height above ground (m)")
        self._spin_g.setToolTip("Gravitational acceleration (9.81 m/s² on Earth)")
        self._spin_drag.setToolTip("Drag coefficient (0 = vacuum, increase for air)")
        self._combo_drag.setToolTip("Linear (~v) or quadratic (~v²) drag law")
        self._chk_compare.setToolTip("Show the no-drag trajectory for comparison")
        self._btn_compute.setToolTip("Recompute with current parameters")
        self._btn_reset_view.setToolTip("Auto-range the plot")

    def _build_ui(self) -> None:
        main = QHBoxLayout(self)
        main.setContentsMargins(8, 8, 8, 8)

        ctrl_w = QWidget()
        ctrl_w.setFixedWidth(240)
        ctrl = QVBoxLayout(ctrl_w)
        ctrl.setContentsMargins(4, 4, 4, 4)

        # Launch parameters
        launch = QGroupBox("Launch")
        ll = QVBoxLayout(launch)
        r, self._spin_v0 = _spin_row("Speed v\u2080 (m/s):", 1.0, 200.0, 30.0)
        ll.addLayout(r)
        r, self._spin_theta = _spin_row("Angle \u03b8 (\u00b0):", 0.0, 90.0, 45.0)
        ll.addLayout(r)
        r, self._spin_h0 = _spin_row("Height h\u2080 (m):", 0.0, 100.0, 0.0)
        ll.addLayout(r)
        ctrl.addWidget(launch)

        # Environment
        env = QGroupBox("Environment")
        el = QVBoxLayout(env)
        r, self._spin_g = _spin_row("Gravity g:", 0.1, 30.0, DEFAULT_G, 2)
        el.addLayout(r)
        r, self._spin_drag = _spin_row("Drag coeff k:", 0.0, 1.0, 0.0, 3)
        el.addLayout(r)
        rd = QHBoxLayout()
        lt = QLabel("Drag type:")
        lt.setFixedWidth(110)
        rd.addWidget(lt)
        self._combo_drag = QComboBox()
        self._combo_drag.addItems(["linear", "quadratic"])
        rd.addWidget(self._combo_drag)
        el.addLayout(rd)
        ctrl.addWidget(env)

        # Compare
        cmp_grp = QGroupBox("Display")
        cl = QVBoxLayout(cmp_grp)
        self._chk_compare = QCheckBox("Compare with vacuum")
        self._chk_compare.setChecked(True)
        cl.addWidget(self._chk_compare)
        ctrl.addWidget(cmp_grp)

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
            title="Projectile Trajectory", x_label="x (m)", y_label="y (m)",
        )
        self._plot.plot_item.addLegend(offset=(10, 10))
        self._plot.plot_item.getAxis("left").enableAutoSIPrefix(False)
        self._plot.plot_item.getAxis("bottom").enableAutoSIPrefix(False)
        self._line_traj = self._plot.add_line(name="trajectory", width=3)
        self._line_vacuum = self._plot.plot_item.plot(
            [], [], pen=pg.mkPen("#999999", width=2, style=Qt.PenStyle.DashLine),
            name="vacuum",
        )
        self._dot_apex = self._plot.add_scatter(size=10)
        # Ground line
        self._plot.plot_item.addLine(
            y=0, pen=pg.mkPen("#666666", width=1),
        )
        main.addWidget(self._plot, 1)

    def _compute(self) -> None:
        v0 = self._spin_v0.value()
        theta = self._spin_theta.value()
        h0 = self._spin_h0.value()
        g = self._spin_g.value()
        drag = self._spin_drag.value()
        drag_type = self._combo_drag.currentText()

        # Numerical (with possible drag)
        self._t, self._x, self._y = numerical_trajectory(
            v0, theta, g=g, h0=h0, drag=drag, drag_type=drag_type,
        )
        self._line_traj.setData(self._x, self._y)

        # Apex marker
        if len(self._y) > 0:
            apex_idx = int(np.argmax(self._y))
            self._dot_apex.setData([self._x[apex_idx]], [self._y[apex_idx]])
        else:
            self._dot_apex.setData([], [])

        # Vacuum comparison
        if self._chk_compare.isChecked():
            _, x_vac, y_vac = analytic_trajectory(v0, theta, g=g, h0=h0)
            self._line_vacuum.setData(x_vac, y_vac)
        else:
            self._line_vacuum.setData([], [])

        # Metrics
        m = trajectory_metrics(self._t, self._x, self._y)
        self._readout.setText(
            f"Range: {m['range']:.2f} m\n"
            f"Max height: {m['max_height']:.2f} m\n"
            f"Time of flight: {m['time_of_flight']:.2f} s"
        )

        # Lock view to data
        if len(self._x) > 0:
            x_max = float(max(self._x.max(), 1.0))
            y_max = float(max(self._y.max(), 1.0))
            self._plot.plot_item.setLimits(
                xMin=-x_max * 0.1, xMax=x_max * 1.5,
                yMin=-y_max * 0.2, yMax=y_max * 1.5,
            )
            self._plot.plot_item.setXRange(-x_max * 0.05, x_max * 1.1)
            self._plot.plot_item.setYRange(-y_max * 0.1, y_max * 1.2)

    def _reset_view(self) -> None:
        self._plot.plot_item.autoRange()

    def get_params(self) -> dict[str, Any]:
        return {
            "v0": self._spin_v0.value(),
            "theta": self._spin_theta.value(),
            "h0": self._spin_h0.value(),
            "g": self._spin_g.value(),
            "drag": self._spin_drag.value(),
            "drag_type": self._combo_drag.currentText(),
            "compare": self._chk_compare.isChecked(),
        }

    def set_params(self, p: dict[str, Any]) -> None:
        for k, s in [
            ("v0", self._spin_v0), ("theta", self._spin_theta),
            ("h0", self._spin_h0), ("g", self._spin_g),
            ("drag", self._spin_drag),
        ]:
            if k in p:
                s.setValue(p[k])
        if "drag_type" in p:
            idx = self._combo_drag.findText(p["drag_type"])
            if idx >= 0:
                self._combo_drag.setCurrentIndex(idx)
        if "compare" in p:
            self._chk_compare.setChecked(p["compare"])
        self._compute()

    def get_data(self) -> dict[str, np.ndarray]:
        return {"t": self._t, "x": self._x, "y": self._y}

    def stop(self) -> None:
        pass
