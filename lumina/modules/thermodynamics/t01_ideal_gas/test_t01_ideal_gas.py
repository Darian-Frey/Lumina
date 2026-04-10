"""Tests for T01 — Ideal Gas physics."""
import numpy as np
import pytest
from lumina.modules.thermodynamics.t01_ideal_gas.physics import (
    K_B, compute_pressure, compute_speeds, compute_temperature,
    init_particles, step_particles,
)

class TestInit:
    def test_shapes(self) -> None:
        pos, vel = init_particles(100, seed=0)
        assert pos.shape == (100, 2)
        assert vel.shape == (100, 2)

    def test_within_box(self) -> None:
        pos, _ = init_particles(200, box_w=10, box_h=10, seed=0)
        assert np.all(pos > 0)
        assert np.all(pos < 10)

    def test_zero_mean_velocity(self) -> None:
        _, vel = init_particles(500, seed=0)
        np.testing.assert_allclose(vel.mean(axis=0), [0, 0], atol=1e-10)

class TestStep:
    def test_wall_reflection(self) -> None:
        pos = np.array([[0.2, 5.0]])
        vel = np.array([[-10.0, 0.0]])
        new_pos, new_vel, imp = step_particles(pos, vel, 1.0, 10.0, 10.0, 0.15, 0.1)
        assert new_vel[0, 0] > 0  # Reflected

class TestTemperature:
    def test_reasonable(self) -> None:
        _, vel = init_particles(500, temperature=300.0, seed=0)
        T = compute_temperature(vel, 4.65e-26)
        assert 200 < T < 400

class TestPressure:
    def test_positive(self) -> None:
        P = compute_pressure(1e-20, 40.0, 0.01)
        assert P > 0

class TestSpeeds:
    def test_shape(self) -> None:
        _, vel = init_particles(100, seed=0)
        speeds = compute_speeds(vel)
        assert speeds.shape == (100,)
        assert np.all(speeds >= 0)
