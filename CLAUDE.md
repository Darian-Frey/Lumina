# CLAUDE.md — Lumina Project Handoff

This file provides context for Claude Code working on the Lumina project. Read this before touching any code.

---

## Project Overview

**Lumina** is an interactive simulation suite for physics and mathematics. It targets the gap between free classroom tools (PhET, Physion) and expensive institutional software (MATLAB, Mathematica, COMSOL).

**Primary audience:** A-level / AS-level students, first and second year undergraduates, independent researchers, educators.

**Repo:** https://github.com/Darian-Frey/Lumina  
**Maintainer:** Shane Hartley (Darian-Frey)  
**Machine:** ThinkPad P15 Gen 2i, Linux  
**IDE:** Antigravity + Claude Code plugin  

---

## Tech Stack

| Component | Choice | Notes |
|-----------|--------|-------|
| Language | Python 3.11+ | C++20 available for performance-critical modules |
| GUI framework | PyQt6 | Maintainer has deep Qt experience — use it |
| Plotting | pyqtgraph (primary), matplotlib (fallback) | pyqtgraph preferred for real-time simulation; matplotlib for static/export |
| Numerics | NumPy, SciPy | Standard — do not introduce alternatives without discussion |
| Distribution | PyInstaller | Targeting .AppImage (Linux), .exe (Windows), .dmg (macOS) |
| Tests | pytest | All modules must have tests before merge |

---

## Repository Structure

```
lumina/
├── launcher/               # Main application shell
│   ├── __init__.py
│   ├── main.py             # Entry point
│   ├── mainwindow.py       # Top-level QMainWindow
│   └── module_loader.py    # Dynamic module discovery and loading
├── modules/
│   ├── mechanics/          # M01–M10
│   ├── waves/              # W01–W10
│   ├── electromagnetism/   # E01–E10
│   ├── thermodynamics/     # T01–T08
│   ├── quantum/            # Q01–Q10
│   ├── astrophysics/       # A01–A08
│   ├── pure_maths/         # P01–P10
│   ├── applied_maths/      # AP01–AP10
│   └── special_topics/     # S01–S06
├── core/
│   ├── __init__.py
│   ├── engine.py           # SimulationBase class — all modules inherit from this
│   ├── plot.py             # Shared plot widget wrappers
│   ├── config.py           # Global constants and settings
│   └── utils.py            # Shared maths helpers
├── data/
│   └── sparc/              # 175 SPARC galaxy rotation curve datasets
├── tests/
│   ├── test_core.py
│   └── modules/            # Per-module test files mirror modules/ layout
├── docs/
├── SIMS_SPEC.md            # Master simulation specification — source of truth
├── CLAUDE.md               # This file
└── README.md
```

---

## Architecture: Launcher + Modules

Lumina uses a **plugin architecture**. The launcher is a free shell; simulations are individual modules loaded dynamically.

### SimulationBase

Every simulation module must subclass `SimulationBase` from `core/engine.py`:

```python
from core.engine import SimulationBase

class SimpleHarmonicMotion(SimulationBase):
    ID = "M04"
    NAME = "Simple Harmonic Motion"
    CATEGORY = "mechanics"
    LEVEL = "A-level"           # "GCSE" | "A-level" | "University" | "Research"
    EFFORT = "Low"              # "Low" | "Medium" | "High"
    DESCRIPTION = "Spring-mass system, simple pendulum, phase space diagram, energy exchange."
    TAGS = ["oscillation", "SHM", "pendulum", "phase space"]

    def build_ui(self) -> QWidget:
        """Return the fully constructed simulation widget."""
        ...

    def reset(self) -> None:
        """Return simulation to its initial state."""
        ...

    def export(self, path: str) -> None:
        """Export current state as PNG + CSV."""
        ...
```

The launcher discovers modules by scanning `modules/` for classes that subclass `SimulationBase`. Do not hardcode module lists anywhere in the launcher.

### Module layout

Each module lives in its own subdirectory:

```
modules/mechanics/m04_shm/
├── __init__.py             # Exports the SimulationBase subclass
├── sim.py                  # Simulation logic
├── ui.py                   # Qt widget construction
├── physics.py              # Pure maths/physics — no Qt imports allowed here
└── test_m04.py             # Module tests
```

Keep `physics.py` free of Qt. This allows physics logic to be tested without a display.

---

## Coding Standards

### General
- Python 3.11+. Use type hints everywhere.
- Line length: 100 characters.
- Formatter: `black`. Linter: `ruff`. Run both before committing.
- Docstrings: Google style.
- No global mutable state outside of `config.py`.

### Qt / PyQt6
- Use `QTimer` for simulation loops — never `time.sleep()` in the GUI thread.
- Heavy computation goes in a `QThread` worker with signals for result delivery.
- Use `pyqtSignal` / `pyqtSlot` with explicit type annotations.
- All UI construction happens in the main thread.
- Clean up timers and threads in `closeEvent`.

### Numerics
- NumPy for array operations — avoid Python loops over arrays.
- SciPy for ODE integration (`scipy.integrate.solve_ivp` with `method='RK45'` as default).
- Use `np.float64` explicitly where precision matters.
- Never use `scipy.integrate.odeint` (deprecated interface).

