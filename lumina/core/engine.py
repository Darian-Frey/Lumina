"""
lumina/core/engine.py
---------------------
Base class for all Lumina simulation modules.

Every simulation module must subclass SimulationBase and implement the
abstract methods defined here. The launcher discovers modules by scanning
for SimulationBase subclasses — do not hardcode module lists anywhere.

Usage
-----
    from lumina.core.engine import SimulationBase

    class MySimulation(SimulationBase):
        ID = "M04"
        NAME = "Simple Harmonic Motion"
        CATEGORY = "mechanics"
        LEVEL = "A-level"
        EFFORT = "Low"
        DESCRIPTION = "Spring-mass system, pendulum, phase diagrams."
        TAGS = ["SHM", "oscillation", "pendulum"]

        def build_ui(self) -> QWidget:
            ...

        def reset(self) -> None:
            ...

        def export(self, path: str) -> None:
            ...
"""

from __future__ import annotations

import abc
import json
import logging
from pathlib import Path
from typing import Any, ClassVar

from PyQt6.QtWidgets import QWidget

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Level and category constants — use these, do not use raw strings elsewhere
# ---------------------------------------------------------------------------

class Level:
    GCSE = "GCSE"
    A_LEVEL = "A-level"
    UNIVERSITY = "University"
    RESEARCH = "Research"


class Category:
    MECHANICS = "mechanics"
    WAVES = "waves"
    ELECTROMAGNETISM = "electromagnetism"
    THERMODYNAMICS = "thermodynamics"
    QUANTUM = "quantum"
    ASTROPHYSICS = "astrophysics"
    PURE_MATHS = "pure_maths"
    APPLIED_MATHS = "applied_maths"
    SPECIAL_TOPICS = "special_topics"


class Effort:
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


# ---------------------------------------------------------------------------
# SimulationBase
# ---------------------------------------------------------------------------

class SimulationBase(abc.ABC):
    """Abstract base class for all Lumina simulation modules.

    Class attributes
    ----------------
    ID : str
        Unique simulation identifier from SIMS_SPEC.md (e.g. "M04", "AP01").
    NAME : str
        Human-readable display name shown in the launcher.
    CATEGORY : str
        One of the Category constants above.
    LEVEL : str
        One of the Level constants above.
    EFFORT : str
        One of the Effort constants — for internal tracking only, not shown to users.
    DESCRIPTION : str
        One-sentence description shown in the launcher module browser.
    TAGS : list[str]
        Searchable tags for the launcher search bar.
    """

    ID: ClassVar[str]
    NAME: ClassVar[str]
    CATEGORY: ClassVar[str]
    LEVEL: ClassVar[str]
    EFFORT: ClassVar[str]
    DESCRIPTION: ClassVar[str]
    TAGS: ClassVar[list[str]] = []
    HELP_TEXT: ClassVar[str] = ""

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Validate that required class attributes are defined on subclasses."""
        super().__init_subclass__(**kwargs)
        required = ("ID", "NAME", "CATEGORY", "LEVEL", "EFFORT", "DESCRIPTION")
        for attr in required:
            if not hasattr(cls, attr):
                raise TypeError(
                    f"{cls.__name__} must define class attribute '{attr}'. "
                    f"See CLAUDE.md for the SimulationBase contract."
                )

    # ------------------------------------------------------------------
    # Abstract interface — all subclasses must implement these
    # ------------------------------------------------------------------

    @abc.abstractmethod
    def build_ui(self) -> QWidget:
        """Construct and return the simulation's Qt widget.

        This method is called once by the launcher when the module is first
        opened. The returned widget is embedded in the launcher's content area.

        Must be called from the main thread. All Qt object creation must
        happen here, not in __init__.

        Returns
        -------
        QWidget
            The fully constructed simulation widget.
        """

    @abc.abstractmethod
    def reset(self) -> None:
        """Return the simulation to its initial state.

        Called when the user clicks the Reset button in the launcher toolbar.
        Must stop any running timers or threads before reinitialising state.
        """

    @abc.abstractmethod
    def export(self, path: str) -> None:
        """Export the current simulation state to disk.

        Implementations should write at minimum:
          - A PNG of the current plot at 300 dpi
          - A CSV of the current data

        Parameters
        ----------
        path : str
            Directory path to write output files into. Filenames should be
            derived from self.ID and self.NAME.
        """

    # ------------------------------------------------------------------
    # Optional hooks — override as needed
    # ------------------------------------------------------------------

    def on_show(self) -> None:
        """Called when the module becomes visible in the launcher.

        Override to resume paused timers or restart animations.
        Default implementation does nothing.
        """

    def on_hide(self) -> None:
        """Called when the module is hidden or another module is selected.

        Override to pause timers and reduce CPU usage.
        Default implementation does nothing.
        """

    def on_close(self) -> None:
        """Called when the launcher is closing.

        Override to clean up QThread workers and QTimers.
        Default implementation does nothing.
        """

    # ------------------------------------------------------------------
    # Concrete helpers available to all subclasses
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # State persistence — save/load simulation parameters
    # ------------------------------------------------------------------

    def get_state(self) -> dict[str, Any]:
        """Return the current simulation state as a JSON-serialisable dict.

        Override in subclasses to include simulation-specific parameters
        (slider values, initial conditions, etc.). The base implementation
        returns metadata only.

        Returns
        -------
        dict
            Simulation state suitable for JSON serialisation.
        """
        return {
            "id": self.ID,
            "name": self.NAME,
            "category": self.CATEGORY,
            "level": self.LEVEL,
        }

    def set_state(self, state: dict[str, Any]) -> None:
        """Restore simulation state from a dict.

        Override in subclasses to restore simulation-specific parameters.
        The base implementation does nothing — subclasses should apply
        the parameter values to their sliders/controls.

        Parameters
        ----------
        state : dict
            A state dict previously returned by get_state().
        """

    def save_state(self, path: str | Path) -> None:
        """Save current simulation state to a JSON file.

        Parameters
        ----------
        path : str or Path
            Output file path.
        """
        path = Path(path)
        state = self.get_state()
        path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        self.log(f"State saved to {path}", logging.INFO)

    def load_state(self, path: str | Path) -> None:
        """Load simulation state from a JSON file.

        Parameters
        ----------
        path : str or Path
            Input file path.
        """
        path = Path(path)
        state = json.loads(path.read_text(encoding="utf-8"))
        if state.get("id") != self.ID:
            raise ValueError(
                f"State file is for '{state.get('id')}', "
                f"but this simulation is '{self.ID}'"
            )
        self.set_state(state)
        self.log(f"State loaded from {path}", logging.INFO)

    # ------------------------------------------------------------------
    # Concrete helpers available to all subclasses
    # ------------------------------------------------------------------

    def log(self, message: str, level: int = logging.DEBUG) -> None:
        """Write a prefixed message to the Lumina logger.

        Parameters
        ----------
        message : str
            The message to log.
        level : int
            A logging level constant (e.g. logging.INFO). Default: DEBUG.
        """
        logger.log(level, "[%s] %s", self.ID, message)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.ID!r} name={self.NAME!r}>"
