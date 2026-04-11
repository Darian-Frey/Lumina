"""AP01 ODE Phase Portrait — UI module."""

from __future__ import annotations

from typing import Any

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QVBoxLayout, QWidget,
)

from lumina.core.config import BTN_STYLE_COMPUTE, BTN_STYLE_RESET, current_mid_colour
from lumina.core.plot import SimPlotWidget
from lumina.modules.applied_maths.ap01_phase_portrait.physics import (
    PRESET_SYSTEMS, classify_fixed_point, compute_streamlines,
    compute_trajectory, compute_vector_field, find_fixed_points,
)

_FP_COLOURS = {
    "stable node": "#2ca02c", "unstable node": "#d62728",
    "saddle": "#ff7f0e", "stable spiral": "#1f77b4",
    "unstable spiral": "#9467bd", "centre": "#17becf", "unknown": "#7f7f7f",
}

_FP_SYMBOLS = {
    "stable node": "o", "unstable node": "o",
    "saddle": "d", "stable spiral": "o",
    "unstable spiral": "o", "centre": "s", "unknown": "t",
}

# Maximum zoom-out factor relative to the preset's default range
_MAX_ZOOM_FACTOR: float = 5.0


class PhasePortraitWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._trajectories: list[pg.PlotDataItem] = []
        self._field_items: list[Any] = []
        self._stream_items: list[pg.PlotDataItem] = []
        self._fp_items: list[Any] = []
        self._warning_item: pg.TextItem | None = None
        # Store the preset's default range for zoom limiting
        self._default_xr: tuple[float, float] = (-3, 3)
        self._default_yr: tuple[float, float] = (-3, 3)
        self._build_ui()
        self._setup_tooltips()
        self._on_preset_changed()

    def _setup_tooltips(self) -> None:
        self._combo.setToolTip("Choose a preset ODE system or edit the equations below")
        self._edit_f.setToolTip("Expression for dx/dt — use x, y, and named parameters")
        self._edit_g.setToolTip("Expression for dy/dt — use x, y, and named parameters")
        self._chk_streamlines.setToolTip("Show auto-computed trajectories from seed points")
        self._chk_field.setToolTip("Show direction arrows on a grid")

    def _build_ui(self) -> None:
        main = QHBoxLayout(self)
        main.setContentsMargins(8, 8, 8, 8)

        ctrl_w = QWidget()
        ctrl_w.setFixedWidth(240)
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

        # Display options
        disp_grp = QGroupBox("Display")
        dl = QVBoxLayout(disp_grp)
        self._chk_streamlines = QCheckBox("Show streamlines")
        self._chk_streamlines.setChecked(True)
        dl.addWidget(self._chk_streamlines)
        self._chk_field = QCheckBox("Show vector field")
        self._chk_field.setChecked(True)
        dl.addWidget(self._chk_field)
        ctrl.addWidget(disp_grp)

        # Compute button
        btn = QPushButton("Compute")
        btn.setStyleSheet(BTN_STYLE_COMPUTE)
        btn.clicked.connect(self._compute)
        ctrl.addWidget(btn)

        btn_clear = QPushButton("Clear Trajectories")
        btn_clear.clicked.connect(self._clear_trajectories)
        ctrl.addWidget(btn_clear)

        btn_reset_view = QPushButton("Reset View")
        btn_reset_view.setStyleSheet(BTN_STYLE_RESET)
        btn_reset_view.clicked.connect(self._reset_view)
        ctrl.addWidget(btn_reset_view)

        # Hint
        hint = QLabel("Click plot to add trajectories.\n"
                       "Zoom with scroll, then Compute.\n"
                       "Reset View to return to default.")
        hint.setFont(QFont("sans-serif", 8))
        hint.setStyleSheet("color: #888888;")
        hint.setWordWrap(True)
        ctrl.addWidget(hint)

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

        # Clamp zoom range when the user scrolls
        self._plot.plot_item.sigRangeChanged.connect(self._clamp_zoom)

        main.addWidget(self._plot, 1)

    # ------------------------------------------------------------------
    # Zoom limiting
    # ------------------------------------------------------------------

    def _get_max_range(self) -> tuple[tuple[float, float], tuple[float, float]]:
        """Return the maximum allowed view range (5x the preset default)."""
        dx = (self._default_xr[1] - self._default_xr[0]) * _MAX_ZOOM_FACTOR
        dy = (self._default_yr[1] - self._default_yr[0]) * _MAX_ZOOM_FACTOR
        cx = (self._default_xr[0] + self._default_xr[1]) / 2
        cy = (self._default_yr[0] + self._default_yr[1]) / 2
        return (cx - dx / 2, cx + dx / 2), (cy - dy / 2, cy + dy / 2)

    def _clamp_zoom(self) -> None:
        """Prevent the user from zooming out beyond the max range."""
        vb = self._plot.plot_item.vb
        xr_view, yr_view = vb.viewRange()
        max_xr, max_yr = self._get_max_range()

        needs_clamp = False
        new_xr = list(xr_view)
        new_yr = list(yr_view)

        if xr_view[0] < max_xr[0]:
            new_xr[0] = max_xr[0]
            needs_clamp = True
        if xr_view[1] > max_xr[1]:
            new_xr[1] = max_xr[1]
            needs_clamp = True
        if yr_view[0] < max_yr[0]:
            new_yr[0] = max_yr[0]
            needs_clamp = True
        if yr_view[1] > max_yr[1]:
            new_yr[1] = max_yr[1]
            needs_clamp = True

        if needs_clamp:
            # Temporarily disconnect to avoid recursion
            self._plot.plot_item.sigRangeChanged.disconnect(self._clamp_zoom)
            vb.setRange(xRange=new_xr, yRange=new_yr, padding=0)
            self._plot.plot_item.sigRangeChanged.connect(self._clamp_zoom)

    # ------------------------------------------------------------------
    # Preset / state
    # ------------------------------------------------------------------

    def _on_preset_changed(self) -> None:
        idx = self._combo.currentIndex()
        name, f_expr, g_expr, params, xr, yr = PRESET_SYSTEMS[idx]
        self._edit_f.setText(f_expr)
        self._edit_g.setText(g_expr)

        # Store default range for zoom limiting
        self._default_xr = xr
        self._default_yr = yr

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
            plbl = QLabel(f"{pname}:")
            plbl.setFixedWidth(110)
            plbl.setFont(QFont("sans-serif", 9))
            row.addWidget(plbl)
            spin = QDoubleSpinBox()
            spin.setRange(-100, 100)
            spin.setValue(pval)
            spin.setDecimals(2)
            spin.setSingleStep(0.1)
            spin.setFixedWidth(80)
            row.addWidget(spin)
            self._param_layout.addLayout(row)
            self._param_spins[pname] = spin

        # Clear everything and reset view
        self._clear_trajectories()

        # Disconnect clamp during programmatic range set
        self._plot.plot_item.sigRangeChanged.disconnect(self._clamp_zoom)
        self._plot.plot_item.setXRange(xr[0], xr[1], padding=0.05)
        self._plot.plot_item.setYRange(yr[0], yr[1], padding=0.05)
        self._plot.plot_item.sigRangeChanged.connect(self._clamp_zoom)

        self._compute()

    def _get_visible_range(self) -> tuple[tuple[float, float], tuple[float, float]]:
        vb = self._plot.plot_item.vb
        rect = vb.viewRange()
        return (rect[0][0], rect[0][1]), (rect[1][0], rect[1][1])

    def _get_state(self) -> tuple[str, str, dict[str, float], tuple[float, float], tuple[float, float]]:
        f_expr = self._edit_f.text()
        g_expr = self._edit_g.text()
        params = {k: s.value() for k, s in self._param_spins.items()}
        xr, yr = self._get_visible_range()
        return f_expr, g_expr, params, xr, yr

    def _reset_view(self) -> None:
        """Reset to the preset's default range and recompute."""
        self._clear_trajectories()
        self._plot.plot_item.sigRangeChanged.disconnect(self._clamp_zoom)
        self._plot.plot_item.setXRange(
            self._default_xr[0], self._default_xr[1], padding=0.05,
        )
        self._plot.plot_item.setYRange(
            self._default_yr[0], self._default_yr[1], padding=0.05,
        )
        self._plot.plot_item.sigRangeChanged.connect(self._clamp_zoom)
        self._compute()

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _clear_layer(self, items: list) -> None:
        for item in items:
            self._plot.plot_item.removeItem(item)
        items.clear()

    def _clear_warning(self) -> None:
        if self._warning_item is not None:
            self._plot.plot_item.removeItem(self._warning_item)
            self._warning_item = None

    def _show_warning(self, xr: tuple[float, float], yr: tuple[float, float]) -> None:
        """Show a centred warning that the view is far from equilibria."""
        self._clear_warning()
        cx = (xr[0] + xr[1]) / 2
        cy = (yr[0] + yr[1]) / 2
        self._warning_item = pg.TextItem(
            text="No fixed points in view\nPress Reset View or zoom in",
            color="#cc0000", anchor=(0.5, 0.5),
        )
        self._warning_item.setFont(QFont("sans-serif", 12, QFont.Weight.Bold))
        self._warning_item.setPos(cx, cy)
        self._plot.plot_item.addItem(self._warning_item)

    def _compute(self) -> None:
        f_expr, g_expr, params, xr, yr = self._get_state()

        # Clear previous layers
        self._clear_layer(self._field_items)
        self._clear_layer(self._stream_items)
        self._clear_layer(self._fp_items)
        self._clear_warning()
        self._plot.reset_pen_cycle()

        if self._chk_field.isChecked():
            self._draw_quiver(f_expr, g_expr, params, xr, yr)

        if self._chk_streamlines.isChecked():
            self._draw_streamlines(f_expr, g_expr, params, xr, yr)

        has_fps = self._draw_fixed_points(f_expr, g_expr, params, xr, yr)

        if not has_fps:
            self._show_warning(xr, yr)

    def _draw_quiver(
        self, f_expr: str, g_expr: str, params: dict[str, float],
        xr: tuple[float, float], yr: tuple[float, float],
    ) -> None:
        """Draw vector field as a single batched PlotCurveItem."""
        n = 16
        X, Y, DX, DY = compute_vector_field(f_expr, g_expr, params, xr, yr, n, n)

        sx = (xr[1] - xr[0]) / n * 0.32
        sy = (yr[1] - yr[0]) / n * 0.32

        all_x: list[float] = []
        all_y: list[float] = []

        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                x0, y0 = X[i, j], Y[i, j]
                dx, dy = DX[i, j] * sx, DY[i, j] * sy

                all_x.extend([x0, x0 + dx])
                all_y.extend([y0, y0 + dy])

                angle = np.arctan2(dy, dx)
                head_len = np.sqrt(dx ** 2 + dy ** 2) * 0.3
                for da in [2.7, -2.7]:
                    hx = x0 + dx - head_len * np.cos(angle + da)
                    hy = y0 + dy - head_len * np.sin(angle + da)
                    all_x.extend([x0 + dx, hx])
                    all_y.extend([y0 + dy, hy])

        arrows = pg.PlotCurveItem(
            x=np.array(all_x), y=np.array(all_y),
            connect="pairs",
            pen=pg.mkPen(current_mid_colour(), width=1.2),
        )
        self._plot.plot_item.addItem(arrows)
        self._field_items.append(arrows)

    def _draw_streamlines(
        self, f_expr: str, g_expr: str, params: dict[str, float],
        xr: tuple[float, float], yr: tuple[float, float],
    ) -> None:
        """Draw streamlines — bounded to the visible region."""
        streams = compute_streamlines(
            f_expr, g_expr, params, xr, yr, n_seeds=3, t_max=10.0, dt=0.03,
        )

        colours = ["#1f77b4", "#2ca02c", "#9467bd", "#17becf",
                    "#ff7f0e", "#e377c2", "#8c564b", "#bcbd22", "#d62728"]

        for idx, (sx, sy) in enumerate(streams):
            if len(sx) < 3:
                continue
            colour = colours[idx % len(colours)]
            line = self._plot.plot_item.plot(
                sx, sy, pen=pg.mkPen(colour, width=1.8),
            )
            self._stream_items.append(line)

    def _draw_fixed_points(
        self, f_expr: str, g_expr: str, params: dict[str, float],
        xr: tuple[float, float], yr: tuple[float, float],
    ) -> bool:
        """Find, classify, and draw fixed points. Returns True if any found."""
        fps = find_fixed_points(f_expr, g_expr, params, xr, yr)

        # Filter to only those within the visible range
        visible_fps = [
            (xf, yf) for xf, yf in fps
            if xr[0] <= xf <= xr[1] and yr[0] <= yf <= yr[1]
        ]

        lines = []
        for xf, yf in visible_fps:
            cls = classify_fixed_point(f_expr, g_expr, params, xf, yf)
            colour = _FP_COLOURS.get(cls, "#7f7f7f")
            symbol = _FP_SYMBOLS.get(cls, "o")
            scatter = pg.ScatterPlotItem(
                [xf], [yf], size=16, symbol=symbol,
                brush=pg.mkBrush(colour), pen=pg.mkPen("#000000", width=2),
            )
            self._plot.plot_item.addItem(scatter)
            self._fp_items.append(scatter)

            label = pg.TextItem(text=f" {cls}", color=colour, anchor=(0, 1))
            label.setFont(QFont("sans-serif", 8, QFont.Weight.Bold))
            label.setPos(xf, yf)
            self._plot.plot_item.addItem(label)
            self._fp_items.append(label)

            lines.append(f"({xf:.2f}, {yf:.2f}): {cls}")

        self._fp_readout.setText(
            "Fixed points:\n" + "\n".join(lines) if lines else "No fixed points in view"
        )
        return len(visible_fps) > 0

    # ------------------------------------------------------------------
    # User trajectories
    # ------------------------------------------------------------------

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

        pad_x = (xr[1] - xr[0]) * 0.3
        pad_y = (yr[1] - yr[0]) * 0.3
        bounds = (xr[0] - pad_x, xr[1] + pad_x, yr[0] - pad_y, yr[1] + pad_y)

        try:
            t, x, y = compute_trajectory(
                f_expr, g_expr, params, x0, y0, bounds=bounds,
            )
            if len(x) > 2:
                pen = self._plot.next_pen(width=2)
                line = self._plot.plot_item.plot(x, y, pen=pen)
                self._trajectories.append(line)
        except (ValueError, RuntimeError):
            pass

    # ------------------------------------------------------------------
    # State save/load
    # ------------------------------------------------------------------

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
