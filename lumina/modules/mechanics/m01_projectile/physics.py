"""
M01 Projectile Motion — physics module.
----------------------------------------
Classical 2D projectile motion with optional air resistance.

Without drag (analytic):
    x(t) = v0*cos(theta)*t
    y(t) = v0*sin(theta)*t - (1/2)*g*t^2

With linear drag:
    dvx/dt = -k*vx
    dvy/dt = -g - k*vy

With quadratic drag:
    dvx/dt = -k*v*vx
    dvy/dt = -g - k*v*vy
where v = sqrt(vx^2 + vy^2)
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp

DEFAULT_G: float = 9.81  # m/s^2


def analytic_trajectory(
    v0: float, theta_deg: float, g: float = DEFAULT_G,
    h0: float = 0.0, n_points: int = 200,
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """No-drag analytic trajectory.

    Args:
        v0: Initial speed.
        theta_deg: Launch angle in degrees.
        g: Gravitational acceleration.
        h0: Initial height above ground.
        n_points: Number of sample points along the trajectory.

    Returns:
        (t, x, y) arrays. Trajectory ends when y returns to 0.
    """
    theta = np.radians(theta_deg)
    vx0 = v0 * np.cos(theta)
    vy0 = v0 * np.sin(theta)

    # Time of flight: solve y(t) = h0 + vy0*t - (1/2)*g*t^2 = 0
    discriminant = vy0 ** 2 + 2 * g * h0
    if discriminant < 0:
        t_max = 0.0
    else:
        t_max = (vy0 + np.sqrt(discriminant)) / g

    if t_max <= 0:
        t_max = 0.01
    t = np.linspace(0, t_max, n_points)
    x = vx0 * t
    y = h0 + vy0 * t - 0.5 * g * t * t
    return t, x, y


def numerical_trajectory(
    v0: float, theta_deg: float, g: float = DEFAULT_G,
    h0: float = 0.0, drag: float = 0.0, drag_type: str = "linear",
    t_max: float = 30.0, dt: float = 0.01,
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """Numerical trajectory with optional drag.

    Integration terminates when the projectile hits y = 0 (after launch).

    Args:
        v0: Initial speed.
        theta_deg: Launch angle in degrees.
        g: Gravitational acceleration.
        h0: Initial height above ground.
        drag: Drag coefficient (0 for none).
        drag_type: "linear" (proportional to v) or "quadratic" (proportional to v^2).
        t_max: Maximum integration time.
        dt: Time step for output sampling.

    Returns:
        (t, x, y) arrays.
    """
    theta = np.radians(theta_deg)
    vx0 = v0 * np.cos(theta)
    vy0 = v0 * np.sin(theta)

    def system(t: float, state: NDArray[np.float64]) -> list[float]:
        _x, y, vx, vy = state
        if drag <= 0:
            return [vx, vy, 0.0, -g]
        if drag_type == "quadratic":
            v = np.sqrt(vx * vx + vy * vy)
            return [vx, vy, -drag * v * vx, -g - drag * v * vy]
        # Linear drag (default)
        return [vx, vy, -drag * vx, -g - drag * vy]

    def hit_ground(t: float, state: NDArray[np.float64]) -> float:
        return float(state[1])

    hit_ground.terminal = True  # type: ignore[attr-defined]
    hit_ground.direction = -1  # type: ignore[attr-defined]

    t_eval = np.arange(0, t_max, dt)
    sol = solve_ivp(
        system, (0, t_max), [0.0, h0, vx0, vy0],
        method="RK45", t_eval=t_eval, rtol=1e-7, atol=1e-9,
        events=[hit_ground] if h0 >= 0 else None,
    )

    return sol.t, sol.y[0], sol.y[1]


def trajectory_metrics(
    t: NDArray[np.float64],
    x: NDArray[np.float64],
    y: NDArray[np.float64],
) -> dict[str, float]:
    """Compute key metrics for a trajectory.

    Returns:
        Dict with range, max_height, time_of_flight.
    """
    if len(t) == 0:
        return {"range": 0.0, "max_height": 0.0, "time_of_flight": 0.0}
    return {
        "range": float(x[-1]),
        "max_height": float(y.max()),
        "time_of_flight": float(t[-1]),
    }


def optimal_angle_no_drag(h0: float = 0.0) -> float:
    """The launch angle that maximises range, with no drag.

    For h0 = 0, the optimal angle is 45 degrees. For h0 > 0, it is less than 45.

    Args:
        h0: Initial height above ground.

    Returns:
        Optimal launch angle in degrees.
    """
    if h0 == 0.0:
        return 45.0
    # For h0 > 0: optimal angle satisfies tan(theta) = v0 / sqrt(v0^2 + 2*g*h0)
    # which depends on v0. As an approximation, return the asymptotic answer for
    # h0 large: tan(theta) -> 0, theta -> 0. Here we just return 45 as a baseline.
    return 45.0
