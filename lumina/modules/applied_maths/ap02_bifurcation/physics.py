"""
AP02 Bifurcation Diagram — physics module.
-------------------------------------------
Pure maths — no Qt imports.

Logistic map: x_{n+1} = r * x_n * (1 - x_n)
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

DEFAULT_R_MIN: float = 2.5
DEFAULT_R_MAX: float = 4.0
DEFAULT_N_R: int = 1000
DEFAULT_N_ITER: int = 1000
DEFAULT_N_DISCARD: int = 500
DEFAULT_X0: float = 0.5


def logistic_map(x: float | NDArray[np.float64], r: float) -> float | NDArray[np.float64]:
    """Iterate the logistic map once: x_{n+1} = r * x * (1 - x).

    Args:
        x: Current value(s).
        r: Control parameter.

    Returns:
        Next iterate(s).
    """
    return r * x * (1.0 - x)


def compute_bifurcation(
    r_min: float = DEFAULT_R_MIN,
    r_max: float = DEFAULT_R_MAX,
    n_r: int = DEFAULT_N_R,
    n_iter: int = DEFAULT_N_ITER,
    n_discard: int = DEFAULT_N_DISCARD,
    x0: float = DEFAULT_X0,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Compute the bifurcation diagram for the logistic map.

    For each value of r, iterate the map n_iter times, discard the first
    n_discard transient iterates, and record the remaining attracting values.

    Args:
        r_min: Minimum r value.
        r_max: Maximum r value.
        n_r: Number of r values to sample.
        n_iter: Total iterations per r value.
        n_discard: Transient iterations to discard.
        x0: Initial condition.

    Returns:
        Tuple of (r_values, x_values) arrays for scatter plotting.
        Both arrays have length n_r * (n_iter - n_discard).
    """
    n_keep = n_iter - n_discard
    r_arr = np.linspace(r_min, r_max, n_r)

    # Vectorised: iterate all r values simultaneously
    x = np.full(n_r, x0, dtype=np.float64)

    # Discard transients
    for _ in range(n_discard):
        x = r_arr * x * (1.0 - x)

    # Collect attractor values
    r_out = np.empty(n_r * n_keep, dtype=np.float64)
    x_out = np.empty(n_r * n_keep, dtype=np.float64)

    for i in range(n_keep):
        x = r_arr * x * (1.0 - x)
        start = i * n_r
        r_out[start: start + n_r] = r_arr
        x_out[start: start + n_r] = x

    return r_out, x_out


def find_period(
    r: float,
    n_iter: int = 2000,
    n_discard: int = 1000,
    x0: float = DEFAULT_X0,
    tol: float = 1e-8,
) -> int:
    """Estimate the period of the logistic map at a given r.

    Args:
        r: Control parameter.
        n_iter: Total iterations.
        n_discard: Transient to discard.
        x0: Initial condition.
        tol: Tolerance for detecting repeated values.

    Returns:
        Estimated period (1 for fixed point, 2 for period-2, etc.).
        Returns -1 if no period detected (chaotic).
    """
    x = x0
    for _ in range(n_discard):
        x = r * x * (1.0 - x)

    # Record attractor values
    values: list[float] = [x]
    for _ in range(n_iter - n_discard):
        x = r * x * (1.0 - x)
        # Check if we've returned to a previous value
        for j, v in enumerate(values):
            if abs(x - v) < tol:
                return len(values) - j
        values.append(x)
        if len(values) > 256:
            return -1  # Likely chaotic

    return -1


def lyapunov_exponent(
    r: float,
    n_iter: int = 10000,
    n_discard: int = 1000,
    x0: float = DEFAULT_X0,
) -> float:
    """Compute the Lyapunov exponent of the logistic map at parameter r.

    Lambda = (1/N) * sum(ln|df/dx|) = (1/N) * sum(ln|r*(1-2x)|)

    Args:
        r: Control parameter.
        n_iter: Total iterations.
        n_discard: Transient to discard.
        x0: Initial condition.

    Returns:
        Lyapunov exponent. Negative = stable, positive = chaotic.
    """
    x = x0
    for _ in range(n_discard):
        x = r * x * (1.0 - x)

    lyap_sum = 0.0
    n = n_iter - n_discard
    for _ in range(n):
        deriv = abs(r * (1.0 - 2.0 * x))
        if deriv > 0:
            lyap_sum += np.log(deriv)
        x = r * x * (1.0 - x)

    return lyap_sum / n
