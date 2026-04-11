"""Q01 Particle in a Box — simulation wiring."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from PyQt6.QtWidgets import QWidget

from lumina.core.engine import Category, Effort, Level, SimulationBase
from lumina.modules.quantum.q01_particle_in_box.ui import ParticleInBoxWidget


class ParticleInBox(SimulationBase):
    ID = "Q01"
    NAME = "Particle in a Box"
    CATEGORY = Category.QUANTUM
    LEVEL = Level.A_LEVEL
    EFFORT = Effort.LOW
    DESCRIPTION = "Infinite square well — energy levels, wavefunctions, and time evolution."
    TAGS = ["quantum", "wavefunction", "energy levels", "infinite well", "eigenstate"]
    HELP_TEXT = """# Particle in a Box

The infinite square well — one of the simplest exactly-solvable quantum systems and the foundation of quantum mechanics teaching.

## What it shows
A quantum particle confined between two infinitely high walls. The energy is quantised — only specific discrete values are allowed. Each energy level has a corresponding wavefunction with a characteristic number of nodes.

## The physics
- Energy levels: E_n = n^2 * pi^2 * hbar^2 / (2 * m * L^2)
- Wavefunctions: psi_n(x) = sqrt(2/L) * sin(n * pi * x / L)
- Quantum number n: 1, 2, 3, ... (n = 1 is the ground state)
- Nodes (zero crossings inside the well): n - 1
- Energy spacing: E_{n+1} - E_n grows as (2n + 1)

## Controls
- L: width of the well — wider boxes have lower energies (E ~ 1/L^2)
- n: which eigenstate to display (1 = ground state)
- levels shown: number of energy levels in the top plot
- Show |1> + |2> + |3>: superposition mode with time evolution
- speed: how fast the superposition evolves
- Play / Pause: animate the time evolution
- Compute: refresh the plots
- Reset View: return to t = 0

## Plots
- Energy Levels: discrete dots showing E_1, E_2, ..., E_n
- Wavefunction: psi(x) — real part (blue) and imaginary part (orange, in superposition mode)
- Probability Density: |psi(x)|^2 — where the particle is likely to be found

## Try this
- Start with n = 1 — the ground state has no nodes inside the well
- Increase to n = 2, 3, 4 — count the nodes (always n - 1)
- Watch the energy level spacing grow as n^2
- Toggle superposition mode and press Play — watch the probability density slosh back and forth
- Halve L and observe the energies quadruple
"""

    def __init__(self) -> None:
        self._widget: ParticleInBoxWidget | None = None

    def build_ui(self) -> QWidget:
        self._widget = ParticleInBoxWidget()
        return self._widget

    def reset(self) -> None:
        if self._widget:
            self._widget.stop()
            self._widget.set_params({
                "L": 1.0, "n": 1, "n_max": 5,
                "superposition": False, "speed": 1.0,
            })

    def export(self, path: str) -> None:
        if not self._widget:
            return
        d = Path(path)
        d.mkdir(parents=True, exist_ok=True)

        data = self._widget.get_data()
        np.savetxt(
            d / f"{self.ID}_wavefunction.csv",
            np.column_stack([data["x"], data["psi"], data["prob"]]),
            delimiter=",", header="x,psi,prob", comments="",
        )

        for name, plot in [
            ("energy_levels", self._widget._plot_energy),
            ("wavefunction", self._widget._plot_wf),
            ("probability_density", self._widget._plot_prob),
        ]:
            plot.export_png(d / f"{self.ID}_{name}.png")

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
