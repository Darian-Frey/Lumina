"""Tests for M01 — Projectile Motion physics."""

import numpy as np
import pytest

from lumina.modules.mechanics.m01_projectile.physics import (
    analytic_trajectory, numerical_trajectory, optimal_angle_no_drag,
    trajectory_metrics,
)


class TestAnalyticTrajectory:
    def test_starts_at_origin(self) -> None:
        t, x, y = analytic_trajectory(v0=20, theta_deg=45)
        assert x[0] == pytest.approx(0.0)
        assert y[0] == pytest.approx(0.0)

    def test_ends_at_ground(self) -> None:
        t, x, y = analytic_trajectory(v0=20, theta_deg=45)
        assert y[-1] == pytest.approx(0.0, abs=0.01)

    def test_45_degrees_max_range(self) -> None:
        """45 degrees should give the maximum range when h0 = 0."""
        ranges = []
        for theta in [30, 40, 45, 50, 60]:
            _, x, _ = analytic_trajectory(v0=20, theta_deg=theta)
            ranges.append(x[-1])
        # The middle value (45) should be the largest
        assert max(ranges) == ranges[2]

    def test_range_formula(self) -> None:
        """Range = v0^2 sin(2theta) / g."""
        v0 = 25.0
        theta = 30.0
        g = 9.81
        _, x, _ = analytic_trajectory(v0=v0, theta_deg=theta, g=g)
        expected = v0 ** 2 * np.sin(np.radians(2 * theta)) / g
        assert x[-1] == pytest.approx(expected, abs=0.05)

    def test_max_height_formula(self) -> None:
        """Max height = (v0 sin(theta))^2 / (2g)."""
        v0 = 20.0
        theta = 60.0
        g = 9.81
        _, _, y = analytic_trajectory(v0=v0, theta_deg=theta, g=g, n_points=1000)
        expected = (v0 * np.sin(np.radians(theta))) ** 2 / (2 * g)
        assert y.max() == pytest.approx(expected, abs=0.01)


class TestNumericalTrajectory:
    def test_no_drag_matches_analytic(self) -> None:
        """Without drag, numerical should match analytic to high precision."""
        v0, theta = 25.0, 40.0
        _, x_a, y_a = analytic_trajectory(v0, theta, n_points=500)
        _, x_n, y_n = numerical_trajectory(v0, theta, drag=0.0)
        # Compare the range
        assert x_n[-1] == pytest.approx(x_a[-1], abs=0.5)
        # Compare the max height
        assert y_n.max() == pytest.approx(y_a.max(), abs=0.1)

    def test_drag_reduces_range(self) -> None:
        v0, theta = 30.0, 45.0
        _, x_no_drag, _ = numerical_trajectory(v0, theta, drag=0.0)
        _, x_drag, _ = numerical_trajectory(v0, theta, drag=0.05)
        assert x_drag[-1] < x_no_drag[-1]

    def test_quadratic_drag_works(self) -> None:
        _, x, y = numerical_trajectory(
            v0=30, theta_deg=45, drag=0.01, drag_type="quadratic",
        )
        assert len(x) > 0
        assert y[-1] == pytest.approx(0.0, abs=0.5)

    def test_initial_height(self) -> None:
        """Starting from h0 > 0 should give a longer flight."""
        _, _, _ = numerical_trajectory(v0=20, theta_deg=45, h0=0.0)
        _, _, _ = numerical_trajectory(v0=20, theta_deg=45, h0=10.0)
        # With h0 > 0, the projectile takes longer to reach the ground
        m1 = trajectory_metrics(*numerical_trajectory(v0=20, theta_deg=45, h0=0))
        m2 = trajectory_metrics(*numerical_trajectory(v0=20, theta_deg=45, h0=10))
        assert m2["time_of_flight"] > m1["time_of_flight"]


class TestMetrics:
    def test_empty_trajectory(self) -> None:
        m = trajectory_metrics(np.array([]), np.array([]), np.array([]))
        assert m["range"] == 0.0
        assert m["max_height"] == 0.0
        assert m["time_of_flight"] == 0.0

    def test_known_values(self) -> None:
        t = np.array([0, 0.5, 1.0])
        x = np.array([0, 5, 10])
        y = np.array([0, 3, 0])
        m = trajectory_metrics(t, x, y)
        assert m["range"] == 10.0
        assert m["max_height"] == 3.0
        assert m["time_of_flight"] == 1.0


class TestOptimalAngle:
    def test_h0_zero_is_45(self) -> None:
        assert optimal_angle_no_drag(h0=0.0) == 45.0
