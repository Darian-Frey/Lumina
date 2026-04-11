"""M01 Projectile Motion — simulation wiring."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from PyQt6.QtWidgets import QWidget

from lumina.core.engine import Category, Effort, Level, SimulationBase
from lumina.modules.mechanics.m01_projectile.ui import ProjectileWidget


class ProjectileMotion(SimulationBase):
    ID = "M01"
    NAME = "Projectile Motion"
    CATEGORY = Category.MECHANICS
    LEVEL = Level.GCSE
    EFFORT = Effort.LOW
    DESCRIPTION = "Launch projectiles with adjustable angle, speed, and air resistance."
    TAGS = ["projectile", "kinematics", "drag", "trajectory", "ballistics"]
    HELP_TEXT = """# Projectile Motion

Classical projectile motion — the motion of an object launched into the air under gravity, with optional air resistance.

## What it shows
A projectile launched from height h0 with initial speed v0 at angle theta. Without drag the trajectory is a perfect parabola. With drag, the path becomes asymmetric and the range decreases.

## The physics

Without drag (vacuum):
- x(t) = v0 cos(theta) t
- y(t) = h0 + v0 sin(theta) t - (1/2) g t^2
- Range R = v0^2 sin(2theta) / g (when h0 = 0)
- Maximum height H = (v0 sin(theta))^2 / (2g) + h0
- Optimal angle for max range: 45 degrees (when h0 = 0)

With linear drag:
- dvx/dt = -k vx
- dvy/dt = -g - k vy
- Trajectory becomes asymmetric

With quadratic drag (more realistic for fast projectiles):
- dvx/dt = -k v vx
- dvy/dt = -g - k v vy
- Even greater asymmetry

## Controls
- v0: initial speed in m/s
- theta: launch angle from horizontal (0 = horizontal, 90 = vertical)
- h0: launch height above ground
- g: gravitational acceleration (9.81 on Earth, 1.62 on the Moon)
- drag k: drag coefficient (0 for vacuum)
- type: linear or quadratic drag law
- Compare with vacuum: dashed line shows the no-drag trajectory for comparison
- Compute: refresh the plot
- Reset View: auto-fit the plot

## Plots
- Solid blue: actual trajectory (with drag if k > 0)
- Dashed grey: vacuum trajectory for comparison
- Dot: apex (highest point)
- Black line at y = 0: ground level

## Try this
- Set drag = 0 and try different angles — verify 45 degrees gives the longest range
- Add drag k = 0.05 — the optimal angle drops below 45 degrees
- Set h0 > 0 (e.g. cliff at 50 m) — even without drag, the optimal angle is below 45
- Switch g to 1.62 (Moon) — see how much further things travel
- Use quadratic drag for high speeds (v0 > 50)
"""

    def __init__(self) -> None:
        self._widget: ProjectileWidget | None = None

    def build_ui(self) -> QWidget:
        self._widget = ProjectileWidget()
        return self._widget

    def reset(self) -> None:
        if self._widget:
            self._widget.set_params({
                "v0": 30.0, "theta": 45.0, "h0": 0.0,
                "g": 9.81, "drag": 0.0, "drag_type": "linear",
                "compare": True,
            })

    def export(self, path: str) -> None:
        if not self._widget:
            return
        d = Path(path)
        d.mkdir(parents=True, exist_ok=True)
        data = self._widget.get_data()
        np.savetxt(
            d / f"{self.ID}_trajectory.csv",
            np.column_stack([data["t"], data["x"], data["y"]]),
            delimiter=",", header="t,x,y", comments="",
        )
        self._widget._plot.export_png(d / f"{self.ID}_trajectory.png")

    def get_state(self) -> dict[str, Any]:
        s = super().get_state()
        if self._widget:
            s["params"] = self._widget.get_params()
        return s

    def set_state(self, state: dict[str, Any]) -> None:
        if self._widget and "params" in state:
            self._widget.set_params(state["params"])
