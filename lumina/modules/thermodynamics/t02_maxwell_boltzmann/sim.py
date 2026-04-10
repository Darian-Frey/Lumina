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
