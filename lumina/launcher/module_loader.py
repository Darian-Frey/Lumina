"""
lumina/launcher/module_loader.py
--------------------------------
Dynamic module discovery — scans ``lumina/modules/`` for SimulationBase
subclasses and registers their metadata for the launcher dashboard.

No module lists are hardcoded. A new module is discovered automatically
by placing it in the correct directory with a SimulationBase subclass
exported from its ``__init__.py``.
"""

from __future__ import annotations

import importlib
import logging
import pkgutil
from typing import TYPE_CHECKING

import lumina.modules as _modules_pkg
from lumina.core.engine import SimulationBase

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def discover_modules() -> list[type[SimulationBase]]:
    """Walk the ``lumina.modules`` package tree and collect SimulationBase subclasses.

    Returns:
        A list of concrete SimulationBase subclass *types* (not instances),
        sorted by their ID attribute.
    """
    found: list[type[SimulationBase]] = []

    # Walk all sub-packages under lumina/modules/
    package_path = _modules_pkg.__path__
    prefix = _modules_pkg.__name__ + "."

    for importer, modname, ispkg in pkgutil.walk_packages(package_path, prefix):
        try:
            module = importlib.import_module(modname)
        except Exception:
            logger.warning("Failed to import %s", modname, exc_info=True)
            continue

        # Look for SimulationBase subclasses in the module's namespace
        for attr_name in dir(module):
            obj = getattr(module, attr_name)
            if (
                isinstance(obj, type)
                and issubclass(obj, SimulationBase)
                and obj is not SimulationBase
                and not getattr(obj, "__abstractmethods__", None)
            ):
                # Avoid duplicates (a class may be re-exported)
                if obj not in found:
                    found.append(obj)
                    logger.info("Discovered module: %s (%s)", obj.ID, obj.NAME)

    found.sort(key=lambda cls: cls.ID)
    return found
