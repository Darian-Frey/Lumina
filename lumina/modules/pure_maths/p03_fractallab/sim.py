"""P03 FractalLab — simulation wiring."""
from __future__ import annotations
from pathlib import Path
from typing import Any
from PyQt6.QtWidgets import QWidget
from lumina.core.engine import Category, Effort, Level, SimulationBase
from lumina.modules.pure_maths.p03_fractallab.ui import FractalLabWidget

class FractalLab(SimulationBase):
    ID = "P03"
    NAME = "FractalLab"
    CATEGORY = Category.PURE_MATHS
    LEVEL = Level.A_LEVEL
    EFFORT = Effort.LOW
    DESCRIPTION = "Mandelbrot and Julia sets with deep zoom and colour mapping."
    TAGS = ["fractal", "Mandelbrot", "Julia", "complex", "iteration", "zoom"]

    def __init__(self) -> None:
        self._widget: FractalLabWidget | None = None

    def build_ui(self) -> QWidget:
        self._widget = FractalLabWidget()
        return self._widget

    def reset(self) -> None:
        if self._widget:
            self._widget._zoom_stack.clear()
            self._widget.set_params({"type": "Mandelbrot", "max_iter": 256})

    def export(self, path: str) -> None:
        if not self._widget: return
        d = Path(path)
        d.mkdir(parents=True, exist_ok=True)
        self._widget._plot.export_png(d / f"{self.ID}_fractal.png")

    def get_state(self) -> dict[str, Any]:
        s = super().get_state()
        if self._widget: s["params"] = self._widget.get_params()
        return s

    def set_state(self, state: dict[str, Any]) -> None:
        if self._widget and "params" in state:
            self._widget.set_params(state["params"])
