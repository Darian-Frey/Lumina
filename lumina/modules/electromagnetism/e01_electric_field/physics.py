"""
E01 Electric Field Lines — physics module.
-------------------------------------------
Compute the electric field from a collection of point charges
using Coulomb's law.

Uses Gaussian units with k = 1 for clarity. The shape of the
field is independent of unit choice.

E(r) = sum_i q_i * (r - r_i) / |r - r_i|^3
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

# Charge tuple type: (x, y, q)
Charge = tuple[float, float, float]


def coulomb_field(
    X: NDArray[np.float64],
    Y: NDArray[np.float64],
    charges: list[Charge],
    softening: float = 0.05,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Compute the electric field at every point in (X, Y) from a list of charges.

    Args:
        X: Meshgrid of x coordinates.
        Y: Meshgrid of y coordinates.
        charges: List of (x, y, q) tuples.
        softening: Small distance added to avoid singularities at charge locations.

    Returns:
        Tuple of (Ex, Ey) field component meshgrids.
    """
    Ex = np.zeros_like(X, dtype=np.float64)
    Ey = np.zeros_like(Y, dtype=np.float64)

    for cx, cy, q in charges:
        dx = X - cx
        dy = Y - cy
        r_sq = dx * dx + dy * dy + softening * softening
        r3 = r_sq ** 1.5
        Ex += q * dx / r3
        Ey += q * dy / r3

    return Ex, Ey


def field_magnitude(
    Ex: NDArray[np.float64], Ey: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Magnitude of the electric field at every point."""
    return np.sqrt(Ex ** 2 + Ey ** 2)


def potential(
    X: NDArray[np.float64],
    Y: NDArray[np.float64],
    charges: list[Charge],
    softening: float = 0.05,
) -> NDArray[np.float64]:
    """Compute the electric potential V(r) = sum_i q_i / |r - r_i|.

    Args:
        X: Meshgrid of x coordinates.
        Y: Meshgrid of y coordinates.
        charges: List of (x, y, q) tuples.
        softening: Distance softening to avoid divergences.

    Returns:
        Potential meshgrid.
    """
    V = np.zeros_like(X, dtype=np.float64)
    for cx, cy, q in charges:
        dx = X - cx
        dy = Y - cy
        r = np.sqrt(dx * dx + dy * dy + softening * softening)
        V += q / r
    return V


def trace_field_line(
    x0: float, y0: float, charges: list[Charge],
    direction: int = 1,
    n_steps: int = 1000,
    step_size: float = 0.02,
    bounds: tuple[float, float, float, float] | None = None,
    min_distance_sq: float = 0.01,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Trace a field line starting from (x0, y0).

    Uses RK4-style integration along the normalised field direction.

    Args:
        x0, y0: Starting position.
        charges: List of (x, y, q) tuples.
        direction: +1 to follow field forward, -1 to follow backward.
        n_steps: Maximum integration steps.
        step_size: Distance per step.
        bounds: Optional (xmin, xmax, ymin, ymax) for early termination.
        min_distance_sq: Squared distance to a charge that terminates the line.

    Returns:
        Tuple of (x_path, y_path) arrays.
    """
    xs = [x0]
    ys = [y0]
    x, y = x0, y0

    for _ in range(n_steps):
        # Get normalised field direction
        Ex, Ey = _field_at_point(x, y, charges)
        mag = np.sqrt(Ex * Ex + Ey * Ey)
        if mag < 1e-12:
            break

        dx = direction * step_size * Ex / mag
        dy = direction * step_size * Ey / mag
        x += dx
        y += dy
        xs.append(x)
        ys.append(y)

        # Stop if we're very close to a charge
        for cx, cy, _ in charges:
            if (x - cx) ** 2 + (y - cy) ** 2 < min_distance_sq:
                return np.array(xs), np.array(ys)

        # Stop if outside bounds
        if bounds is not None:
            xmin, xmax, ymin, ymax = bounds
            if x < xmin or x > xmax or y < ymin or y > ymax:
                break

    return np.array(xs), np.array(ys)


def _field_at_point(
    x: float, y: float, charges: list[Charge], softening: float = 0.05,
) -> tuple[float, float]:
    """Field at a single point — used internally for line tracing."""
    Ex = 0.0
    Ey = 0.0
    for cx, cy, q in charges:
        dx = x - cx
        dy = y - cy
        r_sq = dx * dx + dy * dy + softening * softening
        r3 = r_sq ** 1.5
        Ex += q * dx / r3
        Ey += q * dy / r3
    return Ex, Ey


def generate_field_lines(
    charges: list[Charge],
    n_lines_per_charge: int = 16,
    bounds: tuple[float, float, float, float] = (-3, 3, -3, 3),
) -> list[tuple[NDArray[np.float64], NDArray[np.float64]]]:
    """Generate field lines starting near each charge.

    For positive charges, lines start outward (forward integration).
    For negative charges, lines are traced backward from the seed positions.
    The number of lines is proportional to |q|.

    Args:
        charges: List of (x, y, q) tuples.
        n_lines_per_charge: Base number of lines for unit charge magnitude.
        bounds: View bounds for line termination.

    Returns:
        List of (x_path, y_path) arrays, one per traced line.
    """
    lines: list[tuple[NDArray[np.float64], NDArray[np.float64]]] = []
    seed_radius = 0.08

    for cx, cy, q in charges:
        if q == 0:
            continue
        n_lines = max(4, int(n_lines_per_charge * abs(q)))
        direction = 1 if q > 0 else -1

        for i in range(n_lines):
            angle = 2 * np.pi * i / n_lines
            sx = cx + seed_radius * np.cos(angle)
            sy = cy + seed_radius * np.sin(angle)

            try:
                xs, ys = trace_field_line(
                    sx, sy, charges,
                    direction=direction,
                    bounds=bounds,
                )
                if len(xs) > 2:
                    lines.append((xs, ys))
            except (ValueError, RuntimeError):
                continue

    return lines
