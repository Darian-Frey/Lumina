"""Tests for M10 — Double Pendulum physics."""

from __future__ import annotations

import numpy as np
import pytest

from lumina.modules.mechanics.m10_double_pendulum.physics import (
    double_pendulum_derivatives,
    pendulum_cartesian,
    solve_double_pendulum,
    total_energy,
)


class TestDerivatives:
    def test_at_rest_hanging_down(self) -> None:
        """Both pendulums hanging straight down (theta=0) with no velocity."""
        state = np.array([0.0, 0.0, 0.0, 0.0])
        result = double_pendulum_derivatives(0.0, state)
        # No angular velocity, no torque at equilibrium
        np.testing.assert_allclose(result, [0.0, 0.0, 0.0, 0.0], atol=1e-10)

    def test_returns_correct_shape(self) -> None:
        state = np.array([1.0, 0.5, 2.0, -0.3])
        result = double_pendulum_derivatives(0.0, state)
        assert result.shape == (4,)


class TestSolve:
    def test_output_shapes(self) -> None:
        t, th1, w1, th2, w2 = solve_double_pendulum(t_max=1.0, dt=0.01)
        assert len(t) == len(th1) == len(w1) == len(th2) == len(w2)
        assert len(t) == 100

    def test_starts_at_ic(self) -> None:
        t, th1, w1, th2, w2 = solve_double_pendulum(
            theta1=0.5, omega1=0.1, theta2=1.0, omega2=-0.2, t_max=0.1,
        )
        np.testing.assert_allclose(th1[0], 0.5, atol=1e-6)
        np.testing.assert_allclose(w1[0], 0.1, atol=1e-6)
        np.testing.assert_allclose(th2[0], 1.0, atol=1e-6)
        np.testing.assert_allclose(w2[0], -0.2, atol=1e-6)

    def test_energy_conservation(self) -> None:
        """Total energy should be approximately conserved."""
        t, th1, w1, th2, w2 = solve_double_pendulum(t_max=10.0)
        E = total_energy(th1, w1, th2, w2)
        # Energy drift should be < 0.1% of initial energy
        E0 = E[0]
        drift = np.max(np.abs(E - E0))
        assert drift < abs(E0) * 0.001, f"Energy drift {drift} exceeds 0.1% of E0={E0}"


class TestCartesian:
    def test_hanging_down(self) -> None:
        """Both at theta=0 should give x=0, y pointing down."""
        th1 = np.array([0.0])
        th2 = np.array([0.0])
        x1, y1, x2, y2 = pendulum_cartesian(th1, th2, L1=1.0, L2=1.0)
        np.testing.assert_allclose(x1, [0.0], atol=1e-10)
        np.testing.assert_allclose(y1, [-1.0], atol=1e-10)
        np.testing.assert_allclose(x2, [0.0], atol=1e-10)
        np.testing.assert_allclose(y2, [-2.0], atol=1e-10)

    def test_horizontal(self) -> None:
        """theta1 = pi/2 should put bob1 at (L1, 0)."""
        th1 = np.array([np.pi / 2])
        th2 = np.array([np.pi / 2])
        x1, y1, x2, y2 = pendulum_cartesian(th1, th2, L1=1.0, L2=1.0)
        np.testing.assert_allclose(x1, [1.0], atol=1e-10)
        np.testing.assert_allclose(y1, [0.0], atol=1e-10)
        np.testing.assert_allclose(x2, [2.0], atol=1e-10)
        np.testing.assert_allclose(y2, [0.0], atol=1e-10)


class TestEnergy:
    def test_at_rest_hanging_down(self) -> None:
        """Energy at equilibrium position (both hanging down, no velocity)."""
        th1 = np.array([0.0])
        w1 = np.array([0.0])
        th2 = np.array([0.0])
        w2 = np.array([0.0])
        E = total_energy(th1, w1, th2, w2, m1=1.0, m2=1.0, L1=1.0, L2=1.0, g=9.81)
        # PE = -m1*g*L1 - m2*g*(L1+L2) = -9.81 - 19.62 = -29.43
        expected = -1.0 * 9.81 * 1.0 - 1.0 * 9.81 * 2.0
        np.testing.assert_allclose(E, [expected], atol=1e-10)
