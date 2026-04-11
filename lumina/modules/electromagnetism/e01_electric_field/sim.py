"""E01 Electric Field Lines — simulation wiring."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PyQt6.QtWidgets import QWidget

from lumina.core.engine import Category, Effort, Level, SimulationBase
from lumina.modules.electromagnetism.e01_electric_field.ui import ElectricFieldWidget


class ElectricField(SimulationBase):
    ID = "E01"
    NAME = "Electric Field Lines"
    CATEGORY = Category.ELECTROMAGNETISM
    LEVEL = Level.GCSE
    EFFORT = Effort.LOW
    DESCRIPTION = "Field lines and vector field from point charges in 2D."
    TAGS = ["electric field", "Coulomb", "field lines", "dipole", "potential"]
    HELP_TEXT = """# Electric Field Lines

Visualise the electric field from a collection of point charges using Coulomb's law.

## What it shows
The electric field surrounding stationary charges. Field lines start on positive charges and end on negative charges (or extend to infinity). The density of lines indicates field strength.

## The physics
- Coulomb's law: E(r) = sum_i q_i * (r - r_i) / |r - r_i|^3
- Field lines: paths tangent to E at every point
- Direction: lines point away from + charges, toward - charges
- Density: more lines per unit area = stronger field
- Potential: V(r) = sum_i q_i / |r - r_i|

## Controls
- Configuration: choose a preset charge arrangement
- Show field lines: streamlines following E
- Show vector arrows: direction at each grid point
- Show potential: colour-coded background (red = high V, blue = low V)
- Compute: refresh the visualisation
- Reset View: return to default range

## Presets
- Single positive: radial outward field
- Single negative: radial inward field
- Dipole: classic + and - charge pair
- Two positive: like charges repel — note the saddle point between them
- Quadrupole: 2+ and 2- arranged in a square
- Three charges: asymmetric configuration

## Try this
- Start with the dipole — observe how lines connect + to -
- Switch to two positive charges — notice the field pushes outward and there's a null point in the middle
- Toggle the potential view to see how it relates to the field (E = -grad V)
- Add the quadrupole and look for null points where the field vanishes
"""

    def __init__(self) -> None:
        self._widget: ElectricFieldWidget | None = None

    def build_ui(self) -> QWidget:
        self._widget = ElectricFieldWidget()
        return self._widget

    def reset(self) -> None:
        if self._widget:
            self._widget.set_params({
                "preset": "Dipole",
                "show_lines": True,
                "show_field": True,
                "show_potential": False,
            })

    def export(self, path: str) -> None:
        if not self._widget:
            return
        d = Path(path)
        d.mkdir(parents=True, exist_ok=True)
        self._widget._plot.export_png(d / f"{self.ID}_field.png")

    def get_state(self) -> dict[str, Any]:
        s = super().get_state()
        if self._widget:
            s["params"] = self._widget.get_params()
        return s

    def set_state(self, state: dict[str, Any]) -> None:
        if self._widget and "params" in state:
            self._widget.set_params(state["params"])
