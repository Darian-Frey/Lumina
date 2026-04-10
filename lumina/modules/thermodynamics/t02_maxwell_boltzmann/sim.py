"""T02 Maxwell-Boltzmann — simulation wiring."""
from __future__ import annotations
from pathlib import Path
from typing import Any
import numpy as np
from PyQt6.QtWidgets import QWidget
from lumina.core.engine import Category, Effort, Level, SimulationBase
from lumina.modules.thermodynamics.t02_maxwell_boltzmann.ui import MaxwellBoltzmannWidget

class MaxwellBoltzmann(SimulationBase):
    ID = "T02"
    NAME = "Maxwell-Boltzmann Distribution"
    CATEGORY = Category.THERMODYNAMICS
    LEVEL = Level.A_LEVEL
    EFFORT = Effort.LOW
    DESCRIPTION = "Speed distribution updating live as temperature changes."
    TAGS = ["Maxwell-Boltzmann", "temperature", "speed distribution", "kinetic theory"]
    HELP_TEXT = """# Maxwell-Boltzmann Distribution

Visualise how molecular speeds are distributed at different temperatures.

## What it shows
The Maxwell-Boltzmann distribution describes the probability of finding a molecule with a given speed in an ideal gas at thermal equilibrium. The shape depends only on temperature and molecular mass.

## Controls
- T (K): temperature — higher T shifts the distribution to faster speeds
- Compute: update the distribution curve
- Reset View: auto-range the plot

## Plot
- Blue curve: the Maxwell-Boltzmann probability density f(v)
- Green dashed line (v_mp): most probable speed — peak of the distribution
- Orange dashed line (v_avg): mean speed
- Red dashed line (v_rms): root-mean-square speed

## Key equations
- f(v) = 4*pi*(m/2*pi*k_B*T)^(3/2) * v^2 * exp(-m*v^2/(2*k_B*T))
- v_mp = sqrt(2*k_B*T/m) — most probable speed
- v_avg = sqrt(8*k_B*T/(pi*m)) — mean speed
- v_rms = sqrt(3*k_B*T/m) — root-mean-square speed
- Always: v_mp < v_avg < v_rms

## Try this
- Compare T=300K (room temperature) with T=1000K
- Notice how the peak shifts right and flattens as T increases
- The area under the curve is always 1 (normalised probability)
"""

    def __init__(self) -> None:
        self._widget: MaxwellBoltzmannWidget | None = None

    def build_ui(self) -> QWidget:
        self._widget = MaxwellBoltzmannWidget()
        return self._widget

    def reset(self) -> None:
        if self._widget: self._widget.set_params({"T": 300})

    def export(self, path: str) -> None:
        if not self._widget: return
        d = Path(path)
        d.mkdir(parents=True, exist_ok=True)
        data = self._widget.get_data()
        np.savetxt(d / f"{self.ID}_mb.csv",
                   np.column_stack([data["v"], data["fv"]]),
                   delimiter=",", header="v,f(v)", comments="")
        self._widget._plot.export_png(d / f"{self.ID}_distribution.png")

    def get_state(self) -> dict[str, Any]:
        s = super().get_state()
        if self._widget: s["params"] = self._widget.get_params()
        return s

    def set_state(self, state: dict[str, Any]) -> None:
        if self._widget and "params" in state:
            self._widget.set_params(state["params"])
