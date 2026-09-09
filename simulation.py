"""Shared ring-road simulator for all supported attacks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .attacks import AttackStrategy, StepContext
from .config import Scenario, SimulationConfig
from .models import clip_acceleration, idm_acceleration


@dataclass(frozen=True)
class SimulationResult:
    spacing: np.ndarray
    speed: np.ndarray
    acceleration: np.ndarray
    initial_spacing_m: float
    seed: int


def _controlled_acceleration(
    step: int,
    vehicle: int,
    speed: np.ndarray,
    spacing: np.ndarray,
    parameters: np.ndarray,
    noise: float,
    config: SimulationConfig,
) -> float:
    value = idm_acceleration(
        parameters[vehicle],
        speed[step, vehicle],
        speed[step, config.vehicle_count - 1],
        spacing[step, vehicle],
    ) + noise
    return clip_acceleration(
        value,
        config.acceleration_min_mps2,
        config.acceleration_max_mps2,
    )


def _human_acceleration(
    step: int,
    vehicle: int,
    speed: np.ndarray,
    spacing: np.ndarray,
    parameters: np.ndarray,
    config: SimulationConfig,
) -> float:
    front = (vehicle - 1) % config.vehicle_count
    value = idm_acceleration(
        parameters[vehicle],
        speed[step, vehicle],
        speed[step, front],
        spacing[step, vehicle],
    )
    return clip_acceleration(
        value,
        config.acceleration_min_mps2,
        config.acceleration_max_mps2,
    )


def simulate(
    config: SimulationConfig,
    scenario: Scenario,
    human_parameters: Sequence[float],
    acc_parameters: Sequence[float],
    strategy: AttackStrategy,
    seed: int,
) -> SimulationResult:
    """Run one seeded realization of a mixed-traffic attack scenario."""

    config.validate()
    rng = np.random.RandomState(seed)
    spacing = np.zeros((config.num_steps, config.vehicle_count), dtype=float)
    speed = np.zeros_like(spacing)
    acceleration = np.zeros_like(spacing)
    spacing[0, :] = config.initial_spacing_m

    parameters = np.tile(np.asarray(human_parameters, dtype=float), (config.vehicle_count, 1))
    parameters[list(scenario.acc_indices), :] = np.asarray(acc_parameters, dtype=float)
    acc_indices = set(scenario.acc_indices)
    attack_indices = set(scenario.attack_indices)
    gap_floor = strategy.nominal_spacing_floor_m

    for step in range(1, config.num_steps):
        previous = step - 1
        attack_active = config.attack_start_step <= step < config.attack_end_step
        for vehicle in range(config.vehicle_count):
            # Draw for every vehicle to preserve the seeded sequence of the source scripts.
            noise = float(rng.normal(0.0, config.acceleration_noise_std))
            front = (vehicle - 1) % config.vehicle_count

            if vehicle in attack_indices and attack_active:
                context = StepContext(
                    step=step,
                    vehicle=vehicle,
                    speed=speed,
                    spacing=spacing,
                    acceleration=acceleration,
                    idm_parameters=parameters,
                    noise=noise,
                    config=config,
                )
                accel_value, speed_value, spacing_value = strategy.update(context)
            else:
                controlled = vehicle == 0 or vehicle in acc_indices
                if controlled:
                    accel_value = _controlled_acceleration(
                        previous,
                        vehicle,
                        speed,
                        spacing,
                        parameters,
                        noise,
                        config,
                    )
                else:
                    accel_value = _human_acceleration(
                        previous,
                        vehicle,
                        speed,
                        spacing,
                        parameters,
                        config,
                    )
                speed_value = max(
                    speed[previous, vehicle] + accel_value * config.delta_t,
                    config.minimum_speed_mps,
                )
                spacing_value = max(
                    spacing[previous, vehicle]
                    + (speed[previous, front] - speed[previous, vehicle])
                    * config.delta_t,
                    gap_floor,
                )

            acceleration[previous, vehicle] = accel_value
            speed[step, vehicle] = speed_value
            spacing[step, vehicle] = spacing_value

    return SimulationResult(
        spacing=spacing,
        speed=speed,
        acceleration=acceleration,
        initial_spacing_m=config.initial_spacing_m,
        seed=seed,
    )
