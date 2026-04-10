"""T01 Ideal Gas — simulation wiring."""
from __future__ import annotations
from pathlib import Path
from typing import Any
import numpy as np
from PyQt6.QtWidgets import QWidget
from lumina.core.engine import Category, Effort, Level, SimulationBase
from lumina.modules.thermodynamics.t01_ideal_gas.ui import IdealGasWidget

class IdealGas(SimulationBase):
    ID = "T01"
    NAME = "Ideal Gas Simulation"
    CATEGORY = Category.THERMODYNAMICS
    LEVEL = Level.GCSE
    EFFORT = Effort.LOW
    DESCRIPTION = "Particle box with pressure, temperature, and volume controls."
    TAGS = ["ideal gas", "PV=nRT", "particles", "temperature", "pressure"]

    def __init__(self) -> None:
        self._widget: IdealGasWidget | None = None

    def build_ui(self) -> QWidget:
        self._widget = IdealGasWidget()
        return self._widget

    def reset(self) -> None:
        if self._widget:
            self._widget.stop()
            self._widget.set_params({"n": 200, "T": 300})

    def export(self, path: str) -> None:
        if not self._widget:
            return
        d = Path(path)
        d.mkdir(parents=True, exist_ok=True)
        data = self._widget.get_data()
        np.savetxt(d / f"{self.ID}_speeds.csv", data["speeds"], header="speed", comments="")

    def get_state(self) -> dict[str, Any]:
        s = super().get_state()
        if self._widget: s["params"] = self._widget.get_params()
        return s

    def set_state(self, state: dict[str, Any]) -> None:
        if self._widget and "params" in state:
            self._widget.set_params(state["params"])

    def on_hide(self) -> None:
        if self._widget: self._widget.stop()

    def on_close(self) -> None:
        if self._widget: self._widget.stop()
