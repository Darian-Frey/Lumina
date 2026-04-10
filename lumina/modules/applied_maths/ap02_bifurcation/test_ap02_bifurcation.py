"""Tests for AP02 — Bifurcation Diagram physics."""

from __future__ import annotations

import numpy as np
import pytest

from lumina.modules.applied_maths.ap02_bifurcation.physics import (
    compute_bifurcation,
    find_period,
    logistic_map,
    lyapunov_exponent,
)


class TestLogisticMap:
    def test_fixed_point(self) -> None:
        """At r=2, fixed point is x*=0.5."""
        x = 0.5
        assert logistic_map(x, 2.0) == pytest.approx(0.5)

    def test_known_value(self) -> None:
        assert logistic_map(0.25, 3.0) == pytest.approx(0.5625)

    def test_zero_stays_zero(self) -> None:
        assert logistic_map(0.0, 3.5) == 0.0

    def test_vectorised(self) -> None:
        x = np.array([0.0, 0.5, 1.0])
        result = logistic_map(x, 2.0)
        np.testing.assert_allclose(result, [0.0, 0.5, 0.0])


class TestComputeBifurcation:
    def test_output_shapes(self) -> None:
        r, x = compute_bifurcation(n_r=100, n_iter=200, n_discard=100)
        assert len(r) == len(x)
        assert len(r) == 100 * 100  # n_r * n_keep

    def test_r_range(self) -> None:
        r, x = compute_bifurcation(r_min=3.0, r_max=3.5, n_r=50)
        assert r.min() >= 3.0
        assert r.max() <= 3.5

    def test_x_bounded(self) -> None:
        _, x = compute_bifurcation()
        assert np.all(x >= 0)
        assert np.all(x <= 1)


class TestFindPeriod:
    def test_fixed_point_r2(self) -> None:
        """r=2 has a stable fixed point (period 1)."""
        assert find_period(2.0) == 1

    def test_period2_r3_2(self) -> None:
        """r=3.2 has a period-2 cycle."""
        assert find_period(3.2) == 2

    def test_chaotic_r3_9(self) -> None:
        """r=3.9 should be chaotic (period=-1)."""
        assert find_period(3.9) == -1


class TestLyapunovExponent:
    def test_negative_stable(self) -> None:
        """Lyapunov exponent should be negative for r=2.8 (stable period-1)."""
        assert lyapunov_exponent(2.8) < 0

    def test_positive_chaotic(self) -> None:
        """Lyapunov exponent should be positive for r=3.9 (chaotic)."""
        assert lyapunov_exponent(3.9) > 0

    def test_near_zero_at_onset(self) -> None:
        """Near the onset of chaos (~r=3.57), exponent should be close to 0."""
        lyap = lyapunov_exponent(3.57)
        assert abs(lyap) < 0.5
