"""Collision-adjusted phase metrics and robust summaries."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from .attacks import PARAMETER_COLUMNS
from .collision import CollisionEvent
from .config import Scenario, SimulationConfig
from .simulation import SimulationResult


METRIC_COLUMNS = (
    "average_speed_mps",
    "spacing_fluctuation_std_m",
    "speed_fluctuation_std_mps",
    "speed_range_mean_mps",
    "mean_ttc_seconds",
    "mean_thw_seconds",
)

IDENTITY_COLUMNS = (
    "attack_type",
    "vehicle_type",
    "scenario",
    "description",
    "setting_id",
)


def mean_std_text(mean_value: float, std_value: float) -> str:
    if pd.isna(mean_value):
        return ""
    if pd.isna(std_value):
        std_value = 0.0
    return f"{mean_value:.3f} ± {std_value:.3f}"


def finite_mean(values: np.ndarray) -> float:
    finite = values[np.isfinite(values)]
    return float(np.mean(finite)) if finite.size else np.nan


def phase_slice_with_collision(
    start_step: int,
    end_step: int,
    collision_step: float,
) -> tuple[int, int, str]:
    """End a phase one step before collision and suppress all later phases."""

    if pd.isna(collision_step):
        return start_step, end_step, "normal"
    collision_step_int = int(collision_step)
    if collision_step_int < start_step:
        return start_step, start_step, "stopped_before_phase"
    if start_step <= collision_step_int < end_step:
        return start_step, collision_step_int, "truncated_by_collision"
    return start_step, end_step, "normal"


def build_identity(
    attack_type: str,
    vehicle_type: str,
    scenario: Scenario,
    setting_id: str,
    parameters: Mapping[str, Any],
) -> dict[str, Any]:
    identity: dict[str, Any] = {
        "attack_type": attack_type,
        "vehicle_type": vehicle_type,
        "scenario": scenario.name,
        "description": scenario.description,
        "setting_id": setting_id,
        "acc_indices": str(list(scenario.acc_indices)),
        "attack_indices": str(list(scenario.attack_indices)),
        "analysis_vehicle_group": "attacked_ACC",
    }
    identity.update({column: np.nan for column in PARAMETER_COLUMNS})
    identity.update(parameters)
    return identity


def _empty_metrics() -> dict[str, float]:
    return {metric: np.nan for metric in METRIC_COLUMNS}


def calculate_phase_metrics_for_run(
    result: SimulationResult,
    collision: CollisionEvent,
    scenario: Scenario,
    config: SimulationConfig,
    identity: Mapping[str, Any],
    run_number: int,
) -> pd.DataFrame:
    """Calculate all metrics for attacked ACC vehicles in each phase."""

    rows: list[dict[str, Any]] = []
    collision_record = collision.to_record()
    attack_indices = list(scenario.attack_indices)
    front_indices = [(index - 1) % config.vehicle_count for index in attack_indices]

    for phase, (start_seconds, end_seconds) in config.phase_windows_seconds.items():
        start_step = int(round(start_seconds * config.sample_rate_hz))
        end_step = int(round(end_seconds * config.sample_rate_hz))
        effective_start, effective_end, status = phase_slice_with_collision(
            start_step,
            end_step,
            collision.step,
        )
        row: dict[str, Any] = {
            **identity,
            "run": run_number,
            "phase": phase,
            "time_window_seconds": f"{start_seconds:g}-{end_seconds:g}",
            "effective_start_seconds": np.nan,
            "effective_end_seconds": np.nan,
            "valid_steps": max(0, effective_end - effective_start),
            "calculation_status": status,
            **collision_record,
        }

        if effective_end <= effective_start:
            row.update(_empty_metrics())
            rows.append(row)
            continue

        selected_speed = result.speed[effective_start:effective_end, :][:, attack_indices]
        selected_spacing = result.spacing[effective_start:effective_end, :][
            :, attack_indices
        ]
        selected_front_speed = result.speed[effective_start:effective_end, :][
            :, front_indices
        ]
        relative_speed = selected_speed - selected_front_speed
        ttc = np.full_like(relative_speed, np.inf)
        closing = relative_speed > 1e-6
        ttc[closing] = selected_spacing[closing] / relative_speed[closing]
        safe_speed = np.where(selected_speed <= 1e-6, 1e-6, selected_speed)
        thw = selected_spacing / safe_speed
        speed_ranges = np.max(selected_speed, axis=0) - np.min(selected_speed, axis=0)

        row.update(
            {
                "effective_start_seconds": effective_start * config.delta_t,
                "effective_end_seconds": (effective_end - 1) * config.delta_t,
                "average_speed_mps": float(np.mean(selected_speed)),
                "spacing_fluctuation_std_m": float(
                    np.mean(np.std(selected_spacing, axis=0))
                ),
                "speed_fluctuation_std_mps": float(
                    np.mean(np.std(selected_speed, axis=0))
                ),
                "speed_range_mean_mps": float(np.mean(speed_ranges)),
                "mean_ttc_seconds": finite_mean(ttc),
                "mean_thw_seconds": float(np.mean(thw)),
            }
        )
        rows.append(row)

    return pd.DataFrame(rows)


def summarize_run_metrics(run_metrics: pd.DataFrame, runs_per_case: int) -> pd.DataFrame:
    """Aggregate seeded runs as mean ± sample standard deviation."""

    group_columns = [*IDENTITY_COLUMNS, "phase", "time_window_seconds"]
    rows: list[dict[str, Any]] = []
    for keys, group in run_metrics.groupby(group_columns, sort=False, dropna=False):
        row = dict(zip(group_columns, keys))
        for column in (
            *PARAMETER_COLUMNS,
            "acc_indices",
            "attack_indices",
            "analysis_vehicle_group",
        ):
            row[column] = group[column].iloc[0]
        row["runs_per_case"] = runs_per_case
        row["valid_run_count"] = int(group["average_speed_mps"].count())
        row["collision_run_count"] = int(group["collision_occurred"].sum())
        row["collision_rate"] = row["collision_run_count"] / runs_per_case
        row["truncated_run_count"] = int(
            (group["calculation_status"] == "truncated_by_collision").sum()
        )
        row["stopped_before_phase_run_count"] = int(
            (group["calculation_status"] == "stopped_before_phase").sum()
        )
        for metric in METRIC_COLUMNS:
            valid_count = int(group[metric].count())
            mean_value = group[metric].mean(skipna=True)
            std_value = group[metric].std(skipna=True, ddof=1)
            if valid_count == 1:
                std_value = 0.0
            row[f"{metric}_mean"] = (
                round(float(mean_value), 3) if not pd.isna(mean_value) else np.nan
            )
            row[f"{metric}_std"] = (
                round(float(std_value), 3) if not pd.isna(std_value) else np.nan
            )
            row[f"{metric}_mean_std"] = mean_std_text(mean_value, std_value)
        rows.append(row)
    return pd.DataFrame(rows)


def summarize_collision_events(
    collision_events: pd.DataFrame,
    runs_per_case: int,
) -> pd.DataFrame:
    """Summarize earliest intersections across the seeded runs."""

    rows: list[dict[str, Any]] = []
    for keys, group in collision_events.groupby(
        list(IDENTITY_COLUMNS), sort=False, dropna=False
    ):
        row = dict(zip(IDENTITY_COLUMNS, keys))
        for column in (*PARAMETER_COLUMNS, "acc_indices", "attack_indices"):
            row[column] = group[column].iloc[0]
        collided = group[group["collision_occurred"]]
        row["runs_per_case"] = runs_per_case
        row["collision_run_count"] = int(len(collided))
        row["collision_rate"] = round(len(collided) / runs_per_case, 3)
        if collided.empty:
            row.update(
                {
                    "earliest_collision_time_seconds": np.nan,
                    "earliest_collision_time_interpolated_seconds": np.nan,
                    "mean_collision_time_seconds": np.nan,
                    "std_collision_time_seconds": np.nan,
                    "collision_time_mean_std": "",
                    "collision_time_interpolated_mean_std": "",
                    "collision_phases": "none",
                    "collision_vehicle_indices": "none",
                    "collision_front_vehicle_indices": "none",
                }
            )
        else:
            mean_time = collided["collision_time_seconds"].mean()
            std_time = collided["collision_time_seconds"].std(ddof=1)
            mean_interpolated = collided[
                "collision_time_interpolated_seconds"
            ].mean()
            std_interpolated = collided[
                "collision_time_interpolated_seconds"
            ].std(ddof=1)
            if len(collided) == 1:
                std_time = 0.0
                std_interpolated = 0.0
            row.update(
                {
                    "earliest_collision_time_seconds": round(
                        float(collided["collision_time_seconds"].min()), 3
                    ),
                    "earliest_collision_time_interpolated_seconds": round(
                        float(
                            collided[
                                "collision_time_interpolated_seconds"
                            ].min()
                        ),
                        3,
                    ),
                    "mean_collision_time_seconds": round(float(mean_time), 3),
                    "std_collision_time_seconds": round(float(std_time), 3),
                    "collision_time_mean_std": mean_std_text(mean_time, std_time),
                    "collision_time_interpolated_mean_std": mean_std_text(
                        mean_interpolated, std_interpolated
                    ),
                    "collision_phases": "; ".join(
                        f"{phase}:{count}"
                        for phase, count in collided[
                            "collision_phase"
                        ].value_counts().items()
                    ),
                    "collision_vehicle_indices": "; ".join(
                        f"{int(vehicle)}:{count}"
                        for vehicle, count in collided[
                            "collision_vehicle_index"
                        ].value_counts().items()
                    ),
                    "collision_front_vehicle_indices": "; ".join(
                        f"{int(vehicle)}:{count}"
                        for vehicle, count in collided[
                            "collision_front_vehicle_index"
                        ].value_counts().items()
                    ),
                }
            )
        rows.append(row)
    return pd.DataFrame(rows)
