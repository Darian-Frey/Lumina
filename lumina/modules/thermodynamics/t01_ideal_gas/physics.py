"""T01 Ideal Gas Simulation — physics module. No Qt imports."""
from __future__ import annotations
import numpy as np
from numpy.typing import NDArray

K_B: float = 1.380649e-23  # Boltzmann constant (J/K)
DEFAULT_N: int = 200
DEFAULT_BOX: float = 10.0
DEFAULT_MASS: float = 4.65e-26  # ~N2 molecule
DEFAULT_RADIUS: float = 0.15

def init_particles(
    n: int = DEFAULT_N, box_w: float = DEFAULT_BOX, box_h: float = DEFAULT_BOX,
    temperature: float = 300.0, mass: float = DEFAULT_MASS, seed: int = 42,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Initialise particles with random positions and MB-distributed velocities.
    Returns (positions [n,2], velocities [n,2])."""
    rng = np.random.default_rng(seed)
    margin = DEFAULT_RADIUS * 2
    pos = rng.uniform(margin, box_w - margin, (n, 2))
    # 2D Maxwell-Boltzmann: each component ~ N(0, sqrt(kT/m))
    sigma = np.sqrt(K_B * temperature / mass)
    vel = rng.normal(0, sigma, (n, 2))
    # Zero centre-of-mass velocity
    vel -= vel.mean(axis=0)
    return pos, vel

def step_particles(
    pos: NDArray[np.float64], vel: NDArray[np.float64],
    mass: float, box_w: float, box_h: float, radius: float, dt: float,
) -> tuple[NDArray[np.float64], NDArray[np.float64], float]:
    """Advance particles by dt. Returns (new_pos, new_vel, wall_impulse)."""
    pos = pos + vel * dt
    wall_impulse = 0.0

    # Wall collisions
    for i in range(len(pos)):
        for axis in range(2):
            box_size = box_w if axis == 0 else box_h
            if pos[i, axis] < radius:
                pos[i, axis] = radius
                wall_impulse += 2 * mass * abs(vel[i, axis])
                vel[i, axis] = abs(vel[i, axis])
            elif pos[i, axis] > box_size - radius:
                pos[i, axis] = box_size - radius
                wall_impulse += 2 * mass * abs(vel[i, axis])
                vel[i, axis] = -abs(vel[i, axis])

    return pos, vel, wall_impulse

def compute_temperature(vel: NDArray[np.float64], mass: float) -> float:
    """Compute temperature from kinetic energy: T = m * <v^2> / (2 * k_B) for 2D."""
    v_sq = np.sum(vel ** 2, axis=1).mean()
    return mass * v_sq / (2 * K_B)

def compute_pressure(wall_impulse: float, perimeter: float, dt: float) -> float:
    """Pressure = total wall impulse / (perimeter * dt)."""
    if dt > 0 and perimeter > 0:
        return wall_impulse / (perimeter * dt)
    return 0.0

def compute_speeds(vel: NDArray[np.float64]) -> NDArray[np.float64]:
    """Compute speed magnitudes."""
    return np.sqrt(np.sum(vel ** 2, axis=1))
