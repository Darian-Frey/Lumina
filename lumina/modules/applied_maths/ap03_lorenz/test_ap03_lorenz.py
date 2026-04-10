"""
Tests for AP03 — Lorenz Attractor.
-----------------------------------
Physics tests must be deterministic and have 100% coverage of physics.py.
"""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import numpy as np
import pytest

from lumina.modules.applied_maths.ap03_lorenz.physics import (
    DEFAULT_BETA,
    DEFAULT_IC,
    DEFAULT_RHO,
    DEFAULT_SIGMA,
    compute_divergence,
    lorenz_derivatives,
    solve_lorenz,
)


class TestLorenzDerivatives:
    def test_at_origin_is_zero(self) -> None:
        """At (0, 0, 0) all derivatives should be zero."""
        state = np.array([0.0, 0.0, 0.0])
        result = lorenz_derivatives(0.0, state)
        np.testing.assert_allclose(result, [0.0, 0.0, 0.0])

    def test_known_values(self) -> None:
        """Check derivatives at a known point."""
        state = np.array([1.0, 1.0, 1.0])
        result = lorenz_derivatives(0.0, state, sigma=10.0, rho=28.0, beta=8.0 / 3.0)
        # dx/dt = 10*(1-1) = 0
        # dy/dt = 1*(28-1) - 1 = 26
        # dz/dt = 1*1 - (8/3)*1 = 1 - 8/3 = -5/3
        expected = np.array([0.0, 26.0, 1.0 - 8.0 / 3.0])
        np.testing.assert_allclose(result, expected, atol=1e-10)

    def test_sigma_effect(self) -> None:
        """Verify sigma only affects dx/dt."""
        state = np.array([1.0, 2.0, 3.0])
        r1 = lorenz_derivatives(0.0, state, sigma=5.0)
        r2 = lorenz_derivatives(0.0, state, sigma=20.0)
        # dx/dt differs
        assert r1[0] != r2[0]
        # dy/dt and dz/dt unchanged
        assert r1[1] == r2[1]
        assert r1[2] == r2[2]


class TestSolveLorenz:
    def test_output_shapes(self) -> None:
        """Output arrays should all have the same length."""
        t, x, y, z = solve_lorenz(t_max=1.0, dt=0.01)
        assert len(t) == len(x) == len(y) == len(z)
        assert len(t) == 100  # 1.0 / 0.01

    def test_starts_at_ic(self) -> None:
        """Trajectory should start at the initial condition."""
        t, x, y, z = solve_lorenz(ic=(5.0, 10.0, 15.0), t_max=0.1)
        np.testing.assert_allclose(x[0], 5.0, atol=1e-6)
        np.testing.assert_allclose(y[0], 10.0, atol=1e-6)
        np.testing.assert_allclose(z[0], 15.0, atol=1e-6)

    def test_bounded(self) -> None:
        """With default parameters, trajectory should stay bounded."""
        _, x, y, z = solve_lorenz(t_max=50.0)
        assert np.all(np.abs(x) < 100)
        assert np.all(np.abs(y) < 100)
        assert np.all(np.abs(z) < 100)

    def test_deterministic(self) -> None:
        """Same parameters should give identical results."""
        t1, x1, y1, z1 = solve_lorenz()
        t2, x2, y2, z2 = solve_lorenz()
        np.testing.assert_array_equal(x1, x2)
        np.testing.assert_array_equal(y1, y2)
        np.testing.assert_array_equal(z1, z2)

    def test_fixed_point_stability(self) -> None:
        """Starting near a fixed point with rho < 1 should converge to origin."""
        t, x, y, z = solve_lorenz(rho=0.5, ic=(0.1, 0.1, 0.1), t_max=20.0)
        # Should decay toward origin
        assert abs(x[-1]) < abs(x[0])
        assert abs(y[-1]) < abs(y[0])


class TestComputeDivergence:
    def test_output_shapes(self) -> None:
        """Time and distance arrays should match."""
        t, dist = compute_divergence(t_max=1.0, dt=0.01)
        assert len(t) == len(dist)

    def test_initial_separation_small(self) -> None:
        """Initial separation should be ~1e-6 (the perturbation size)."""
        _, dist = compute_divergence(t_max=0.1)
        assert dist[0] < 1e-5

    def test_divergence_grows(self) -> None:
        """Separation should grow over time (chaos)."""
        _, dist = compute_divergence(t_max=20.0)
        assert dist[-1] > dist[0] * 100  # Should grow significantly
