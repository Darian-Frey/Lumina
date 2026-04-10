"""Tests for P03 — FractalLab physics."""
import numpy as np
import pytest
from lumina.modules.pure_maths.p03_fractallab.physics import (
    burning_ship, colour_map, julia_set, mandelbrot_scalar,
    mandelbrot_set, multibrot, newton_fractal, tricorn,
)

class TestMandelbrotScalar:
    def test_origin_in_set(self) -> None:
        assert mandelbrot_scalar(0 + 0j) == 256

    def test_escapes_immediately(self) -> None:
        assert mandelbrot_scalar(2 + 0j) == 1

    def test_minus_one_in_set(self) -> None:
        # -1 is in the set (period 2)
        assert mandelbrot_scalar(-1 + 0j) == 256

class TestMandelbrotSet:
    def test_shape(self) -> None:
        result = mandelbrot_set(-2, 1, -1.5, 1.5, 100, 80, 64)
        assert result.shape == (80, 100)

    def test_dtype(self) -> None:
        result = mandelbrot_set(-2, 1, -1.5, 1.5, 50, 50, 64)
        assert result.dtype == np.int32

    def test_origin_pixel_in_set(self) -> None:
        # Small region around origin
        result = mandelbrot_set(-0.01, 0.01, -0.01, 0.01, 10, 10, 256)
        assert result[5, 5] == 256  # Centre pixel should be in set

class TestJuliaSet:
    def test_shape(self) -> None:
        result = julia_set(-2, 2, -2, 2, 100, 80, -0.7, 0.27015, 64)
        assert result.shape == (80, 100)

class TestBurningShip:
    def test_shape(self) -> None:
        result = burning_ship(-2.5, 1.5, -2, 1, 100, 80, 64)
        assert result.shape == (80, 100)

    def test_has_structure(self) -> None:
        """Should have both escaped and non-escaped points."""
        result = burning_ship(-2.5, 1.5, -2, 1, 100, 80, 64)
        assert np.any(result < 64)
        assert np.any(result == 64)


class TestTricorn:
    def test_shape(self) -> None:
        result = tricorn(-2.5, 1.5, -2, 2, 100, 80, 64)
        assert result.shape == (80, 100)

    def test_origin_in_set(self) -> None:
        result = tricorn(-0.01, 0.01, -0.01, 0.01, 10, 10, 256)
        assert result[5, 5] == 256


class TestMultibrot:
    def test_shape(self) -> None:
        result = multibrot(-2, 2, -2, 2, 100, 80, power=3, max_iter=64)
        assert result.shape == (80, 100)

    def test_power_2_matches_mandelbrot(self) -> None:
        """Multibrot with power=2 should match Mandelbrot."""
        mb = mandelbrot_set(-2, 1, -1.5, 1.5, 50, 50, 64)
        multi = multibrot(-2, 1, -1.5, 1.5, 50, 50, power=2, max_iter=64)
        np.testing.assert_array_equal(mb, multi)


class TestNewtonFractal:
    def test_shape(self) -> None:
        result = newton_fractal(-2, 2, -2, 2, 100, 80, 64)
        assert result.shape == (80, 100)

    def test_converges(self) -> None:
        """Most points should converge (iteration < max_iter)."""
        result = newton_fractal(-2, 2, -2, 2, 100, 80, 256)
        converged = np.sum(result < 256)
        assert converged > 0.5 * result.size


class TestColourMap:
    def test_shape(self) -> None:
        iters = np.full((50, 60), 128, dtype=np.int32)
        rgb = colour_map(iters, 256)
        assert rgb.shape == (50, 60, 3)
        assert rgb.dtype == np.uint8

    def test_set_points_black(self) -> None:
        iters = np.full((10, 10), 256, dtype=np.int32)  # All in set
        rgb = colour_map(iters, 256)
        assert np.all(rgb == 0)
