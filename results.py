"""Stable CSV, JSON and directory output conventions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd

from .config import Scenario, SimulationConfig
from .metrics import METRIC_COLUMNS
from .simulation import SimulationResult


def save_matrix(matrix: np.ndarray, path: Path) -> None:
    pd.DataFrame(matrix).to_csv(
        path,
        index=False,
        header=False,
        float_format="%.6f",
    )


def _write_csv(frame: pd.DataFrame, path: Path) -> None:
    frame.to_csv(path, index=False, float_format="%.3f")


def write_case_outputs(
    case_directory: Path,
    mean_result: SimulationResult,
    run_metrics: pd.DataFrame,
    robust_metrics: pd.DataFrame,
    collision_events: pd.DataFrame,
    collision_summary: pd.DataFrame,
    scenario: Scenario,
    vehicle_type: str,
    attack_type: str,
    setting_id: str,
    parameters: Mapping[str, Any],
    config: SimulationConfig,
) -> None:
    """Write one scenario/attack-setting result bundle."""

    phase_directory = case_directory / "metrics_by_phase"
    robust_phase_directory = case_directory / "robust_metrics_by_phase"
    phase_directory.mkdir(parents=True, exist_ok=True)
    robust_phase_directory.mkdir(parents=True, exist_ok=True)

    save_matrix(mean_result.spacing, case_directory / "average_spacing.csv")
    save_matrix(mean_result.speed, case_directory / "average_speed.csv")
    save_matrix(mean_result.acceleration, case_directory / "average_acceleration.csv")

    _write_csv(run_metrics.round(3), case_directory / "per_run_collision_adjusted_phase_metrics.csv")
    _write_csv(
        robust_metrics,
        case_directory / "phase_metrics_collision_adjusted_mean_std.csv",
    )
    # Keep the historic name while making its contents the authoritative robust table.
    _write_csv(robust_metrics, case_directory / "phase_metrics.csv")
    for phase, phase_frame in robust_metrics.groupby("phase", sort=False):
        _write_csv(phase_frame, phase_directory / f"{phase}.csv")
        _write_csv(phase_frame, robust_phase_directory / f"{phase}.csv")

    _write_csv(collision_events.round(3), case_directory / "collision_events_by_run.csv")
    _write_csv(collision_summary, case_directory / "collision_summary.csv")

    payload = {
        "scenario": {
            "name": scenario.name,
            "description": scenario.description,
            "acc_indices": list(scenario.acc_indices),
            "attack_indices": list(scenario.attack_indices),
        },
        "vehicle_type": vehicle_type,
        "attack_type": attack_type,
        "setting_id": setting_id,
        "attack_parameters": dict(parameters),
        "runs_per_case": config.runs_per_case,
        "random_seeds": [
            config.random_seed_start + index for index in range(config.runs_per_case)
        ],
        "collision_detection_method": "trajectory_unwrapped_intersection",
        "collision_vehicle_group": "attacked ACC vehicles only",
        "metrics_vehicle_group": "attacked ACC vehicles only",
        "collision_step_is_excluded_from_metrics": True,
        "attack_window_seconds": [
            config.attack_start_seconds,
            config.attack_end_seconds,
        ],
        "phase_windows_seconds": {
            phase: list(window)
            for phase, window in config.phase_windows_seconds.items()
        },
    }
    with (case_directory / "config.json").open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def write_batch_outputs(
    output_directory: Path,
    robust_metrics: pd.DataFrame,
    run_metrics: pd.DataFrame,
    collision_events: pd.DataFrame,
    collision_summary: pd.DataFrame,
) -> None:
    """Write attack/vehicle-level summaries using the established filenames."""

    output_directory.mkdir(parents=True, exist_ok=True)
    _write_csv(
        robust_metrics,
        output_directory / "summary_collision_adjusted_phase_metrics_mean_std.csv",
    )
    _write_csv(robust_metrics, output_directory / "summary_phase_metrics.csv")
    _write_csv(
        run_metrics.round(3),
        output_directory / "summary_per_run_collision_adjusted_phase_metrics.csv",
    )
    _write_csv(
        collision_events.round(3),
        output_directory / "summary_collision_events_by_run.csv",
    )
    _write_csv(collision_summary, output_directory / "summary_collision_events.csv")

    pivot = robust_metrics.pivot_table(
        index=["scenario", "description", "setting_id"],
        columns="phase",
        values=[f"{metric}_mean_std" for metric in METRIC_COLUMNS],
        aggfunc="first",
        dropna=False,
    )
    pivot.to_csv(
        output_directory / "summary_collision_adjusted_phase_metrics_pivot.csv"
    )
    pivot.to_csv(output_directory / "summary_phase_metrics_pivot.csv")


def write_combined_outputs(
    output_directory: Path,
    robust_metrics: pd.DataFrame,
    collision_summary: pd.DataFrame,
) -> None:
    """Write cross-attack tables when multiple batches are selected."""

    if robust_metrics.empty:
        return
    _write_csv(
        robust_metrics,
        output_directory / "all_attacks_collision_adjusted_phase_metrics_mean_std.csv",
    )
    _write_csv(
        collision_summary,
        output_directory / "all_attacks_collision_summary.csv",
    )
    comparison_values = [
        "average_speed_mps_mean_std",
        "spacing_fluctuation_std_m_mean_std",
        "speed_fluctuation_std_mps_mean_std",
        "mean_thw_seconds_mean_std",
    ]
    pivot = robust_metrics.pivot_table(
        index=[
            "attack_type",
            "vehicle_type",
            "scenario",
            "description",
            "setting_id",
        ],
        columns="phase",
        values=comparison_values,
        aggfunc="first",
        dropna=False,
    )
    pivot.to_csv(output_directory / "all_attacks_phase_metrics_pivot.csv")
