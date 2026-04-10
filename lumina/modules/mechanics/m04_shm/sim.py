"""M04 Simple Harmonic Motion — simulation wiring."""
from __future__ import annotations
from pathlib import Path
from typing import Any
import numpy as np
from PyQt6.QtWidgets import QWidget
from lumina.core.engine import Category, Effort, Level, SimulationBase
from lumina.modules.mechanics.m04_shm.ui import SHMWidget

class SimpleHarmonicMotion(SimulationBase):
    ID = "M04"
    NAME = "Simple Harmonic Motion"
    CATEGORY = Category.MECHANICS
    LEVEL = Level.A_LEVEL
    EFFORT = Effort.LOW
    DESCRIPTION = "Spring-mass system, pendulum, phase space, energy exchange, damping."
    TAGS = ["SHM", "oscillation", "pendulum", "spring", "phase space", "damping"]
    HELP_TEXT = """# Simple Harmonic Motion

Explore spring-mass oscillations, phase space, energy exchange, and damping.

## What it shows
Simple harmonic motion is the foundation of all oscillatory physics. A mass on a spring follows x(t) = A cos(wt + phi), with angular frequency w = sqrt(k/m).

## Controls
- k (N/m): spring constant — stiffer spring means higher frequency
- m (kg): mass — heavier mass means lower frequency
- A (m): amplitude — maximum displacement from equilibrium
- phi (rad): initial phase angle
- gamma (1/s): damping coefficient — 0 for undamped, increase for damping
- Play: animate the phase space dot moving along the trajectory
- Compute: recalculate with current parameters
- Reset View: auto-range all plots

## Plots
- Displacement x(t): the oscillation over time, with damping envelope (dashed)
- Phase Space: x vs v plot — an ellipse for undamped, a spiral for damped
- Energy: kinetic (blue), potential (orange), and total (green) energy vs time

## Damping modes
- Underdamped (gamma < omega0): oscillates with decreasing amplitude
- Critical (gamma = omega0): fastest return to equilibrium without oscillation
- Overdamped (gamma > omega0): slow exponential decay, no oscillation

## Key equations
- omega0 = sqrt(k/m)
- Period T = 2*pi/omega0
- Energy E = (1/2)*k*A^2 (constant for undamped)
"""

    def __init__(self) -> None:
        self._widget: SHMWidget | None = None

    def build_ui(self) -> QWidget:
        self._widget = SHMWidget()
        return self._widget

    def reset(self) -> None:
        if self._widget:
            self._widget.stop()
            self._widget.set_params({"k": 5.0, "m": 1.0, "A": 1.0, "phi": 0.0, "gamma": 0.0})

    def export(self, path: str) -> None:
        if not self._widget:
            return
        d = Path(path)
        d.mkdir(parents=True, exist_ok=True)
        data = self._widget.get_data()
        np.savetxt(d / f"{self.ID}_shm.csv",
                   np.column_stack([data["t"], data["x"], data["v"], data["KE"], data["PE"]]),
                   delimiter=",", header="t,x,v,KE,PE", comments="")
        self._widget._plot_xt.export_png(d / f"{self.ID}_displacement.png")

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
