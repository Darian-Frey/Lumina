"""AP05 Linear Algebra Visualiser — simulation wiring."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from PyQt6.QtWidgets import QWidget

from lumina.core.engine import Category, Effort, Level, SimulationBase
from lumina.modules.applied_maths.ap05_linear_algebra.ui import LinearAlgebraWidget


class LinearAlgebra(SimulationBase):
    ID = "AP05"
    NAME = "Linear Algebra Visualiser"
    CATEGORY = Category.APPLIED_MATHS
    LEVEL = Level.A_LEVEL
    EFFORT = Effort.LOW
    DESCRIPTION = "Visualise 2x2 matrix transformations, eigenvectors, and determinants."
    TAGS = ["linear algebra", "matrix", "eigenvector", "transformation", "determinant"]
    HELP_TEXT = """# Linear Algebra Visualiser

See what 2x2 matrix transformations actually do — and how eigenvectors, eigenvalues, and the determinant relate to the visual effect.

## What it shows
A 2D linear transformation y = M x applied to:
- The unit square (blue)
- The unit circle (green, becomes an ellipse)
- A coordinate grid (faint grey)
- The eigenvectors as red and orange axes (when real)

## Controls
- Preset: choose a common transformation
- Matrix M: adjust the four entries directly
  - Top row: [a, b]
  - Bottom row: [c, d]
- Compute: re-apply the matrix
- Reset View: return to the identity matrix

## Presets
- Identity: no change
- Rotation: rigid rotation by 45° or 90°
- Scale: uniform or non-uniform scaling
- Shear: skews the square
- Reflect: flips across an axis
- Singular: determinant = 0, collapses to a line

## Key concepts
- det(M) = area scaling factor (negative = orientation flipped)
- trace(M) = sum of eigenvalues
- Eigenvectors: directions that don't change under M (only scaled by lambda)
- Eigenvalues: the scaling factors along eigenvector directions
- Singular matrix (det = 0) collapses 2D space onto a line

## Try this
- Identity: see all shapes unchanged
- Rotation 45°: square stays a square but rotates
- Shear x: square becomes a parallelogram, eigenvectors aligned with x-axis
- Singular: the green circle collapses onto the red eigenvector
- Set a = d = 1 and b = c = 0.5 — symmetric matrix has perpendicular eigenvectors
"""

    def __init__(self) -> None:
        self._widget: LinearAlgebraWidget | None = None

    def build_ui(self) -> QWidget:
        self._widget = LinearAlgebraWidget()
        return self._widget

    def reset(self) -> None:
        if self._widget:
            self._widget.set_params({"preset": "Identity"})

    def export(self, path: str) -> None:
        if not self._widget:
            return
        d = Path(path)
        d.mkdir(parents=True, exist_ok=True)
        data = self._widget.get_data()
        np.savetxt(
            d / f"{self.ID}_matrix.csv",
            data["M"],
            delimiter=",", header="row1,row2", comments="",
        )
        self._widget._plot.export_png(d / f"{self.ID}_transformation.png")

    def get_state(self) -> dict[str, Any]:
        s = super().get_state()
        if self._widget:
            s["params"] = self._widget.get_params()
        return s

    def set_state(self, state: dict[str, Any]) -> None:
        if self._widget and "params" in state:
            self._widget.set_params(state["params"])
