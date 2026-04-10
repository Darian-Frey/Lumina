"""AP01 ODE Phase Portrait — UI module."""

from __future__ import annotations

from typing import Any

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QVBoxLayout, QWidget,
)

from lumina.core.plot import SimPlotWidget
from lumina.modules.applied_maths.ap01_phase_portrait.physics import (
    PRESET_SYSTEMS, classify_fixed_point, compute_trajectory,
    compute_vector_field, find_fixed_points,
)

_FP_COLOURS = {
    "stable node": "#2ca02c", "unstable node": "#d62728",
    "saddle": "#ff7f0e", "stable spiral": "#1f77b4",
    "unstable spiral": "#9467bd", "centre": "#17becf", "unknown": "#7f7f7f",
}


class PhasePortraitWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._trajectories: list[pg.PlotDataItem] = []
        self._build_ui()
        self._on_preset_changed()

    def _build_ui(self) -> None:
        main = QHBoxLayout(self)
        main.setContentsMargins(8, 8, 8, 8)

        ctrl_w = QWidget()
        ctrl_w.setFixedWidth(260)
        ctrl = QVBoxLayout(ctrl_w)
        ctrl.setContentsMargins(4, 4, 4, 4)

        # Preset selector
        pg_grp = QGroupBox("System")
        pgl = QVBoxLayout(pg_grp)
        self._combo = QComboBox()
        for name, *_ in PRESET_SYSTEMS:
            self._combo.addItem(name)
        self._combo.currentIndexChanged.connect(self._on_preset_changed)
        pgl.addWidget(self._combo)

        pgl.addWidget(QLabel("dx/dt ="))
        self._edit_f = QLineEdit()
        self._edit_f.setFont(QFont("monospace", 10))
        pgl.addWidget(self._edit_f)

        pgl.addWidget(QLabel("dy/dt ="))
        self._edit_g = QLineEdit()
        self._edit_g.setFont(QFont("monospace", 10))
        pgl.addWidget(self._edit_g)
        ctrl.addWidget(pg_grp)

        # Parameters
        param_grp = QGroupBox("Parameters")
        self._param_layout = QVBoxLayout(param_grp)
        self._param_spins: dict[str, QDoubleSpinBox] = {}
        ctrl.addWidget(param_grp)

        # Range
        rng = QGroupBox("Range")
        rl = QVBoxLayout(rng)
        row = QHBoxLayout()
        row.addWidget(QLabel("x:"))
        self._spin_xmin = QDoubleSpinBox()
        self._spin_xmin.setRange(-50, 50)
        self._spin_xmin.setValue(-3)
        row.addWidget(self._spin_xmin)
        row.addWidget(QLabel("to"))
        self._spin_xmax = QDoubleSpinBox()
        self._spin_xmax.setRange(-50, 50)
        self._spin_xmax.setValue(3)
        row.addWidget(self._spin_xmax)
        rl.addLayout(row)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("y:"))
        self._spin_ymin = QDoubleSpinBox()
        self._spin_ymin.setRange(-50, 50)
        self._spin_ymin.setValue(-3)
        row2.addWidget(self._spin_ymin)
        row2.addWidget(QLabel("to"))
        self._spin_ymax = QDoubleSpinBox()
        self._spin_ymax.setRange(-50, 50)
        self._spin_ymax.setValue(3)
        row2.addWidget(self._spin_ymax)
        rl.addLayout(row2)
        ctrl.addWidget(rng)

        btn = QPushButton("Compute")
        btn.clicked.connect(self._compute)
        ctrl.addWidget(btn)

        btn_clear = QPushButton("Clear Trajectories")
        btn_clear.clicked.connect(self._clear_trajectories)
        ctrl.addWidget(btn_clear)

        self._fp_readout = QLabel()
        self._fp_readout.setFont(QFont("monospace", 9))
        self._fp_readout.setWordWrap(True)
        ctrl.addWidget(self._fp_readout)

        ctrl.addStretch()
        main.addWidget(ctrl_w)

        # Plot
        self._plot = SimPlotWidget(title="Phase Portrait", x_label="x", y_label="y")
        self._plot.plot_item.setAspectLocked(False)
        self._plot.plot_widget.scene().sigMouseClicked.connect(self._on_click)
        main.addWidget(self._plot, 1)

    def _on_preset_changed(self) -> None:
        idx = self._combo.currentIndex()
        name, f_expr, g_expr, params, xr, yr = PRESET_SYSTEMS[idx]
        self._edit_f.setText(f_expr)
        self._edit_g.setText(g_expr)

        # Rebuild param spinboxes
        while self._param_layout.count():
            child = self._param_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                while child.layout().count():
                    sub = child.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()

        self._param_spins.clear()
        for pname, pval in params.items():
            row = QHBoxLayout()
            row.addWidget(QLabel(pname))
            spin = QDoubleSpinBox()
            spin.setRange(-100, 100)
            spin.setValue(pval)
            spin.setDecimals(2)
            spin.setSingleStep(0.1)
            row.addWidget(spin)
            self._param_layout.addLayout(row)
            self._param_spins[pname] = spin

        self._spin_xmin.setValue(xr[0])
        self._spin_xmax.setValue(xr[1])
        self._spin_ymin.setValue(yr[0])
        self._spin_ymax.setValue(yr[1])
        self._compute()

    def _get_state(self) -> tuple[str, str, dict[str, float], tuple[float, float], tuple[float, float]]:
        f_expr = self._edit_f.text()
        g_expr = self._edit_g.text()
        params = {k: s.value() for k, s in self._param_spins.items()}
        xr = (self._spin_xmin.value(), self._spin_xmax.value())
        yr = (self._spin_ymin.value(), self._spin_ymax.value())
        return f_expr, g_expr, params, xr, yr

    def _compute(self) -> None:
        f_expr, g_expr, params, xr, yr = self._get_state()
        self._plot.clear()
        self._trajectories.clear()

        # Vector field
        X, Y, DX, DY = compute_vector_field(f_expr, g_expr, params, xr, yr, 20, 20)
        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                arrow = pg.ArrowItem(
                    pos=(X[i, j] + DX[i, j] * 0.08, Y[i, j] + DY[i, j] * 0.08),
                    angle=float(np.degrees(np.arctan2(DY[i, j], DX[i, j])) - 180),
                    tipAngle=30, headLen=6, tailLen=0, brush="#cccccc", pen="#aaaaaa",
                )
                self._plot.plot_item.addItem(arrow)

        # Fixed points
        fps = find_fixed_points(f_expr, g_expr, params, xr, yr)
        lines = []
        for xf, yf in fps:
            cls = classify_fixed_point(f_expr, g_expr, params, xf, yf)
            colour = _FP_COLOURS.get(cls, "#7f7f7f")
            scatter = pg.ScatterPlotItem(
                [xf], [yf], size=12, brush=pg.mkBrush(colour),
                pen=pg.mkPen("k", width=1),
            )
            self._plot.plot_item.addItem(scatter)
            lines.append(f"({xf:.2f}, {yf:.2f}): {cls}")

        self._fp_readout.setText("Fixed points:\n" + "\n".join(lines) if lines else "No fixed points found")

    def _clear_trajectories(self) -> None:
        for t in self._trajectories:
            self._plot.plot_item.removeItem(t)
        self._trajectories.clear()

    def _on_click(self, event: Any) -> None:
        pos = event.scenePos()
        vb = self._plot.plot_item.vb
        mouse_point = vb.mapSceneToView(pos)
        x0, y0 = mouse_point.x(), mouse_point.y()

        f_expr, g_expr, params, xr, yr = self._get_state()
        if not (xr[0] <= x0 <= xr[1] and yr[0] <= y0 <= yr[1]):
            return

        try:
            t, x, y = compute_trajectory(f_expr, g_expr, params, x0, y0)
            pen = self._plot.next_pen()
            line = self._plot.plot_item.plot(x, y, pen=pen)
            self._trajectories.append(line)
        except Exception:
            pass  # Invalid region

    def get_params(self) -> dict[str, Any]:
        return {
            "preset": self._combo.currentIndex(),
            "f_expr": self._edit_f.text(),
            "g_expr": self._edit_g.text(),
            "params": {k: s.value() for k, s in self._param_spins.items()},
        }

    def set_params(self, p: dict[str, Any]) -> None:
        if "preset" in p:
            self._combo.setCurrentIndex(p["preset"])
        if "f_expr" in p:
            self._edit_f.setText(p["f_expr"])
        if "g_expr" in p:
            self._edit_g.setText(p["g_expr"])
        self._compute()

    def get_data(self) -> dict[str, np.ndarray]:
        return {}

    def stop(self) -> None:
        pass
