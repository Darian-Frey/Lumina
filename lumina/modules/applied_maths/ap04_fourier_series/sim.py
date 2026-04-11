"""AP04 Fourier Series Builder — simulation wiring."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from PyQt6.QtWidgets import QWidget

from lumina.core.engine import Category, Effort, Level, SimulationBase
from lumina.modules.applied_maths.ap04_fourier_series.ui import FourierSeriesWidget


class FourierSeries(SimulationBase):
    ID = "AP04"
    NAME = "Fourier Series Builder"
    CATEGORY = Category.APPLIED_MATHS
    LEVEL = Level.A_LEVEL
    EFFORT = Effort.LOW
    DESCRIPTION = "Compute Fourier series for arbitrary periodic functions."
    TAGS = ["Fourier", "series", "harmonic analysis", "spectrum", "approximation"]
    HELP_TEXT = """# Fourier Series Builder

Compute the Fourier series of arbitrary periodic functions and visualise both the approximation and the coefficient spectrum.

## What it shows
For a function f(x) periodic on [-pi, pi], the Fourier series writes:

f(x) = a_0/2 + sum_{n=1}^{infinity} (a_n cos(n x) + b_n sin(n x))

where the coefficients are integrals:
- a_n = (1/pi) integral f(x) cos(n x) dx
- b_n = (1/pi) integral f(x) sin(n x) dx

The module truncates the sum at N harmonics and shows how well the partial sum approximates the target function. Both the function and the coefficients are displayed.

## Difference from W02 (Fourier Synthesiser)
- W02: forward — pick coefficients for a known waveform and watch it build
- AP04: inverse — start from a function and find its coefficients

## Controls
- Target Function: choose from 6 preset waveforms
- N: number of harmonics in the partial sum
- Compute: recompute everything
- Reset View: auto-range the plots

## Presets
- Square wave: only odd sine terms (b_n = 4/(n*pi) for odd n)
- Triangle wave: only odd sine terms with 1/n^2 falloff
- Sawtooth wave: all sine terms with 1/n falloff
- Half-rectified sine: cosine series with even-n terms
- Full-rectified sine: cosine series with all-even terms
- Parabola: cosine series, all even terms

## Plots
- Top: target function (red dashed) vs Fourier approximation (blue solid)
- Bottom: a_n (blue) and b_n (orange) coefficients as bar chart

## Try this
- Watch how Gibbs phenomenon appears at discontinuities — never goes away
- Compare the coefficient spectra of square and sawtooth waves — both have 1/n falloff but different parities
- The parabola has only even-n cosine terms — try N = 5 vs N = 50
"""

    def __init__(self) -> None:
        self._widget: FourierSeriesWidget | None = None

    def build_ui(self) -> QWidget:
        self._widget = FourierSeriesWidget()
        return self._widget

    def reset(self) -> None:
        if self._widget:
            self._widget.set_params({"function": "Square wave", "n_max": 10})

    def export(self, path: str) -> None:
        if not self._widget:
            return
        d = Path(path)
        d.mkdir(parents=True, exist_ok=True)
        data = self._widget.get_data()
        np.savetxt(
            d / f"{self.ID}_coefficients.csv",
            np.column_stack([np.arange(len(data["a"])), data["a"], data["b"]]),
            delimiter=",", header="n,a_n,b_n", comments="",
        )
        self._widget._plot_fn.export_png(d / f"{self.ID}_function.png")
        self._widget._plot_coeffs.export_png(d / f"{self.ID}_coefficients.png")

    def get_state(self) -> dict[str, Any]:
        s = super().get_state()
        if self._widget:
            s["params"] = self._widget.get_params()
        return s

    def set_state(self, state: dict[str, Any]) -> None:
        if self._widget and "params" in state:
            self._widget.set_params(state["params"])
