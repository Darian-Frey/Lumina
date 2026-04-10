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
    HELP_TEXT = """# Wave Superposition

Combine sinusoidal waves and explore beats, standing waves, and interference.

## What it shows
The principle of superposition: when two or more waves overlap, the resultant displacement is the sum of the individual displacements. This produces fascinating patterns including beats and standing waves.

## Controls
- Wave 1-5 panels: each has amplitude (A), frequency (f), and phase (phi)
- Tick the checkbox to enable/disable each wave
- Colour stripe on each panel matches the plot line colour
- Presets: quickly set up common demonstrations
- Play/Pause: animate the waves in time
- Reset View: auto-range both plots

## Presets
- Beats: two waves with close frequencies (5.0 and 5.5 Hz) — the amplitude modulates at the beat frequency |f1 - f2|
- Standing Wave: two identical waves travelling in opposite directions — creates nodes (zero displacement) and antinodes (maximum displacement)

## Plots
- Individual Waves: each enabled wave shown in its own colour
- Superposition: the sum of all enabled waves

## Key concepts
- Beat frequency = |f1 - f2|
- Standing wave: 2A cos(wt) sin(kx) — nodes at fixed positions
- Constructive interference: waves in phase add up
- Destructive interference: waves out of phase cancel
"""

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
