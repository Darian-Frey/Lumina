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
