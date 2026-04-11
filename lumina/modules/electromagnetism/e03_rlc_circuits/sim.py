"""E03 RC/RL/LC/RLC Circuits — simulation wiring."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from PyQt6.QtWidgets import QWidget

from lumina.core.engine import Category, Effort, Level, SimulationBase
from lumina.modules.electromagnetism.e03_rlc_circuits.ui import CircuitsWidget


class RLCCircuits(SimulationBase):
    ID = "E03"
    NAME = "RC/RL/LC Circuits"
    CATEGORY = Category.ELECTROMAGNETISM
    LEVEL = Level.A_LEVEL
    EFFORT = Effort.LOW
    DESCRIPTION = "Transient and oscillatory behaviour of simple linear circuits."
    TAGS = ["circuit", "RC", "RL", "LC", "RLC", "transient", "resonance"]
    HELP_TEXT = """# RC / RL / LC / RLC Circuits

Transient and oscillatory behaviour of the four canonical first- and second-order linear circuits.

## Circuits available

### RC charging
Capacitor charging through a resistor from a step source V.
- q(t) = C V (1 - exp(-t/RC))
- i(t) = (V/R) exp(-t/RC)
- Time constant: tau = RC

### RC discharging
Charged capacitor discharging through a resistor (no source).
- q(t) = Q0 exp(-t/RC)
- Same exponential decay

### RL building
Inductor current building up under a step voltage.
- i(t) = (V/R)(1 - exp(-Rt/L))
- v_L(t) = V exp(-Rt/L)
- Time constant: tau = L/R

### RL decaying
Inductor current decaying with no source.
- i(t) = I0 exp(-Rt/L)

### LC oscillation
Lossless LC tank — perpetual oscillation.
- q(t) = Q0 cos(omega*t)
- omega = 1/sqrt(LC)

### RLC damped
Damped harmonic oscillator with three regimes:
- Underdamped (R/(2L) < omega0): exponentially-decaying oscillation
- Critically damped (R/(2L) = omega0): fastest decay without oscillation
- Overdamped (R/(2L) > omega0): slow exponential decay

## Controls
- Circuit: choose the topology
- R, L, C: component values
- V or Q0: source voltage (or initial charge for discharging modes)
- t_max: total simulation time
- Compute: refresh
- Reset View: auto-range

## Key concepts
- Time constant tau: time to decay to 1/e ≈ 37%
- Resonant frequency omega_0 = 1/sqrt(LC)
- Quality factor Q = (1/R) sqrt(L/C) — measures damping
- Higher Q means sharper resonance and longer ringing

## Try this
- Watch how doubling R doubles the RC time constant
- See critical damping in the RLC mode by setting R = 2 sqrt(L/C)
- Set R = 0 in RLC mode to recover pure LC oscillation
- Compare RC and RL time constants — they have different unit dependencies
"""

    def __init__(self) -> None:
        self._widget: CircuitsWidget | None = None

    def build_ui(self) -> QWidget:
        self._widget = CircuitsWidget()
        return self._widget

    def reset(self) -> None:
        if self._widget:
            self._widget.set_params({
                "mode": "RC charging",
                "R": 100.0, "L": 1.0, "C": 1e-3,
                "V": 5.0, "t_max": 0.5,
            })

    def export(self, path: str) -> None:
        if not self._widget:
            return
        d = Path(path)
        d.mkdir(parents=True, exist_ok=True)
        data = self._widget.get_data()
        np.savetxt(
            d / f"{self.ID}_circuit.csv",
            np.column_stack([data["t"], data["y1"], data["y2"]]),
            delimiter=",", header="t,y1,y2", comments="",
        )
        self._widget._plot_y1.export_png(d / f"{self.ID}_plot1.png")
        self._widget._plot_y2.export_png(d / f"{self.ID}_plot2.png")

    def get_state(self) -> dict[str, Any]:
        s = super().get_state()
        if self._widget:
            s["params"] = self._widget.get_params()
        return s

    def set_state(self, state: dict[str, Any]) -> None:
        if self._widget and "params" in state:
            self._widget.set_params(state["params"])
