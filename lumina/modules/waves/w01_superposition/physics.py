"""
W01 Wave Superposition — physics module.
-----------------------------------------
Pure maths — no Qt imports.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

DEFAULT_N_POINTS: int = 1000
DEFAULT_X_MAX: float = 10.0


def sine_wave(
    x: NDArray[np.float64], t: float, A: float, k: float, omega: float, phi: float,
) -> NDArray[np.float64]:
    """Compute A * sin(k*x - omega*t + phi)."""
    return A * np.sin(k * x - omega * t + phi)


def superposition(
    x: NDArray[np.float64], t: float, waves: list[tuple[float, float, float, float]],
) -> NDArray[np.float64]:
    """Sum multiple sinusoidal waves. waves = [(A, k, omega, phi), ...]."""
    result = np.zeros_like(x)
    for A, k, omega, phi in waves:
        result += sine_wave(x, t, A, k, omega, phi)
    return result


def beat_frequency(f1: float, f2: float) -> float:
    """Return |f1 - f2|."""
    return abs(f1 - f2)


def standing_wave(
    x: NDArray[np.float64], t: float, A: float, k: float, omega: float,
) -> NDArray[np.float64]:
    """Compute 2A * cos(omega*t) * sin(k*x)."""
    return 2.0 * A * np.cos(omega * t) * np.sin(k * x)


def wavelength_to_k(wavelength: float) -> float:
    """Convert wavelength to wave number k = 2*pi/lambda."""
    return 2.0 * np.pi / wavelength


def frequency_to_omega(frequency: float) -> float:
    """Convert frequency to angular frequency omega = 2*pi*f."""
    return 2.0 * np.pi * frequency
