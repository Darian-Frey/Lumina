"""Tests for AP05 — Linear Algebra Visualiser physics."""

import numpy as np
import pytest

from lumina.modules.applied_maths.ap05_linear_algebra.physics import (
    PRESET_MATRICES, determinant, eigenvalues_2x2, eigenvectors_2x2,
    svd_2x2, transform_points, unit_circle, unit_grid, unit_square,
)


class TestTransform:
    def test_identity(self) -> None:
        M = np.eye(2)
        pts = np.array([[1.0, 2.0], [3.0, 4.0]])
        result = transform_points(pts, M)
        np.testing.assert_allclose(result, pts)

    def test_rotation_90(self) -> None:
        M = np.array([[0.0, -1.0], [1.0, 0.0]])
        pts = np.array([[1.0], [0.0]])
        result = transform_points(pts, M)
        np.testing.assert_allclose(result, np.array([[0.0], [1.0]]), atol=1e-10)

    def test_scale(self) -> None:
        M = np.diag([2.0, 3.0])
        pts = np.array([[1.0, 0.0], [0.0, 1.0]])
        result = transform_points(pts, M)
        np.testing.assert_allclose(result, np.array([[2.0, 0.0], [0.0, 3.0]]))


class TestShapes:
    def test_unit_square_corners(self) -> None:
        sq = unit_square()
        assert sq.shape == (2, 5)
        # First and last point are the same (closed polygon)
        np.testing.assert_allclose(sq[:, 0], sq[:, -1])

    def test_unit_circle_radius(self) -> None:
        circle = unit_circle(100)
        radii = np.sqrt(circle[0] ** 2 + circle[1] ** 2)
        np.testing.assert_allclose(radii, np.ones(100), atol=1e-10)

    def test_unit_grid_shape(self) -> None:
        grid = unit_grid(n=5, extent=1.0)
        assert grid.shape == (2, 25)


class TestDeterminant:
    def test_identity(self) -> None:
        assert determinant(np.eye(2)) == pytest.approx(1.0)

    def test_singular(self) -> None:
        M = np.array([[1.0, 2.0], [2.0, 4.0]])
        assert determinant(M) == pytest.approx(0.0)

    def test_rotation_unit(self) -> None:
        theta = 0.7
        M = np.array([
            [np.cos(theta), -np.sin(theta)],
            [np.sin(theta),  np.cos(theta)],
        ])
        assert determinant(M) == pytest.approx(1.0)

    def test_scale(self) -> None:
        M = np.diag([2.0, 3.0])
        assert determinant(M) == pytest.approx(6.0)


class TestEigenvalues:
    def test_identity_eigenvalues_one(self) -> None:
        eigs = eigenvalues_2x2(np.eye(2))
        assert np.allclose(eigs, [1.0, 1.0])

    def test_diagonal(self) -> None:
        M = np.diag([3.0, -1.0])
        eigs = sorted(eigenvalues_2x2(M).real)
        assert eigs[0] == pytest.approx(-1.0)
        assert eigs[1] == pytest.approx(3.0)

    def test_rotation_90_complex(self) -> None:
        """A 90° rotation has imaginary eigenvalues +/- i."""
        M = np.array([[0.0, -1.0], [1.0, 0.0]])
        eigs = eigenvalues_2x2(M)
        # Both eigenvalues are purely imaginary
        assert np.allclose(eigs.real, [0.0, 0.0])


class TestEigenvectors:
    def test_diagonal_eigenvectors_are_axes(self) -> None:
        M = np.diag([3.0, 5.0])
        _, vecs = eigenvectors_2x2(M)
        # The eigenvectors of a diagonal matrix are the standard basis
        # (up to sign and ordering)
        v1 = vecs[:, 0]
        v2 = vecs[:, 1]
        # One should be along x, the other along y
        assert (
            (abs(v1[0]) > 0.99 and abs(v1[1]) < 0.01)
            or (abs(v1[0]) < 0.01 and abs(v1[1]) > 0.99)
        )


class TestSVD:
    def test_singular_values_nonneg(self) -> None:
        M = np.array([[1.5, 2.3], [-0.5, 1.0]])
        _, sigma, _ = svd_2x2(M)
        assert np.all(sigma >= 0)

    def test_reconstruct(self) -> None:
        M = np.array([[2.0, 1.0], [1.0, 3.0]])
        U, sigma, V_T = svd_2x2(M)
        reconstructed = U @ np.diag(sigma) @ V_T
        np.testing.assert_allclose(reconstructed, M, atol=1e-10)


class TestPresets:
    def test_all_presets_2x2(self) -> None:
        for name, M in PRESET_MATRICES.items():
            assert M.shape == (2, 2)
