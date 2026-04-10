"""Tests for W01 — Wave Superposition physics."""

import numpy as np
import pytest

from lumina.modules.waves.w01_superposition.physics import (
    beat_frequency, frequency_to_omega, sine_wave, standing_wave,
    superposition, wavelength_to_k,
)


class TestSineWave:
    def test_at_origin(self) -> None:
        x = np.array([0.0])
        assert sine_wave(x, 0.0, 1.0, 1.0, 1.0, 0.0)[0] == pytest.approx(0.0)

    def test_with_phase(self) -> None:
        x = np.array([0.0])
        result = sine_wave(x, 0.0, 2.0, 1.0, 1.0, np.pi / 2)
        assert result[0] == pytest.approx(2.0)

    def test_amplitude(self) -> None:
        x = np.linspace(0, 10, 1000)
        y = sine_wave(x, 0.0, 3.0, 1.0, 0.0, 0.0)
        assert np.max(np.abs(y)) == pytest.approx(3.0, abs=0.01)


class TestSuperposition:
    def test_two_identical(self) -> None:
        x = np.linspace(0, 10, 100)
        w1 = (1.0, 1.0, 1.0, 0.0)
        single = sine_wave(x, 0.0, *w1)
        double = superposition(x, 0.0, [w1, w1])
        np.testing.assert_allclose(double, 2 * single)

    def test_empty(self) -> None:
        x = np.linspace(0, 10, 100)
        result = superposition(x, 0.0, [])
        np.testing.assert_allclose(result, np.zeros(100))


class TestStandingWave:
    def test_node_at_origin(self) -> None:
        x = np.array([0.0])
        result = standing_wave(x, 0.5, 1.0, 1.0, 1.0)
        assert result[0] == pytest.approx(0.0, abs=1e-10)

    def test_node_at_pi(self) -> None:
        x = np.array([np.pi])
        result = standing_wave(x, 0.0, 1.0, 1.0, 1.0)
        assert result[0] == pytest.approx(0.0, abs=1e-10)


class TestHelpers:
    def test_beat_frequency(self) -> None:
        assert beat_frequency(5.0, 5.5) == pytest.approx(0.5)
        assert beat_frequency(3.0, 3.0) == pytest.approx(0.0)

    def test_wavelength_to_k(self) -> None:
        assert wavelength_to_k(1.0) == pytest.approx(2 * np.pi)

    def test_frequency_to_omega(self) -> None:
        assert frequency_to_omega(1.0) == pytest.approx(2 * np.pi)
