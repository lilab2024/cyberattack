"""Attack parameter grids and attacked-vehicle update strategies."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any, Mapping, Protocol

import numpy as np

from .config import ProjectConfig, SimulationConfig
from .models import clip_acceleration, idm_acceleration


SUPPORTED_ATTACKS = ("DPDA", "PA", "AVA", "BA", "FA")
PARAMETER_COLUMNS = (
    "delay_seconds",
    "ghost_offset",
    "k_value",
    "phi_label",
    "phi_radians",
    "blind_distance_m",
)


def _format_number(value: float) -> str:
    return f"{value:g}".replace(".", "p")


@dataclass(frozen=True)
class AttackCase:
    """One point in an attack parameter sweep."""

    attack_type: str
    parameters: Mapping[str, Any]

    @property
    def setting_id(self) -> str:
        attack = self.attack_type
        if attack == "DPDA":
            return f"delay_{int(self.parameters['delay_seconds']):02d}s"
        if attack == "PA":
            return f"ghost_offset_{int(self.parameters['ghost_offset'])}"
        if attack == "AVA":
            return (
                f"k_{_format_number(float(self.parameters['k_value']))}"
                f"_phi_{self.parameters['phi_label']}"
            )
        if attack == "BA":
            return f"blind_{int(self.parameters['blind_distance_m']):02d}m"
        return "fa"

    def case_directory_name(self, scenario_name: str) -> str:
        return f"scenario_{scenario_name}_{self.setting_id}"

    def tabular_parameters(self) -> dict[str, Any]:
        values = {column: np.nan for column in PARAMETER_COLUMNS}
        values.update(self.parameters)
        return values


def build_attack_cases(
    config: ProjectConfig,
    attack_type: str,
    overrides: Mapping[str, list[Any]] | None = None,
) -> list[AttackCase]:
    """Expand one attack's configured parameter grid."""

    attack_type = attack_type.upper()
    if attack_type not in SUPPORTED_ATTACKS:
        raise ValueError(f"unsupported attack type: {attack_type}")
    sweep = dict(config.attack_sweeps[attack_type])
    if overrides:
        sweep.update({key: value for key, value in overrides.items() if value is not None})

    if attack_type == "DPDA":
        return [
            AttackCase(attack_type, {"delay_seconds": float(value)})
            for value in sweep["delay_seconds"]
        ]
    if attack_type == "PA":
        return [
            AttackCase(attack_type, {"ghost_offset": int(value)})
            for value in sweep["ghost_offset"]
        ]
    if attack_type == "AVA":
        phi_values = sweep["phi"]
        return [
            AttackCase(
                attack_type,
                {
                    "k_value": float(k_value),
                    "phi_label": str(phi["label"]),
                    "phi_radians": float(phi["radians"]),
                },
            )
            for k_value, phi in product(sweep["k_value"], phi_values)
        ]
    if attack_type == "BA":
        return [
            AttackCase(attack_type, {"blind_distance_m": float(value)})
            for value in sweep["blind_distance_m"]
        ]
    return [AttackCase("FA", {})]


@dataclass
class StepContext:
    """Read/write state exposed to one attack strategy."""

    step: int
    vehicle: int
    speed: np.ndarray
    spacing: np.ndarray
    acceleration: np.ndarray
    idm_parameters: np.ndarray
    noise: float
    config: SimulationConfig

    def controlled_acceleration(self, state_step: int) -> float:
        value = idm_acceleration(
            self.idm_parameters[self.vehicle],
            self.speed[state_step, self.vehicle],
            self.speed[state_step, self.config.vehicle_count - 1],
            self.spacing[state_step, self.vehicle],
        ) + self.noise
        return clip_acceleration(
            value,
            self.config.acceleration_min_mps2,
            self.config.acceleration_max_mps2,
        )


class AttackStrategy(Protocol):
    """Interface implemented by all five attack mechanisms."""

    nominal_spacing_floor_m: float

    def update(self, context: StepContext) -> tuple[float, float, float]:
        """Return acceleration, speed and spacing for the attacked vehicle."""


