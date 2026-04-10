"""
W02 Fourier Synthesiser — physics module.
------------------------------------------
Pure maths — no Qt imports.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def square_wave_coefficients(n_max: int) -> list[tuple[int, float]]:
    """Fourier sine coefficients for a square wave. b_n = 4/(n*pi) for odd n."""
    return [(n, 4.0 / (n * np.pi)) for n in range(1, n_max + 1, 2)]


def triangle_wave_coefficients(n_max: int) -> list[tuple[int, float]]:
    """Fourier sine coefficients for a triangle wave."""
    coeffs = []
    for n in range(1, n_max + 1, 2):
        b_n = 8.0 * (-1) ** ((n - 1) // 2) / (n ** 2 * np.pi ** 2)
        coeffs.append((n, b_n))
    return coeffs


def sawtooth_wave_coefficients(n_max: int) -> list[tuple[int, float]]:
    """Fourier sine coefficients for a sawtooth wave. b_n = -2*(-1)^n/(n*pi)."""
    return [(n, -2.0 * (-1) ** n / (n * np.pi)) for n in range(1, n_max + 1)]


def fourier_partial_sum(
    x: NDArray[np.float64], coefficients: list[tuple[int, float]],
) -> NDArray[np.float64]:
    """Compute the partial Fourier sum: sum of b_n * sin(n * x)."""
    result = np.zeros_like(x)
    for n, b_n in coefficients:
        result += b_n * np.sin(n * x)
    return result


def target_waveform(x: NDArray[np.float64], kind: str) -> NDArray[np.float64]:
    """Return the exact target waveform over [-pi, pi] periodically extended.

    Args:
        x: Spatial array.
        kind: One of "square", "triangle", "sawtooth".

    Returns:
        Waveform values normalised to [-1, 1].
    """
    # Wrap to [-pi, pi]
    xw = np.mod(x + np.pi, 2 * np.pi) - np.pi

    if kind == "square":
        return np.sign(xw)
    elif kind == "triangle":
        return 2.0 * np.abs(xw) / np.pi - 1.0
    elif kind == "sawtooth":
        return xw / np.pi
    else:
        raise ValueError(f"Unknown waveform: {kind}")


def gibbs_overshoot(
    coefficients: list[tuple[int, float]], n_sample: int = 10000,
) -> float:
    """Estimate the Gibbs overshoot as a percentage above the target max (1.0).

    Returns:
        Overshoot percentage (e.g. 8.95 for ~9% Gibbs overshoot).
    """
    x = np.linspace(-np.pi, np.pi, n_sample)
    y = fourier_partial_sum(x, coefficients)
    peak = np.max(y)
    return max(0.0, (peak - 1.0) * 100.0)
