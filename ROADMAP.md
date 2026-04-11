# Lumina — Development Roadmap

> For the full simulation spec and phase overview, see [`SIMS_SPEC.md`](SIMS_SPEC.md).

---

## Phase 1 — v0.1 (Current)

### Stage 1 — Core Infrastructure ✅

| Step | File | What | Status |
|------|------|------|--------|
| 1.1 | `lumina/core/config.py` | Global constants, paths, themes, palettes, button styles, category colours | ✅ Done |
| 1.2 | `lumina/core/engine.py` | `SimulationBase` ABC with save/load state, HELP_TEXT | ✅ Done |
| 1.3 | `lumina/core/utils.py` | Safe expression evaluator, maths helpers, RNG seeding | ✅ Done |
| 1.4 | `lumina/core/plot.py` | `SimPlotWidget` — theme-aware, colourblind palette, PNG/CSV export | ✅ Done |
| 1.5 | `lumina/core/help_dialog.py` | `HelpDialog` — scrollable formatted help popup | ✅ Done |
| 1.6 | `tests/test_core.py` | 25 tests for engine, config, utils | ✅ Done |

### Stage 2 — Launcher Shell ✅

| Step | File | What | Status |
|------|------|------|--------|
| 2.1 | `lumina/launcher/main.py` | Entry point, QApplication setup, theme loading | ✅ Done |
| 2.2 | `lumina/launcher/mainwindow.py` | Dashboard with category sidebar, card grid, search/filter, simulation host, toolbar with icons | ✅ Done |
| 2.3 | `lumina/launcher/module_loader.py` | Dynamic module discovery | ✅ Done |
| 2.4 | `lumina/launcher/theme.py` | Dark / light / high-contrast stylesheets, QSettings persistence | ✅ Done |

### Stage 3 — Simulations ✅

| ID | Name | Physics Tests | Features | Status |
|----|------|--------------|----------|--------|
| AP01 | ODE Phase Portrait | 10 | Editable equations, vector field, streamlines, fixed point classification, click-to-add trajectories, zoom limits | ✅ Done |
| AP02 | Bifurcation Diagram | 13 | Logistic map, Lyapunov exponent, zoom-aware recomputation, axis clamping | ✅ Done |
| AP03 | Lorenz Attractor | 11 | 4-panel view (XZ, XY, time series, sensitivity), animated trail | ✅ Done |
| M04 | Simple Harmonic Motion | 8 | Phase space, energy exchange, damping modes, zoom limits | ✅ Done |
| M10 | Chaotic Double Pendulum | 8 | Real-time animation, trajectory trail, energy conservation check | ✅ Done |
| P03 | FractalLab | 17 | 6 fractal types (Mandelbrot, Julia, Burning Ship, Tricorn, Multibrot, Newton), zoom-recompute | ✅ Done |
| T01 | Ideal Gas Simulation | 7 | 2D particle dynamics, wall collisions, PV readout, speed histogram | ✅ Done |
| T02 | Maxwell-Boltzmann | 6 | PDF curve, labelled v_mp/v_avg/v_rms markers | ✅ Done |
| W01 | Wave Superposition | 10 | 5-wave mixer, colour-matched panels, beats/standing wave presets | ✅ Done |
| W02 | Fourier Synthesiser | 12 | Square/triangle/sawtooth, Gibbs overshoot, partial sum vs target | ✅ Done |

**Total: 127 tests, all passing.**

### Stage 4 — Polish ✅

| Step | What | Status |
|------|------|--------|
| 4.1 | All 10 modules load, render, export, save/load state | ✅ Verified |
| 4.2 | Dashboard cards with category colour banners and icons | ✅ Done |
| 4.3 | Toolbar buttons with Unicode icons and tooltips | ✅ Done |
| 4.4 | Help system — ? button with formatted help dialog | ✅ Done |
| 4.5 | Tooltips on every control in every module | ✅ Done |
| 4.6 | Zoom limits and Reset View on all modules | ✅ Done |
| 4.7 | Consistent 240px control panel width across all modules | ✅ Done |
| 4.8 | Dark / light / high-contrast themes tested | ✅ Verified |
| 4.9 | Colourblind palette toggle tested | ✅ Verified |
| 4.10 | CSV + PNG export tested on all modules | ✅ Verified |

### Remaining for v0.1 release

| Step | What | Status |
|------|------|--------|
| 4.11 | Dark mode visual fix — theme-aware plots, cards, toolbar, module colours | ✅ Done |
| 4.12 | PyInstaller spec file + build script + packaging docs | ✅ Done |
| 4.13 | README update — installation instructions, feature list, screenshots section | ✅ Done |

**v0.1 ship checklist complete.** Only step left is running `./build.sh` on your machine and uploading screenshots to `docs/images/`.

---

## Platform Features (v0.1)

| Feature | Status |
|---------|--------|
| CSV + PNG export on every simulation | ✅ Done |
| Safe expression evaluator (Level 2 editable equations) | ✅ Done (AP01) |
| JSON state save/load (.lumina files) | ✅ Done |
| Dark / light / high-contrast themes | ✅ Done |
| Colourblind-safe Okabe-Ito palette toggle | ✅ Done |
| Help system (? button + tooltips) | ✅ Done |
| Category-coloured dashboard cards with icons | ✅ Done |
| Zoom limits to prevent navigation to meaningless regions | ✅ Done |

---

## Phase 2 — v0.2–v0.3 (Next)

**Simulations:** Q01, Q02, E01, E03, A01 (RotoCurve), A02, M01, W04, AP04, AP05

**Platform features:**
- Side-by-side model comparison
- Session replay
- Guided mode (preset-driven walkthroughs)

## Phase 3 — v0.4–v0.5

**Simulations:** Q04, Q07, E07, T06, A03, A08, P02, P04, AP06, AP07

**Platform features:**
- Full keyboard navigation (WCAG 2.1)
- Favourites and recents

## Phase 4 — v1.0

**Simulations:** All remaining high-effort and research-level modules.

**Platform features:**
- LMS integration
- Plugin API for third-party modules

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-10 | Build order: AP03 first | Visually striking, validates full pipeline |
| 2026-04-10 | No new dependencies for v0.1 | Distribution surface must stay minimal |
| 2026-04-10 | Tests at repo root (`tests/`) | Matches pyproject.toml testpaths |
| 2026-04-10 | No C++ rewrite — optimise Python first | Performance issues are algorithmic, not language-speed |
| 2026-04-10 | Zoom limits on all modules | Prevents users navigating to meaningless regions |
| 2026-04-10 | Compute button (not auto-recompute on zoom) for AP01/AP02/P03 | Prevents cascading recompute freezes |
| 2026-04-11 | 6 fractal types in FractalLab | Burning Ship, Tricorn, Multibrot, Newton added |
| 2026-04-11 | Help system: ? button + tooltips | Option B + C from research — professional tools use both |
| 2026-04-11 | Dashboard card redesign with category colour banners and icons | Professional polish — elevates from dev tool to product feel |
| 2026-04-11 | Theme re-launches active simulation on change | Cleanest way to propagate plot colour changes without a global signal system |
| 2026-04-11 | Cards and toolbar buttons inherit theme colours from Qt stylesheet | Removes hardcoded light-mode assumptions that broke dark mode |
| 2026-04-11 | Plain `?` for help button instead of emoji | Unicode emoji had fixed red/brown rendering that clashed with the blue button |

---

*Last updated: 2026-04-11 (dark mode pass complete)*
*Maintainer: Darian-Frey*
