# Lumina — Development Roadmap

> Detailed build plan for Phase 1 (v0.1). For the full simulation spec and phase overview, see [`SIMS_SPEC.md`](SIMS_SPEC.md).

---

## Phase 1 Build Plan

### Stage 1 — Core Infrastructure

Everything else depends on this. No module can be built until the core is solid.

| Step | File | What | Status |
|------|------|------|--------|
| 1.1 | `lumina/core/config.py` | Global constants, paths, theme settings, colour palettes (including colourblind-safe set) | Not started |
| 1.2 | `lumina/core/engine.py` | `SimulationBase` ABC — `build_ui()`, `reset()`, `export()`, `save_state()`, `load_state()`, metadata fields (ID, NAME, CATEGORY, LEVEL, TAGS) | Not started |
| 1.3 | `lumina/core/utils.py` | Shared maths helpers, expression parser for editable equations, RNG seeding utilities | Not started |
| 1.4 | `lumina/core/plot.py` | `SimPlotWidget` wrapper around `pg.PlotWidget` — theme-aware, colourblind-safe palette, built-in export (PNG), axis labelling helpers | Not started |
| 1.5 | `lumina/core/equations.py` | `EquationPanel` widget — renders LaTeX via matplotlib mathtext, parameter highlighting, optional edit mode with expression parsing | Not started |
| 1.6 | `tests/test_core.py` | Tests for engine, config, utils, plot, equations | Not started |

### Stage 2 — Launcher Shell

The dashboard that hosts everything. Must be functional before modules are useful.

| Step | File | What | Status |
|------|------|------|--------|
| 2.1 | `lumina/launcher/main.py` | Entry point — `QApplication` setup, theme loading, argument parsing | Not started |
| 2.2 | `lumina/launcher/mainwindow.py` | `QMainWindow` — sidebar (category tree), central area (card grid / simulation host), top bar (search, level filter, theme toggle) | Not started |
| 2.3 | `lumina/launcher/module_loader.py` | Dynamic module discovery — scan `modules/` for `SimulationBase` subclasses, register metadata | Not started |
| 2.4 | `lumina/launcher/theme.py` | Qt stylesheet loader — dark / light / high-contrast, colourblind palette toggle, persisted in QSettings | Not started |
| 2.5 | `lumina/launcher/preset.py` | `.lumina` preset file handler — load/save JSON state, apply to simulation, instructional text overlay | Not started |

### Stage 3 — Simulations (build order)

Each module follows the standard layout: `__init__.py`, `sim.py`, `ui.py`, `physics.py`, `test_*.py`.

Physics in `physics.py` (no Qt imports). UI in `ui.py`. Wiring in `sim.py`.

| Order | ID | Name | Key physics | Differentiating features | Status |
|-------|-----|------|------------|-------------------------|--------|
| 1 | AP03 | Lorenz Attractor | `dx/dt = sigma(y-x)`, `dy/dt = x(rho-z)-y`, `dz/dt = xy - beta*z`. Default: sigma=10, rho=28, beta=8/3. `solve_ivp` RK45. | 3D trajectory (pyqtgraph GLViewWidget), time series, sensitivity comparison (two ICs), **editable equations (Level 2)**, live equation panel | Not started |
| 2 | M10 | Double Pendulum | Lagrangian mechanics — 4 coupled first-order ODEs (theta1, omega1, theta2, omega2). Parameters: m1, m2, L1, L2, g. | Real-time animation + trajectory trace of lower bob, Lyapunov exponent readout, energy conservation check, live equation panel | Not started |
| 3 | AP02 | Bifurcation Diagram | Logistic map `x_{n+1} = r*x_n*(1-x_n)`. r in [2.5, 4.0]. 1000 r values, 1000 iterations (discard 500 transient). | Scatter plot with zoom into Feigenbaum regions, period-doubling markers, live equation panel, **editable map function (Level 2)** | Not started |
| 4 | AP01 | ODE Phase Portrait | User-defined 2D system `dx/dt = f(x,y)`, `dy/dt = g(x,y)`. Nullclines via contour. Fixed points via `fsolve`. Classification via Jacobian eigenvalues. | Vector field (quiver), click-to-add trajectories, fixed point markers (node/saddle/spiral/centre), **editable equations (Level 2)**, live equation panel | Not started |
| 5 | W01 | Wave Superposition | `y(x,t) = sum A_i * sin(k_i*x - omega_i*t + phi_i)`. 2-5 waves. | Individual waves + sum, beats demo, standing wave demo, **editable wave functions (Level 2)**, live equation panel | Not started |
| 6 | W02 | Fourier Synthesiser | Square: `b_n = 4/(n*pi)` odd n. Triangle: `b_n = 8*(-1)^((n-1)/2)/(n^2*pi^2)` odd n. Sawtooth: `b_n = -2*(-1)^n/(n*pi)`. | Harmonic sliders (N=1 to 50), Gibbs phenomenon, target waveform overlay, live equation panel showing partial sum | Not started |
| 7 | M04 | Simple Harmonic Motion | Spring-mass: `x(t) = A*cos(omega*t + phi)`, `omega = sqrt(k/m)`. Pendulum: `omega = sqrt(g/L)`. Damping: underdamped, critical, overdamped. | Phase space (x vs v), energy exchange (KE/PE bar + plot), damping mode selector, live equation panel | Not started |
| 8 | T01 | Ideal Gas Simulation | 2D molecular dynamics — 200-500 elastic particles, circle-circle collisions. Measure P from wall impulses, verify PV=NkT. | Particle animation, real-time PV readout, isothermal/isobaric/isochoric mode toggles, live equation panel | Not started |
| 9 | T02 | Maxwell-Boltzmann | `f(v) = 4*pi*n*(m/(2*pi*k_B*T))^(3/2) * v^2 * exp(-m*v^2/(2*k_B*T))`. | Live speed histogram vs theoretical curve, v_mp / v_avg / v_rms markers, pairs with T01, live equation panel | Not started |
| 10 | P03 | FractalLab | Mandelbrot: `z_{n+1} = z_n^2 + c`, escape at `|z| > 2`. Julia: fixed c, vary z_0. Escape-time colouring, max 256-1000 iterations. | Mouse-rectangle zoom, colour map selector (HSV, cubehelix, custom), Julia/Mandelbrot toggle, custom iteration rule input, live equation panel | Not started |

