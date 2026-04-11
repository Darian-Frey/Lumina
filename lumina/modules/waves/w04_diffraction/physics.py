"""
W04 Diffraction & Interference — physics module.
--------------------------------------------------
Single slit, double slit, and N-slit diffraction patterns.

Single slit (Fraunhofer):
    I(theta) = I_0 * (sin(beta) / beta)^2
    where beta = (pi * a * sin(theta)) / lambda

Double slit (Young):
    I(theta) = 4 I_0 cos^2(delta/2) * (sin(beta)/beta)^2
    where delta = (2*pi*d*sin(theta)) / lambda
    Note: this includes the single-slit envelope.

N-slit grating:
    I(theta) = I_0 * (sin(N*delta/2) / sin(delta/2))^2 * (sin(beta)/beta)^2
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def single_slit_intensity(
    theta: NDArray[np.float64], a: float, wavelength: float, I0: float = 1.0,
) -> NDArray[np.float64]:
    """Fraunhofer single-slit diffraction intensity.

    Args:
        theta: Angle from central axis in radians.
        a: Slit width.
        wavelength: Light wavelength.
        I0: Central peak intensity.

    Returns:
        Intensity at each theta.
    """
    beta = (np.pi * a * np.sin(theta)) / wavelength
    # Use np.sinc to avoid division by zero (sinc(0) = 1)
    # numpy's sinc is sin(pi*x)/(pi*x), so beta/pi gives the right form
    sinc_val = np.sinc(beta / np.pi)
    return I0 * sinc_val ** 2


def double_slit_intensity(
    theta: NDArray[np.float64], a: float, d: float, wavelength: float,
    I0: float = 1.0,
) -> NDArray[np.float64]:
    """Young's double slit intensity (with single slit envelope).

    Args:
        theta: Angle from central axis.
        a: Slit width (each slit).
        d: Slit separation (centre to centre).
        wavelength: Light wavelength.
        I0: Reference intensity.

    Returns:
        Intensity at each theta.
    """
    beta = (np.pi * a * np.sin(theta)) / wavelength
    delta = (np.pi * d * np.sin(theta)) / wavelength
    envelope = np.sinc(beta / np.pi) ** 2
    interference = np.cos(delta) ** 2
    return 4 * I0 * envelope * interference


def n_slit_intensity(
    theta: NDArray[np.float64], a: float, d: float, N: int,
    wavelength: float, I0: float = 1.0,
) -> NDArray[np.float64]:
    """N-slit diffraction grating intensity.

    Args:
        theta: Angle from central axis.
        a: Slit width.
        d: Slit separation.
        N: Number of slits.
        wavelength: Light wavelength.
        I0: Reference intensity.

    Returns:
        Intensity at each theta.
    """
    beta = (np.pi * a * np.sin(theta)) / wavelength
    delta = (np.pi * d * np.sin(theta)) / wavelength
    envelope = np.sinc(beta / np.pi) ** 2

    # Multi-slit interference factor: (sin(N*delta) / sin(delta))^2
    # At points where sin(delta) -> 0, the limit is N^2 (principal maxima).
    sin_delta = np.sin(delta)
    sin_N_delta = np.sin(N * delta)
    safe_mask = np.abs(sin_delta) > 1e-12
    factor = np.full_like(delta, float(N ** 2))
    with np.errstate(divide="ignore", invalid="ignore"):
        factor[safe_mask] = (sin_N_delta[safe_mask] / sin_delta[safe_mask]) ** 2
    return I0 * envelope * factor


def fringe_spacing(d: float, wavelength: float, screen_distance: float) -> float:
    """Spacing between adjacent maxima in a Young's double-slit experiment.

    Small angle approximation: y = (m * lambda * D) / d
    Spacing: dy = (lambda * D) / d

    Args:
        d: Slit separation.
        wavelength: Light wavelength.
        screen_distance: Distance from slits to screen.

    Returns:
        Fringe spacing on the screen.
    """
    return (wavelength * screen_distance) / d


def first_minimum_angle(a: float, wavelength: float) -> float:
    """Angle of the first single-slit minimum: sin(theta) = lambda / a.

    Args:
        a: Slit width.
        wavelength: Light wavelength.

    Returns:
        Angle in radians.
    """
    if wavelength >= a:
        return np.pi / 2
    return float(np.arcsin(wavelength / a))
