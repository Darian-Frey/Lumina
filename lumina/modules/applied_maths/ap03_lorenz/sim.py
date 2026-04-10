"""
AP03 Lorenz Attractor — simulation wiring.
-------------------------------------------
Connects the physics module and UI module to SimulationBase.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from PyQt6.QtWidgets import QWidget

from lumina.core.engine import Category, Effort, Level, SimulationBase
from lumina.modules.applied_maths.ap03_lorenz.ui import LorenzWidget


class LorenzAttractor(SimulationBase):
    """AP03 — Lorenz Attractor simulation module."""

    ID = "AP03"
    NAME = "Lorenz Attractor"
    CATEGORY = Category.APPLIED_MATHS
    LEVEL = Level.UNIVERSITY
    EFFORT = Effort.LOW
    DESCRIPTION = "3D strange attractor with sensitive dependence on initial conditions."
    TAGS = ["lorenz", "chaos", "attractor", "ODE", "dynamical systems"]
    HELP_TEXT = """# Lorenz Attractor

The Lorenz system — the original example of deterministic chaos.

## What it shows
Edward Lorenz discovered this system in 1963 while modelling atmospheric convection. Despite being fully deterministic, nearby trajectories diverge exponentially — the famous "butterfly effect".

## The equations
- dx/dt = sigma * (y - x)
- dy/dt = x * (rho - z) - y
- dz/dt = x * y - beta * z

## Controls
- sigma (Prandtl number): controls the rate of rotation, default 10
- rho (Rayleigh number): controls the driving force, default 28
- beta (geometry factor): related to the aspect ratio, default 8/3
- x0, y0, z0: initial conditions
- speed: animation playback speed (frames per tick)
- trail: number of points in the animated trail
- Play/Pause: start or stop the trajectory animation
- Restart: reset animation to the beginning
- Recompute: recalculate the trajectory with current parameters
- Reset View: auto-range all four plots

## Plots
- X-Z and X-Y Phase Space: the butterfly-shaped strange attractor
- Time Series: x(t) showing the characteristic irregular switching
- Sensitivity to ICs: log-scale separation between two nearby trajectories

## Try this
- Set rho < 1 to see the trajectory decay to the origin
- Set rho = 28 (default) for the classic chaotic regime
- Change x0 by 0.001 and compare — the trajectories diverge rapidly
"""

    def __init__(self) -> None:
        self._widget: LorenzWidget | None = None

    def build_ui(self) -> QWidget:
        self._widget = LorenzWidget()
        return self._widget

    def reset(self) -> None:
        if self._widget is not None:
            self._widget.stop()
            self._widget.set_params({
                "sigma": 10.0,
                "rho": 28.0,
                "beta": 8.0 / 3.0,
                "x0": 1.0,
                "y0": 1.0,
                "z0": 1.0,
                "speed": 10.0,
                "trail": 500.0,
            })

    def export(self, path: str) -> None:
        if self._widget is None:
            return
        export_dir = Path(path)
        export_dir.mkdir(parents=True, exist_ok=True)

        # Export CSV
        data = self._widget.get_data()
        csv_path = export_dir / f"{self.ID}_lorenz_data.csv"
        header = "t,x,y,z"
        np.savetxt(
            csv_path,
            np.column_stack([data["t"], data["x"], data["y"], data["z"]]),
            delimiter=",",
            header=header,
            comments="",
        )

        # Export plots as PNG
        for name, plot in [
            ("xz", self._widget._plot_xz),
            ("xy", self._widget._plot_xy),
            ("timeseries", self._widget._plot_ts),
            ("divergence", self._widget._plot_div),
        ]:
            png_path = export_dir / f"{self.ID}_lorenz_{name}.png"
            plot.export_png(png_path)

        self.log(f"Exported to {export_dir}")

    def get_state(self) -> dict[str, Any]:
        state = super().get_state()
        if self._widget is not None:
            state["params"] = self._widget.get_params()
        return state

    def set_state(self, state: dict[str, Any]) -> None:
        if self._widget is not None and "params" in state:
            self._widget.set_params(state["params"])

    def on_hide(self) -> None:
        if self._widget is not None:
            self._widget.stop()

    def on_close(self) -> None:
        if self._widget is not None:
            self._widget.stop()
