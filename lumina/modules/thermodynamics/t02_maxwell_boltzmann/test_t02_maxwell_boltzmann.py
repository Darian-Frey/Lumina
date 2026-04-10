"""Tests for T02 — Maxwell-Boltzmann physics."""
import numpy as np
import pytest
from lumina.modules.thermodynamics.t02_maxwell_boltzmann.physics import (
    K_B, mb_pdf_2d, mb_pdf_3d, mean_speed, most_probable_speed, rms_speed,
)

M = 4.65e-26  # N2
T = 300.0

class TestPDF:
    def test_3d_integrates_to_one(self) -> None:
        v = np.linspace(0, 3000, 10000)
        fv = mb_pdf_3d(v, M, T)
        integral = np.trapezoid(fv, v)
        assert integral == pytest.approx(1.0, abs=0.01)

    def test_2d_integrates_to_one(self) -> None:
        v = np.linspace(0, 3000, 10000)
        fv = mb_pdf_2d(v, M, T)
        integral = np.trapezoid(fv, v)
        assert integral == pytest.approx(1.0, abs=0.01)

    def test_pdf_nonnegative(self) -> None:
        v = np.linspace(0, 2000, 500)
        assert np.all(mb_pdf_3d(v, M, T) >= 0)

class TestCharacteristicSpeeds:
    def test_ordering(self) -> None:
        vmp = most_probable_speed(M, T)
        vavg = mean_speed(M, T)
        vrms = rms_speed(M, T)
        assert vmp < vavg < vrms

    def test_temperature_scaling(self) -> None:
        v1 = most_probable_speed(M, 300)
        v2 = most_probable_speed(M, 1200)
        assert v2 == pytest.approx(v1 * 2, rel=0.01)  # sqrt(T) scaling, factor 2

    def test_known_vmp(self) -> None:
        vmp = most_probable_speed(M, T)
        expected = np.sqrt(2 * K_B * T / M)
        assert vmp == pytest.approx(expected)
