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
    HELP_TEXT = """# Fourier Synthesiser

Build any waveform from sine harmonics and watch the series converge.

## What it shows
Joseph Fourier showed that any periodic function can be represented as a sum of sines and cosines. This module demonstrates how adding more harmonics progressively approximates the target waveform.

## Controls
- Target Waveform: choose square, triangle, or sawtooth
- N (harmonics): number of Fourier terms to include (1-50)
- Compute: update the plots
- Reset View: auto-range both plots

## Plots
- Individual Harmonics: each sine component shown separately
- Partial Sum vs Target: the blue curve is the Fourier approximation, the red dashed curve is the exact target waveform

## Key concepts
- Square wave: only odd harmonics, b_n = 4/(n*pi)
- Triangle wave: only odd harmonics, b_n = 8*(-1)^((n-1)/2)/(n^2*pi^2)
- Sawtooth wave: all harmonics, b_n = -2*(-1)^n/(n*pi)
- Gibbs phenomenon: ~9% overshoot at discontinuities that persists as N increases
- More harmonics = better approximation away from discontinuities

## Try this
- Start with N=1 and slowly increase — watch the shape emerge
- Compare N=5 vs N=50 for the square wave
- Look at the Gibbs overshoot near the jumps — it never goes away!
"""

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
