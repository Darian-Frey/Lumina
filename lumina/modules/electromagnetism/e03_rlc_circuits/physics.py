"""
E03 RC/RL/LC/RLC Circuits — physics module.
--------------------------------------------
Transient behaviour of simple linear circuits driven by a step voltage.

RC charging: q(t) = C*V*(1 - exp(-t/(R*C)))
RC discharging: q(t) = Q0 * exp(-t/(R*C))
RL building: i(t) = (V/R) * (1 - exp(-R*t/L))
RL decaying: i(t) = I0 * exp(-R*t/L)
LC: q(t) = Q0 * cos(omega*t), omega = 1/sqrt(L*C)
RLC: damped oscillator, three regimes (underdamped/critical/overdamped)
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def rc_charging(
    t: NDArray[np.float64], V: float, R: float, C: float,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Charge and current in an RC circuit charging from V=0 toward V.

    Returns:
        (q(t), i(t)) arrays.
    """
    tau = R * C
    q = C * V * (1.0 - np.exp(-t / tau))
    i = (V / R) * np.exp(-t / tau)
    return q, i


def rc_discharging(
    t: NDArray[np.float64], Q0: float, R: float, C: float,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Charge and current in an RC circuit discharging from Q0 to zero."""
    tau = R * C
    q = Q0 * np.exp(-t / tau)
    i = -(Q0 / (R * C)) * np.exp(-t / tau)
    return q, i


def rl_building(
    t: NDArray[np.float64], V: float, R: float, L: float,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Current and voltage across inductor in RL circuit building up.

    Returns:
        (i(t), v_L(t)) arrays.
    """
    tau = L / R
    i = (V / R) * (1.0 - np.exp(-t / tau))
    v_L = V * np.exp(-t / tau)
    return i, v_L


def rl_decaying(
    t: NDArray[np.float64], I0: float, R: float, L: float,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Current and inductor voltage in an RL circuit decaying from I0."""
    tau = L / R
    i = I0 * np.exp(-t / tau)
    v_L = -I0 * R * np.exp(-t / tau)
    return i, v_L


def lc_oscillation(
    t: NDArray[np.float64], Q0: float, L: float, C: float,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Lossless LC oscillation: q(t) = Q0*cos(omega*t).

    Returns:
        (q(t), i(t)) arrays.
    """
    omega = 1.0 / np.sqrt(L * C)
    q = Q0 * np.cos(omega * t)
    i = -Q0 * omega * np.sin(omega * t)
    return q, i


def rlc_response(
    t: NDArray[np.float64], Q0: float, R: float, L: float, C: float,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Damped RLC response from initial charge Q0, no driving voltage.

    Three regimes:
      - underdamped: alpha < omega0 -> exponentially-damped sinusoid
      - critically damped: alpha == omega0
      - overdamped: alpha > omega0 -> sum of two decaying exponentials

    Where alpha = R/(2L) and omega0 = 1/sqrt(L*C).

    Returns:
        (q(t), i(t)) arrays.
    """
    alpha = R / (2.0 * L)
    omega0 = 1.0 / np.sqrt(L * C)

    if alpha < omega0:
        omega_d = np.sqrt(omega0 ** 2 - alpha ** 2)
        q = Q0 * np.exp(-alpha * t) * (
            np.cos(omega_d * t) + (alpha / omega_d) * np.sin(omega_d * t)
        )
        i = -Q0 * np.exp(-alpha * t) * (
            omega0 ** 2 / omega_d
        ) * np.sin(omega_d * t)
    elif alpha > omega0:
        s1 = -alpha + np.sqrt(alpha ** 2 - omega0 ** 2)
        s2 = -alpha - np.sqrt(alpha ** 2 - omega0 ** 2)
        A = Q0 * s2 / (s2 - s1)
        B = -Q0 * s1 / (s2 - s1)
        q = A * np.exp(s1 * t) + B * np.exp(s2 * t)
        i = A * s1 * np.exp(s1 * t) + B * s2 * np.exp(s2 * t)
    else:
        # Critical
        q = Q0 * (1.0 + alpha * t) * np.exp(-alpha * t)
        i = -Q0 * alpha ** 2 * t * np.exp(-alpha * t)

    return q, i


def damping_regime(R: float, L: float, C: float) -> str:
    """Classify the damping regime of an RLC circuit.

    Returns:
        One of "underdamped", "critical", "overdamped".
    """
    alpha = R / (2.0 * L)
    omega0 = 1.0 / np.sqrt(L * C)
    if abs(alpha - omega0) < 1e-12:
        return "critical"
    elif alpha < omega0:
        return "underdamped"
    else:
        return "overdamped"


def resonant_frequency(L: float, C: float) -> float:
    """Resonant angular frequency omega_0 = 1/sqrt(L*C)."""
    return 1.0 / np.sqrt(L * C)


def quality_factor(R: float, L: float, C: float) -> float:
    """Quality factor Q = (1/R) * sqrt(L/C). Higher Q = sharper resonance."""
    if R <= 0:
        return float("inf")
    return (1.0 / R) * np.sqrt(L / C)
