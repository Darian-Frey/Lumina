"""W02 Fourier Synthesiser — simulation wiring."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from PyQt6.QtWidgets import QWidget

from lumina.core.engine import Category, Effort, Level, SimulationBase
from lumina.modules.waves.w02_fourier_synth.ui import FourierSynthWidget


class FourierSynthesiser(SimulationBase):
    ID = "W02"
    NAME = "Fourier Synthesiser"
    CATEGORY = Category.WAVES
    LEVEL = Level.A_LEVEL
    EFFORT = Effort.LOW
    DESCRIPTION = "Build waveforms from harmonics and watch the series converge."
    TAGS = ["Fourier", "harmonics", "series", "Gibbs", "square wave", "synthesis"]

    def __init__(self) -> None:
        self._widget: FourierSynthWidget | None = None

    def build_ui(self) -> QWidget:
        self._widget = FourierSynthWidget()
        return self._widget

    def reset(self) -> None:
        if self._widget:
            self._widget.set_params({"kind": "square", "n": 5})

    def export(self, path: str) -> None:
        if not self._widget:
            return
        d = Path(path)
        d.mkdir(parents=True, exist_ok=True)
        data = self._widget.get_data()
        np.savetxt(
            d / f"{self.ID}_fourier.csv",
            np.column_stack([data["x"], data["partial_sum"], data["target"]]),
            delimiter=",", header="x,partial_sum,target", comments="",
        )
        self._widget._plot_sum.export_png(d / f"{self.ID}_fourier.png")

    def get_state(self) -> dict[str, Any]:
        s = super().get_state()
        if self._widget:
            s["params"] = self._widget.get_params()
        return s

    def set_state(self, state: dict[str, Any]) -> None:
        if self._widget and "params" in state:
            self._widget.set_params(state["params"])
