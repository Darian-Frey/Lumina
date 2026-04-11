<div align="center">

<br/>

```
██╗     ██╗   ██╗███╗   ███╗██╗███╗   ██╗ █████╗
██║     ██║   ██║████╗ ████║██║████╗  ██║██╔══██╗
██║     ██║   ██║██╔████╔██║██║██╔██╗ ██║███████║
██║     ██║   ██║██║╚██╔╝██║██║██║╚██╗██║██╔══██║
███████╗╚██████╔╝██║ ╚═╝ ██║██║██║ ╚████║██║  ██║
╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝
```

**From chaotic pendulums to galactic rotation curves — Lumina brings physics and mathematics to life through 80+ interactive simulations. Built for curious minds from A-level through to university and beyond.**

<br/>

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.0+-41CD52?logo=qt&logoColor=white)](https://pypi.org/project/PyQt6/)
[![Simulations](https://img.shields.io/badge/v0.1-10%20Simulations-8A2BE2)](SIMS_SPEC.md)
[![Tests](https://img.shields.io/badge/Tests-127%20passing-4caf50)]()
[![Status](https://img.shields.io/badge/Status-v0.1%20Release-green)]()

<br/>

</div>

---

## What is Lumina?

Lumina is an **interactive simulation suite** for physics and mathematics, targeting the gap that has existed too long between two extremes:

- **Below** — Free tools like PhET are excellent but stop at introductory level
- **Above** — MATLAB, Mathematica, and COMSOL cost hundreds or thousands of pounds and require institutional licences

Lumina lives in between. It is designed for the student who has outgrown classroom simulations but cannot afford enterprise software — covering everything from A-level fundamentals to graduate-level research topics.

---

## Simulation Categories

| Category | Count | Level Range |
|----------|-------|-------------|
| ⚙️ Classical Mechanics | 10 | 🟢 → 🟣 |
| 🌊 Waves & Optics | 10 | 🟢 → 🟣 |
| ⚡ Electromagnetism | 10 | 🟢 → 🟣 |
| 🌡️ Thermodynamics & Statistical Mechanics | 8 | 🟢 → 🟣 |
| ⚛️ Quantum Mechanics | 10 | 🟡 → 🟣 |
| 🌌 Astrophysics & Gravity | 8 | 🟡 → 🟣 |
| 📐 Pure Mathematics | 10 | 🟢 → 🟣 |
| 📊 Applied Mathematics | 10 | 🟢 → 🔴 |
| 🔬 Special Topics | 6 | 🔴 → 🟣 |

**82 simulations planned. 10 shipping in v0.1.** See [`SIMS_SPEC.md`](SIMS_SPEC.md) for the full specification, build status, and phased roadmap.

## Screenshots

Add screenshots to `docs/images/` and reference them here. Suggested set:

- `dashboard.png` — the module dashboard with category cards
- `ap03_lorenz.png` — the Lorenz attractor in action
- `p03_fractallab.png` — a deep zoom into the Mandelbrot set
- `m10_pendulum.png` — the chaotic double pendulum mid-swing
- `ap01_phase_portrait.png` — a Van der Pol phase portrait with streamlines

### Difficulty key

| Symbol | Level |
|--------|-------|
| 🟢 | GCSE / early A-level |
| 🟡 | A-level / AS-level |
| 🔴 | A-level Further / First-year university |
| 🟣 | Second-year university and above |

---

## What's in v0.1

Ten working simulations with 127 passing tests. Every module has been tested, polished, and documented.

### Simulations

| ID | Name | What it shows |
|----|------|---------------|
| **AP01** | ODE Phase Portrait | Vector fields, nullclines, fixed points with stability classification, editable equations, click-to-add trajectories |
| **AP02** | Bifurcation Diagram | Logistic map period-doubling to chaos, Lyapunov exponent, zoom-recompute for high-resolution detail |
| **AP03** | Lorenz Attractor | 3D strange attractor in four views, sensitivity to initial conditions, animated trajectories |
| **M04** | Simple Harmonic Motion | Spring-mass and pendulum, phase space ellipses, energy exchange, damping regimes |
| **M10** | Chaotic Double Pendulum | Real-time Lagrangian mechanics, trajectory trail, energy conservation check |
| **P03** | FractalLab | Six fractal types: Mandelbrot, Julia, Burning Ship, Tricorn, Multibrot, Newton. Deep zoom with full-resolution recompute |
| **T01** | Ideal Gas | 2D molecular dynamics with elastic collisions, live PV readout, speed histogram |
| **T02** | Maxwell-Boltzmann | Speed distribution vs temperature, labelled v_mp / v_avg / v_rms markers |
| **W01** | Wave Superposition | Five-wave mixer with colour-matched panels, beats and standing wave presets |
| **W02** | Fourier Synthesiser | Square, triangle, sawtooth synthesis with Gibbs phenomenon demonstration |

### Features that set Lumina apart

- **CSV + PNG export** on every simulation — no competitor offers this
- **Editable equations** — modify the system ODE in AP01 and watch it re-integrate live
- **Dark / light / high-contrast themes** with full plot support
- **Colourblind-safe palette** (Okabe-Ito) toggle
- **State save/load** to `.lumina` preset files — share parameter configurations
- **Zoom limits and Reset View** on every plot to prevent getting lost in empty space
- **Built-in help system** — `?` button per simulation + tooltips on every control
- **Category-coded dashboard** with search, level filter, and icons

---

## Architecture

Lumina uses a **launcher + modules** architecture. The launcher shell is free and open; modules are unlocked individually or as themed bundles.

```
lumina/
├── launcher/               # Main application shell (PyQt6)
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
│   ├── engine.py           # Shared simulation base classes
│   ├── plot.py             # Shared plotting utilities (pyqtgraph)
│   └── config.py           # Global settings
├── data/
│   └── sparc/              # SPARC galaxy rotation curve data (175 galaxies)
├── tests/
├── SIMS_SPEC.md
└── README.md
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| GUI | PyQt6 |
| Plotting | pyqtgraph / matplotlib |
| Numerics | NumPy, SciPy |
| Distribution | PyInstaller (.AppImage / .exe / .dmg) |

---

## Roadmap

### Phase 1 — Launch Set (v0.1)
Ten simulations targeting broad appeal and low build effort. Designed to ship fast and validate the market.

`M04` Simple Harmonic Motion · `M10` Chaotic Double Pendulum · `W01` Wave Superposition · `W02` Fourier Synthesiser · `T01` Ideal Gas · `T02` Maxwell-Boltzmann · `AP01` ODE Phase Portrait · `AP02` Bifurcation Diagram · `AP03` Lorenz Attractor · `P03` FractalLab

### Phase 2 — Core Expansion (v0.2–v0.3)
Quantum, astrophysics, and electromagnetism pillars. Introduces RotoCurve as the first research-grade module.

### Phase 3 — University Tier (v0.4–v0.5)
Medium-effort modules for first and second year undergraduates.

### Phase 4 — Research & Special Topics (v1.0)
High-effort and graduate-level modules. Premium tier.

Full details in [`SIMS_SPEC.md`](SIMS_SPEC.md).

---

## Target Audience

- **A-level and AS-level students** — particularly Further Mathematics and Physics
- **First and second year undergraduates** — Physics, Mathematics, Engineering
- **Independent researchers** — especially in gravitational physics and applied mathematics
- **Educators** — looking for tools to supplement or replace inaccessible institutional software

---

## Getting Started

### Requirements

- Python 3.11 or later
- Linux, macOS, or Windows

### Install from source

```bash
git clone https://github.com/Darian-Frey/Lumina.git
cd Lumina
pip install -r requirements.txt
python -m lumina
```

On Linux, if you get a Qt `xcb` error, install the missing system library:

```bash
sudo apt install libxcb-cursor0
```

### Run the tests

```bash
pip install -r requirements-dev.txt
pytest tests/ lumina/modules/ -v
```

All 127 tests should pass.

### Build a standalone executable

```bash
pip install pyinstaller
./build.sh
```

This produces `dist/Lumina`, a single-file executable. See [`docs/packaging.md`](docs/packaging.md) for AppImage, .exe, and .dmg instructions.

---

## Contributing

Lumina is a solo project in early development. Contributions, feedback, and simulation suggestions are welcome via [Issues](https://github.com/Darian-Frey/Lumina/issues).

If you are an educator or researcher who would like to see a specific simulation added, please open a Feature Request issue with the `simulation-request` label.

---

## Related Work

**RotoCurve / CODA** — The astrophysics pipeline underpinning the A01 module is part of an ongoing research programme in modified gravity and holographic complexity. See the [CODA repository](https://github.com/Darian-Frey) for details.

---

## Licence

MIT — see [`LICENSE`](LICENSE) for details.

---

<div align="center">
<br/>
<sub>Built on a ThinkPad. Powered by curiosity.</sub>
<br/>
<sub>v0.1 — April 2026</sub>
<br/><br/>
</div>