"""
tests/test_core.py
------------------
Tests for lumina.core — config, engine, utils, plot.
"""

from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path

import numpy as np
import pytest
from PyQt6.QtWidgets import QWidget

from lumina.core.config import (
    APP_NAME,
    APP_VERSION,
    PACKAGE_ROOT,
    PALETTE_COLOURBLIND,
    PALETTE_STANDARD,
    THEME_LIGHT,
    THEME_PLOT_BACKGROUNDS,
)
from lumina.core.engine import Category, Effort, Level, SimulationBase
from lumina.core.utils import (
    ExpressionError,
    clamp,
    make_callable,
    normalise,
    safe_eval,
    seeded_rng,
)


# ---------------------------------------------------------------------------
# Config tests
# ---------------------------------------------------------------------------


class TestConfig:
    def test_app_metadata(self) -> None:
        assert APP_NAME == "Lumina"
        assert "0.1" in APP_VERSION

    def test_package_root_exists(self) -> None:
        assert PACKAGE_ROOT.is_dir()
        assert (PACKAGE_ROOT / "core").is_dir()

    def test_palettes_have_entries(self) -> None:
        assert len(PALETTE_STANDARD) >= 8
        assert len(PALETTE_COLOURBLIND) >= 6

    def test_theme_backgrounds(self) -> None:
        assert THEME_LIGHT in THEME_PLOT_BACKGROUNDS
        assert THEME_PLOT_BACKGROUNDS[THEME_LIGHT].startswith("#")


# ---------------------------------------------------------------------------
# Engine tests
# ---------------------------------------------------------------------------


class ConcreteSimulation(SimulationBase):
    """Minimal concrete subclass for testing."""

    ID = "TEST01"
    NAME = "Test Simulation"
    CATEGORY = Category.MECHANICS
    LEVEL = Level.A_LEVEL
    EFFORT = Effort.LOW
    DESCRIPTION = "A test simulation."
    TAGS = ["test"]

    def __init__(self) -> None:
        self._value: float = 0.0

    def build_ui(self) -> QWidget:
        return QWidget()

    def reset(self) -> None:
        self._value = 0.0

    def export(self, path: str) -> None:
        Path(path).mkdir(parents=True, exist_ok=True)
        (Path(path) / f"{self.ID}_data.csv").write_text("x,y\n1,2\n")

    def get_state(self) -> dict:
        state = super().get_state()
        state["value"] = self._value
        return state

    def set_state(self, state: dict) -> None:
        self._value = state.get("value", 0.0)


class TestSimulationBase:
    def test_metadata(self) -> None:
        sim = ConcreteSimulation()
        assert sim.ID == "TEST01"
        assert sim.NAME == "Test Simulation"
        assert sim.CATEGORY == "mechanics"
        assert sim.LEVEL == "A-level"

    def test_repr(self) -> None:
        sim = ConcreteSimulation()
        r = repr(sim)
        assert "TEST01" in r
        assert "Test Simulation" in r

    def test_reset(self) -> None:
        sim = ConcreteSimulation()
        sim._value = 42.0
        sim.reset()
        assert sim._value == 0.0

    def test_export(self) -> None:
        sim = ConcreteSimulation()
        with tempfile.TemporaryDirectory() as tmpdir:
            sim.export(tmpdir)
            csv_path = Path(tmpdir) / "TEST01_data.csv"
            assert csv_path.exists()
            assert "x,y" in csv_path.read_text()

    def test_save_load_state(self) -> None:
        sim = ConcreteSimulation()
        sim._value = 99.5

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        sim.save_state(path)

        # Verify JSON was written
        data = json.loads(Path(path).read_text())
        assert data["id"] == "TEST01"
        assert data["value"] == 99.5

        # Load into a fresh instance
        sim2 = ConcreteSimulation()
        assert sim2._value == 0.0
        sim2.load_state(path)
        assert sim2._value == 99.5

        Path(path).unlink()

    def test_load_state_wrong_id(self) -> None:
        sim = ConcreteSimulation()

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            json.dump({"id": "WRONG", "value": 1.0}, f)
            path = f.name

        with pytest.raises(ValueError, match="WRONG"):
            sim.load_state(path)

        Path(path).unlink()

    def test_missing_attribute_raises(self) -> None:
        with pytest.raises(TypeError, match="must define class attribute"):

            class BadSim(SimulationBase):
                ID = "BAD"
                # Missing other required attributes

    def test_on_show_hide_close_defaults(self) -> None:
        sim = ConcreteSimulation()
        # These should not raise
        sim.on_show()
        sim.on_hide()
        sim.on_close()


# ---------------------------------------------------------------------------
# Utils tests
# ---------------------------------------------------------------------------


class TestUtils:
    def test_seeded_rng_reproducible(self) -> None:
        rng1 = seeded_rng(123)
        rng2 = seeded_rng(123)
        assert rng1.random() == rng2.random()

    def test_normalise(self) -> None:
        arr = np.array([2.0, 4.0, 6.0])
        result = normalise(arr)
        np.testing.assert_allclose(result, [0.0, 0.5, 1.0])

    def test_normalise_constant(self) -> None:
        arr = np.array([5.0, 5.0, 5.0])
        result = normalise(arr)
        np.testing.assert_allclose(result, [0.0, 0.0, 0.0])

    def test_clamp(self) -> None:
        assert clamp(5.0, 0.0, 10.0) == 5.0
        assert clamp(-1.0, 0.0, 10.0) == 0.0
        assert clamp(15.0, 0.0, 10.0) == 10.0

    def test_safe_eval_arithmetic(self) -> None:
        assert safe_eval("2 + 3") == 5
        assert safe_eval("2 * 3 + 1") == 7
        assert safe_eval("2 ** 3") == 8

    def test_safe_eval_functions(self) -> None:
        result = safe_eval("sin(pi / 2)")
        assert abs(result - 1.0) < 1e-10

        result = safe_eval("sqrt(4)")
        assert abs(result - 2.0) < 1e-10

    def test_safe_eval_variables(self) -> None:
        result = safe_eval("x + y", {"x": 3, "y": 7})
        assert result == 10

    def test_safe_eval_rejects_unknown(self) -> None:
        with pytest.raises(ExpressionError, match="Unknown"):
            safe_eval("badname + 1")

    def test_safe_eval_rejects_attribute_access(self) -> None:
        with pytest.raises(ExpressionError, match="Unsupported"):
            safe_eval("os.system('echo hi')")

    def test_safe_eval_rejects_bad_syntax(self) -> None:
        with pytest.raises(ExpressionError, match="Invalid syntax"):
            safe_eval("2 +")

    def test_make_callable(self) -> None:
        f = make_callable("sigma * (y - x)", ["x", "y", "sigma"])
        assert f(1.0, 2.0, 10.0) == 10.0
        assert f(0.0, 0.0, 10.0) == 0.0

    def test_make_callable_wrong_arg_count(self) -> None:
        f = make_callable("x + y", ["x", "y"])
        with pytest.raises(ExpressionError, match="Expected 2"):
            f(1.0)

    def test_make_callable_numpy_arrays(self) -> None:
        f = make_callable("sin(x)", ["x"])
        x = np.array([0.0, math.pi / 2, math.pi])
        result = f(x)
        np.testing.assert_allclose(result, [0.0, 1.0, 0.0], atol=1e-10)