### Plotting (pyqtgraph)
- Prefer `pg.PlotWidget` embedded in layouts over standalone windows.
- Set `setBackground('w')` for light theme consistency.
- Use `pg.mkPen` and `pg.mkBrush` — never raw colour strings.
- For animated plots, update data on existing `PlotDataItem` objects rather than clearing and redrawing.

---

## Phase 1 — Current Build Target

The ten simulations to build for v0.1:

| ID | Name | File location |
|----|------|---------------|
| M04 | Simple Harmonic Motion | `modules/mechanics/m04_shm/` |
| M10 | Chaotic Double Pendulum | `modules/mechanics/m10_double_pendulum/` |
| W01 | Wave Superposition | `modules/waves/w01_superposition/` |
| W02 | Fourier Synthesiser | `modules/waves/w02_fourier_synth/` |
| T01 | Ideal Gas Simulation | `modules/thermodynamics/t01_ideal_gas/` |
| T02 | Maxwell-Boltzmann Distribution | `modules/thermodynamics/t02_maxwell_boltzmann/` |
| AP01 | ODE Phase Portrait | `modules/applied_maths/ap01_phase_portrait/` |
| AP02 | Bifurcation Diagram | `modules/applied_maths/ap02_bifurcation/` |
| AP03 | Lorenz Attractor | `modules/applied_maths/ap03_lorenz/` |
| P03 | FractalLab | `modules/pure_maths/p03_fractallab/` |

Build order suggestion: AP03 → M10 → AP02 → AP01 → W01 → W02 → M04 → T01 → T02 → P03. Start with the visually striking ones (Lorenz, double pendulum) to build momentum.

---

## Key Module: RotoCurve (A01) ✅

RotoCurve is the one complete module — it is the most technically distinctive part of Lumina and must be treated carefully.

**What it does:** Fits galactic rotation curves from the SPARC dataset against three models:
- Newtonian (dark matter halo)
- MOND (Modified Newtonian Dynamics, Milgrom 1983)
- CODA (Covariant Dark matter Analogue — maintainer's original framework)

**Key files (to be migrated from CODA repo):**
- `core/mimetic_engine.py` — CODA field equations
- `tools/sparc_refinery_v4.py` — SPARC data loader and preprocessor
- `data/sparc/` — 175 galaxy datasets

**Critical constants — do not change without discussion:**
```python
A0_CANONICAL = 1.2e-10        # m/s^2 — MOND canonical acceleration scale
A0_CODA = 1.264e-10           # m/s^2 — CODA zero-parameter prediction (+4.46%)
F_Q_LIMIT = (2/3)             # Correct F(Q) ~ (2/3) Q^{3/2} limit
CAUSALITY_BOUND = 0.35        # lambda <= 0.35
SPARC_N_GALAXIES = 175        # Do not hardcode subsets
```

**Known limitation:** μ_std interpolation performs poorly on high-mass bulge-dominated galaxies. This is a known theoretical gap, not a bug — do not attempt to patch it with ad-hoc corrections.

**The caustic guard amplitude λ was driven to zero by the SPARC data** — the peaked likelihood profile confirms SPARC actively disfavours the guard. λ = 0 is the correct value; do not reintroduce it.

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run a specific module
pytest tests/modules/test_m04.py -v

# Run with coverage
pytest tests/ --cov=lumina --cov-report=term-missing
```

Rules:
- Every `physics.py` file must have 100% test coverage.
- GUI tests use `pytest-qt` — do not skip them.
- Physics tests must be deterministic — seed any RNG with a fixed value.
- A module is not done until its tests pass.

---

## Do Not

- **Do not introduce new dependencies without discussion.** The dependency surface must stay minimal for distribution reasons.
- **Do not use `matplotlib` for real-time animation** — it is too slow. Use pyqtgraph.
- **Do not put physics logic in UI files.** `physics.py` must remain importable without Qt.
- **Do not hardcode paths.** Use `pathlib.Path` and resolve relative to the package root.
- **Do not modify RotoCurve physics constants** without explicit instruction. They are grounded in peer-review-targeted research.
- **Do not use `odeint`.** Use `solve_ivp`.
- **Do not use bare `except` clauses.**
- **Do not commit with failing tests.**

---

## Useful References

- Full simulation specification: [`SIMS_SPEC.md`](SIMS_SPEC.md)
- SPARC dataset paper: Lelli et al. 2016, AJ 152, 157
- MOND review: Famaey & McGaugh 2012, Living Reviews in Relativity
- PyQt6 docs: https://doc.qt.io/qtforpython-6/
- pyqtgraph docs: https://pyqtgraph.readthedocs.io/

---

## Current Status

| Item | Status |
|------|--------|
| Repo | Live, empty |
| Launcher shell | Not started |
| `core/engine.py` | Not started |
| Phase 1 modules | Not started |
| RotoCurve (A01) | Complete in CODE-GEO repo — needs migration |
| Tests | Not started |
| PyInstaller build | Not started |
| Gumroad listing | Not started |

---

*Last updated: April 2026*