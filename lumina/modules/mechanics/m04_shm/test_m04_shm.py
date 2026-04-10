"""Tests for M04 — Simple Harmonic Motion physics."""
import numpy as np
import pytest
from lumina.modules.mechanics.m04_shm.physics import (
    classify_damping, damped_shm, kinetic_energy, phase_space_ellipse,
    potential_energy, shm_solution, spring_omega, pendulum_omega,
)

class TestOmega:
    def test_spring(self) -> None:
        assert spring_omega(4.0, 1.0) == pytest.approx(2.0)
    def test_pendulum(self) -> None:
        assert pendulum_omega(9.81, 1.0) == pytest.approx(np.sqrt(9.81))

class TestSHM:
    def test_at_t0(self) -> None:
        t = np.array([0.0])
        x, v = shm_solution(t, 2.0, 3.0, 0.0)
        assert x[0] == pytest.approx(2.0)
        assert v[0] == pytest.approx(0.0)

    def test_amplitude(self) -> None:
        t = np.linspace(0, 10, 1000)
        x, _ = shm_solution(t, 3.0, 2.0, 0.0)
        assert np.max(np.abs(x)) == pytest.approx(3.0, abs=0.01)

class TestDamping:
    def test_classify(self) -> None:
        assert classify_damping(5.0, 1.0) == "underdamped"
        assert classify_damping(5.0, 5.0) == "critical"
        assert classify_damping(5.0, 8.0) == "overdamped"

    def test_underdamped_decays(self) -> None:
        t = np.linspace(0, 10, 1000)
        x = damped_shm(t, 1.0, 5.0, 0.5, 0.0)
        assert abs(x[-1]) < abs(x[0])

class TestEnergy:
    def test_conservation(self) -> None:
        t = np.linspace(0, 10, 1000)
        x, v = shm_solution(t, 1.0, 2.0, 0.0)
        ke = kinetic_energy(1.0, v)
        pe = potential_energy(4.0, x)  # k = m*omega^2 = 1*4 = 4
        total = ke + pe
        np.testing.assert_allclose(total, total[0], atol=1e-10)

class TestPhaseSpace:
    def test_ellipse_shape(self) -> None:
        x, v = phase_space_ellipse(2.0, 3.0, 100)
        assert len(x) == 100
        assert np.max(np.abs(x)) == pytest.approx(2.0, abs=0.1)
