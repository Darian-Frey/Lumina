# Lumina — Simulation Specification

> From chaotic pendulums to galactic rotation curves — Lumina brings physics and mathematics to life through 80+ interactive simulations. Built for curious minds from A-level through to university and beyond.

---

## Contents

- [Overview](#overview)
- [Difficulty Key](#difficulty-key)
- [Build Effort Key](#build-effort-key)
- [Status Key](#status-key)
- [Classical Mechanics](#-classical-mechanics)
- [Waves & Optics](#-waves--optics)
- [Electromagnetism](#-electromagnetism)
- [Thermodynamics & Statistical Mechanics](#️-thermodynamics--statistical-mechanics)
- [Quantum Mechanics](#-quantum-mechanics)
- [Astrophysics & Gravity](#-astrophysics--gravity)
- [Pure Mathematics](#-pure-mathematics)
- [Applied Mathematics](#-applied-mathematics)
- [Special Topics](#-special-topics)
- [Phase Roadmap](#phase-roadmap)
- [Summary](#summary)

---

## Overview

Lumina is an interactive simulation suite targeting the gap between free classroom tools (PhET, Physion) and expensive institutional software (MATLAB, Mathematica, COMSOL). The primary audience is:

- **A-level / AS-level students** (particularly Further Maths and Physics)
- **First and second year undergraduates** (Physics, Maths, Engineering)
- **Independent researchers and educators**

Simulations are delivered as standalone desktop modules under a unified launcher shell. Modules are unlocked individually or as themed bundles.

---

## Difficulty Key

| Symbol | Level |
|--------|-------|
| 🟢 | GCSE / early A-level |
| 🟡 | A-level / AS-level |
| 🔴 | A-level Further / First-year university |
| 🟣 | Second-year university and above |

---

## Build Effort Key

| Label | Estimated time (solo developer) |
|-------|-------------------------------|
| Low | 1–3 days |
| Medium | 1–2 weeks |
| High | 2–4 weeks |

---

## Status Key

| Symbol | Meaning |
|--------|---------|
| ✅ | Complete |
| 🚧 | In progress |
| 📋 | Planned |

---

## ⚙️ Classical Mechanics

| ID | Name | Description | Level | Effort | Status |
|----|------|-------------|-------|--------|--------|
| M01 | Projectile Motion | Launch angle, initial velocity, air resistance toggle, range and height readouts | 🟢 | Low | 📋 |
| M02 | Newton's Laws Sandbox | Apply forces to objects on inclines and flat surfaces, static and kinetic friction | 🟢 | Low | 📋 |
| M03 | Circular Motion | Centripetal force, banking angle, conical pendulum, vary mass/speed/radius | 🟡 | Low | 📋 |
| M04 | Simple Harmonic Motion | Spring-mass system, simple pendulum, phase space diagram, energy exchange | 🟡 | Low | 📋 |
| M05 | Coupled Oscillators | Two pendulums linked by a spring, normal modes, energy transfer between modes | 🔴 | Medium | 📋 |
| M06 | N-Body Gravity | Up to 10 gravitating bodies, real-time orbital path tracing, centre of mass frame | 🔴 | Medium | 📋 |
| M07 | Lagrangian Sandbox | Define kinetic and potential energy symbolically, derive and solve equations of motion | 🟣 | High | 📋 |
| M08 | Rigid Body Rotation | Moment of inertia tensor, Euler angles, torque, gyroscopic precession | 🔴 | Medium | 📋 |
| M09 | Collision Lab | 1D and 2D elastic and inelastic collisions, centre of momentum frame toggle | 🟡 | Low | 📋 |
| M10 | Chaotic Double Pendulum | Double pendulum with trajectory tracing and Lyapunov exponent readout | 🔴 | Low | 📋 |

---

## 🌊 Waves & Optics

| ID | Name | Description | Level | Effort | Status |
|----|------|-------------|-------|--------|--------|
| W01 | Wave Superposition | Add sinusoidal waves, visualise beats, standing waves, vary amplitude/frequency/phase | 🟢 | Low | 📋 |
| W02 | Fourier Synthesiser | Draw a waveform by adding harmonics, watch the series converge live | 🟡 | Low | 📋 |
| W03 | Fourier Transform Visualiser | Real signal to frequency domain, windowing functions, spectrogram view | 🔴 | Medium | 📋 |
| W04 | Diffraction & Interference | Single slit, double slit, diffraction grating — vary wavelength and slit separation | 🟡 | Low | 📋 |
| W05 | Doppler Effect | Moving source and/or observer, shock cone, vary speed and frequency | 🟢 | Low | 📋 |
| W06 | Polarisation | Malus's law, linear and circular polarisation, wave plates, Stokes parameters | 🟡 | Low | 📋 |
| W07 | Ray Optics Sandbox | Mirrors, converging/diverging lenses, prisms — drag and drop, live ray tracing | 🟢 | Medium | 📋 |
| W08 | Wave Equation Solver | 2D wave on a membrane, selectable boundary conditions, normal mode decomposition | 🔴 | Medium | 📋 |
| W09 | Dispersion & Group Velocity | Phase velocity vs group velocity, Gaussian wave packets, anomalous dispersion | 🔴 | Medium | 📋 |
| W10 | Fabry-Pérot Etalon | Interference fringes, cavity finesse, free spectral range, mirror reflectivity | 🟣 | Medium | 📋 |

---

## ⚡ Electromagnetism

| ID | Name | Description | Level | Effort | Status |
|----|------|-------------|-------|--------|--------|
| E01 | Electric Field Lines | Point charges, dipoles, conductors — drag charges, watch field update live | 🟢 | Low | 📋 |
| E02 | Gauss's Law Visualiser | Gaussian surfaces, electric flux, symmetry arguments for common charge distributions | 🟡 | Medium | 📋 |
| E03 | RC / RL / LC Circuits | Transient charge/discharge, phasor diagrams, resonance in LC circuits | 🟡 | Low | 📋 |
| E04 | Magnetic Field Mapper | Biot-Savart for current loops, straight wires and solenoids, field line visualisation | 🟡 | Medium | 📋 |
| E05 | Electromagnetic Induction | Moving conductor in a field, Faraday's law, Lenz's law, induced EMF readout | 🟡 | Medium | 📋 |
| E06 | Maxwell's Equations Visualiser | Divergence and curl of E and B, Gauss's and Ampère's laws in differential form | 🔴 | High | 📋 |
| E07 | Electromagnetic Wave | Propagating E and B field, polarisation, Poynting vector, vary frequency | 🔴 | Medium | 📋 |
| E08 | AC Circuit Analyser | Phasors, complex impedance, RLC resonance, power factor, admittance | 🔴 | Medium | 📋 |
| E09 | Hall Effect | Current-carrying conductor in a magnetic field, charge carrier sign, Hall voltage | 🔴 | Low | 📋 |
| E10 | Plasma Oscillations | Electron fluid model, plasma frequency, Langmuir waves | 🟣 | High | 📋 |

---

## 🌡️ Thermodynamics & Statistical Mechanics

| ID | Name | Description | Level | Effort | Status |
|----|------|-------------|-------|--------|--------|
| T01 | Ideal Gas Simulation | Particle box, pressure/temperature/volume controls, real-time PV readout | 🟢 | Low | 📋 |
| T02 | Maxwell-Boltzmann Distribution | Particle speed histogram updating live as temperature changes | 🟡 | Low | 📋 |
| T03 | Heat Engine Cycles | Carnot, Otto, Diesel — animated PV diagram, efficiency readout | 🟡 | Low | 📋 |
| T04 | Entropy Visualiser | Microstates, macrostates, irreversibility demonstration, Boltzmann H-theorem | 🔴 | Medium | 📋 |
| T05 | Random Walk & Diffusion | 2D Brownian motion, MSD vs time, diffusion coefficient extraction | 🟡 | Low | 📋 |
| T06 | Ising Model | 2D ferromagnet, Metropolis Monte Carlo, phase transition, magnetisation vs temperature | 🔴 | Medium | 📋 |
| T07 | Phase Transitions | Van der Waals gas, Maxwell construction, spinodal decomposition, coexistence curve | 🟣 | High | 📋 |
| T08 | Heat Equation Solver | 1D and 2D thermal conduction, selectable boundary conditions, steady-state finder | 🔴 | Medium | 📋 |

---

## ⚛️ Quantum Mechanics

| ID | Name | Description | Level | Effort | Status |
|----|------|-------------|-------|--------|--------|
| Q01 | Particle in a Box | Energy levels, wavefunctions, probability density, vary well width | 🟡 | Low | 📋 |
| Q02 | Quantum Tunnelling | Rectangular barrier, vary width and height, transmission coefficient plot | 🟡 | Low | 📋 |
| Q03 | Quantum Harmonic Oscillator | Ladder operators, Hermite polynomial eigenstates, coherent states | 🔴 | Medium | 📋 |
| Q04 | Hydrogen Atom Orbitals | 3D probability density clouds, all (n, l, m) combinations, cross-section view | 🔴 | Medium | 📋 |
| Q05 | Bloch Sphere | Qubit state visualisation, single-qubit gate application, measurement collapse | 🔴 | Medium | 📋 |
| Q06 | Double Slit (Quantum) | Photon-by-photon buildup, which-path information, decoherence toggle | 🔴 | Medium | 📋 |
| Q07 | Wavepacket Dynamics | Gaussian packet propagation, spreading, scattering off barriers and steps | 🔴 | Medium | 📋 |
| Q08 | Spin & Stern-Gerlach | Spin-½ system, measurement along arbitrary axis, sequential measurements | 🔴 | Medium | 📋 |
| Q09 | Quantum Harmonic Lattice | 1D chain, phonon dispersion relation, density of states, Debye model | 🟣 | High | 📋 |
| Q10 | Schrödinger Equation Solver | Arbitrary potential well input, numerical eigenvalue solver, time evolution | 🟣 | High | 📋 |

---

## 🌌 Astrophysics & Gravity

| ID | Name | Description | Level | Effort | Status |
|----|------|-------------|-------|--------|--------|
| A01 | RotoCurve | Galactic rotation curve fitter — MOND, CODA, and CDM models against SPARC data | 🟣 | Low | ✅ |
| A02 | Orbital Mechanics | Kepler orbits, Hohmann transfers, Lagrange points, vary orbital elements | 🟡 | Medium | 📋 |
| A03 | Gravitational Lensing | Point mass lens, Einstein ring, deflection angle vs impact parameter | 🔴 | Medium | 📋 |
| A04 | Stellar Evolution | HR diagram, main sequence lifetime, mass-luminosity relation, stellar tracks | 🟡 | Low | 📋 |
| A05 | Binary Star System | Tidal locking, Roche lobe overflow, mass transfer, light curve | 🔴 | Medium | 📋 |
| A06 | Schwarzschild Geodesics | Timelike and null geodesics near a black hole, ISCO, photon sphere, effective potential | 🟣 | High | 📋 |
| A07 | Gravitational Wave Strain | Binary inspiral, chirp mass, post-Newtonian waveform, LIGO-style strain plot | 🟣 | High | 📋 |
| A08 | Cosmological Expansion | Hubble flow, redshift vs distance, Friedmann equations, vary Ω parameters | 🔴 | Medium | 📋 |

---

## 📐 Pure Mathematics

| ID | Name | Description | Level | Effort | Status |
|----|------|-------------|-------|--------|--------|
| P01 | Function Explorer | Plot any f(x), live derivative and integral overlay, root and extrema finder | 🟢 | Low | 📋 |
| P02 | Complex Function Visualiser | Domain colouring, Riemann surface projection, poles and zeros, Möbius transforms | 🔴 | Medium | 📋 |
| P03 | FractalLab | Mandelbrot and Julia sets, custom iteration rules, deep zoom, colouring schemes | 🟡 | Low | 📋 |
| P04 | Tiling Lab | Penrose P2/P3, Ammann-Beenker, custom aperiodic tilings, local isomorphism explorer | 🔴 | Medium | 📋 |
| P05 | Group Theory Visualiser | Cayley tables, subgroup lattice, cosets, homomorphisms, common finite groups | 🔴 | Medium | 📋 |
| P06 | Knot Theory | Knot diagrams, Reidemeister moves, Alexander and Jones polynomial invariants | 🟣 | High | 📋 |
| P07 | Topology Surfaces | Möbius strip, Klein bottle, torus, genus and Euler characteristic | 🔴 | Medium | 📋 |
| P08 | Number Theory Explorer | Prime sieves, modular arithmetic, Collatz conjecture, Goldbach visualisation | 🟡 | Low | 📋 |
| P09 | Projective Geometry | Cross-ratio, conics, duality, homogeneous coordinates, perspectivity | 🔴 | Medium | 📋 |
| P10 | Cellular Automata | Conway's Game of Life, Rule 110, custom 1D and 2D rule explorer | 🟡 | Low | 📋 |

---

## 📊 Applied Mathematics

| ID | Name | Description | Level | Effort | Status |
|----|------|-------------|-------|--------|--------|
| AP01 | ODE Phase Portrait | Nullclines, trajectory field, fixed points, stability classification | 🟡 | Low | 📋 |
| AP02 | Bifurcation Diagram | Logistic map, period-doubling route to chaos, parameter sweep | 🟡 | Low | 📋 |
| AP03 | Lorenz Attractor | 3D strange attractor, sensitive dependence, vary σ/ρ/β parameters | 🔴 | Low | 📋 |
| AP04 | Fourier Series Builder | Approximate square, sawtooth, triangle and custom waveforms, Gibbs phenomenon | 🟡 | Low | 📋 |
| AP05 | Linear Algebra Visualiser | 2D and 3D matrix transformations, eigenvectors, SVD, PCA on point clouds | 🟡 | Low | 📋 |
| AP06 | Numerical Methods | Euler, midpoint, RK4 — compare accuracy and stability on selectable ODEs | 🔴 | Medium | 📋 |
| AP07 | PDE Solver | Heat equation, wave equation, Laplace equation — 1D and 2D, various BCs | 🔴 | High | 📋 |
| AP08 | Monte Carlo Visualiser | π estimation, numerical integration, importance sampling, convergence rate | 🟡 | Low | 📋 |
| AP09 | Graph Theory | Dijkstra, Prim, graph colouring, planarity, adjacency matrix view | 🟡 | Low | 📋 |
| AP10 | Probability Distributions | PDF and CDF for common distributions, sampling, Central Limit Theorem demo | 🟢 | Low | 📋 |

---

## 🔬 Special Topics

| ID | Name | Description | Level | Effort | Status |
|----|------|-------------|-------|--------|--------|
| S01 | Fluid Dynamics (2D) | Streamlines, vortex shedding, simple Navier-Stokes CFD, Reynolds number | 🟣 | High | 📋 |
| S02 | Elasticity & Stress | FEM beam bending, stress and strain tensors, failure criteria | 🟣 | High | 📋 |
| S03 | Neural Network Visualiser | Live training, decision boundary evolution, loss landscape | 🔴 | Medium | 📋 |
| S04 | Crystal Lattice | Bravais lattices, reciprocal space, Brillouin zones, structure factor | 🟣 | Medium | 📋 |
| S05 | Particle Detector Sim | Track reconstruction, shower development, detector geometry | 🟣 | High | 📋 |
| S06 | Renormalisation Group | Block spin transformation, fixed points, universality classes | 🟣 | High | 📋 |

---

## Phase Roadmap

### Phase 1 — Launch Set (v0.1)
Ten simulations chosen for low build effort, broad visual appeal, and coverage across disciplines. Target: shippable in 4–6 weeks.

**Simulations:**

| ID | Name | Rationale |
|----|------|-----------|
| M04 | Simple Harmonic Motion | Universal A-level topic, highly visual |
| M10 | Chaotic Double Pendulum | Instantly compelling, low complexity to build |
| W01 | Wave Superposition | Core curriculum, beats are visually satisfying |
| W02 | Fourier Synthesiser | Strong viral potential, immediately engaging |
| T01 | Ideal Gas Simulation | GCSE/A-level staple, particle animation is intuitive |
| T02 | Maxwell-Boltzmann Distribution | Pairs naturally with T01 |
| AP01 | ODE Phase Portrait | Huge undergraduate demand, low effort |
| AP02 | Bifurcation Diagram | Chaos angle is highly shareable |
| AP03 | Lorenz Attractor | Visually striking, trivial to implement |
| P03 | FractalLab | Broadest possible audience, zoom is compelling |

**Platform features (v0.1):**

| Feature | Description | Effort |
|---------|-------------|--------|
| Launcher dashboard | Category sidebar, card grid, search/filter, level badges | Medium |
| CSV + PNG export | One-click export on every simulation via `SimulationBase.export()` | Low |
| Live equation display (Level 1) | LaTeX-rendered equation panel, parameter values update as sliders move | Medium |
| Editable equations (Level 2) | User can modify the equation itself; simulation re-integrates live (AP01, AP03, W01, W02) | Medium |
| JSON presets (save/load) | `.lumina` preset files — teachers share parameter configs with instructional text | Low |
| Dark / light / high-contrast themes | Qt stylesheet theming, toggle in settings | Low |
| Colourblind-safe palette toggle | Switchable colour palette in config, covers all plots | Low |
| Session state save/load | Save and resume simulation state to file | Medium |

### Phase 2 — Core Expansion (v0.2–v0.3)
Adds quantum, astrophysics, and electromagnetism pillars. Introduces RotoCurve as the first research-grade module.

**Simulations:** Q01, Q02, E01, E03, A01 (RotoCurve), A02, M01, W04, AP04, AP05

**Platform features (v0.2–v0.3):**

| Feature | Description | Effort |
|---------|-------------|--------|
| Side-by-side model comparison | Split-pane or overlay mode — run two models against same ICs | Medium |
| Session replay | Record parameter exploration as timestamped sequence, playback for teaching | Medium |
| Guided mode | Preset-driven walkthrough that locks controls and shows step-by-step prompts | Low |

### Phase 3 — University Tier (v0.4–v0.5)
Medium-effort modules targeting first and second year undergraduates.

**Simulations:** Q04, Q07, E07, T06, A03, A08, P02, P04, AP06, AP07

**Platform features (v0.4–v0.5):**

| Feature | Description | Effort |
|---------|-------------|--------|
| Keyboard navigation | Full keyboard-driven control of all simulations (WCAG 2.1) | Medium |
| Favourites and recents | Stored in QSettings, shown on launcher dashboard | Low |

### Phase 4 — Research & Special Topics (v1.0)
High-effort modules and Special Topics. Monetised as premium tier.

**Simulations:** All remaining High effort and 🟣 modules.

**Platform features (v1.0):**

| Feature | Description | Effort |
|---------|-------------|--------|
| LMS integration | Export results to Moodle / Canvas / Google Classroom | High |
| Plugin API | Third-party module development support | High |

---

## Summary

| Category | Total Sims | Low Effort | Medium Effort | High Effort |
|----------|-----------|------------|---------------|-------------|
| Classical Mechanics | 10 | 6 | 3 | 1 |
| Waves & Optics | 10 | 5 | 5 | 0 |
| Electromagnetism | 10 | 4 | 4 | 2 |
| Thermodynamics | 8 | 4 | 3 | 1 |
| Quantum Mechanics | 10 | 2 | 6 | 2 |
| Astrophysics & Gravity | 8 | 2 | 4 | 2 |
| Pure Mathematics | 10 | 3 | 6 | 1 |
| Applied Mathematics | 10 | 7 | 2 | 1 |
| Special Topics | 6 | 0 | 2 | 4 |
| **Total** | **82** | **33** | **35** | **14** |

---

*Last updated: April 2026*
*Maintainer: Darian-Frey*