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


# ---------------------------------------------------------------------------
# Generic iteration engine — all fractal types use this
# ---------------------------------------------------------------------------

def _iterate_escape(
    Z: NDArray[np.complex128],
    C: NDArray[np.complex128],
    max_iter: int,
    step_fn: str = "mandelbrot",
    power: int = 2,
) -> NDArray[np.int32]:
    """Generic escape-time iteration.

    Args:
        Z: Initial z values (height x width complex array).
        C: c values (height x width complex array).
        max_iter: Maximum iterations.
        step_fn: One of "mandelbrot", "burning_ship", "tricorn",
            "multibrot", "newton".
        power: Exponent for multibrot (z^power + c).

    Returns:
        2D array of iteration counts.
    """
    iterations = np.full(Z.shape, max_iter, dtype=np.int32)
    mask = np.ones(Z.shape, dtype=bool)

    if step_fn == "newton":
        return _newton_fractal(Z, max_iter)

    for i in range(max_iter):
        if step_fn == "mandelbrot":
            Z[mask] = Z[mask] ** 2 + C[mask]
        elif step_fn == "burning_ship":
            zr = np.abs(Z[mask].real)
            zi = np.abs(Z[mask].imag)
            Z[mask] = (zr + 1j * zi) ** 2 + C[mask]
        elif step_fn == "tricorn":
            Z[mask] = np.conj(Z[mask]) ** 2 + C[mask]
        elif step_fn == "multibrot":
            Z[mask] = Z[mask] ** power + C[mask]

        escaped = mask & (np.abs(Z) > 2.0)
        iterations[escaped] = i
        mask[escaped] = False
        if not mask.any():
            break

    return iterations


def _newton_fractal(
    Z: NDArray[np.complex128], max_iter: int, tol: float = 1e-6,
) -> NDArray[np.int32]:
    """Newton's method fractal for z^3 - 1 = 0.

    Coloured by iteration count to convergence. The three roots are
    1, e^(2pi*i/3), e^(4pi*i/3).

    Returns:
        2D array of iteration counts (converged early = low count).
    """
    iterations = np.full(Z.shape, max_iter, dtype=np.int32)
    mask = np.ones(Z.shape, dtype=bool)

    for i in range(max_iter):
        z = Z[mask]
        z2 = z * z
        z3 = z2 * z
        # Newton step: z - f(z)/f'(z) = z - (z^3 - 1)/(3z^2)
        denom = 3.0 * z2
        # Avoid division by zero
        safe = np.abs(denom) > 1e-12
        z_new = np.where(safe, z - (z3 - 1.0) / np.where(safe, denom, 1.0), z)
        Z[mask] = z_new

        # Check convergence (close to any root)
        roots = np.array([1.0, np.exp(2j * np.pi / 3), np.exp(4j * np.pi / 3)])
        converged_mask = np.zeros(z_new.shape, dtype=bool)
        for root in roots:
            converged_mask |= np.abs(z_new - root) < tol

        # Map back to full array indices
        full_converged = np.zeros(Z.shape, dtype=bool)
        full_converged[mask] = converged_mask
        just_converged = mask & full_converged
        iterations[just_converged] = i
        mask[just_converged] = False

        if not mask.any():
            break

    return iterations


# ---------------------------------------------------------------------------
# Public API — each fractal type
# ---------------------------------------------------------------------------

def _make_grid(
    x_min: float, x_max: float, y_min: float, y_max: float,
    width: int, height: int,
) -> NDArray[np.complex128]:
    """Create a complex-valued grid for the given bounds."""
    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    return x[np.newaxis, :] + 1j * y[:, np.newaxis]


def mandelbrot_set(
    x_min: float, x_max: float, y_min: float, y_max: float,
    width: int, height: int, max_iter: int = DEFAULT_MAX_ITER,
) -> NDArray[np.int32]:
    """Standard Mandelbrot set: z = z^2 + c."""
    C = _make_grid(x_min, x_max, y_min, y_max, width, height)
    Z = np.zeros_like(C)
    return _iterate_escape(Z, C, max_iter, "mandelbrot")


