"""
lumina/launcher/module_loader.py
--------------------------------
Dynamic module discovery — scans ``lumina/modules/`` for SimulationBase
subclasses and registers their metadata for the launcher dashboard.

In development mode this uses ``pkgutil.walk_packages`` to find modules
on the filesystem. In a frozen PyInstaller build, the filesystem walk
misses modules bundled in the PYZ archive, so we also try an explicit
fallback list of known module paths.
"""

from __future__ import annotations

import importlib
import logging
import pkgutil
import sys

import lumina.modules as _modules_pkg
from lumina.core.engine import SimulationBase

logger = logging.getLogger(__name__)

# Explicit fallback list — used when pkgutil.walk_packages can't see frozen modules.
# Add new modules here when they're created. Order doesn't matter (sorted later).
_KNOWN_MODULES: list[str] = [
    "lumina.modules.applied_maths.ap01_phase_portrait.sim",
    "lumina.modules.applied_maths.ap02_bifurcation.sim",
    "lumina.modules.applied_maths.ap03_lorenz.sim",
    "lumina.modules.mechanics.m04_shm.sim",
    "lumina.modules.mechanics.m10_double_pendulum.sim",
    "lumina.modules.pure_maths.p03_fractallab.sim",
    "lumina.modules.quantum.q01_particle_in_box.sim",
    "lumina.modules.thermodynamics.t01_ideal_gas.sim",
    "lumina.modules.thermodynamics.t02_maxwell_boltzmann.sim",
    "lumina.modules.waves.w01_superposition.sim",
    "lumina.modules.waves.w02_fourier_synth.sim",
]


def _is_concrete_simulation(obj: object) -> bool:
    """Check if obj is a concrete (instantiable) SimulationBase subclass."""
    return (
        isinstance(obj, type)
        and issubclass(obj, SimulationBase)
        and obj is not SimulationBase
        and not getattr(obj, "__abstractmethods__", None)
    )


def _collect_from_module(module: object, found: list[type[SimulationBase]]) -> None:
    """Find SimulationBase subclasses in a module's namespace and add to found list."""
    for attr_name in dir(module):
        obj = getattr(module, attr_name)
        if _is_concrete_simulation(obj) and obj not in found:
            found.append(obj)
            logger.info("Discovered module: %s (%s)", obj.ID, obj.NAME)


def discover_modules() -> list[type[SimulationBase]]:
    """Discover all SimulationBase subclasses.

    Uses two strategies in sequence:
      1. Walk ``lumina.modules`` with ``pkgutil.walk_packages`` (works in dev mode).
      2. Try the explicit ``_KNOWN_MODULES`` list (catches frozen PyInstaller modules
         that walk_packages misses because they live in the PYZ archive).

    Returns:
        A list of concrete SimulationBase subclass *types*, sorted by ID.
    """
    found: list[type[SimulationBase]] = []

    # Strategy 1: filesystem walk
    package_path = _modules_pkg.__path__
    prefix = _modules_pkg.__name__ + "."

    for _importer, modname, _ispkg in pkgutil.walk_packages(package_path, prefix):
        try:
            module = importlib.import_module(modname)
        except Exception:
            logger.warning("Failed to import %s", modname, exc_info=True)
            continue
        _collect_from_module(module, found)

    # Strategy 2: explicit fallback (catches frozen modules in PYZ archive)
    is_frozen = getattr(sys, "frozen", False)
    for modname in _KNOWN_MODULES:
        try:
            module = importlib.import_module(modname)
        except Exception:
            if is_frozen:
                logger.warning(
                    "Failed to import known module %s", modname, exc_info=True,
                )
            continue
        _collect_from_module(module, found)

    found.sort(key=lambda cls: cls.ID)
    return found
