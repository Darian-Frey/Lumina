"""Tests for AP01 — ODE Phase Portrait physics."""

import numpy as np
import pytest

from lumina.modules.applied_maths.ap01_phase_portrait.physics import (
    classify_fixed_point, compute_trajectory, compute_vector_field,
    find_fixed_points,
)


class TestVectorField:
    def test_shape(self) -> None:
        X, Y, DX, DY = compute_vector_field("y", "-x", {}, (-3, 3), (-3, 3), 10, 10)
        assert X.shape == (10, 10)
        assert DX.shape == (10, 10)

    def test_normalised(self) -> None:
        _, _, DX, DY = compute_vector_field("y", "-x", {}, (-3, 3), (-3, 3), 10, 10)
        mag = np.sqrt(DX ** 2 + DY ** 2)
        # All non-zero arrows should be unit length
        np.testing.assert_allclose(mag[mag > 0.01], 1.0, atol=1e-6)


class TestFixedPoints:
    def test_linear_origin(self) -> None:
        fps = find_fixed_points("y", "-x", {}, (-3, 3), (-3, 3))
        assert any(abs(x) < 0.01 and abs(y) < 0.01 for x, y in fps)

    def test_lotka_volterra(self) -> None:
        params = {"a": 1.0, "b": 0.5, "c": 1.0, "d": 0.5}
        fps = find_fixed_points(
            "a*x - b*x*y", "-c*y + d*x*y", params, (-0.5, 6), (-0.5, 6),
        )
        # Should find (0, 0) and (c/d, a/b) = (2, 2)
        assert any(abs(x) < 0.1 and abs(y) < 0.1 for x, y in fps)
        assert any(abs(x - 2.0) < 0.1 and abs(y - 2.0) < 0.1 for x, y in fps)


class TestClassification:
    def test_centre(self) -> None:
        # dx/dt = y, dy/dt = -x is a centre at origin
        cls = classify_fixed_point("y", "-x", {}, 0.0, 0.0)
        assert cls == "centre"

    def test_saddle(self) -> None:
        # dx/dt = x, dy/dt = -y has eigenvalues +1, -1
        cls = classify_fixed_point("x", "-y", {}, 0.0, 0.0)
        assert cls == "saddle"

    def test_stable_node(self) -> None:
        # dx/dt = -x, dy/dt = -2*y
        cls = classify_fixed_point("-x", "-2*y", {}, 0.0, 0.0)
        assert cls == "stable node"

    def test_unstable_node(self) -> None:
        cls = classify_fixed_point("x", "2*y", {}, 0.0, 0.0)
        assert cls == "unstable node"


class TestTrajectory:
    def test_starts_at_ic(self) -> None:
        t, x, y = compute_trajectory("y", "-x", {}, 1.0, 0.0, t_max=0.1)
        assert abs(x[0] - 1.0) < 1e-6
        assert abs(y[0] - 0.0) < 1e-6

    def test_output_shapes(self) -> None:
        t, x, y = compute_trajectory("y", "-x", {}, 1.0, 0.0, t_max=1.0, dt=0.01)
        assert len(t) == len(x) == len(y)
        assert len(t) == 100