### Stage 4 — Polish and Ship

| Step | What | Status |
|------|------|--------|
| 4.1 | Integration tests — all 10 modules load, render, export, save/load state | Not started |
| 4.2 | Preset files — create 2-3 example `.lumina` presets per module | Not started |
| 4.3 | PyInstaller packaging — .AppImage (Linux), .exe (Windows), .dmg (macOS) | Not started |
| 4.4 | Performance pass — profile on low-end hardware, optimise bottlenecks | Not started |
| 4.5 | README update — installation instructions, screenshots, feature list | Not started |
| 4.6 | CHANGELOG update — v0.1 release notes | Not started |

---

## Platform Features (v0.1)

Features baked into the core, available to all simulations.

### Export (CSV + PNG)
- Every simulation inherits `export(path)` from `SimulationBase`
- Exports current plot as PNG and parameter/data state as CSV
- Triggered from toolbar button or File menu
- **Why it matters:** No free competitor offers this. Students doing coursework need data export constantly.

### Live Equation Display
- **Level 1 (all sims):** LaTeX-rendered equation panel. Parameter values highlight and update in real-time as sliders move. Read-only. Uses matplotlib mathtext for rendering.
- **Level 2 (AP01, AP03, W01, W02, AP02, P03):** Equation is editable. User can modify terms (e.g. add a damping term to Lorenz, change the iteration rule in FractalLab). A lightweight expression parser converts the input to a callable function. Simulation re-integrates live.
- **Why it matters:** PhET deliberately hides equations. Falstad shows static formulas. Nobody links the maths to the visuals dynamically.

### JSON Presets
- `.lumina` files — JSON containing simulation ID, parameter state, locked controls list, and optional instructional text
- Teachers create presets and share via email / LMS
- Students open a preset to get a guided starting state
- **Why it matters:** No desktop simulation tool offers shareable parameter configurations.

### Theming
- Dark / light / high-contrast modes via Qt stylesheets
- Colourblind-safe palette toggle (Okabe-Ito or similar) applied to all plots
- Persisted in QSettings
- **Why it matters:** PhET, Falstad, Desmos are all light-only. Colourblind support is absent from every free competitor.

### State Save/Load
- `save_state()` / `load_state()` on `SimulationBase` — serialise full simulation state to JSON
- Resume where you left off
- **Why it matters:** PhET resets on refresh. No free sim tool persists state.

---

## Dependencies

No new dependencies beyond what is already in `requirements.txt`:

| Dependency | Used for |
|-----------|----------|
| PyQt6 | GUI framework, theming, QTimer animation loops |
| pyqtgraph | Real-time plotting, 3D GLViewWidget (Lorenz), PlotWidget |
| NumPy | Array operations, vectorised fractal computation |
| SciPy | `solve_ivp` (RK45) for ODE integration, `fsolve` for fixed points |
| matplotlib | LaTeX equation rendering (mathtext), static/export plots |

**Expression parsing for Level 2 editable equations:** Use Python's `ast.parse` in `ast.literal_eval`-safe mode + a restricted evaluator, or `sympy.sympify` if symbolic differentiation is needed (Jacobian computation for AP01). `sympy` would be a new dependency — discuss before adding.

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-10 | Build order: AP03 first | Visually striking, trivial physics, validates full pipeline end-to-end |
| 2026-04-10 | Level 1 equations for all sims, Level 2 for AP01/AP03/W01/W02/AP02/P03 | Level 2 requires expression parsing; only makes sense where arbitrary equations are meaningful |
| 2026-04-10 | No new dependencies for v0.1 (pending sympy discussion) | Distribution surface must stay minimal per CLAUDE.md |
| 2026-04-10 | Tests at repo root (`tests/`) not inside `lumina/` | Matches `testpaths = ["tests"]` in pyproject.toml |

---

*Last updated: 2026-04-10*
*Maintainer: Darian-Frey*
