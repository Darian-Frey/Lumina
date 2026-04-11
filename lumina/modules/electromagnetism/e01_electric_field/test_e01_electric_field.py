"""Tests for E01 — Electric Field Lines physics."""

import numpy as np
import pytest

from lumina.modules.electromagnetism.e01_electric_field.physics import (
    coulomb_field, field_magnitude, generate_field_lines, potential,
    trace_field_line,
)


class TestCoulombField:
    def test_shapes(self) -> None:
        x = np.linspace(-2, 2, 20)
        y = np.linspace(-2, 2, 20)
        X, Y = np.meshgrid(x, y)
        Ex, Ey = coulomb_field(X, Y, [(0.0, 0.0, 1.0)])
        assert Ex.shape == X.shape
        assert Ey.shape == Y.shape

    def test_radial_field_from_point_charge(self) -> None:
        """Field from a single positive charge at origin should point radially outward."""
        X = np.array([[1.0, 0.0], [-1.0, 0.0]])
        Y = np.array([[0.0, 1.0], [0.0, -1.0]])
        Ex, Ey = coulomb_field(X, Y, [(0.0, 0.0, 1.0)])
        # At (1, 0): field points +x
        assert Ex[0, 0] > 0
        assert Ey[0, 0] == pytest.approx(0.0, abs=1e-10)
        # At (-1, 0): field points -x
        assert Ex[1, 0] < 0
        # At (0, 1): field points +y
        assert Ex[0, 1] == pytest.approx(0.0, abs=1e-10)
        assert Ey[0, 1] > 0

    def test_negative_charge_inward(self) -> None:
        X = np.array([[1.0]])
        Y = np.array([[0.0]])
        Ex, Ey = coulomb_field(X, Y, [(0.0, 0.0, -1.0)])
        # Field points toward charge (negative x direction)
        assert Ex[0, 0] < 0

    def test_dipole_field_at_midpoint(self) -> None:
        """For a dipole with + at (-1, 0) and - at (+1, 0), field at midpoint
        points in +x direction (away from + and toward -)."""
        charges = [(-1.0, 0.0, 1.0), (1.0, 0.0, -1.0)]
        X = np.array([[0.0]])
        Y = np.array([[0.0]])
        Ex, Ey = coulomb_field(X, Y, charges)
        assert Ex[0, 0] > 0
        assert Ey[0, 0] == pytest.approx(0.0, abs=1e-10)


class TestFieldMagnitude:
    def test_nonneg(self) -> None:
        Ex = np.array([[1.0, -2.0], [3.0, -4.0]])
        Ey = np.array([[2.0, 0.0], [-1.0, 5.0]])
        mag = field_magnitude(Ex, Ey)
        assert np.all(mag >= 0)

    def test_known_values(self) -> None:
        Ex = np.array([[3.0]])
        Ey = np.array([[4.0]])
        mag = field_magnitude(Ex, Ey)
        assert mag[0, 0] == pytest.approx(5.0)


class TestPotential:
    def test_positive_charge_positive_potential(self) -> None:
        X = np.array([[1.0]])
        Y = np.array([[0.0]])
        V = potential(X, Y, [(0.0, 0.0, 1.0)])
        assert V[0, 0] > 0

    def test_negative_charge_negative_potential(self) -> None:
        X = np.array([[1.0]])
        Y = np.array([[0.0]])
        V = potential(X, Y, [(0.0, 0.0, -1.0)])
        assert V[0, 0] < 0

    def test_falls_with_distance(self) -> None:
        X = np.array([[1.0, 2.0, 5.0]])
        Y = np.array([[0.0, 0.0, 0.0]])
        V = potential(X, Y, [(0.0, 0.0, 1.0)])
        assert V[0, 0] > V[0, 1] > V[0, 2]


class TestTraceFieldLine:
    def test_outward_from_positive_charge(self) -> None:
        """A field line from near a positive charge should move outward."""
        charges = [(0.0, 0.0, 1.0)]
        xs, ys = trace_field_line(0.5, 0.0, charges, n_steps=50)
        # Distance from origin should grow
        d_start = np.sqrt(xs[0] ** 2 + ys[0] ** 2)
        d_end = np.sqrt(xs[-1] ** 2 + ys[-1] ** 2)
        assert d_end > d_start

    def test_terminates_at_bounds(self) -> None:
        charges = [(0.0, 0.0, 1.0)]
        xs, ys = trace_field_line(
            0.5, 0.0, charges, n_steps=10000,
            bounds=(-1, 1, -1, 1),
        )
        # Should stop before reaching 10000 steps
        assert len(xs) < 10000


class TestGenerateFieldLines:
    def test_returns_lines(self) -> None:
        charges = [(-1.0, 0.0, 1.0), (1.0, 0.0, -1.0)]
        lines = generate_field_lines(charges, n_lines_per_charge=8)
        assert len(lines) > 0
        for xs, ys in lines:
            assert len(xs) == len(ys)
            assert len(xs) > 1

    def test_no_charges_no_lines(self) -> None:
        lines = generate_field_lines([], n_lines_per_charge=8)
        assert lines == []
