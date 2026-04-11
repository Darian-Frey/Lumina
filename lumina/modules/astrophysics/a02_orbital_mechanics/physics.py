"""
A02 Orbital Mechanics — physics module.
----------------------------------------
Two-body Keplerian orbits — closed-form ellipse and numerical integration.

Uses normalised units where GM = 1. Distance unit = AU-like, time unit
chosen so that a circular orbit at r = 1 has period 2*pi.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp

GM_DEFAULT: float = 1.0


def kepler_orbit(
    a: float, e: float, n_points: int = 360,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Closed-form Keplerian orbit (ellipse) in the orbital plane.

    The orbit equation in polar form: r = a(1 - e^2) / (1 + e cos(theta))

    Args:
        a: Semi-major axis.
        e: Eccentricity (0 = circle, 0 <= e < 1 for ellipse).
        n_points: Number of sample points around the orbit.

    Returns:
        (x, y) arrays of orbit positions.
    """
    theta = np.linspace(0, 2 * np.pi, n_points)
    r = a * (1 - e ** 2) / (1 + e * np.cos(theta))
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y


def orbital_period(a: float, GM: float = GM_DEFAULT) -> float:
    """Orbital period from Kepler's third law: T = 2*pi*sqrt(a^3/GM).

    Args:
        a: Semi-major axis.
        GM: Gravitational parameter of the central body.

    Returns:
        Period.
    """
    return 2 * np.pi * np.sqrt(a ** 3 / GM)


def vis_viva(r: float, a: float, GM: float = GM_DEFAULT) -> float:
    """Vis-viva speed at distance r from a body in an orbit of semi-major axis a.

    v^2 = GM * (2/r - 1/a)

    Args:
        r: Current distance.
        a: Semi-major axis.
        GM: Gravitational parameter.

    Returns:
        Speed.
    """
    return float(np.sqrt(GM * (2.0 / r - 1.0 / a)))


def numerical_orbit(
    r0: float, v0: float, theta0: float = 0.0,
    GM: float = GM_DEFAULT, t_max: float = 20.0, dt: float = 0.05,
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """Numerically integrate a two-body orbit.

    Args:
        r0: Initial distance from the central mass.
        v0: Initial speed (perpendicular to the radial direction by default).
        theta0: Initial angle (radians).
        GM: Gravitational parameter.
        t_max: Maximum integration time.
        dt: Time step for output.

    Returns:
        (t, x, y) arrays.
    """
    x0 = r0 * np.cos(theta0)
    y0 = r0 * np.sin(theta0)
    # Velocity perpendicular to radial direction (counter-clockwise)
    vx0 = -v0 * np.sin(theta0)
    vy0 = v0 * np.cos(theta0)

    def system(t: float, state: NDArray[np.float64]) -> list[float]:
        x, y, vx, vy = state
        r3 = (x * x + y * y) ** 1.5
        return [vx, vy, -GM * x / r3, -GM * y / r3]

    t_eval = np.arange(0, t_max, dt)
    sol = solve_ivp(
        system, (0, t_max), [x0, y0, vx0, vy0],
        method="RK45", t_eval=t_eval, rtol=1e-9, atol=1e-12,
    )
    return sol.t, sol.y[0], sol.y[1]


def orbital_energy(
    r: float, v: float, GM: float = GM_DEFAULT,
) -> float:
    """Specific orbital energy: epsilon = v^2/2 - GM/r.

    Negative -> bound (elliptic), zero -> parabolic, positive -> hyperbolic.
    """
    return v ** 2 / 2.0 - GM / r


def semi_major_axis_from_energy(
    energy: float, GM: float = GM_DEFAULT,
) -> float:
    """a = -GM / (2 epsilon) for a bound orbit."""
    if energy >= 0:
        return float("inf")
    return -GM / (2.0 * energy)


def hohmann_transfer(
    r1: float, r2: float, GM: float = GM_DEFAULT,
) -> tuple[float, float, float]:
    """Compute Hohmann transfer between two circular orbits.

    Args:
        r1: Initial circular orbit radius.
        r2: Final circular orbit radius.
        GM: Gravitational parameter.

    Returns:
        (delta_v1, delta_v2, transfer_time) — velocity changes at each end
        and the time for the transfer half-orbit.
    """
    a_t = (r1 + r2) / 2.0
    v1_circ = np.sqrt(GM / r1)
    v2_circ = np.sqrt(GM / r2)
    v_peri = np.sqrt(GM * (2.0 / r1 - 1.0 / a_t))
    v_apo = np.sqrt(GM * (2.0 / r2 - 1.0 / a_t))
    dv1 = float(v_peri - v1_circ)
    dv2 = float(v2_circ - v_apo)
    t_transfer = float(np.pi * np.sqrt(a_t ** 3 / GM))
    return dv1, dv2, t_transfer
