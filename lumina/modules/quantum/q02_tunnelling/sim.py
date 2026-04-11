"""Q02 Quantum Tunnelling — simulation wiring."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from PyQt6.QtWidgets import QWidget

from lumina.core.engine import Category, Effort, Level, SimulationBase
from lumina.modules.quantum.q02_tunnelling.ui import TunnellingWidget


class QuantumTunnelling(SimulationBase):
    ID = "Q02"
    NAME = "Quantum Tunnelling"
    CATEGORY = Category.QUANTUM
    LEVEL = Level.A_LEVEL
    EFFORT = Effort.LOW
    DESCRIPTION = "Particle tunnelling through a rectangular potential barrier."
    TAGS = ["quantum", "tunnelling", "barrier", "transmission", "wavefunction"]
    HELP_TEXT = """# Quantum Tunnelling

One of the most counterintuitive predictions of quantum mechanics: a particle can pass through a barrier even when its energy is less than the barrier height.

## What it shows
A quantum particle of energy E hitting a rectangular potential barrier of height V0 and width a. Classically, if E < V0 the particle bounces back. Quantum mechanically, there is a non-zero probability T that it tunnels through.

## The physics

For E < V0 (tunnelling regime):
- T = 1 / (1 + (V0^2 sinh^2(kappa*a)) / (4 E (V0 - E)))
- kappa = sqrt(2m(V0 - E)) / hbar
- T decreases exponentially with barrier width

For E > V0 (above barrier):
- T = 1 / (1 + (V0^2 sin^2(k2*a)) / (4 E (E - V0)))
- T oscillates — perfect transmission at certain energies (resonances)

Reflection: R = 1 - T

## Controls
- E: particle energy (in normalised units)
- V0: barrier height
- a: barrier width
- Compute: refresh the plots
- Reset View: redraw at default scale

## Plots
- Top: the barrier (grey) with the wavefunction shown as Re[psi] (blue) and Im[psi] (orange). The horizontal red dashed line shows the energy E.
- Bottom: transmission probability T(E) as a function of energy. The current operating point is marked with a dot.

## Try this
- Start with E < V0 — see the wavefunction decay exponentially inside the barrier
- Increase E above V0 — the wavefunction oscillates inside the barrier
- Watch for resonances in T(E) above V0 where T = 1 (perfect transmission)
- Halve the barrier width a — tunnelling probability rises dramatically
- Try E very close to V0 — interesting transitional behaviour

## Real-world examples
- Alpha decay (alpha particles tunnel out of nuclei)
- Scanning Tunnelling Microscope (electrons tunnel between tip and sample)
- Tunnel diodes
- Field emission from cold cathodes
"""

    def __init__(self) -> None:
        self._widget: TunnellingWidget | None = None

    def build_ui(self) -> QWidget:
        self._widget = TunnellingWidget()
        return self._widget

    def reset(self) -> None:
        if self._widget:
            self._widget.set_params({"E": 2.0, "V0": 5.0, "a": 1.5})

    def export(self, path: str) -> None:
        if not self._widget:
            return
        d = Path(path)
        d.mkdir(parents=True, exist_ok=True)
        data = self._widget.get_data()
        np.savetxt(
            d / f"{self.ID}_transmission.csv",
            np.column_stack([data["E"], data["T"]]),
            delimiter=",", header="E,T", comments="",
        )
        self._widget._plot_wf.export_png(d / f"{self.ID}_wavefunction.png")
        self._widget._plot_T.export_png(d / f"{self.ID}_transmission.png")

    def get_state(self) -> dict[str, Any]:
        s = super().get_state()
        if self._widget:
            s["params"] = self._widget.get_params()
        return s

    def set_state(self, state: dict[str, Any]) -> None:
        if self._widget and "params" in state:
            self._widget.set_params(state["params"])
