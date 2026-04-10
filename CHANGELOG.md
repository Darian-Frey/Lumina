# Changelog

All notable changes to Lumina will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Lumina uses [Semantic Versioning](https://semver.org/).

---

## [0.1.0] - 2026-04-11

### Added

**Core infrastructure**
- `SimulationBase` abstract base class with `build_ui()`, `reset()`, `export()`, `save_state()`, `load_state()`, `HELP_TEXT`
- `SimPlotWidget` — theme-aware pyqtgraph wrapper with colourblind palette, PNG/CSV export
- Safe expression evaluator (`safe_eval`, `make_callable`) for Level 2 editable equations
- `HelpDialog` — scrollable formatted help popup for each simulation
- Global config with constants, paths, themes, palettes, button styles, category colours

**Launcher**
- Dashboard with category sidebar, search bar, level filter
- Simulation cards with category colour banners and Unicode icons
- Dynamic module discovery — no hardcoded module lists
- Dark / light / high-contrast themes with QSettings persistence
- Colourblind-safe Okabe-Ito palette toggle
- Toolbar with icons: Dashboard, Reset, Export, Save, Load, Help (?)

**Simulations (10 modules)**
- AP01 ODE Phase Portrait — editable equations, vector field, streamlines, fixed point classification, click-to-add trajectories
- AP02 Bifurcation Diagram — logistic map, Lyapunov exponent, zoom-aware recomputation
- AP03 Lorenz Attractor — 4-panel view, animated trail, sensitivity to ICs
- M04 Simple Harmonic Motion — phase space, energy exchange, damping modes
- M10 Chaotic Double Pendulum — real-time animation, trajectory trail, energy conservation
- P03 FractalLab — 6 fractal types (Mandelbrot, Julia, Burning Ship, Tricorn, Multibrot, Newton), zoom-recompute at full resolution
- T01 Ideal Gas Simulation — 2D particle dynamics, wall collisions, PV readout
- T02 Maxwell-Boltzmann Distribution — PDF curve with labelled v_mp, v_avg, v_rms markers
- W01 Wave Superposition — 5-wave mixer, colour-matched panels, beats and standing wave presets
- W02 Fourier Synthesiser — square/triangle/sawtooth, Gibbs overshoot, partial sum vs target overlay

**Quality**
- 127 tests (all passing) covering physics, engine, config, and utilities
- Zoom limits on all modules to prevent navigation to meaningless regions
- Reset View button on all modules
- Tooltips on every control in every module
- CSV + PNG export verified on all modules
- Consistent 240px control panel width across all modules

**Project files**
- `SIMS_SPEC.md` — master specification for all 82 planned simulations
- `ROADMAP.md` — detailed build plan and decision log
- `CLAUDE.md` — Claude Code handoff document
- `pyproject.toml` — project metadata, black, ruff, mypy, pytest configuration
- `.gitignore`, `requirements.txt`, `requirements-dev.txt`
- GitHub issue templates for bug reports and simulation requests

---

<!-- Add new versions above this line -->
