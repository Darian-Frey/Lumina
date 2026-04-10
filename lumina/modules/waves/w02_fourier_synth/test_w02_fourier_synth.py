"""Tests for W02 — Fourier Synthesiser physics."""

import numpy as np
import pytest

from lumina.modules.waves.w02_fourier_synth.physics import (
    fourier_partial_sum, gibbs_overshoot, sawtooth_wave_coefficients,
    square_wave_coefficients, target_waveform, triangle_wave_coefficients,
)


class TestSquareWave:
    def test_b1(self) -> None:
        coeffs = square_wave_coefficients(1)
        assert len(coeffs) == 1
        assert coeffs[0][0] == 1
        assert coeffs[0][1] == pytest.approx(4.0 / np.pi)

    def test_b3(self) -> None:
        coeffs = square_wave_coefficients(3)
        assert len(coeffs) == 2  # n=1 and n=3
        assert coeffs[1][0] == 3
        assert coeffs[1][1] == pytest.approx(4.0 / (3 * np.pi))

    def test_only_odd(self) -> None:
        coeffs = square_wave_coefficients(10)
        ns = [n for n, _ in coeffs]
        assert all(n % 2 == 1 for n in ns)


class TestTriangleWave:
    def test_b1(self) -> None:
        coeffs = triangle_wave_coefficients(1)
        assert coeffs[0][1] == pytest.approx(8.0 / np.pi ** 2)


class TestSawtoothWave:
    def test_b1(self) -> None:
        coeffs = sawtooth_wave_coefficients(1)
        # b_1 = -2*(-1)^1/(1*pi) = 2/pi
        assert coeffs[0][1] == pytest.approx(2.0 / np.pi)

    def test_includes_even(self) -> None:
        coeffs = sawtooth_wave_coefficients(4)
        ns = [n for n, _ in coeffs]
        assert 2 in ns


class TestPartialSum:
    def test_at_zero(self) -> None:
        x = np.array([0.0])
        coeffs = square_wave_coefficients(20)
        result = fourier_partial_sum(x, coeffs)
        assert result[0] == pytest.approx(0.0, abs=1e-10)

    def test_approximates_square(self) -> None:
        x = np.linspace(0.2, 2.5, 100)  # Away from discontinuity
        coeffs = square_wave_coefficients(50)
        y = fourier_partial_sum(x, coeffs)
        target = target_waveform(x, "square")
        np.testing.assert_allclose(y, target, atol=0.15)


class TestTargetWaveform:
    def test_square_positive(self) -> None:
        x = np.array([1.0])
        assert target_waveform(x, "square")[0] == 1.0

    def test_square_negative(self) -> None:
        x = np.array([-1.0])
        assert target_waveform(x, "square")[0] == -1.0

    def test_unknown_raises(self) -> None:
        with pytest.raises(ValueError):
            target_waveform(np.array([0.0]), "cosine")


class TestGibbs:
    def test_overshoot_present(self) -> None:
        coeffs = square_wave_coefficients(50)
        overshoot = gibbs_overshoot(coeffs)
        assert overshoot > 5.0  # Gibbs overshoot ~9% as N->inf, higher at finite N
        assert overshoot < 20.0
