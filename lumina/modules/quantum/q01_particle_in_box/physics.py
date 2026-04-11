"""
Q01 Particle in a Box — physics module.
----------------------------------------
The infinite square well — one of the simplest exactly-solvable quantum systems.

Boundary: V(x) = 0 for 0 < x < L, infinite outside.
Energy levels: E_n = n^2 * pi^2 * hbar^2 / (2 * m * L^2)
Wavefunctions: psi_n(x) = sqrt(2/L) * sin(n * pi * x / L)
Probability density: |psi_n(x)|^2

This module uses normalised units (hbar = m = 1) for clarity. The
energy scale is then E_n = n^2 * pi^2 / (2 * L^2).
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def energy_level(n: int, L: float = 1.0, m: float = 1.0, hbar: float = 1.0) -> float:
    """Energy of the nth eigenstate of the infinite square well.

    Args:
        n: Quantum number (must be >= 1).
        L: Width of the well.
        m: Particle mass.
        hbar: Reduced Planck constant.

    Returns:
        Energy E_n.
    """
    if n < 1:
        raise ValueError(f"Quantum number n must be >= 1, got {n}")
    return (n ** 2) * (np.pi ** 2) * (hbar ** 2) / (2.0 * m * (L ** 2))


def wavefunction(
    x: NDArray[np.float64], n: int, L: float = 1.0,
) -> NDArray[np.float64]:
    """nth normalised wavefunction of the infinite square well.

    Args:
        x: Position array (should span [0, L]).
        n: Quantum number (>= 1).
        L: Width of the well.

    Returns:
        psi_n(x) as a real-valued array.
    """
    if n < 1:
        raise ValueError(f"Quantum number n must be >= 1, got {n}")
    psi = np.sqrt(2.0 / L) * np.sin(n * np.pi * x / L)
    # Wavefunction is zero outside the well
    psi[(x < 0) | (x > L)] = 0.0
    return psi


def probability_density(
    x: NDArray[np.float64], n: int, L: float = 1.0,
) -> NDArray[np.float64]:
    """Probability density |psi_n(x)|^2 for the nth eigenstate.

    Args:
        x: Position array.
        n: Quantum number.
        L: Width of the well.

    Returns:
        |psi_n(x)|^2 as an array.
    """
    psi = wavefunction(x, n, L)
    return psi ** 2


def superposition(
    x: NDArray[np.float64],
    coefficients: list[tuple[int, complex]],
    L: float = 1.0,
) -> NDArray[np.complex128]:
    """Linear superposition of eigenstates: sum c_n * psi_n(x).

    Args:
        x: Position array.
        coefficients: List of (n, c_n) pairs. c_n may be complex.
        L: Width of the well.

    Returns:
        Complex-valued wavefunction.
    """
    result = np.zeros_like(x, dtype=np.complex128)
    for n, c_n in coefficients:
        result += c_n * wavefunction(x, n, L)
    return result


def time_evolved_state(
    x: NDArray[np.float64],
    coefficients: list[tuple[int, complex]],
    t: float,
    L: float = 1.0,
    m: float = 1.0,
    hbar: float = 1.0,
) -> NDArray[np.complex128]:
    """Time-evolved superposition state.

    Each eigenstate picks up a phase factor exp(-i * E_n * t / hbar).

    Args:
        x: Position array.
        coefficients: List of (n, c_n) pairs.
        t: Time.
        L: Width of the well.
        m: Particle mass.
        hbar: Reduced Planck constant.

    Returns:
        Complex wavefunction at time t.
    """
    result = np.zeros_like(x, dtype=np.complex128)
    for n, c_n in coefficients:
        E_n = energy_level(n, L, m, hbar)
        phase = np.exp(-1j * E_n * t / hbar)
        result += c_n * phase * wavefunction(x, n, L)
    return result


def normalise_coefficients(
    coefficients: list[tuple[int, complex]],
) -> list[tuple[int, complex]]:
    """Normalise a list of expansion coefficients so that sum |c_n|^2 = 1.

    Args:
        coefficients: List of (n, c_n) pairs.

    Returns:
        Normalised coefficients.
    """
    norm_sq = sum(abs(c) ** 2 for _, c in coefficients)
    if norm_sq == 0:
        return coefficients
    norm = np.sqrt(norm_sq)
    return [(n, c / norm) for n, c in coefficients]
