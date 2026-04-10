"""
AP03 Lorenz Attractor — physics module.
---------------------------------------
Pure maths / physics — no Qt imports allowed here.

The Lorenz system (1963):
    dx/dt = sigma * (y - x)
    dy/dt = x * (rho - z) - y
    dz/dt = x * y - beta * z

Default parameters: sigma=10, rho=28, beta=8/3.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp

# Default Lorenz parameters
DEFAULT_SIGMA: float = 10.0
DEFAULT_RHO: float = 28.0
DEFAULT_BETA: float = 8.0 / 3.0

# Default initial conditions
DEFAULT_IC: tuple[float, float, float] = (1.0, 1.0, 1.0)

# Default integration settings
DEFAULT_T_MAX: float = 50.0
DEFAULT_DT: float = 0.01


def lorenz_derivatives(
    t: float,
    state: NDArray[np.float64],
    sigma: float = DEFAULT_SIGMA,
    rho: float = DEFAULT_RHO,
    beta: float = DEFAULT_BETA,
) -> NDArray[np.float64]:
    """Compute the Lorenz system derivatives.

    Args:
        t: Current time (unused, required by solve_ivp interface).
        state: Array [x, y, z].
        sigma: Prandtl number.
        rho: Rayleigh number.
        beta: Geometry factor.

    Returns:
        Array [dx/dt, dy/dt, dz/dt].
    """
    x, y, z = state
    dxdt = sigma * (y - x)
    dydt = x * (rho - z) - y
    dzdt = x * y - beta * z
    return np.array([dxdt, dydt, dzdt])


def solve_lorenz(
    sigma: float = DEFAULT_SIGMA,
    rho: float = DEFAULT_RHO,
    beta: float = DEFAULT_BETA,
    ic: tuple[float, float, float] = DEFAULT_IC,
    t_max: float = DEFAULT_T_MAX,
    dt: float = DEFAULT_DT,
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """Integrate the Lorenz system using RK45.

    Args:
        sigma: Prandtl number.
        rho: Rayleigh number.
        beta: Geometry factor.
        ic: Initial conditions (x0, y0, z0).
        t_max: Maximum integration time.
        dt: Maximum time step for dense output.

    Returns:
        Tuple of (t, x, y, z) arrays.
    """
    t_span = (0.0, t_max)
    t_eval = np.arange(0.0, t_max, dt)

    sol = solve_ivp(
        fun=lambda t, state: lorenz_derivatives(t, state, sigma, rho, beta),
        t_span=t_span,
        y0=np.array(ic, dtype=np.float64),
        method="RK45",
        t_eval=t_eval,
        rtol=1e-8,
        atol=1e-10,
    )

    return sol.t, sol.y[0], sol.y[1], sol.y[2]


def compute_divergence(
    sigma: float = DEFAULT_SIGMA,
    rho: float = DEFAULT_RHO,
    beta: float = DEFAULT_BETA,
    ic1: tuple[float, float, float] = DEFAULT_IC,
    ic2: tuple[float, float, float] | None = None,
    t_max: float = DEFAULT_T_MAX,
    dt: float = DEFAULT_DT,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Compute the separation between two nearby trajectories.

    Demonstrates sensitive dependence on initial conditions.

    Args:
        sigma: Prandtl number.
        rho: Rayleigh number.
        beta: Geometry factor.
        ic1: First initial condition.
        ic2: Second initial condition. If None, perturbs ic1 by 1e-6.
        t_max: Maximum integration time.
        dt: Time step.

    Returns:
        Tuple of (t, distance) arrays where distance = |trajectory1 - trajectory2|.
    """
    if ic2 is None:
        ic2 = (ic1[0] + 1e-6, ic1[1], ic1[2])

    t1, x1, y1, z1 = solve_lorenz(sigma, rho, beta, ic1, t_max, dt)
    _, x2, y2, z2 = solve_lorenz(sigma, rho, beta, ic2, t_max, dt)

    distance = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)
    return t1, distance
