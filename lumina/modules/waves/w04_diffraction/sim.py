"""W04 Diffraction & Interference — simulation wiring."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from PyQt6.QtWidgets import QWidget

from lumina.core.engine import Category, Effort, Level, SimulationBase
from lumina.modules.waves.w04_diffraction.ui import DiffractionWidget


class Diffraction(SimulationBase):
    ID = "W04"
    NAME = "Diffraction & Interference"
    CATEGORY = Category.WAVES
    LEVEL = Level.A_LEVEL
    EFFORT = Effort.LOW
    DESCRIPTION = "Single slit, double slit (Young's), and N-slit grating patterns."
    TAGS = ["diffraction", "interference", "Young", "double slit", "grating"]
    HELP_TEXT = """# Diffraction & Interference

Three classic diffraction setups: single slit, double slit (Young's experiment), and N-slit diffraction gratings.

## What it shows
The angular intensity distribution of light passing through one or more slits, computed in the Fraunhofer (far-field) regime.

## The physics

### Single slit (Fraunhofer)
- I(theta) = I0 (sin(beta) / beta)^2
- beta = pi a sin(theta) / lambda
- First minima at sin(theta) = lambda / a
- Wider slits give narrower central peaks

### Double slit (Young's experiment)
- I(theta) = 4 I0 cos^2(delta/2) * (sin(beta)/beta)^2
- delta = 2 pi d sin(theta) / lambda
- Multiplies the single-slit envelope by an interference factor
- Fringe spacing on screen: dy = lambda D / d (small angle)

### N-slit grating
- I(theta) = I0 (sin(N delta/2) / sin(delta/2))^2 * (sin(beta)/beta)^2
- Sharper principal maxima as N increases
- Same envelope as single slit

## Controls
- Setup: choose between single slit, double slit, or N-slit grating
- a: slit width (same units as wavelength)
- d: slit separation (only for multi-slit modes)
- lambda: light wavelength
- N: number of slits (grating mode only)
- Compute: recompute the pattern
- Reset View: auto-range the plot

## Try this
- Start with the single slit and watch how a/lambda controls the pattern width
- Switch to double slit and observe the interference fringes within the diffraction envelope
- Increase N in grating mode — see how the principal peaks become very sharp
- Set a = d for the multi-slit mode — what happens to the missing orders?
- Increase wavelength relative to slit width — the pattern stretches out

## Real-world relevance
- Single slit: telescope diffraction limit (resolution depends on aperture)
- Double slit: foundation experiment for wave-particle duality
- Grating: spectrometers split light into its colours
"""

    def __init__(self) -> None:
        self._widget: DiffractionWidget | None = None

    def build_ui(self) -> QWidget:
        self._widget = DiffractionWidget()
        return self._widget

    def reset(self) -> None:
        if self._widget:
            self._widget.set_params({
                "mode": "Double slit (Young)",
                "a": 0.05, "d": 0.2,
                "wavelength": 0.01, "N": 5,
            })

    def export(self, path: str) -> None:
        if not self._widget:
            return
        d = Path(path)
        d.mkdir(parents=True, exist_ok=True)
        data = self._widget.get_data()
        np.savetxt(
            d / f"{self.ID}_pattern.csv",
            np.column_stack([data["theta"], data["I"]]),
            delimiter=",", header="theta_rad,intensity", comments="",
        )
        self._widget._plot.export_png(d / f"{self.ID}_pattern.png")

    def get_state(self) -> dict[str, Any]:
        s = super().get_state()
        if self._widget:
            s["params"] = self._widget.get_params()
        return s

    def set_state(self, state: dict[str, Any]) -> None:
        if self._widget and "params" in state:
            self._widget.set_params(state["params"])
