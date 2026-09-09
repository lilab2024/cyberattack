"""Trajectory-intersection collision detection."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from .config import Scenario, SimulationConfig
from .simulation import SimulationResult


COLLISION_METHOD = "trajectory_unwrapped_intersection"


@dataclass(frozen=True)
class CollisionEvent:
    occurred: bool
    step: float = np.nan
    time_seconds: float = np.nan
    interpolated_time_seconds: float = np.nan
    phase: str = "none"
    vehicle_index: float = np.nan
    front_vehicle_index: float = np.nan
    trajectory_gap_m: float = np.nan
    detection_method: str = COLLISION_METHOD

    def to_record(self) -> dict[str, object]:
        raw = asdict(self)
        return {
            "collision_occurred": raw["occurred"],
            "collision_step": raw["step"],
            "collision_time_seconds": raw["time_seconds"],
            "collision_time_interpolated_seconds": raw[
                "interpolated_time_seconds"
            ],
            "collision_phase": raw["phase"],
            "collision_vehicle_index": raw["vehicle_index"],
            "collision_front_vehicle_index": raw["front_vehicle_index"],
            "collision_spacing_m": raw["trajectory_gap_m"],
            "collision_detection_method": raw["detection_method"],
        }


def calculate_unwrapped_positions(
    speed: np.ndarray,
    initial_spacing_m: float,
    config: SimulationConfig,
) -> np.ndarray:
    """Integrate velocity to reproduce the unwrapped trajectory plot."""

    cumulative_distance = np.cumsum(speed * config.delta_t, axis=0)
    initial_positions = (
        config.road_length_m
        - initial_spacing_m * np.arange(config.vehicle_count, dtype=float)
    )
    return cumulative_distance + initial_positions[None, :]


def phase_for_step(step: int, config: SimulationConfig) -> str:
    collision_time = step * config.delta_t
    for phase, (start, end) in config.phase_windows_seconds.items():
        if start <= collision_time < end:
            return phase
    first_phase_start = min(start for start, _ in config.phase_windows_seconds.values())
    if collision_time < first_phase_start:
        return "before_pre"
    return "after_analysis_window"


def detect_first_collision(
    result: SimulationResult,
    scenario: Scenario,
    config: SimulationConfig,
) -> CollisionEvent:
    """Find the earliest attacked-vehicle/front-vehicle trajectory intersection."""

    positions = calculate_unwrapped_positions(
        result.speed,
        result.initial_spacing_m,
        config,
    )
    earliest: tuple[int, float, int, int, float] | None = None

    for vehicle in scenario.attack_indices:
        front = (vehicle - 1) % config.vehicle_count
        trajectory_gap = positions[:, front] - positions[:, vehicle]
        intersections = np.flatnonzero(trajectory_gap <= 0.0)
        if intersections.size == 0:
            continue

        step = int(intersections[0])
        interpolated_time = step * config.delta_t
        if step > 0 and trajectory_gap[step - 1] > 0.0:
            previous_gap = trajectory_gap[step - 1]
            current_gap = trajectory_gap[step]
            denominator = previous_gap - current_gap
            if denominator != 0.0:
                fraction = previous_gap / denominator
                interpolated_time = (step - 1 + fraction) * config.delta_t
        candidate = (step, interpolated_time, vehicle, front, float(trajectory_gap[step]))
        if earliest is None or candidate[0] < earliest[0]:
            earliest = candidate

    if earliest is None:
        return CollisionEvent(occurred=False)

    step, interpolated_time, vehicle, front, gap = earliest
    return CollisionEvent(
        occurred=True,
        step=float(step),
        time_seconds=step * config.delta_t,
        interpolated_time_seconds=float(interpolated_time),
        phase=phase_for_step(step, config),
        vehicle_index=float(vehicle),
        front_vehicle_index=float(front),
        trajectory_gap_m=gap,
    )
