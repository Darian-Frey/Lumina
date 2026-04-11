"""Tests for AP04 — Fourier Series Builder physics."""

import numpy as np
import pytest

from lumina.modules.applied_maths.ap04_fourier_series.physics import (
    PRESETS, fourier_coefficients, fourier_partial_sum,
    full_rectified_sine, half_rectified_sine, parabola,
    sawtooth_wave, square_wave, triangle_wave,
)


class TestPresetWaveforms:
    def test_square_wave_values(self) -> None:
        x = np.array([0.5, np.pi - 0.1, np.pi + 0.1, 2 * np.pi - 0.1])
        f = square_wave(x)
        assert f[0] == 1.0
        assert f[1] == 1.0
        assert f[2] == -1.0
        assert f[3] == -1.0

    def test_triangle_wave_zero_at_origin(self) -> None:
        f = triangle_wave(np.array([0.0]))
        assert f[0] == pytest.approx(0.0)

    def test_triangle_wave_peak_at_pi_over_2(self) -> None:
        f = triangle_wave(np.array([np.pi / 2]))
        assert f[0] == pytest.approx(1.0)

    def test_sawtooth_zero_at_origin(self) -> None:
        f = sawtooth_wave(np.array([0.0]))
        assert f[0] == pytest.approx(0.0)

    def test_half_rectified_zero_below_zero(self) -> None:
        f = half_rectified_sine(np.array([-np.pi / 2]))
        assert f[0] == 0.0

    def test_full_rectified_always_nonneg(self) -> None:
        x = np.linspace(-np.pi, np.pi, 100)
        assert np.all(full_rectified_sine(x) >= 0)

    def test_parabola_min_at_zero(self) -> None:
        f = parabola(np.array([0.0]))
        assert f[0] == pytest.approx(0.0)


class TestCoefficients:
    def test_square_wave_only_odd_b(self) -> None:
        x = np.linspace(-np.pi, np.pi, 5000)
        f = square_wave(x)
        a, b = fourier_coefficients(f, x, n_max=10)
        # Square wave is odd, so all a_n should be near zero
        assert np.all(np.abs(a) < 0.05)
        # b_1 = 4/pi
        assert b[1] == pytest.approx(4.0 / np.pi, abs=0.05)
        # b_2 = 0 (even harmonics absent)
        assert abs(b[2]) < 0.05
        # b_3 = 4/(3 pi)
        assert b[3] == pytest.approx(4.0 / (3 * np.pi), abs=0.05)

    def test_sawtooth_b1(self) -> None:
        x = np.linspace(-np.pi, np.pi, 5000)
        f = sawtooth_wave(x)
        a, b = fourier_coefficients(f, x, n_max=5)
        # Sawtooth: b_n = 2 * (-1)^(n+1) / (n * pi)
        assert b[1] == pytest.approx(2.0 / np.pi, abs=0.05)
        assert b[2] == pytest.approx(-2.0 / (2 * np.pi), abs=0.05)


class TestReconstruction:
    def test_partial_sum_at_n_zero(self) -> None:
        x = np.array([0.0])
        a = np.array([2.0])
        b = np.array([0.0])
        result = fourier_partial_sum(x, a, b)
        assert result[0] == pytest.approx(1.0)  # a_0 / 2

    def test_round_trip_square_wave(self) -> None:
        """For N=50, the partial sum should be close to the square wave away
        from discontinuities."""
        x = np.linspace(-np.pi, np.pi, 5000)
        f = square_wave(x)
        a, b = fourier_coefficients(f, x, n_max=50)
        approx = fourier_partial_sum(x, a, b)

        # Check away from x = 0 and x = ±pi (discontinuities)
        mask = (np.abs(x) > 0.3) & (np.abs(x - np.pi) > 0.3) & (np.abs(x + np.pi) > 0.3)
        assert np.allclose(approx[mask], f[mask], atol=0.15)


class TestPresetsDict:
    def test_all_presets_callable(self) -> None:
        x = np.linspace(-np.pi, np.pi, 100)
        for name, fn in PRESETS.items():
            result = fn(x)
            assert result.shape == x.shape
            assert not np.any(np.isnan(result))
