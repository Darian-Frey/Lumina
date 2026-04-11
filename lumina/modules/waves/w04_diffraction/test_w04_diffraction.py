"""Tests for W04 — Diffraction & Interference physics."""

import numpy as np
import pytest

from lumina.modules.waves.w04_diffraction.physics import (
    double_slit_intensity, first_minimum_angle, fringe_spacing,
    n_slit_intensity, single_slit_intensity,
)


class TestSingleSlit:
    def test_central_peak_at_zero(self) -> None:
        """At theta = 0, intensity should equal I0."""
        theta = np.array([0.0])
        I = single_slit_intensity(theta, a=0.05, wavelength=0.01, I0=2.0)
        assert I[0] == pytest.approx(2.0)

    def test_first_min_at_lambda_over_a(self) -> None:
        """First minimum at sin(theta) = lambda / a."""
        a = 0.05
        wavelength = 0.01
        theta_min = np.arcsin(wavelength / a)
        theta = np.array([theta_min])
        I = single_slit_intensity(theta, a, wavelength)
        assert I[0] == pytest.approx(0.0, abs=1e-10)

    def test_symmetric(self) -> None:
        theta = np.array([-0.2, -0.1, 0.0, 0.1, 0.2])
        I = single_slit_intensity(theta, a=0.05, wavelength=0.01)
        # Pattern is symmetric about theta = 0
        np.testing.assert_allclose(I, I[::-1], atol=1e-12)

    def test_nonneg(self) -> None:
        theta = np.linspace(-1, 1, 200)
        I = single_slit_intensity(theta, a=0.05, wavelength=0.01)
        assert np.all(I >= 0)


class TestDoubleSlit:
    def test_central_peak(self) -> None:
        """At theta = 0, double-slit intensity is 4 I0 (constructive)."""
        theta = np.array([0.0])
        I = double_slit_intensity(theta, a=0.02, d=0.1, wavelength=0.01, I0=1.0)
        assert I[0] == pytest.approx(4.0)

    def test_symmetric(self) -> None:
        theta = np.linspace(-0.3, 0.3, 100)
        I = double_slit_intensity(theta, a=0.02, d=0.1, wavelength=0.01)
        np.testing.assert_allclose(I, I[::-1], atol=1e-12)

    def test_interference_minimum(self) -> None:
        """First interference min where d sin(theta) = lambda/2."""
        d = 0.1
        wavelength = 0.01
        theta_min = np.arcsin(wavelength / (2 * d))
        I = double_slit_intensity(
            np.array([theta_min]), a=0.02, d=d, wavelength=wavelength,
        )
        assert I[0] == pytest.approx(0.0, abs=1e-10)


class TestNSlit:
    def test_central_peak_scales_as_n_squared(self) -> None:
        """At theta = 0, the N-slit intensity is N^2 I0 envelope = N^2 I0."""
        theta = np.array([0.0])
        for N in [2, 3, 5, 10]:
            I = n_slit_intensity(
                theta, a=0.02, d=0.1, N=N, wavelength=0.01, I0=1.0,
            )
            assert I[0] == pytest.approx(N ** 2)

    def test_symmetric(self) -> None:
        theta = np.linspace(-0.2, 0.2, 100)
        I = n_slit_intensity(theta, a=0.02, d=0.1, N=5, wavelength=0.01)
        np.testing.assert_allclose(I, I[::-1], atol=1e-10)

    def test_nonneg(self) -> None:
        theta = np.linspace(-0.3, 0.3, 200)
        I = n_slit_intensity(theta, a=0.02, d=0.1, N=10, wavelength=0.01)
        assert np.all(I >= -1e-10)


class TestHelpers:
    def test_fringe_spacing_formula(self) -> None:
        d = 0.1
        wavelength = 0.01
        D = 2.0
        spacing = fringe_spacing(d, wavelength, D)
        assert spacing == pytest.approx(wavelength * D / d)

    def test_first_minimum_angle(self) -> None:
        a = 0.05
        wavelength = 0.01
        theta = first_minimum_angle(a, wavelength)
        assert theta == pytest.approx(np.arcsin(wavelength / a))

    def test_first_min_lambda_larger_than_a(self) -> None:
        """When lambda > a, no real minimum — return pi/2."""
        theta = first_minimum_angle(a=0.005, wavelength=0.01)
        assert theta == pytest.approx(np.pi / 2)
