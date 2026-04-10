"""AP01 ODE Phase Portrait — simulation wiring."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PyQt6.QtWidgets import QWidget

from lumina.core.engine import Category, Effort, Level, SimulationBase
from lumina.modules.applied_maths.ap01_phase_portrait.ui import PhasePortraitWidget


class OdePhasePortrait(SimulationBase):
    ID = "AP01"
    NAME = "ODE Phase Portrait"
    CATEGORY = Category.APPLIED_MATHS
    LEVEL = Level.A_LEVEL
    EFFORT = Effort.LOW
    DESCRIPTION = "Nullclines, trajectories, fixed points, and stability classification."
    TAGS = ["ODE", "phase portrait", "nullcline", "fixed point", "dynamical systems"]
    HELP_TEXT = """# ODE Phase Portrait

Visualise the dynamics of two-dimensional ordinary differential equation systems.

## What it shows
The phase portrait displays the behaviour of a 2D dynamical system dx/dt = f(x,y), dy/dt = g(x,y). Arrow fields show the direction of flow at each point, streamlines show how trajectories evolve, and fixed points are classified by stability.

## Controls
- System dropdown: choose a preset ODE system or type your own equations
- dx/dt and dy/dt fields: editable equations using x, y, and named parameters
- Parameter spinboxes: adjust system parameters (e.g. mu for Van der Pol)
- Compute button: recalculate the field and streamlines for the current view
- Reset View: return to the default range for the selected system
- Show streamlines / Show vector field: toggle display layers

## Interaction
- Click anywhere on the plot to add a trajectory from that initial condition
- Scroll to zoom in/out, then press Compute to refresh the field
- Clear Trajectories removes user-added trajectories

## Fixed Point Classification
- Stable node: all trajectories approach (green circle)
- Unstable node: all trajectories repel (red circle)
- Saddle: attracts along one axis, repels along another (orange diamond)
- Stable spiral: spirals inward (blue circle)
- Unstable spiral: spirals outward (purple circle)
- Centre: closed orbits, neutrally stable (cyan square)

## Preset Systems
- Linear 2x2: configurable 2x2 matrix system
- Van der Pol: classic nonlinear oscillator with limit cycle
- Lotka-Volterra: predator-prey population dynamics
- Simple Pendulum: with optional damping
- Duffing (unforced): double-well potential with damping
"""

    def __init__(self) -> None:
        self._widget: PhasePortraitWidget | None = None

    def build_ui(self) -> QWidget:
        self._widget = PhasePortraitWidget()
        return self._widget

    def reset(self) -> None:
        if self._widget:
            self._widget._combo.setCurrentIndex(0)
            self._widget._on_preset_changed()

    def export(self, path: str) -> None:
        if not self._widget:
            return
        d = Path(path)
        d.mkdir(parents=True, exist_ok=True)
        self._widget._plot.export_png(d / f"{self.ID}_phase_portrait.png")

    def get_state(self) -> dict[str, Any]:
        s = super().get_state()
        if self._widget:
            s["params"] = self._widget.get_params()
        return s

    def set_state(self, state: dict[str, Any]) -> None:
        if self._widget and "params" in state:
            self._widget.set_params(state["params"])
