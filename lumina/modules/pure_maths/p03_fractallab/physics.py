"""P03 FractalLab — physics module. No Qt imports."""
from __future__ import annotations
import numpy as np
from numpy.typing import NDArray

DEFAULT_MAX_ITER: int = 256


def mandelbrot_scalar(c: complex, max_iter: int = DEFAULT_MAX_ITER) -> int:
    """Return the escape iteration count for a single c value."""
    z = 0 + 0j
    for i in range(max_iter):
        z = z * z + c
        if abs(z) > 2.0:
            return i
    return max_iter


def mandelbrot_set(
    x_min: float, x_max: float, y_min: float, y_max: float,
    width: int, height: int, max_iter: int = DEFAULT_MAX_ITER,
) -> NDArray[np.int32]:
    """Compute Mandelbrot set escape iterations (vectorised).

    Returns:
        2D array of shape (height, width) with iteration counts.
    """
    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    C = x[np.newaxis, :] + 1j * y[:, np.newaxis]

    Z = np.zeros_like(C)
    iterations = np.full(C.shape, max_iter, dtype=np.int32)
    mask = np.ones(C.shape, dtype=bool)

    for i in range(max_iter):
        Z[mask] = Z[mask] ** 2 + C[mask]
        escaped = mask & (np.abs(Z) > 2.0)
        iterations[escaped] = i
        mask[escaped] = False
        if not mask.any():
            break

    return iterations


def julia_set(
    x_min: float, x_max: float, y_min: float, y_max: float,
    width: int, height: int, c_real: float, c_imag: float,
    max_iter: int = DEFAULT_MAX_ITER,
) -> NDArray[np.int32]:
    """Compute Julia set for a fixed c = c_real + i*c_imag.

    Returns:
        2D array of shape (height, width) with iteration counts.
    """
    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    Z = x[np.newaxis, :] + 1j * y[:, np.newaxis]
    c = complex(c_real, c_imag)

    iterations = np.full(Z.shape, max_iter, dtype=np.int32)
    mask = np.ones(Z.shape, dtype=bool)

    for i in range(max_iter):
        Z[mask] = Z[mask] ** 2 + c
        escaped = mask & (np.abs(Z) > 2.0)
        iterations[escaped] = i
        mask[escaped] = False
        if not mask.any():
            break

    return iterations


def colour_map(
    iterations: NDArray[np.int32], max_iter: int = DEFAULT_MAX_ITER,
) -> NDArray[np.uint8]:
    """Map iteration counts to RGB using HSV colour cycling.

    Points inside the set (iterations == max_iter) are black.

    Returns:
        (height, width, 3) uint8 array.
    """
    h, w = iterations.shape
    rgb = np.zeros((h, w, 3), dtype=np.uint8)

    escaped = iterations < max_iter
    if escaped.any():
        # Log-scaled normalisation spreads colours across the full range
        # instead of clustering near red for low iteration counts
        iters = iterations[escaped].astype(np.float64)
        norm = np.log1p(iters) / np.log1p(max_iter)

        # Map through a smooth multi-stop colour palette
        # Inspired by Ultra Fractal "classic" palette
        t = norm * 6.0  # cycle through palette multiple times for richness
        r = (0.5 + 0.5 * np.cos(2.0 * np.pi * (t + 0.0))) * 255
        g = (0.5 + 0.5 * np.cos(2.0 * np.pi * (t + 0.33))) * 255
        b = (0.5 + 0.5 * np.cos(2.0 * np.pi * (t + 0.67))) * 255

        rgb[escaped, 0] = np.clip(r, 0, 255).astype(np.uint8)
        rgb[escaped, 1] = np.clip(g, 0, 255).astype(np.uint8)
        rgb[escaped, 2] = np.clip(b, 0, 255).astype(np.uint8)

    # Inside set is black (already zeros)
    return rgb
