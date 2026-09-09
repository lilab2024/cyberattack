"""Plots generated from the ten-run mean trajectories."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from .collision import calculate_unwrapped_positions
from .config import Scenario, SimulationConfig
from .simulation import SimulationResult


COLORS = {"human": "#E69F00", "acc": "#0072B2", "attacked": "#D55E00"}


def _legend() -> list[Line2D]:
    return [
        Line2D([0], [0], color=COLORS["human"], lw=2.0, label="Human-driven"),
        Line2D([0], [0], color=COLORS["acc"], lw=2.0, label="ACC"),
        Line2D([0], [0], color=COLORS["attacked"], lw=2.4, label="Attacked ACC"),
    ]


def _style_axis(axis: plt.Axes, config: SimulationConfig, ylabel: str) -> None:
    axis.set_xlabel("Time (s)", fontsize=16)
    axis.set_ylabel(ylabel, fontsize=16)
    axis.tick_params(axis="both", labelsize=13)
    axis.grid(True, color="#D9D9D9", linewidth=0.7)
    axis.axvspan(
        config.attack_start_seconds,
        config.attack_end_seconds,
        color="#808080",
        alpha=0.16,
    )
    axis.legend(handles=_legend(), fontsize=11, loc="best", frameon=False)


def _plot_vehicle_groups(
    axis: plt.Axes,
    time: np.ndarray,
    values: np.ndarray,
    scenario: Scenario,
    config: SimulationConfig,
) -> None:
    attacked = set(scenario.attack_indices)
    acc = set(scenario.acc_indices) - attacked
    human = set(range(config.vehicle_count)) - set(scenario.acc_indices)
    for index in sorted(human):
        axis.plot(time, values[:, index], color=COLORS["human"], lw=1.2, alpha=0.75)
    for index in sorted(acc):
        axis.plot(time, values[:, index], color=COLORS["acc"], lw=1.45, alpha=0.85)
    for index in sorted(attacked):
        axis.plot(time, values[:, index], color=COLORS["attacked"], lw=2.0, alpha=0.95)


def plot_case(
    mean_result: SimulationResult,
    scenario: Scenario,
    config: SimulationConfig,
    case_directory: Path,
) -> None:
    """Write trajectory, spacing, speed and acceleration figures."""

    plots_directory = case_directory / "plots"
    plots_directory.mkdir(parents=True, exist_ok=True)
    time = np.arange(config.num_steps) * config.delta_t
    positions = calculate_unwrapped_positions(
        mean_result.speed,
        mean_result.initial_spacing_m,
        config,
    )

    plot_specs = (
        (positions, "Position (m)", "trajectory_unwrapped.png"),
        (positions % config.road_length_m, "Ring position (m)", "trajectory_ring.png"),
        (mean_result.spacing, "Spacing (m)", "spacing.png"),
        (mean_result.speed, "Speed (m/s)", "speed.png"),
    )
    for values, ylabel, filename in plot_specs:
        figure, axis = plt.subplots(figsize=(12, 8))
        _plot_vehicle_groups(axis, time, values, scenario, config)
        _style_axis(axis, config, ylabel)
        figure.tight_layout()
        figure.savefig(plots_directory / filename, dpi=300)
        plt.close(figure)

    human_indices = [
        index for index in range(config.vehicle_count) if index not in scenario.acc_indices
    ]
    non_attacked_acc = [
        index for index in scenario.acc_indices if index not in scenario.attack_indices
    ]
    samples = (
        (human_indices[0] if human_indices else 0, "human"),
        (non_attacked_acc[0] if non_attacked_acc else scenario.acc_indices[0], "acc"),
        (scenario.attack_indices[0], "attacked"),
    )
    figure, axis = plt.subplots(figsize=(12, 8))
    for index, role in samples:
        axis.plot(
            time,
            mean_result.acceleration[:, index],
            color=COLORS[role],
            lw=1.5 if role != "attacked" else 2.0,
        )
    _style_axis(axis, config, "Acceleration (m/s²)")
    figure.tight_layout()
    figure.savefig(plots_directory / "acceleration_sample.png", dpi=300)
    plt.close(figure)