def julia_set(
    x_min: float, x_max: float, y_min: float, y_max: float,
    width: int, height: int, c_real: float, c_imag: float,
    max_iter: int = DEFAULT_MAX_ITER,
) -> NDArray[np.int32]:
    """Julia set: z = z^2 + c, fixed c, varying z0."""
    Z = _make_grid(x_min, x_max, y_min, y_max, width, height)
    c = complex(c_real, c_imag)
    C = np.full_like(Z, c)
    return _iterate_escape(Z, C, max_iter, "mandelbrot")


def burning_ship(
    x_min: float, x_max: float, y_min: float, y_max: float,
    width: int, height: int, max_iter: int = DEFAULT_MAX_ITER,
) -> NDArray[np.int32]:
    """Burning Ship fractal: z = (|Re(z)| + i|Im(z)|)^2 + c."""
    C = _make_grid(x_min, x_max, y_min, y_max, width, height)
    Z = np.zeros_like(C)
    return _iterate_escape(Z, C, max_iter, "burning_ship")


def tricorn(
    x_min: float, x_max: float, y_min: float, y_max: float,
    width: int, height: int, max_iter: int = DEFAULT_MAX_ITER,
) -> NDArray[np.int32]:
    """Tricorn (Mandelbar): z = conj(z)^2 + c."""
    C = _make_grid(x_min, x_max, y_min, y_max, width, height)
    Z = np.zeros_like(C)
    return _iterate_escape(Z, C, max_iter, "tricorn")


def multibrot(
    x_min: float, x_max: float, y_min: float, y_max: float,
    width: int, height: int, power: int = 3,
    max_iter: int = DEFAULT_MAX_ITER,
) -> NDArray[np.int32]:
    """Multibrot set: z = z^N + c for arbitrary integer N."""
    C = _make_grid(x_min, x_max, y_min, y_max, width, height)
    Z = np.zeros_like(C)
    return _iterate_escape(Z, C, max_iter, "multibrot", power=power)


def newton_fractal(
    x_min: float, x_max: float, y_min: float, y_max: float,
    width: int, height: int, max_iter: int = DEFAULT_MAX_ITER,
) -> NDArray[np.int32]:
    """Newton's fractal for z^3 - 1 = 0."""
    Z = _make_grid(x_min, x_max, y_min, y_max, width, height)
    return _iterate_escape(Z, Z.copy(), max_iter, "newton")


# ---------------------------------------------------------------------------
# Colour mapping
# ---------------------------------------------------------------------------

def colour_map(
    iterations: NDArray[np.int32], max_iter: int = DEFAULT_MAX_ITER,
) -> NDArray[np.uint8]:
    """Map iteration counts to RGB using cosine palette.

    Points inside the set (iterations == max_iter) are black.

    Returns:
        (height, width, 3) uint8 array.
    """
    h, w = iterations.shape
    rgb = np.zeros((h, w, 3), dtype=np.uint8)

    escaped = iterations < max_iter
    if escaped.any():
        iters = iterations[escaped].astype(np.float64)
        norm = np.log1p(iters) / np.log1p(max_iter)

        t = norm * 6.0
        r = (0.5 + 0.5 * np.cos(2.0 * np.pi * (t + 0.0))) * 255
        g = (0.5 + 0.5 * np.cos(2.0 * np.pi * (t + 0.33))) * 255
        b = (0.5 + 0.5 * np.cos(2.0 * np.pi * (t + 0.67))) * 255

        rgb[escaped, 0] = np.clip(r, 0, 255).astype(np.uint8)
        rgb[escaped, 1] = np.clip(g, 0, 255).astype(np.uint8)
        rgb[escaped, 2] = np.clip(b, 0, 255).astype(np.uint8)

    return rgb
