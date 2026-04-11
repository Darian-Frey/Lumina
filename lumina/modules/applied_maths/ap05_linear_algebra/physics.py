"""
AP05 Linear Algebra Visualiser — physics module.
--------------------------------------------------
Visualise 2D linear transformations: matrix multiplication on point sets,
eigenvectors and eigenvalues, determinant as area scaling, SVD decomposition.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def transform_points(
    points: NDArray[np.float64], M: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Apply matrix M to a set of column vectors.

    Args:
        points: (2, N) array of N column vectors.
        M: (2, 2) transformation matrix.

    Returns:
        Transformed (2, N) array.
    """
    return M @ points


def unit_grid(n: int = 11, extent: float = 2.0) -> NDArray[np.float64]:
    """Build a square grid of points to visualise transformations.

    Args:
        n: Number of points per side.
        extent: Half-width of the grid (so range is [-extent, extent]).

    Returns:
        (2, n*n) array of column vectors.
    """
    xs = np.linspace(-extent, extent, n)
    ys = np.linspace(-extent, extent, n)
    X, Y = np.meshgrid(xs, ys)
    return np.vstack([X.ravel(), Y.ravel()])


def unit_square() -> NDArray[np.float64]:
    """The unit square as 5 column vectors (closed polygon)."""
    return np.array([
        [0.0, 1.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 1.0, 0.0],
    ])


def unit_circle(n: int = 100) -> NDArray[np.float64]:
    """Sampled unit circle as a (2, n) array."""
    theta = np.linspace(0, 2 * np.pi, n)
    return np.vstack([np.cos(theta), np.sin(theta)])


def eigenvalues_2x2(M: NDArray[np.float64]) -> NDArray[np.complex128]:
    """Eigenvalues of a 2x2 matrix.

    Returns:
        Complex array of length 2.
    """
    return np.linalg.eigvals(M)


def eigenvectors_2x2(
    M: NDArray[np.float64],
) -> tuple[NDArray[np.complex128], NDArray[np.complex128]]:
    """Eigenvalues and eigenvectors of a 2x2 matrix.

    Returns:
        (eigenvalues, eigenvectors) where eigenvectors is (2, 2) with columns
        as eigenvectors.
    """
    eigvals, eigvecs = np.linalg.eig(M)
    return eigvals, eigvecs


def determinant(M: NDArray[np.float64]) -> float:
    """Determinant of a 2x2 matrix."""
    return float(np.linalg.det(M))


def svd_2x2(
    M: NDArray[np.float64],
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """SVD decomposition: M = U Sigma V^T.

    Returns:
        (U, sigma, V_T) where U and V_T are (2, 2) and sigma is length 2.
    """
    U, sigma, V_T = np.linalg.svd(M)
    return U, sigma, V_T


# Preset transformation matrices
PRESET_MATRICES: dict[str, NDArray[np.float64]] = {
    "Identity": np.array([[1.0, 0.0], [0.0, 1.0]]),
    "Rotation 45\u00b0": np.array([
        [np.cos(np.pi / 4), -np.sin(np.pi / 4)],
        [np.sin(np.pi / 4),  np.cos(np.pi / 4)],
    ]),
    "Rotation 90\u00b0": np.array([[0.0, -1.0], [1.0, 0.0]]),
    "Scale 2x": np.array([[2.0, 0.0], [0.0, 2.0]]),
    "Scale x only": np.array([[2.0, 0.0], [0.0, 1.0]]),
    "Shear x": np.array([[1.0, 1.0], [0.0, 1.0]]),
    "Shear y": np.array([[1.0, 0.0], [1.0, 1.0]]),
    "Reflect x-axis": np.array([[1.0, 0.0], [0.0, -1.0]]),
    "Reflect y-axis": np.array([[-1.0, 0.0], [0.0, 1.0]]),
    "Singular": np.array([[1.0, 2.0], [2.0, 4.0]]),
}
