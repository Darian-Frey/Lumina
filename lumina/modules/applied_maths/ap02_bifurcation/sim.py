"""AP02 Bifurcation Diagram — simulation wiring."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from PyQt6.QtWidgets import QWidget

from lumina.core.engine import Category, Effort, Level, SimulationBase
from lumina.modules.applied_maths.ap02_bifurcation.ui import BifurcationWidget


class BifurcationDiagram(SimulationBase):
    ID = "AP02"
    NAME = "Bifurcation Diagram"
    CATEGORY = Category.APPLIED_MATHS
    LEVEL = Level.A_LEVEL
    EFFORT = Effort.LOW
    DESCRIPTION = "Logistic map period-doubling route to chaos with Lyapunov exponent."
    TAGS = ["bifurcation", "logistic map", "chaos", "Feigenbaum", "Lyapunov"]
    HELP_TEXT = """# Bifurcation Diagram

Explore the period-doubling route to chaos in the logistic map.

## What it shows
The logistic map x_{n+1} = r * x_n * (1 - x_n) is one of the simplest systems that exhibits chaos. As the control parameter r increases, the system transitions from a stable fixed point through period-doubling bifurcations to full chaos.

## Controls
- r samples: number of r values to compute (higher = denser plot)
- iterations: total iterations per r value
- transient: iterations to discard before recording (removes initial transients)
- x0: initial condition for the iteration
- Compute: recompute the diagram for the currently visible r range
- Reset View: return to the default [2.5, 4.0] range

## How to use
- The upper plot shows the bifurcation diagram (attractor values vs r)
- The lower plot shows the Lyapunov exponent (positive = chaos, negative = stable)
- Zoom into a region of interest, then press Compute to refine at higher resolution
- Look for the Feigenbaum cascade: period 1 -> 2 -> 4 -> 8 -> chaos
- The period-3 window near r = 3.83 is particularly interesting

## Key concepts
- Period doubling: the system visits 2^n distinct values per cycle
- Feigenbaum constant: the ratio of successive bifurcation intervals converges to 4.669...
- Lyapunov exponent: measures sensitivity to initial conditions
"""

    def __init__(self) -> None:
        self._widget: BifurcationWidget | None = None

    def build_ui(self) -> QWidget:
        self._widget = BifurcationWidget()
        return self._widget

    def reset(self) -> None:
        if self._widget is not None:
            self._widget.set_params({
                "r_min": 2.5, "r_max": 4.0, "n_r": 1000,
                "n_iter": 1000, "n_discard": 500, "x0": 0.5,
            })

    def export(self, path: str) -> None:
        if self._widget is None:
            return
        d = Path(path)
        d.mkdir(parents=True, exist_ok=True)
        data = self._widget.get_data()
        np.savetxt(
            d / f"{self.ID}_bifurcation.csv",
            np.column_stack([data["r"], data["x"]]),
            delimiter=",", header="r,x", comments="",
        )
        self._widget._plot_bif.export_png(d / f"{self.ID}_bifurcation.png")
        self._widget._plot_lyap.export_png(d / f"{self.ID}_lyapunov.png")

    def get_state(self) -> dict[str, Any]:
        state = super().get_state()
        if self._widget is not None:
            state["params"] = self._widget.get_params()
        return state

    def set_state(self, state: dict[str, Any]) -> None:
        if self._widget is not None and "params" in state:
            self._widget.set_params(state["params"])
