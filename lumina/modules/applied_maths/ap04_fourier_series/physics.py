"""
AP04 Fourier Series Builder — physics module.
-----------------------------------------------
Compute Fourier series approximations to arbitrary periodic functions.

For a function f(x) periodic on [-pi, pi]:
    a_0 = (1/pi) integral f(x) dx from -pi to pi
    a_n = (1/pi) integral f(x) cos(nx) dx
    b_n = (1/pi) integral f(x) sin(nx) dx
    f_N(x) = a_0/2 + sum_{n=1}^{N} (a_n cos(nx) + b_n sin(nx))
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def fourier_coefficients(
    f: NDArray[np.float64],
    x: NDArray[np.float64],
    n_max: int,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Compute Fourier cosine and sine coefficients via numerical integration.

    Args:
        f: Function values sampled on x in [-pi, pi].
        x: Sample positions (uniform grid expected).
        n_max: Highest harmonic index to compute.

    Returns:
        (a_n, b_n) arrays of length n_max + 1. a[0] is a_0, a[n] is a_n, etc.
    """
    a = np.zeros(n_max + 1)
    b = np.zeros(n_max + 1)

    # a_0 = (1/pi) integral f(x) dx
    a[0] = (1.0 / np.pi) * np.trapezoid(f, x)

    for n in range(1, n_max + 1):
        a[n] = (1.0 / np.pi) * np.trapezoid(f * np.cos(n * x), x)
        b[n] = (1.0 / np.pi) * np.trapezoid(f * np.sin(n * x), x)

    return a, b


def fourier_partial_sum(
    x: NDArray[np.float64],
    a: NDArray[np.float64],
    b: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Reconstruct a function from its Fourier coefficients.

    f(x) = a_0/2 + sum (a_n cos(nx) + b_n sin(nx))
    """
    result = np.full_like(x, a[0] / 2.0)
    for n in range(1, len(a)):
        result += a[n] * np.cos(n * x) + b[n] * np.sin(n * x)
    return result


def square_wave(x: NDArray[np.float64]) -> NDArray[np.float64]:
    """Period 2*pi square wave: +1 for x > 0, -1 for x < 0."""
    return np.where(np.mod(x, 2 * np.pi) < np.pi, 1.0, -1.0)


def triangle_wave(x: NDArray[np.float64]) -> NDArray[np.float64]:
    """Period 2*pi triangle wave with peak at pi/2 and trough at -pi/2."""
    xw = np.mod(x + np.pi, 2 * np.pi) - np.pi
    return np.where(
        np.abs(xw) <= np.pi / 2,
        2.0 * xw / np.pi,
        np.sign(xw) * (2.0 - 2.0 * np.abs(xw) / np.pi),
    )


def sawtooth_wave(x: NDArray[np.float64]) -> NDArray[np.float64]:
    """Period 2*pi sawtooth wave."""
    xw = np.mod(x + np.pi, 2 * np.pi) - np.pi
    return xw / np.pi


def half_rectified_sine(x: NDArray[np.float64]) -> NDArray[np.float64]:
    """Half-wave rectified sine: max(sin(x), 0)."""
    return np.maximum(np.sin(x), 0.0)


def full_rectified_sine(x: NDArray[np.float64]) -> NDArray[np.float64]:
    """Full-wave rectified sine: |sin(x)|."""
    return np.abs(np.sin(x))


def parabola(x: NDArray[np.float64]) -> NDArray[np.float64]:
    """Parabola x^2 on [-pi, pi]."""
    xw = np.mod(x + np.pi, 2 * np.pi) - np.pi
    return xw ** 2 / np.pi ** 2  # Normalised to [0, 1]


PRESETS: dict[str, callable] = {
    "Square wave": square_wave,
    "Triangle wave": triangle_wave,
    "Sawtooth wave": sawtooth_wave,
    "Half-rectified sine": half_rectified_sine,
    "Full-rectified sine": full_rectified_sine,
    "Parabola": parabola,
}
