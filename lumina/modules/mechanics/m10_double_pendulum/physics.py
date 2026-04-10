"""
M10 Double Pendulum — physics module.
--------------------------------------
Pure maths / physics — no Qt imports allowed here.

Lagrangian mechanics for the double pendulum:
  - Two point masses m1, m2 on massless rigid rods of lengths L1, L2.
  - State: (theta1, omega1, theta2, omega2).
  - Derived from the Euler-Lagrange equations.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp

# Default parameters
DEFAULT_M1: float = 1.0     # kg
DEFAULT_M2: float = 1.0     # kg
DEFAULT_L1: float = 1.0     # m
DEFAULT_L2: float = 1.0     # m
DEFAULT_G: float = 9.81     # m/s^2

# Default initial conditions (radians and rad/s)
DEFAULT_THETA1: float = np.pi / 2  # 90 degrees
DEFAULT_OMEGA1: float = 0.0
DEFAULT_THETA2: float = np.pi      # 180 degrees
DEFAULT_OMEGA2: float = 0.0

DEFAULT_T_MAX: float = 30.0
DEFAULT_DT: float = 0.005


def double_pendulum_derivatives(
    t: float,
    state: NDArray[np.float64],
    m1: float = DEFAULT_M1,
    m2: float = DEFAULT_M2,
    L1: float = DEFAULT_L1,
    L2: float = DEFAULT_L2,
    g: float = DEFAULT_G,
) -> NDArray[np.float64]:
    """Compute derivatives for the double pendulum system.

    Uses the full Lagrangian equations of motion (no small-angle approximation).

    Args:
        t: Current time (unused, required by solve_ivp).
        state: Array [theta1, omega1, theta2, omega2].
        m1: Mass of first bob.
        m2: Mass of second bob.
        L1: Length of first rod.
        L2: Length of second rod.
        g: Gravitational acceleration.

    Returns:
        Array [dtheta1/dt, domega1/dt, dtheta2/dt, domega2/dt].
    """
    th1, w1, th2, w2 = state
    delta = th1 - th2
    sin_d = np.sin(delta)
    cos_d = np.cos(delta)
    M = m1 + m2

    # Standard double pendulum EOM (mass-matrix form, Cramer's rule).
    # Mass matrix:
    #   [[M*L1,       m2*L2*cos(d)],
    #    [L1*cos(d),  L2           ]]
    # RHS (forcing terms):
    #   f1 = -M*g*sin(th1) - m2*L2*w2^2*sin(d)
    #   f2 = L1*w1^2*sin(d) - g*sin(th2)

    f1 = -M * g * np.sin(th1) - m2 * L2 * w2 ** 2 * sin_d
    f2 = L1 * w1 ** 2 * sin_d - g * np.sin(th2)

    det = L1 * L2 * (M - m2 * cos_d ** 2)

    alpha1 = (L2 * f1 - m2 * L2 * cos_d * f2) / det
    alpha2 = (M * L1 * f2 - L1 * cos_d * f1) / det

    return np.array([w1, alpha1, w2, alpha2])


def solve_double_pendulum(
    m1: float = DEFAULT_M1,
    m2: float = DEFAULT_M2,
    L1: float = DEFAULT_L1,
    L2: float = DEFAULT_L2,
    g: float = DEFAULT_G,
    theta1: float = DEFAULT_THETA1,
    omega1: float = DEFAULT_OMEGA1,
    theta2: float = DEFAULT_THETA2,
    omega2: float = DEFAULT_OMEGA2,
    t_max: float = DEFAULT_T_MAX,
    dt: float = DEFAULT_DT,
) -> tuple[
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
]:
    """Integrate the double pendulum system.

    Returns:
        Tuple of (t, theta1, omega1, theta2, omega2) arrays.
    """
    ic = np.array([theta1, omega1, theta2, omega2], dtype=np.float64)
    t_eval = np.arange(0.0, t_max, dt)

    sol = solve_ivp(
        fun=lambda t, s: double_pendulum_derivatives(t, s, m1, m2, L1, L2, g),
        t_span=(0.0, t_max),
        y0=ic,
        method="RK45",
        t_eval=t_eval,
        rtol=1e-9,
        atol=1e-12,
    )

    return sol.t, sol.y[0], sol.y[1], sol.y[2], sol.y[3]


def pendulum_cartesian(
    theta1: NDArray[np.float64],
    theta2: NDArray[np.float64],
    L1: float = DEFAULT_L1,
    L2: float = DEFAULT_L2,
) -> tuple[
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
]:
    """Convert pendulum angles to Cartesian coordinates.

    Origin is at the pivot. Y-axis points downward (screen convention).

    Returns:
        Tuple of (x1, y1, x2, y2) arrays.
    """
    x1 = L1 * np.sin(theta1)
    y1 = -L1 * np.cos(theta1)
    x2 = x1 + L2 * np.sin(theta2)
    y2 = y1 - L2 * np.cos(theta2)
    return x1, y1, x2, y2


def total_energy(
    theta1: NDArray[np.float64],
    omega1: NDArray[np.float64],
    theta2: NDArray[np.float64],
    omega2: NDArray[np.float64],
    m1: float = DEFAULT_M1,
    m2: float = DEFAULT_M2,
    L1: float = DEFAULT_L1,
    L2: float = DEFAULT_L2,
    g: float = DEFAULT_G,
) -> NDArray[np.float64]:
    """Compute the total energy (KE + PE) of the double pendulum.

    Energy should remain constant (up to numerical integration error).

    Returns:
        Total energy array.
    """
    ke1 = 0.5 * m1 * (L1 * omega1) ** 2
    ke2 = 0.5 * m2 * (
        (L1 * omega1) ** 2
        + (L2 * omega2) ** 2
        + 2 * L1 * L2 * omega1 * omega2 * np.cos(theta1 - theta2)
    )

    pe1 = -m1 * g * L1 * np.cos(theta1)
    pe2 = -m2 * g * (L1 * np.cos(theta1) + L2 * np.cos(theta2))

    return ke1 + ke2 + pe1 + pe2