@dataclass(frozen=True)
class DelayedDataAttack:
    delay_seconds: float
    nominal_spacing_floor_m: float = 0.5

    def update(self, context: StepContext) -> tuple[float, float, float]:
        cfg = context.config
        delayed_second = (context.step - 1) // cfg.sample_rate_hz - self.delay_seconds
        delayed_step = max(0, int(delayed_second * cfg.sample_rate_hz))
        accel = context.controlled_acceleration(delayed_step)
        speed = max(
            context.speed[delayed_step, context.vehicle]
            + context.acceleration[delayed_step, context.vehicle] * cfg.delta_t,
            cfg.minimum_speed_mps,
        )
        front = (context.vehicle - 1) % cfg.vehicle_count
        spacing = max(
            context.spacing[delayed_step, context.vehicle]
            + (
                context.speed[delayed_step, front]
                - context.speed[delayed_step, context.vehicle]
            )
            * cfg.delta_t,
            0.5,
        )
        return accel, speed, spacing


@dataclass(frozen=True)
class PositionAttack:
    ghost_offset: int
    nominal_spacing_floor_m: float = 0.5

    def update(self, context: StepContext) -> tuple[float, float, float]:
        cfg = context.config
        previous = context.step - 1
        source = (context.vehicle - self.ghost_offset) % cfg.vehicle_count
        source_front = (source - 1) % cfg.vehicle_count
        accel = context.controlled_acceleration(previous)
        speed = max(
            context.speed[previous, source]
            + context.acceleration[previous, source] * cfg.delta_t,
            cfg.minimum_speed_mps,
        )
        spacing = max(
            context.spacing[previous, source]
            + (
                context.speed[previous, source_front]
                - context.speed[previous, source]
            )
            * cfg.delta_t,
            0.0,
        )
        return accel, speed, spacing


@dataclass(frozen=True)
class AngularVelocityAttack:
    k_value: float
    phi_radians: float
    nominal_spacing_floor_m: float = 0.5

    def update(self, context: StepContext) -> tuple[float, float, float]:
        cfg = context.config
        previous = context.step - 1
        accel = context.controlled_acceleration(previous)
        theta = (
            self.k_value * (context.step - cfg.attack_start_step) * cfg.delta_t
            + self.phi_radians
        )
        attacked_speed = (
            context.speed[previous, context.vehicle] + accel * cfg.delta_t
        ) * (1.0 + 0.0005 * np.sin(theta))
        speed = max(attacked_speed, cfg.minimum_speed_mps)
        front = (context.vehicle - 1) % cfg.vehicle_count
        spacing = max(
            context.spacing[previous, context.vehicle]
            + (
                context.speed[previous, front]
                - context.speed[previous, context.vehicle]
            )
            * cfg.delta_t,
            0.0,
        )
        return accel, speed, spacing


@dataclass(frozen=True)
class BlindingAttack:
    blind_distance_m: float
    nominal_spacing_floor_m: float = 0.5

    def update(self, context: StepContext) -> tuple[float, float, float]:
        cfg = context.config
        previous = context.step - 1
        accel = context.controlled_acceleration(previous)
        speed = max(
            context.speed[previous, context.vehicle] + accel * cfg.delta_t,
            cfg.minimum_speed_mps,
        )
        front = (context.vehicle - 1) % cfg.vehicle_count
        spacing = min(
            max(
                context.spacing[previous, context.vehicle]
                + context.spacing[previous, front],
                0.0,
            ),
            self.blind_distance_m,
        )
        return accel, speed, spacing


@dataclass(frozen=True)
class FixedSpeedAttack:
    nominal_spacing_floor_m: float = 0.0

    def update(self, context: StepContext) -> tuple[float, float, float]:
        cfg = context.config
        previous = context.step - 1
        front = (context.vehicle - 1) % cfg.vehicle_count
        speed = max(
            context.speed[cfg.attack_start_step - 1, context.vehicle],
            cfg.minimum_speed_mps,
        )
        spacing = max(
            context.spacing[previous, context.vehicle]
            + (
                context.speed[previous, front]
                - context.speed[previous, context.vehicle]
            )
            * cfg.delta_t,
            0.0,
        )
        return 0.0, speed, spacing


def create_strategy(case: AttackCase) -> AttackStrategy:
    """Create the update strategy for an expanded attack case."""

    if case.attack_type == "DPDA":
        return DelayedDataAttack(float(case.parameters["delay_seconds"]))
    if case.attack_type == "PA":
        return PositionAttack(int(case.parameters["ghost_offset"]))
    if case.attack_type == "AVA":
        return AngularVelocityAttack(
            float(case.parameters["k_value"]),
            float(case.parameters["phi_radians"]),
        )
    if case.attack_type == "BA":
        return BlindingAttack(float(case.parameters["blind_distance_m"]))
    if case.attack_type == "FA":
        return FixedSpeedAttack()
    raise ValueError(f"unsupported attack type: {case.attack_type}")
