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

    # Normalise to [0, 1] for escaped points
    escaped = iterations < max_iter
    if escaped.any():
        norm = iterations[escaped].astype(np.float64) / max_iter
        # HSV colour cycle
        hue = norm * 360
        # Simple HSV->RGB using sector method
        c_val = np.ones_like(norm)  # saturation and value = 1
        h_prime = hue / 60.0
        x = c_val * (1 - np.abs(h_prime % 2 - 1))

        r = np.zeros_like(norm)
        g = np.zeros_like(norm)
        b = np.zeros_like(norm)

        for lo, hi, rv, gv, bv in [
            (0, 1, c_val, x, 0), (1, 2, x, c_val, 0), (2, 3, 0, c_val, x),
            (3, 4, 0, x, c_val), (4, 5, x, 0, c_val), (5, 6, c_val, 0, x),
        ]:
            mask = (h_prime >= lo) & (h_prime < hi)
            r[mask] = rv if isinstance(rv, int) else rv[mask]
            g[mask] = gv if isinstance(gv, int) else gv[mask]
            b[mask] = bv if isinstance(bv, int) else bv[mask]

        rgb[escaped, 0] = (r * 255).astype(np.uint8)
        rgb[escaped, 1] = (g * 255).astype(np.uint8)
        rgb[escaped, 2] = (b * 255).astype(np.uint8)

    # Inside set is black (already zeros)
    return rgb
