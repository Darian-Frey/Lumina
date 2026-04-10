"""W01 Wave Superposition — simulation wiring."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from PyQt6.QtWidgets import QWidget

from lumina.core.engine import Category, Effort, Level, SimulationBase
from lumina.modules.waves.w01_superposition.ui import WaveSuperpositionWidget


class WaveSuperposition(SimulationBase):
    ID = "W01"
    NAME = "Wave Superposition"
    CATEGORY = Category.WAVES
    LEVEL = Level.GCSE
    EFFORT = Effort.LOW
    DESCRIPTION = "Add sinusoidal waves, visualise beats and standing waves."
    TAGS = ["waves", "superposition", "beats", "standing wave", "interference"]

    def __init__(self) -> None:
        self._widget: WaveSuperpositionWidget | None = None

    def build_ui(self) -> QWidget:
        self._widget = WaveSuperpositionWidget()
        return self._widget

    def reset(self) -> None:
        if self._widget:
            self._widget.stop()
            self._widget._t = 0.0
            self._widget._update_plots()

    def export(self, path: str) -> None:
        if not self._widget:
            return
        d = Path(path)
        d.mkdir(parents=True, exist_ok=True)
        data = self._widget.get_data()
        np.savetxt(d / f"{self.ID}_waves.csv",
                   np.column_stack([data["x"], data["y_sum"]]),
                   delimiter=",", header="x,y_sum", comments="")
        self._widget._plot_sum.export_png(d / f"{self.ID}_superposition.png")

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
