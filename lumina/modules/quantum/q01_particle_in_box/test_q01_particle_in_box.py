"""Tests for Q01 — Particle in a Box physics."""

import numpy as np
import pytest

from lumina.modules.quantum.q01_particle_in_box.physics import (
    energy_level, normalise_coefficients, probability_density,
    superposition, time_evolved_state, wavefunction,
)


class TestEnergyLevel:
    def test_ground_state_default(self) -> None:
        # E_1 = pi^2 / 2 with L = m = hbar = 1
        E1 = energy_level(1)
        assert E1 == pytest.approx(np.pi ** 2 / 2)

    def test_n_squared_scaling(self) -> None:
        E1 = energy_level(1)
        E2 = energy_level(2)
        E3 = energy_level(3)
        assert E2 == pytest.approx(4 * E1)
        assert E3 == pytest.approx(9 * E1)

    def test_inverse_L_squared_scaling(self) -> None:
        E_L1 = energy_level(1, L=1.0)
        E_L2 = energy_level(1, L=2.0)
        assert E_L2 == pytest.approx(E_L1 / 4)

    def test_n_zero_raises(self) -> None:
        with pytest.raises(ValueError):
            energy_level(0)

    def test_negative_n_raises(self) -> None:
        with pytest.raises(ValueError):
            energy_level(-1)


class TestWavefunction:
    def test_normalisation(self) -> None:
        """Integral of |psi|^2 from 0 to L should equal 1."""
        L = 2.0
        x = np.linspace(0, L, 5000)
        for n in [1, 2, 3, 5, 10]:
            psi = wavefunction(x, n, L)
            integral = np.trapezoid(psi ** 2, x)
            assert integral == pytest.approx(1.0, abs=0.01)

    def test_zero_at_walls(self) -> None:
        """Wavefunction must vanish at x=0 and x=L."""
        L = 1.5
        x = np.array([0.0, L])
        for n in [1, 2, 3, 5]:
            psi = wavefunction(x, n, L)
            np.testing.assert_allclose(psi, [0.0, 0.0], atol=1e-10)

    def test_zero_outside_well(self) -> None:
        x = np.array([-0.5, 0.5, 1.5])  # 0.5 inside, others outside
        psi = wavefunction(x, 1, L=1.0)
        assert psi[0] == 0.0
        assert psi[1] != 0.0
        assert psi[2] == 0.0

    def test_correct_number_of_nodes(self) -> None:
        """nth eigenstate has n-1 nodes inside the well."""
        L = 1.0
        x = np.linspace(0.001, L - 0.001, 1000)
        for n in [1, 2, 3, 4, 5]:
            psi = wavefunction(x, n, L)
            # Count zero crossings
            sign_changes = np.sum(np.diff(np.sign(psi)) != 0)
            assert sign_changes == n - 1


class TestProbabilityDensity:
    def test_nonneg(self) -> None:
        x = np.linspace(0, 1, 200)
        for n in [1, 3, 5]:
            prob = probability_density(x, n)
            assert np.all(prob >= 0)

    def test_integrates_to_one(self) -> None:
        L = 1.0
        x = np.linspace(0, L, 5000)
        for n in [1, 2, 4]:
            prob = probability_density(x, n, L)
            assert np.trapezoid(prob, x) == pytest.approx(1.0, abs=0.01)


class TestSuperposition:
    def test_empty(self) -> None:
        x = np.linspace(0, 1, 100)
        result = superposition(x, [])
        np.testing.assert_array_equal(result, np.zeros(100, dtype=np.complex128))

    def test_single_state(self) -> None:
        x = np.linspace(0, 1, 100)
        psi_super = superposition(x, [(1, 1.0 + 0j)])
        psi_direct = wavefunction(x, 1, 1.0)
        np.testing.assert_allclose(psi_super.real, psi_direct)
        np.testing.assert_allclose(psi_super.imag, np.zeros(100), atol=1e-10)

    def test_normalised_coefficients(self) -> None:
        coeffs = normalise_coefficients([(1, 1+0j), (2, 1+0j), (3, 1+0j)])
        norm_sq = sum(abs(c) ** 2 for _, c in coeffs)
        assert norm_sq == pytest.approx(1.0)


class TestTimeEvolution:
    def test_at_t_zero(self) -> None:
        """At t=0, time-evolved state equals static superposition."""
        x = np.linspace(0, 1, 100)
        coeffs = [(1, 1+0j), (2, 1+0j)]
        psi_t0 = time_evolved_state(x, coeffs, t=0.0)
        psi_static = superposition(x, coeffs)
        np.testing.assert_allclose(psi_t0, psi_static)

    def test_norm_preserved(self) -> None:
        """|psi|^2 integrated over the box should stay constant in time."""
        L = 1.0
        x = np.linspace(0, L, 5000)
        coeffs = normalise_coefficients([(1, 1+0j), (2, 1+0j), (3, 1+0j)])

        for t in [0.0, 0.5, 1.0, 2.5]:
            psi = time_evolved_state(x, coeffs, t=t, L=L)
            norm = float(np.trapezoid(np.abs(psi) ** 2, x))
            assert norm == pytest.approx(1.0, abs=0.01)
