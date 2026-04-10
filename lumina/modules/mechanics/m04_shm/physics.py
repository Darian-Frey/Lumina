"""M04 Simple Harmonic Motion — physics module. No Qt imports."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def spring_omega(k: float, m: float) -> float:
    """Angular frequency for a spring-mass system: omega = sqrt(k/m)."""
    return np.sqrt(k / m)


def pendulum_omega(g: float, L: float) -> float:
    """Angular frequency for a simple pendulum: omega = sqrt(g/L)."""
    return np.sqrt(g / L)


def shm_solution(
    t: NDArray[np.float64], A: float, omega: float, phi: float,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Undamped SHM: x(t) = A*cos(omega*t + phi), v(t) = -A*omega*sin(omega*t + phi)."""
    x = A * np.cos(omega * t + phi)
    v = -A * omega * np.sin(omega * t + phi)
    return x, v


def damped_shm(
    t: NDArray[np.float64], A: float, omega0: float, gamma: float, phi: float,
) -> NDArray[np.float64]:
    """Damped SHM displacement. gamma = b/(2m).

    Returns x(t) for underdamped, critical, or overdamped regimes.
    """
    if gamma < omega0 - 1e-10:  # Underdamped
        omega_d = np.sqrt(omega0 ** 2 - gamma ** 2)
        return A * np.exp(-gamma * t) * np.cos(omega_d * t + phi)
    elif gamma > omega0 + 1e-10:  # Overdamped
        r1 = -gamma + np.sqrt(gamma ** 2 - omega0 ** 2)
        r2 = -gamma - np.sqrt(gamma ** 2 - omega0 ** 2)
        return A * 0.5 * (np.exp(r1 * t) + np.exp(r2 * t))
    else:  # Critical
        return A * (1 + gamma * t) * np.exp(-gamma * t)


def classify_damping(omega0: float, gamma: float) -> str:
    """Classify damping regime."""
    if abs(gamma - omega0) < 1e-10:
        return "critical"
    elif gamma < omega0:
        return "underdamped"
    else:
        return "overdamped"


def kinetic_energy(m: float, v: NDArray[np.float64]) -> NDArray[np.float64]:
    """KE = 0.5 * m * v^2."""
    return 0.5 * m * v ** 2


def potential_energy(k: float, x: NDArray[np.float64]) -> NDArray[np.float64]:
    """PE = 0.5 * k * x^2."""
    return 0.5 * k * x ** 2


def phase_space_ellipse(
    A: float, omega: float, n_points: int = 500,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Generate (x, v) for one full cycle in phase space."""
    theta = np.linspace(0, 2 * np.pi, n_points)
    x = A * np.cos(theta)
    v = -A * omega * np.sin(theta)
    return x, v
