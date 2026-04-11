"""Tests for Q02 — Quantum Tunnelling physics."""

import numpy as np
import pytest

from lumina.modules.quantum.q02_tunnelling.physics import (
    potential_profile, reflection_coefficient, stationary_state,
    transmission_coefficient, transmission_curve,
)


class TestTransmission:
    def test_below_barrier_is_small(self) -> None:
        """T should be small for E << V0."""
        T = transmission_coefficient(E=0.5, V0=10.0, a=2.0)
        assert 0.0 < T < 0.5

    def test_above_barrier_is_large(self) -> None:
        """T should be close to 1 for E >> V0."""
        T = transmission_coefficient(E=20.0, V0=1.0, a=1.0)
        assert T > 0.9

    def test_zero_energy_is_zero(self) -> None:
        T = transmission_coefficient(E=0.0, V0=5.0, a=1.0)
        assert T == 0.0

    def test_no_barrier_is_one(self) -> None:
        T = transmission_coefficient(E=2.0, V0=0.0, a=1.0)
        assert T == 1.0

    def test_t_in_unit_interval(self) -> None:
        for E in [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]:
            T = transmission_coefficient(E, V0=3.0, a=1.0)
            assert 0.0 <= T <= 1.0

    def test_wider_barrier_lower_T(self) -> None:
        """For E < V0, T decreases with barrier width."""
        T1 = transmission_coefficient(E=2.0, V0=5.0, a=1.0)
        T2 = transmission_coefficient(E=2.0, V0=5.0, a=2.0)
        assert T2 < T1

    def test_higher_E_higher_T_below_barrier(self) -> None:
        """In the tunnelling regime, higher E means more transmission."""
        T1 = transmission_coefficient(E=1.0, V0=5.0, a=1.5)
        T2 = transmission_coefficient(E=3.0, V0=5.0, a=1.5)
        assert T2 > T1


class TestReflection:
    def test_R_plus_T_is_one(self) -> None:
        for E in [0.5, 1.5, 3.0, 8.0]:
            T = transmission_coefficient(E, V0=5.0, a=1.0)
            R = reflection_coefficient(E, V0=5.0, a=1.0)
            assert T + R == pytest.approx(1.0)


class TestTransmissionCurve:
    def test_shape(self) -> None:
        E_arr, T_arr = transmission_curve(0.1, 10.0, V0=5.0, a=1.0, n_points=200)
        assert len(E_arr) == 200
        assert len(T_arr) == 200

    def test_T_in_unit_interval(self) -> None:
        _, T_arr = transmission_curve(0.1, 10.0, V0=5.0, a=1.0)
        assert np.all(T_arr >= 0.0)
        assert np.all(T_arr <= 1.0)

    def test_monotonic_below_barrier(self) -> None:
        """In the tunnelling regime, T is monotonically increasing in E."""
        E_arr, T_arr = transmission_curve(0.1, 4.0, V0=5.0, a=1.0)
        diffs = np.diff(T_arr)
        assert np.all(diffs >= -1e-10)


class TestPotentialProfile:
    def test_shape(self) -> None:
        x = np.linspace(-5, 5, 100)
        V = potential_profile(x, V0=2.0, a=1.0, x0=0.0)
        assert V.shape == x.shape

    def test_zero_outside_barrier(self) -> None:
        x = np.array([-1.0, 0.5, 2.0])
        V = potential_profile(x, V0=2.0, a=1.0, x0=0.0)
        assert V[0] == 0.0
        assert V[1] == 2.0
        assert V[2] == 0.0


class TestStationaryState:
    def test_shape(self) -> None:
        x = np.linspace(-3, 3, 200)
        psi = stationary_state(x, E=2.0, V0=5.0, a=1.0)
        assert psi.shape == x.shape
        assert psi.dtype == np.complex128

    def test_zero_energy_zero_state(self) -> None:
        x = np.linspace(-3, 3, 100)
        psi = stationary_state(x, E=0.0, V0=5.0, a=1.0)
        np.testing.assert_array_equal(psi, np.zeros_like(x, dtype=np.complex128))
