# Supplementary Parameter Sensitivity Analysis

This document summarizes the additional parameter-sensitivity experiments conducted for the cyberattack models used in the study. The analyses examine whether the selected attack parameters produce representative outcomes under different ACC behavior parameterizations and spatial attack configurations.

The selected values should be interpreted as **scenario-specific experimental settings**, not as universal safety limits, collision thresholds, or worst-case attack parameters.

## Contents

- [1. Experimental protocol](#1-experimental-protocol)
- [2. Parameter-selection summary](#2-parameter-selection-summary)
- [3. DPDA: delay and spatial configuration](#3-dpda-delay-and-spatial-configuration)
- [4. PA: ghost-source offset](#4-pa-ghost-source-offset)
- [5. BA: blinding distance](#5-ba-blinding-distance)
- [6. AVA: attack gain and phase](#6-ava-attack-gain-and-phase)
- [7. MA: delay and ghost-source offset](#7-ma-delay-and-ghost-source-offset)

## 1. Experimental protocol

The sensitivity experiments use the same controlled simulation environment as the main study: a 300 m single-lane ring road containing ten vehicles. Two ACC behavior parameterizations are evaluated:

- **EV-ACC:** the IDM parameter set calibrated from EV-ACC trajectory data.
- **ICE-ACC:** the IDM parameter set calibrated from ICE-ACC trajectory data.

These labels denote two empirically calibrated car-following behavior parameterizations within the same IDM structure. They do not explicitly model powertrain dynamics.

### Spatial attack configurations

| Scenario | Compromised-vehicle arrangement |
|:--:|---|
| I | One compromised vehicle |
| II | Two non-adjacent compromised vehicles |
| III | Three non-adjacent compromised vehicles |
| IV | Two adjacent compromised vehicles |

Unless otherwise stated, each parameterization–configuration combination was independently repeated ten times. Scenario IV is used for most detailed tables because the preliminary comparison across all four spatial configurations identified it as the most affected configuration for the reported attacks.

### Reported metrics

| Metric | Description | Unit/reporting format |
|---|---|---|
| Collisions | Number or percentage of runs ending in a collision | `n/10` or `%` |
| `V_avg` | Mean vehicle speed during the evaluated period | m/s |
| Mean VSD | Fleet-level mean speed-fluctuation measure used in the manuscript | m/s |
| Mean SSD | Fleet-level mean spacing-fluctuation measure used in the manuscript | m |
| `t_c` | Mean time at which the first collision occurs | s |

Continuous metrics are reported as **mean ± standard deviation** when both statistics are available. For a collision occurring during an evaluation phase, only valid trajectory samples up to the collision are included; subsequent unavailable phases are not evaluated.

## 2. Parameter-selection summary

| Attack | Parameter varied | Tested values | Setting retained for the main experiments | Selection basis |
|---|---|---|---|---|
| DPDA | Delay `tau_d` | 5, 6, 7, 8, 9, 10 s | 6, 8, and 9 s | Representative lower, intermediate, and higher disturbance levels; not collision thresholds |
| PA | Ghost-source offset | `i−1`, `i−2`, `i−3` | `i−1` | Strongest combined speed/spacing disturbance and lowest information-access requirement among tested offsets |
| BA | Blinding distance `D_B` | 20, 30, 40, 50, 55, 60 m | 50 m | Smallest tested distance yielding configuration-robust 100% collision outcomes |
| AVA | Attack gain `k` | 0.0005, 0.001, 0.002, 0.005, 0.2, 0.5, 1.0 | 0.001 | Representative low-gain disturbance; largest or tied-largest response in three of four ACC–stability-metric combinations |
| AVA | Phase `phi` | `pi/3`, `pi/2`, `pi` | Sensitivity set | Covers an intermediate positive perturbation, maximum positive perturbation, and zero-direct-perturbation reference |
| MA | Delay and source offset | `tau_d` = 6, 8, 9 s; offset = `i−1`, `i−2`, `i−3` | `tau_d` = 9 s and `i−1` | Representative high delay combined with the most influential and readily implementable tested source mismatch |

## 3. DPDA: delay and spatial configuration

The DPDA experiments were designed to separate the effect of the delay magnitude from the effect of the spatial arrangement of compromised vehicles.

### 3.1 Spatial-configuration sensitivity

Collision results aggregated over `tau_d` = 5–10 s are shown below.

| Scenario | Spatial attack configuration | EV-ACC collision rate | ICE-ACC collision rate |
|:--:|---|---:|---:|
| I | One compromised vehicle | 0% | 0% |
| II | Two non-adjacent compromised vehicles | 0% | 0% |
| III | Three non-adjacent compromised vehicles | 0% | 0% |
| **IV** | **Two adjacent compromised vehicles** | **100%** | **100%** |

Scenario IV caused collisions in all 120 runs: 60/60 EV-ACC runs and 60/60 ICE-ACC runs. The collision outcome did not change across the tested delay range, whereas no collision occurred in Scenarios I–III. Within the tested conditions, this contrast indicates that the adjacency of the compromised vehicles was the dominant factor governing DPDA collision occurrence.

### 3.2 Delay-magnitude sensitivity under Scenario IV

| `tau_d` (s) | EV-ACC mean VSD (m/s) | ICE-ACC mean VSD (m/s) | EV-ACC mean SSD (m) | ICE-ACC mean SSD (m) |
|---:|---:|---:|---:|---:|
| 5 | 0.116 ± 0.025 | 0.280 ± 0.045 | 0.588 ± 0.102 | 1.181 ± 0.313 |
| **6** | **0.120 ± 0.023** | **0.318 ± 0.045** | **0.631 ± 0.113** | **1.411 ± 0.316** |
| 7 | 0.127 ± 0.025 | 0.363 ± 0.058 | 0.665 ± 0.125 | 1.669 ± 0.384 |
| **8** | **0.142 ± 0.027** | **0.406 ± 0.068** | **0.690 ± 0.131** | **1.917 ± 0.435** |
| **9** | **0.167 ± 0.030** | **0.444 ± 0.066** | **0.710 ± 0.140** | **2.144 ± 0.421** |
| 10 | 0.193 ± 0.033 | 0.469 ± 0.071 | 0.734 ± 0.152 | 2.309 ± 0.351 |

**Interpretation.** The speed and spacing disturbances generally increased with delay, even though every Scenario IV run already resulted in a collision. From 6 to 9 s, mean VSD increased from 0.120 to 0.167 m/s for EV-ACC and from 0.318 to 0.444 m/s for ICE-ACC. Mean SSD increased from 0.631 to 0.710 m and from 1.411 to 2.144 m, respectively.

The collision time did not respond identically for the two parameterizations: it increased from 80.587 to 82.877 s for EV-ACC but decreased from 77.160 to 75.870 s for ICE-ACC as the delay increased from 6 to 9 s. Therefore, 6, 8, and 9 s were retained as representative lower, intermediate, and higher disturbance levels rather than universal collision thresholds. The 5 and 7 s settings produced weaker or intermediate responses, and 10 s introduced no new collision pattern.

## 4. PA: ghost-source offset

PA replaces the expected information source with data associated with another vehicle position. The offset denotes how far the substituted source is from the expected source: offset 1 corresponds to `i−1`, offset 2 to `i−2`, and offset 3 to `i−3`.

### Results under Scenario IV

| Offset (vehicles) | EV-ACC collisions | ICE-ACC collisions | EV-ACC `V_avg` (m/s) | ICE-ACC `V_avg` (m/s) | EV-ACC mean VSD (m/s) | ICE-ACC mean VSD (m/s) | EV-ACC mean SSD (m) | ICE-ACC mean SSD (m) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **1 (`i−1`)** | **0/10** | **0/10** | **14.867 ± 0.069** | **12.261 ± 0.231** | **0.269 ± 0.057** | **0.480 ± 0.169** | **0.546 ± 0.096** | **1.236 ± 0.297** |
| 2 (`i−2`) | 0/10 | 0/10 | 14.858 ± 0.072 | 12.231 ± 0.242 | 0.251 ± 0.045 | 0.435 ± 0.163 | 0.539 ± 0.101 | 1.173 ± 0.508 |
| 3 (`i−3`) | 0/10 | 0/10 | 14.808 ± 0.077 | 12.085 ± 0.328 | 0.221 ± 0.040 | 0.371 ± 0.131 | 0.531 ± 0.079 | 1.104 ± 0.418 |

**Interpretation.** No collision occurred in any of the 60 Scenario IV runs or in any of the 240 runs covering all four spatial configurations. Under Scenario IV, increasing the offset from one to three vehicles progressively reduced mean VSD and mean SSD for both parameterizations. The one-vehicle offset therefore produced the strongest combined speed and spacing disturbances among the tested offsets.

The `i−1` setting is also the most localized mismatch and places the lowest requirement on externally sourced information: the attacker only needs to access and incorrectly associate information from the nearest alternative vehicle position. Larger offsets require information from more distant vehicles and more complex vehicle identification and matching. For these empirical and implementation-related reasons, `i−1` was retained as the nominal PA setting.

## 5. BA: blinding distance

The blinding-distance range was selected with reference to the initial average net spacing of 25 m. The 20 and 30 m settings examine conditions below and slightly above that spacing. The distance is then increased to 60 m—approximately 2.5 times the initial net spacing—to identify the transition from disturbances absorbed by car-following adjustments to consistently collision-inducing conditions.

For each distance, 80 simulations were conducted: two ACC parameterizations × four spatial configurations × ten repeated runs.

| `D_B` (m) | EV-ACC collision rate | ICE-ACC collision rate | EV-ACC phase (during/after) | ICE-ACC phase (during/after) | EV-ACC mean `t_c` (s) | ICE-ACC mean `t_c` (s) |
|---:|---:|---:|---:|---:|---:|---:|
| 20 | 0% | 0% | — | — | — | — |
| 30 | 0% | 0% | — | — | — | — |
| 40 | 100% | 25% | 40/0 | 8/2 | 71.3 | 85.8 |
| **50** | **100%** | **100%** | **40/0** | **40/0** | **68.2** | **80.6** |
| 55 | 100% | 100% | 40/0 | 40/0 | 67.6 | 77.1 |
| 60 | 100% | 100% | 40/0 | 40/0 | 67.2 | 75.5 |

**Interpretation.** No collision occurred at 20 or 30 m, indicating that the available spacing and longitudinal feedback absorbed the relatively mild disturbances. A distance of 40 m formed a transition regime: every EV-ACC run collided, but only 25% of ICE-ACC runs collided. The combined collision rate was 62.5%, and the outcome still depended strongly on the ACC parameterization and spatial configuration.

At 50 m, all eight ACC-parameterization–spatial-configuration combinations produced a 100% collision rate, and every collision occurred during the attack. Relative to the pre-attack period, mean speed during the attack increased by 3.456 m/s (22.9%) for EV-ACC and by 2.407 m/s (20.2%) for ICE-ACC. The corresponding speed-fluctuation standard deviations increased from 0.288 to 1.488 m/s and from 0.624 to 0.829 m/s.

Increasing the distance to 55 or 60 m did not change the collision rate or affect additional parameterization–configuration combinations; it only caused earlier collisions. Thus, 50 m was selected as the **lower boundary of the configuration-robust high-risk regime**, not because it was assumed to be a universal safe-following-distance threshold or chosen to maximize attack severity.

## 6. AVA: attack gain and phase

The preliminary comparison across all spatial configurations identified Scenario IV as the most affected AVA configuration. Two complementary sensitivity analyses were therefore performed under Scenario IV: one varying the attack gain and another varying the phase.

### 6.1 Gain sensitivity

| Gain `k` | EV-ACC collisions | ICE-ACC collisions | EV-ACC mean VSD (m/s) | ICE-ACC mean VSD (m/s) | EV-ACC mean SSD (m) | ICE-ACC mean SSD (m) |
|---:|---:|---:|---:|---:|---:|---:|
| 0.0005 | 0/10 | 0/10 | 0.364 ± 0.050 | 1.032 ± 0.140 | 1.674 ± 0.220 | 6.922 ± 0.918 |
| **0.001** | **0/10** | **0/10** | **0.365 ± 0.050** | **1.045 ± 0.140** | **1.678 ± 0.220** | **6.923 ± 0.918** |
| 0.002 | 0/10 | 0/10 | 0.364 ± 0.050 | 1.036 ± 0.140 | 1.678 ± 0.220 | 6.919 ± 0.918 |
| 0.005 | 0/10 | 0/10 | 0.365 ± 0.050 | 1.044 ± 0.141 | 1.676 ± 0.219 | 6.909 ± 0.920 |
| 0.2 | 0/10 | 0/10 | 0.430 ± 0.050 | 0.966 ± 0.133 | 1.676 ± 0.225 | 6.131 ± 0.972 |
| 0.5 | 0/10 | 0/10 | 0.459 ± 0.049 | 1.023 ± 0.130 | 1.677 ± 0.210 | 6.687 ± 0.897 |
| 1.0 | 0/10 | 0/10 | 0.391 ± 0.046 | 1.027 ± 0.139 | 1.624 ± 0.220 | 6.830 ± 0.905 |

**Interpretation.** The response was non-monotonic: increasing `k` did not consistently increase every disturbance metric. Among the four combinations formed by the two ACC parameterizations and the two stability metrics, `k = 0.001` produced the largest or tied-largest mean response in three. It yielded the highest ICE-ACC mean VSD (1.045 m/s) and mean SSD (6.923 m) and tied for the largest EV-ACC mean SSD (1.678 m). The exception was EV-ACC mean VSD, which peaked at 0.459 m/s for `k = 0.5`.

The similar outcomes at `k = 0.0005`, `0.001`, and `0.002` show that the qualitative result is stable within the low-gain range. Therefore, `k = 0.001` was retained as a representative nominal setting, while the larger gains serve as stress tests. No collision occurred in any of the 140 gain-sensitivity runs.

### 6.2 Phase sensitivity at `k = 0.001`

| Phase `phi` | EV-ACC collisions | ICE-ACC collisions | EV-ACC `V_avg` (m/s) | ICE-ACC `V_avg` (m/s) | EV-ACC mean VSD (m/s) | ICE-ACC mean VSD (m/s) | EV-ACC mean SSD (m) | ICE-ACC mean SSD (m) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `pi/3` | 0/10 | 0/10 | 15.164 | 11.536 | 0.387 | 1.071 | 1.729 | 6.070 |
| `pi/2` | 0/10 | 0/10 | 15.193 | 11.602 | 0.391 | 1.072 | 1.739 | 5.956 |
| `pi` | 0/10 | 0/10 | 14.946 | 11.043 | 0.363 | 1.028 | 1.670 | 6.930 |

**Interpretation.** The `pi/2` setting produced the largest mean speed and mean VSD for both ACC parameterizations, whereas `pi` produced the smallest values of both metrics. The spacing response differed: EV-ACC mean SSD was largest at `pi/2` and smallest at `pi`, while ICE-ACC mean SSD was smallest at `pi/2` and largest at `pi`. This difference demonstrates that the perturbation is redistributed non-monotonically through the nonlinear car-following interactions. No collision occurred in any of the 60 phase-sensitivity runs.

## 7. MA: delay and ghost-source offset

MA combines the delayed/discretized information effect of DPDA with the ghost-source mismatch of PA. The preliminary spatial comparison found no collision under any tested MA configuration, while Scenario IV produced the strongest overall speed and spacing disturbances. The detailed analysis therefore focuses on Scenario IV.

| Varied parameter | `tau_d` (s) | Offset (vehicles) | EV-ACC collisions | ICE-ACC collisions | EV-ACC `V_avg` (m/s) | ICE-ACC `V_avg` (m/s) | EV-ACC mean VSD (m/s) | ICE-ACC mean VSD (m/s) | EV-ACC mean SSD (m) | ICE-ACC mean SSD (m) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Delay (`i−1` fixed) | 6 | 1 | 0/10 | 0/10 | 15.101 ± 0.034 | 11.613 ± 0.121 | 0.416 ± 0.066 | 1.054 ± 0.128 | 1.024 ± 0.092 | 1.739 ± 0.130 |
| Delay (`i−1` fixed) | 8 | 1 | 0/10 | 0/10 | 15.115 ± 0.032 | 11.489 ± 0.149 | 0.422 ± 0.068 | 1.179 ± 0.136 | 0.955 ± 0.087 | 1.911 ± 0.140 |
| **Delay (`i−1` fixed)** | **9** | **1** | **0/10** | **0/10** | **15.123 ± 0.030** | **11.580 ± 0.109** | **0.431 ± 0.065** | **1.085 ± 0.161** | **0.966 ± 0.091** | **1.927 ± 0.060** |
| Offset (`tau_d = 9 s` fixed) | 9 | 2 | 0/10 | 0/10 | 15.121 ± 0.035 | 11.524 ± 0.143 | 0.428 ± 0.058 | 0.928 ± 0.106 | 0.957 ± 0.186 | 1.897 ± 0.443 |
| Offset (`tau_d = 9 s` fixed) | 9 | 3 | 0/10 | 0/10 | 15.117 ± 0.037 | 11.550 ± 0.079 | 0.415 ± 0.071 | 0.884 ± 0.160 | 0.938 ± 0.197 | 1.872 ± 0.613 |

**Interpretation.** Changing the delay from 6 to 9 s altered the disturbance magnitude but did not change the collision-free outcome. With the delay fixed at 9 s, increasing the source offset from `i−1` to `i−3` reduced both mean VSD and mean SSD for both parameterizations. The `i−1` mismatch was therefore the most influential tested offset and also required access only to the nearest alternative vehicle information.

The adopted MA configuration—`tau_d = 9 s` and offset `i−1`—combines a representative high delay with the most localized and influential tested PA source mismatch. The choice jointly reflects traffic impact and implementation feasibility rather than an attempt to force a predetermined collision outcome.

### Interpretation of the collision-free MA outcome

The absence of collisions under MA, despite collisions under DPDA alone in Scenario IV, illustrates a nonlinear closed-loop interaction rather than a general reduction in risk from combining attacks. PA introduces a lower-acceleration tendency, while DPDA mainly introduces delayed responses. In the tested IDM-controlled system, the conservative acceleration tendency limited rapid gap closure, and the car-following feedback gradually compensated for state deviations caused by the delayed information. Consequently, the two effects did not combine additively, and MA produced a less severe collision outcome than DPDA alone. This result is scenario-dependent and should not be generalized to other hybrid attacks or traffic conditions.


