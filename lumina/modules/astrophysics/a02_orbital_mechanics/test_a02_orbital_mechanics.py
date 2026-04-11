"""Tests for A02 — Orbital Mechanics physics."""

import numpy as np
import pytest

from lumina.modules.astrophysics.a02_orbital_mechanics.physics import (
    GM_DEFAULT, hohmann_transfer, kepler_orbit, numerical_orbit,
    orbital_energy, orbital_period, semi_major_axis_from_energy,
    vis_viva,
)


class TestKeplerOrbit:
    def test_circular_radius(self) -> None:
        x, y = kepler_orbit(a=1.0, e=0.0)
        radii = np.sqrt(x ** 2 + y ** 2)
        np.testing.assert_allclose(radii, np.ones_like(radii), atol=1e-10)

    def test_ellipse_extremes(self) -> None:
        a, e = 2.0, 0.5
        x, y = kepler_orbit(a, e, n_points=1000)
        radii = np.sqrt(x ** 2 + y ** 2)
        # Min radius (perihelion) = a(1-e), max (aphelion) = a(1+e)
        assert radii.min() == pytest.approx(a * (1 - e), abs=0.001)
        assert radii.max() == pytest.approx(a * (1 + e), abs=0.001)


class TestPeriod:
    def test_kepler_third_law(self) -> None:
        a = 4.0
        T = orbital_period(a)
        # T = 2 pi sqrt(a^3 / GM)
        expected = 2 * np.pi * np.sqrt(a ** 3 / GM_DEFAULT)
        assert T == pytest.approx(expected)

    def test_unit_period_at_unit_radius(self) -> None:
        T = orbital_period(1.0)
        assert T == pytest.approx(2 * np.pi)


class TestVisViva:
    def test_circular_speed(self) -> None:
        # For circular orbit (a = r), v = sqrt(GM/r)
        r = 2.0
        v = vis_viva(r, a=r)
        assert v == pytest.approx(np.sqrt(GM_DEFAULT / r))

    def test_perihelion_faster_than_aphelion(self) -> None:
        a, e = 2.0, 0.5
        r_peri = a * (1 - e)
        r_apo = a * (1 + e)
        v_peri = vis_viva(r_peri, a)
        v_apo = vis_viva(r_apo, a)
        assert v_peri > v_apo


class TestNumericalOrbit:
    def test_circular_orbit_stays_circular(self) -> None:
        r0 = 1.0
        v0 = np.sqrt(GM_DEFAULT / r0)  # circular speed
        t, x, y = numerical_orbit(r0=r0, v0=v0, t_max=2 * np.pi)
        radii = np.sqrt(x ** 2 + y ** 2)
        # Radius should stay close to r0
        assert np.all(np.abs(radii - r0) < 0.01)

    def test_starts_at_correct_position(self) -> None:
        r0 = 2.0
        v0 = 0.5
        t, x, y = numerical_orbit(r0=r0, v0=v0, theta0=0.0, t_max=0.1)
        assert x[0] == pytest.approx(r0)
        assert y[0] == pytest.approx(0.0, abs=1e-10)


class TestEnergy:
    def test_circular_energy(self) -> None:
        r = 1.0
        v = np.sqrt(GM_DEFAULT / r)
        E = orbital_energy(r, v)
        # For circular orbit: E = -GM / (2r)
        assert E == pytest.approx(-GM_DEFAULT / (2 * r))

    def test_bound_negative(self) -> None:
        r = 1.0
        v = 0.5  # less than escape
        E = orbital_energy(r, v)
        assert E < 0

    def test_escape_zero(self) -> None:
        r = 1.0
        v_escape = np.sqrt(2 * GM_DEFAULT / r)
        E = orbital_energy(r, v_escape)
        assert E == pytest.approx(0.0)

    def test_a_from_energy(self) -> None:
        r, v = 1.0, 0.8
        E = orbital_energy(r, v)
        a = semi_major_axis_from_energy(E)
        # a should match: -GM/(2E)
        assert a == pytest.approx(-GM_DEFAULT / (2 * E))


class TestHohmann:
    def test_hohmann_two_orbits(self) -> None:
        r1, r2 = 1.0, 4.0
        dv1, dv2, t = hohmann_transfer(r1, r2)
        # Both delta-v should be positive (going outward)
        assert dv1 > 0
        assert dv2 > 0
        # Transfer time = pi * sqrt(a_t^3 / GM), a_t = (r1+r2)/2
        a_t = (r1 + r2) / 2
        expected = np.pi * np.sqrt(a_t ** 3 / GM_DEFAULT)
        assert t == pytest.approx(expected)
