"""
Q02 Quantum Tunnelling — physics module.
-----------------------------------------
Transmission through a rectangular potential barrier.

For a particle of energy E < V0 (barrier height) hitting a barrier of width a:
    T = 1 / (1 + (V0^2 sinh^2(kappa*a)) / (4 E (V0 - E)))
    kappa = sqrt(2m(V0 - E)) / hbar

For E > V0 (above barrier):
    T = 1 / (1 + (V0^2 sin^2(k2*a)) / (4 E (E - V0)))
    k2 = sqrt(2m(E - V0)) / hbar

Reflection: R = 1 - T

Uses normalised units where hbar = m = 1.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def transmission_coefficient(
    E: float, V0: float, a: float, m: float = 1.0, hbar: float = 1.0,
) -> float:
    """Transmission probability through a rectangular barrier.

    Args:
        E: Particle energy.
        V0: Barrier height.
        a: Barrier width.
        m: Particle mass.
        hbar: Reduced Planck constant.

    Returns:
        Transmission probability T (between 0 and 1).
    """
    if E <= 0:
        return 0.0
    if V0 <= 0:
        return 1.0  # No barrier

    if E < V0:
        # Tunnelling regime
        kappa = np.sqrt(2 * m * (V0 - E)) / hbar
        sinh_term = np.sinh(kappa * a)
        denominator = 1.0 + (V0 ** 2 * sinh_term ** 2) / (4 * E * (V0 - E))
        return 1.0 / denominator
    elif E == V0:
        # Limiting case: T = 1 / (1 + m*V0*a^2 / (2*hbar^2))
        return 1.0 / (1.0 + m * V0 * a ** 2 / (2 * hbar ** 2))
    else:
        # Above barrier — resonances
        k2 = np.sqrt(2 * m * (E - V0)) / hbar
        sin_term = np.sin(k2 * a)
        denominator = 1.0 + (V0 ** 2 * sin_term ** 2) / (4 * E * (E - V0))
        return 1.0 / denominator


def reflection_coefficient(
    E: float, V0: float, a: float, m: float = 1.0, hbar: float = 1.0,
) -> float:
    """Reflection probability R = 1 - T."""
    return 1.0 - transmission_coefficient(E, V0, a, m, hbar)


def transmission_curve(
    E_min: float, E_max: float, V0: float, a: float,
    n_points: int = 500, m: float = 1.0, hbar: float = 1.0,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Compute T(E) over a range of energies.

    Args:
        E_min: Minimum energy (must be > 0).
        E_max: Maximum energy.
        V0: Barrier height.
        a: Barrier width.
        n_points: Number of energy samples.

    Returns:
        (E_array, T_array).
    """
    E_arr = np.linspace(max(E_min, 1e-6), E_max, n_points)
    T_arr = np.array([transmission_coefficient(E, V0, a, m, hbar) for E in E_arr])
    return E_arr, T_arr


def potential_profile(
    x: NDArray[np.float64], V0: float, a: float, x0: float = 0.0,
) -> NDArray[np.float64]:
    """Rectangular potential barrier.

    V(x) = V0 for x0 <= x <= x0+a, 0 otherwise.

    Args:
        x: Position array.
        V0: Barrier height.
        a: Barrier width.
        x0: Left edge of barrier.

    Returns:
        Potential at each position.
    """
    V = np.zeros_like(x, dtype=np.float64)
    V[(x >= x0) & (x <= x0 + a)] = V0
    return V


def stationary_state(
    x: NDArray[np.float64], E: float, V0: float, a: float,
    x0: float = 0.0, m: float = 1.0, hbar: float = 1.0,
) -> NDArray[np.complex128]:
    """Approximate stationary scattering state for a particle hitting the barrier.

    Returns the wavefunction amplitude — used for visualisation only. The
    incident wave has unit amplitude in region I (x < x0); the transmitted
    wave has amplitude sqrt(T) in region III (x > x0+a); inside the barrier
    the wavefunction decays exponentially (or oscillates if E > V0).

    Args:
        x: Position array.
        E: Particle energy.
        V0: Barrier height.
        a: Barrier width.
        x0: Left edge of barrier.

    Returns:
        Complex wavefunction.
    """
    if E <= 0:
        return np.zeros_like(x, dtype=np.complex128)

    k1 = np.sqrt(2 * m * E) / hbar
    psi = np.zeros_like(x, dtype=np.complex128)

    T = transmission_coefficient(E, V0, a, m, hbar)
    R = 1.0 - T
    r_amp = np.sqrt(R)
    t_amp = np.sqrt(T)

    # Region I: incident + reflected wave
    region_I = x < x0
    psi[region_I] = (
        np.exp(1j * k1 * x[region_I])
        + r_amp * np.exp(-1j * k1 * x[region_I])
    )

    # Region II: inside the barrier
    region_II = (x >= x0) & (x <= x0 + a)
    if E < V0:
        kappa = np.sqrt(2 * m * (V0 - E)) / hbar
        # Decaying exponential (dominant term)
        decay = np.exp(-kappa * (x[region_II] - x0))
        psi[region_II] = decay
    elif E > V0:
        k2 = np.sqrt(2 * m * (E - V0)) / hbar
        psi[region_II] = np.exp(1j * k2 * (x[region_II] - x0))
    else:
        psi[region_II] = 1.0 - (x[region_II] - x0) / a * 0.5

    # Region III: transmitted wave only
    region_III = x > x0 + a
    psi[region_III] = t_amp * np.exp(1j * k1 * (x[region_III] - x0 - a))

    return psi
