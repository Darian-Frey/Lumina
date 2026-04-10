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
[![Simulations](https://img.shields.io/badge/Simulations-82-8A2BE2)](SIMS_SPEC.md)
[![Status](https://img.shields.io/badge/Status-Early%20Development-orange)]()

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

**82 simulations total.** See [`SIMS_SPEC.md`](SIMS_SPEC.md) for the full specification, build status, and phased roadmap.

### Difficulty key

| Symbol | Level |
|--------|-------|
| 🟢 | GCSE / early A-level |
| 🟡 | A-level / AS-level |
| 🔴 | A-level Further / First-year university |
| 🟣 | Second-year university and above |

---

## Highlights

**RotoCurve** ✅ — Fit MOND, CODA, and Newtonian dark matter models to real SPARC galaxy rotation curve data. The only tool of its kind outside of bespoke research scripts.

**Chaotic Double Pendulum** — Real-time trajectory tracing with Lyapunov exponent readout.

**Fourier Synthesiser** — Build any waveform from harmonics and watch the series converge live.

**Quantum Tunnelling** — Vary barrier width and height, watch transmission probability update instantly.

**Ising Model** — 2D ferromagnet with Metropolis Monte Carlo, visualise the phase transition as temperature sweeps through T_c.

**FractalLab** — Mandelbrot and Julia sets with deep zoom and custom iteration rules.

**Tiling Lab** — Penrose and Ammann-Beenker aperiodic tilings with local isomorphism explorer.

**ODE Phase Portrait** — Nullclines, trajectories, fixed points, and stability classification for any 2D system.

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

> Lumina is in early development. Installation instructions will be added at v0.1.

```bash
git clone https://github.com/Darian-Frey/Lumina.git
cd Lumina
pip install -r requirements.txt
python -m lumina
```

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
<br/><br/>
</div>