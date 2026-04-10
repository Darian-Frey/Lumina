"""M10 Double Pendulum — simulation wiring."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from PyQt6.QtWidgets import QWidget

from lumina.core.engine import Category, Effort, Level, SimulationBase
from lumina.modules.mechanics.m10_double_pendulum.ui import DoublePendulumWidget


class DoublePendulum(SimulationBase):
    """M10 — Chaotic Double Pendulum simulation module."""

    ID = "M10"
    NAME = "Chaotic Double Pendulum"
    CATEGORY = Category.MECHANICS
    LEVEL = Level.UNIVERSITY
    EFFORT = Effort.LOW
    DESCRIPTION = "Double pendulum with trajectory tracing and energy conservation check."
    TAGS = ["chaos", "pendulum", "Lagrangian", "trajectory", "energy"]
    HELP_TEXT = """# Chaotic Double Pendulum

A simple mechanical system that exhibits chaotic behaviour.

## What it shows
Two rigid rods connected end-to-end with point masses at each joint. Despite the simple setup, the motion is chaotic for most initial conditions — tiny changes in starting angles lead to completely different trajectories.

## Controls
- m1, m2 (kg): masses of the first and second bobs
- L1, L2 (m): lengths of the first and second rods
- g (m/s^2): gravitational acceleration
- theta1, theta2 (rad): initial angles (0 = hanging straight down)
- omega1, omega2: initial angular velocities
- speed: animation playback speed
- trail: length of the trajectory trail on the second bob
- Play/Pause: start or stop the animation
- Restart: reset to initial conditions and recompute
- Recompute: recalculate with current parameters
- Reset View: auto-range all plots

## Plots
- Double Pendulum: real-time animation showing the rods, bobs, and trajectory trail
- Tip Trajectory: the path traced by the second bob's tip
- Total Energy: should remain approximately constant (conservation check)

## Try this
- Set theta1 = pi/2, theta2 = pi for dramatic chaotic motion
- Compare theta2 = 3.14 vs theta2 = 3.15 — watch the trajectories diverge
- Set both angles small (e.g. 0.1) for nearly periodic behaviour
- Make m2 >> m1 to see the first bob dragged around by the second
"""

    def __init__(self) -> None:
        self._widget: DoublePendulumWidget | None = None

    def build_ui(self) -> QWidget:
        self._widget = DoublePendulumWidget()
        return self._widget

    def reset(self) -> None:
        if self._widget is not None:
            self._widget.stop()
            self._widget.set_params({
                "m1": 1.0, "m2": 1.0, "L1": 1.0, "L2": 1.0, "g": 9.81,
                "theta1": 1.5708, "theta2": 3.1416,
                "omega1": 0.0, "omega2": 0.0,
                "speed": 5.0, "trail": 600.0,
            })

    def export(self, path: str) -> None:
        if self._widget is None:
            return
        export_dir = Path(path)
        export_dir.mkdir(parents=True, exist_ok=True)

        data = self._widget.get_data()
        csv_path = export_dir / f"{self.ID}_double_pendulum.csv"
        header = "t,theta1,omega1,theta2,omega2,x2,y2,energy"
        np.savetxt(
            csv_path,
            np.column_stack([
                data["t"], data["theta1"], data["omega1"],
                data["theta2"], data["omega2"],
                data["x2"], data["y2"], data["energy"],
            ]),
            delimiter=",", header=header, comments="",
        )

        for name, plot in [
            ("pendulum", self._widget._plot_pend),
            ("trajectory", self._widget._plot_traj),
            ("energy", self._widget._plot_energy),
        ]:
            plot.export_png(export_dir / f"{self.ID}_{name}.png")

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
