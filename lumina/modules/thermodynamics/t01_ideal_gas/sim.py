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
    HELP_TEXT = """# Ideal Gas Simulation

A 2D molecular dynamics simulation of an ideal gas in a box.

## What it shows
Particles bounce around elastically inside a container. The simulation measures temperature from kinetic energy and pressure from wall collisions, demonstrating the microscopic origin of the ideal gas law PV = NkT.

## Controls
- N particles: number of gas molecules (10-500)
- T (K): initial temperature — sets the Maxwell-Boltzmann speed distribution
- Play/Pause: start or stop the simulation
- Reset: reinitialise all particles with new random positions and velocities
- Reset View: restore default plot ranges

## Plots
- Gas Box: real-time particle positions inside the container (black border)
- Speed Distribution: histogram of particle speeds, updating live

## Readout
- T: measured temperature from kinetic energy
- P: measured pressure from wall impulses
- N: number of particles

## Key concepts
- Temperature is proportional to average kinetic energy: T = m<v^2>/(2k_B)
- Pressure comes from momentum transfer at the walls
- The speed distribution should approach the Maxwell-Boltzmann curve
- More particles = smoother statistics, better agreement with theory
"""

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
