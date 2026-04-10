"""T02 Maxwell-Boltzmann Distribution — physics module. No Qt imports."""
from __future__ import annotations
import numpy as np
from numpy.typing import NDArray

K_B: float = 1.380649e-23


def mb_pdf_2d(v: NDArray[np.float64], m: float, T: float) -> NDArray[np.float64]:
    """2D Maxwell-Boltzmann speed distribution: f(v) = (m/(kT)) * v * exp(-mv^2/(2kT))."""
    return (m / (K_B * T)) * v * np.exp(-m * v ** 2 / (2 * K_B * T))


def mb_pdf_3d(v: NDArray[np.float64], m: float, T: float) -> NDArray[np.float64]:
    """3D Maxwell-Boltzmann: f(v) = 4pi*(m/(2pi*kT))^(3/2) * v^2 * exp(-mv^2/(2kT))."""
    coeff = 4 * np.pi * (m / (2 * np.pi * K_B * T)) ** 1.5
    return coeff * v ** 2 * np.exp(-m * v ** 2 / (2 * K_B * T))


def most_probable_speed(m: float, T: float) -> float:
    """v_mp = sqrt(2*kT/m)."""
    return np.sqrt(2 * K_B * T / m)


def mean_speed(m: float, T: float) -> float:
    """v_avg = sqrt(8*kT/(pi*m)) (3D)."""
    return np.sqrt(8 * K_B * T / (np.pi * m))


def rms_speed(m: float, T: float) -> float:
    """v_rms = sqrt(3*kT/m)."""
    return np.sqrt(3 * K_B * T / m)
