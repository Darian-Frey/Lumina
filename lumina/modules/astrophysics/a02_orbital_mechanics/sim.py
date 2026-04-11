"""A02 Orbital Mechanics — simulation wiring."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from PyQt6.QtWidgets import QWidget

from lumina.core.engine import Category, Effort, Level, SimulationBase
from lumina.modules.astrophysics.a02_orbital_mechanics.ui import OrbitalWidget


class OrbitalMechanics(SimulationBase):
    ID = "A02"
    NAME = "Orbital Mechanics"
    CATEGORY = Category.ASTROPHYSICS
    LEVEL = Level.A_LEVEL
    EFFORT = Effort.MEDIUM
    DESCRIPTION = "Kepler orbits — adjust semi-major axis, eccentricity, launch speed."
    TAGS = ["Kepler", "orbit", "ellipse", "two-body", "vis-viva", "Hohmann"]
    HELP_TEXT = """# Orbital Mechanics

Two-body Keplerian orbits. Adjust the semi-major axis, eccentricity, and initial speed to explore the orbit family.

## What it shows
A small body orbiting a central mass under gravity. Both the closed-form ellipse and a numerical integration are shown.

## The physics
- Kepler's first law: orbits are conic sections (circle, ellipse, parabola, hyperbola)
- Kepler's third law: T^2 ~ a^3
- Vis-viva equation: v^2 = GM (2/r - 1/a)
- Specific orbital energy: epsilon = v^2/2 - GM/r
- Negative epsilon -> bound (elliptic), zero -> parabolic, positive -> hyperbolic

## Controls
- a: semi-major axis
- e: eccentricity (0 = circle, 0.95 = highly elliptical)
- v factor: velocity multiplier at perihelion (1.0 = matches the prescribed orbit)
- Play / Pause: animate the planet around the orbit
- Compute: recompute with current parameters
- Reset View: reset the animation and view

## Plots
- Yellow dot: central mass (Sun)
- Dashed grey: closed-form Kepler ellipse from a and e
- Solid blue: numerical integration of the two-body problem
- Blue dot: current planet position (during animation)

## Try this
- e = 0 — perfect circular orbit
- e = 0.5 — moderate ellipse
- e = 0.9 — highly elliptical (comet-like)
- v factor = 1.0 — orbit matches the prescribed ellipse
- v factor < 1.0 — the body falls toward the central mass
- v factor > 1.0 — the body spirals outward; near sqrt(2) it escapes
- Watch how the planet moves faster near perihelion (Kepler's second law)
"""

    def __init__(self) -> None:
        self._widget: OrbitalWidget | None = None

    def build_ui(self) -> QWidget:
        self._widget = OrbitalWidget()
        return self._widget

    def reset(self) -> None:
        if self._widget:
            self._widget.stop()
            self._widget.set_params({"a": 1.5, "e": 0.5, "v_factor": 1.0})

    def export(self, path: str) -> None:
        if not self._widget:
            return
        d = Path(path)
        d.mkdir(parents=True, exist_ok=True)
        data = self._widget.get_data()
        np.savetxt(
            d / f"{self.ID}_orbit.csv",
            np.column_stack([data["t"], data["x"], data["y"]]),
            delimiter=",", header="t,x,y", comments="",
        )
        self._widget._plot.export_png(d / f"{self.ID}_orbit.png")

    def get_state(self) -> dict[str, Any]:
        s = super().get_state()
        if self._widget:
            s["params"] = self._widget.get_params()
        return s

    def set_state(self, state: dict[str, Any]) -> None:
        if self._widget and "params" in state:
            self._widget.set_params(state["params"])

    def on_hide(self) -> None:
        if self._widget:
            self._widget.stop()

    def on_close(self) -> None:
        if self._widget:
            self._widget.stop()
