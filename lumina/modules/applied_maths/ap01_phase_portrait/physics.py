"""
AP01 ODE Phase Portrait — physics module.
------------------------------------------
Pure maths — no Qt imports.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp
from scipy.optimize import fsolve

from lumina.core.utils import safe_eval

# Preset 2D ODE systems: (name, dx/dt expr, dy/dt expr, default params, x_range, y_range)
PRESET_SYSTEMS: list[tuple[str, str, str, dict[str, float], tuple[float, float], tuple[float, float]]] = [
    ("Linear 2x2", "a*x + b*y", "c*x + d*y",
     {"a": 0.0, "b": 1.0, "c": -1.0, "d": 0.0}, (-3, 3), (-3, 3)),
    ("Van der Pol", "y", "mu*(1 - x**2)*y - x",
     {"mu": 1.0}, (-4, 4), (-4, 4)),
    ("Lotka-Volterra", "a*x - b*x*y", "-c*y + d*x*y",
     {"a": 1.0, "b": 0.5, "c": 1.0, "d": 0.5}, (-0.5, 6), (-0.5, 6)),
    ("Simple Pendulum", "y", "-sin(x) - gamma*y",
     {"gamma": 0.0}, (-6, 6), (-4, 4)),
    ("Duffing (unforced)", "y", "-delta*y - alpha*x - beta*x**3",
     {"alpha": -1.0, "beta": 1.0, "delta": 0.2}, (-3, 3), (-3, 3)),
]


def _eval_expr(expr: str, x: float | NDArray, y: float | NDArray,
               params: dict[str, float]) -> float | NDArray:
    """Evaluate an expression with x, y, and extra params."""
    variables: dict[str, object] = {"x": x, "y": y, **params}
    return safe_eval(expr, variables)


def compute_vector_field(
    f_expr: str, g_expr: str, params: dict[str, float],
    x_range: tuple[float, float], y_range: tuple[float, float],
    nx: int = 20, ny: int = 20,
) -> tuple[NDArray, NDArray, NDArray, NDArray]:
    """Compute a vector field on a meshgrid for quiver plotting.

    Returns:
        (X, Y, DX, DY) meshgrids.
    """
    x_vals = np.linspace(x_range[0], x_range[1], nx)
    y_vals = np.linspace(y_range[0], y_range[1], ny)
    X, Y = np.meshgrid(x_vals, y_vals)

    DX = np.zeros_like(X)
    DY = np.zeros_like(Y)

    for i in range(ny):
        for j in range(nx):
            xv, yv = X[i, j], Y[i, j]
            DX[i, j] = float(_eval_expr(f_expr, xv, yv, params))
            DY[i, j] = float(_eval_expr(g_expr, xv, yv, params))

    # Normalise arrows for display
    mag = np.sqrt(DX ** 2 + DY ** 2)
    mag = np.maximum(mag, 1e-10)
    DX_norm = DX / mag
    DY_norm = DY / mag

    return X, Y, DX_norm, DY_norm


def find_fixed_points(
    f_expr: str, g_expr: str, params: dict[str, float],
    x_range: tuple[float, float], y_range: tuple[float, float],
    n_seeds: int = 5, tol: float = 1e-8,
) -> list[tuple[float, float]]:
    """Find fixed points by applying fsolve from a grid of starting points.

    Returns:
        List of (x, y) fixed point locations, deduplicated.
    """
    def system(state: NDArray) -> list[float]:
        xv, yv = state
        return [
            float(_eval_expr(f_expr, xv, yv, params)),
            float(_eval_expr(g_expr, xv, yv, params)),
        ]

    seeds_x = np.linspace(x_range[0], x_range[1], n_seeds)
    seeds_y = np.linspace(y_range[0], y_range[1], n_seeds)

    found: list[tuple[float, float]] = []
    for sx in seeds_x:
        for sy in seeds_y:
            try:
                sol, info, ier, _ = fsolve(system, [sx, sy], full_output=True)
                if ier == 1:
                    xf, yf = float(sol[0]), float(sol[1])
                    # Check it's within range
                    if (x_range[0] - 1 <= xf <= x_range[1] + 1
                            and y_range[0] - 1 <= yf <= y_range[1] + 1):
                        # Deduplicate
                        is_dup = any(
                            abs(xf - ex) < tol and abs(yf - ey) < tol
                            for ex, ey in found
                        )
                        if not is_dup:
                            found.append((xf, yf))
            except (ValueError, RuntimeError):
                continue

    return found


def classify_fixed_point(
    f_expr: str, g_expr: str, params: dict[str, float],
    x0: float, y0: float, h: float = 1e-7,
) -> str:
    """Classify a fixed point by computing the Jacobian numerically.

    Returns:
        One of: "stable node", "unstable node", "saddle", "stable spiral",
        "unstable spiral", "centre", "unknown".
    """
    # Numerical Jacobian via central differences
    def f(x: float, y: float) -> float:
        return float(_eval_expr(f_expr, x, y, params))

    def g(x: float, y: float) -> float:
        return float(_eval_expr(g_expr, x, y, params))

    df_dx = (f(x0 + h, y0) - f(x0 - h, y0)) / (2 * h)
    df_dy = (f(x0, y0 + h) - f(x0, y0 - h)) / (2 * h)
    dg_dx = (g(x0 + h, y0) - g(x0 - h, y0)) / (2 * h)
    dg_dy = (g(x0, y0 + h) - g(x0, y0 - h)) / (2 * h)

    J = np.array([[df_dx, df_dy], [dg_dx, dg_dy]])
    eigenvalues = np.linalg.eigvals(J)

    real_parts = eigenvalues.real
    imag_parts = eigenvalues.imag

    has_imag = np.any(np.abs(imag_parts) > 1e-8)
    both_negative = np.all(real_parts < -1e-8)
    both_positive = np.all(real_parts > 1e-8)
    mixed_sign = (real_parts[0] * real_parts[1]) < -1e-16
    near_zero = np.all(np.abs(real_parts) < 1e-8)

    if mixed_sign and not has_imag:
        return "saddle"
    elif has_imag:
        if near_zero:
            return "centre"
        elif both_negative:
            return "stable spiral"
        elif both_positive:
            return "unstable spiral"
    else:
        if both_negative:
            return "stable node"
        elif both_positive:
            return "unstable node"

    return "unknown"


def compute_trajectory(
    f_expr: str, g_expr: str, params: dict[str, float],
    x0: float, y0: float, t_max: float = 20.0, dt: float = 0.02,
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """Integrate a single trajectory from (x0, y0).

    Returns:
        (t, x, y) arrays.
    """
    def system(t: float, state: NDArray) -> list[float]:
        xv, yv = state
        return [
            float(_eval_expr(f_expr, xv, yv, params)),
            float(_eval_expr(g_expr, xv, yv, params)),
        ]

    t_eval = np.arange(0, t_max, dt)
    sol = solve_ivp(
        system, (0, t_max), [x0, y0],
        method="RK45", t_eval=t_eval, rtol=1e-8, atol=1e-10,
    )
    return sol.t, sol.y[0], sol.y[1]
