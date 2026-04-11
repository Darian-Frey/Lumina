"""Tests for E03 — RC/RL/LC/RLC Circuits physics."""

import numpy as np
import pytest

from lumina.modules.electromagnetism.e03_rlc_circuits.physics import (
    damping_regime, lc_oscillation, quality_factor, rc_charging,
    rc_discharging, resonant_frequency, rl_building, rl_decaying,
    rlc_response,
)


class TestRC:
    def test_charging_starts_at_zero(self) -> None:
        t = np.array([0.0])
        q, i = rc_charging(t, V=5.0, R=100.0, C=1e-3)
        assert q[0] == pytest.approx(0.0)
        assert i[0] == pytest.approx(5.0 / 100.0)

    def test_charging_asymptote(self) -> None:
        """Charge approaches CV as t -> infinity."""
        t = np.array([100.0])  # Many time constants later
        q, _ = rc_charging(t, V=5.0, R=100.0, C=1e-3)
        assert q[0] == pytest.approx(5.0e-3, abs=1e-6)

    def test_charging_at_one_tau(self) -> None:
        """At t = tau, q should be CV*(1 - 1/e) ~= 0.632 CV."""
        R, C, V = 100.0, 1e-3, 5.0
        tau = R * C
        t = np.array([tau])
        q, _ = rc_charging(t, V, R, C)
        assert q[0] == pytest.approx(C * V * (1 - 1/np.e))

    def test_discharging_starts_at_Q0(self) -> None:
        t = np.array([0.0])
        q, _ = rc_discharging(t, Q0=2.0, R=100.0, C=1e-3)
        assert q[0] == pytest.approx(2.0)


class TestRL:
    def test_building_starts_at_zero(self) -> None:
        t = np.array([0.0])
        i, v_L = rl_building(t, V=10.0, R=50.0, L=1.0)
        assert i[0] == pytest.approx(0.0)
        # Inductor voltage equals source voltage at t=0
        assert v_L[0] == pytest.approx(10.0)

    def test_building_asymptote(self) -> None:
        t = np.array([100.0])
        i, _ = rl_building(t, V=10.0, R=50.0, L=1.0)
        assert i[0] == pytest.approx(10.0 / 50.0)

    def test_decaying_starts_at_I0(self) -> None:
        t = np.array([0.0])
        i, _ = rl_decaying(t, I0=2.0, R=50.0, L=1.0)
        assert i[0] == pytest.approx(2.0)


class TestLC:
    def test_starts_at_Q0(self) -> None:
        t = np.array([0.0])
        q, i = lc_oscillation(t, Q0=3.0, L=1.0, C=1e-3)
        assert q[0] == pytest.approx(3.0)
        assert i[0] == pytest.approx(0.0)

    def test_periodic(self) -> None:
        L, C, Q0 = 1.0, 1e-3, 3.0
        omega = 1.0 / np.sqrt(L * C)
        T = 2 * np.pi / omega
        t = np.array([0.0, T])
        q, _ = lc_oscillation(t, Q0, L, C)
        # After one full period, charge returns to Q0
        assert q[1] == pytest.approx(q[0], abs=1e-10)

    def test_energy_conservation(self) -> None:
        """Total energy (1/2)L i^2 + q^2/(2C) should be constant."""
        L, C, Q0 = 1.0, 1e-3, 5.0
        t = np.linspace(0, 0.5, 1000)
        q, i = lc_oscillation(t, Q0, L, C)
        E = 0.5 * L * i ** 2 + q ** 2 / (2 * C)
        np.testing.assert_allclose(E, E[0], rtol=1e-10)


class TestRLC:
    def test_underdamped(self) -> None:
        # alpha = R/(2L) = 5/(2*1) = 2.5
        # omega0 = 1/sqrt(LC) = 1/sqrt(1e-3) ~= 31.6
        regime = damping_regime(R=5.0, L=1.0, C=1e-3)
        assert regime == "underdamped"

    def test_overdamped(self) -> None:
        regime = damping_regime(R=200.0, L=1.0, C=1e-3)
        assert regime == "overdamped"

    def test_critical(self) -> None:
        # alpha = omega0 means R/(2L) = 1/sqrt(LC)
        # R = 2L/sqrt(LC) = 2*sqrt(L/C)
        L, C = 1.0, 1e-3
        R_crit = 2 * np.sqrt(L / C)
        regime = damping_regime(R=R_crit, L=L, C=C)
        assert regime == "critical"

    def test_response_starts_at_Q0(self) -> None:
        t = np.array([0.0])
        q, i = rlc_response(t, Q0=4.0, R=20.0, L=1.0, C=1e-3)
        assert q[0] == pytest.approx(4.0, abs=1e-10)

    def test_response_decays(self) -> None:
        t = np.array([0.0, 5.0])
        q, _ = rlc_response(t, Q0=4.0, R=20.0, L=1.0, C=1e-3)
        # After 5 seconds, charge should have decayed substantially
        assert abs(q[1]) < abs(q[0])


class TestResonance:
    def test_resonant_frequency(self) -> None:
        L, C = 1.0, 1e-3
        omega = resonant_frequency(L, C)
        assert omega == pytest.approx(1.0 / np.sqrt(L * C))

    def test_quality_factor(self) -> None:
        Q = quality_factor(R=10.0, L=1.0, C=1e-3)
        assert Q == pytest.approx((1.0 / 10.0) * np.sqrt(1.0 / 1e-3))
