# Cyberattack Modeling and Comparative Evaluation of EV-ACC and ICE-ACC Vehicles

## Overview

This repository supports our first research work on cyberattack modeling for vehicles equipped with adaptive cruise control (ACC). The study develops a unified simulation framework for examining how representative cyberattacks affect vehicle-level behavior and traffic-flow performance.

Six variants of typical cyberattacks are modeled by modifying the communication, perception, control, or attitude-related information used by the ACC controller. The attacks are implemented within a common car-following framework so that their effects can be evaluated consistently under the same traffic and experimental conditions.

The study also models and compares EV-ACC and ICE-ACC vehicles. Both vehicle types use the same Intelligent Driver Model (IDM) structure but adopt different parameter sets calibrated from real-world car-following trajectories. Therefore, the comparison focuses on differences between the calibrated EV-ACC and ICE-ACC car-following parameterizations rather than the intrinsic cybersecurity characteristics of electric and internal-combustion powertrains.

## Six Cyberattack Variants

| Attack | Main mechanism | Affected information or function |
|---|---|---|
| DPDA | Delays and discretizes the information available to the ACC vehicle | V2V spacing and relative-speed information |
| PA | Replaces legitimate predecessor information with data from an incorrect or ghost source | Information-source selection and controller inputs |
| BA | Simulates a blinding condition that disrupts leader detection within a specified distance | Perceived inter-vehicle spacing and leader availability |
| FA | Freezes the reported speed during the attack interval | Vehicle-speed feedback used by the controller |
| MA | Combines the mechanisms of DPDA and PA | Delayed, discretized, and source-misaligned controller inputs |
| AVA | Introduces multiplicative-additive perturbations associated with attitude information | Attitude-related measurements and the resulting controller inputs |

These variants do not imply identical intrusion processes. They provide controller-level abstractions through which attacks involving different channels and compromised subsystems can be compared on a common simulation platform.

## Simulation and Comparative Analysis

The experiments are conducted on a controlled 300 m single-lane ring road containing ten vehicles. The periodic roadway maintains a fixed vehicle population and traffic density, while allowing cyberattack-induced disturbances and their post-attack residual effects to be observed continuously without interference from roadway inflows, outflows, or lane changes.

The main experimental design includes:

- EV-ACC and ICE-ACC car-following parameterizations calibrated using real-world trajectories;
- different ACC penetration rates and spatial arrangements of compromised vehicles;
- three analysis phases: before, during, and after the attack;
- ten independent runs for each experimental configuration;
- termination of an individual simulation when a collision occurs; and
- vehicle- and traffic-level evaluation using average speed, speed standard deviation, spacing standard deviation, time headway, collision rate, and collision time.

This design enables a systematic comparison of traffic efficiency, traffic stability, safety risk, disturbance propagation, and post-attack evolution under the six cyberattack variants.

## Supplementary Parameter Sensitivity Analysis

Additional parameter sensitivity experiments were conducted to examine whether the observed attack outcomes remain consistent across different attack-parameter settings. The supplementary analysis covers the principal parameters of DPDA, PA, BA, MA, FA, and AVA and reports the corresponding collision outcomes and traffic-performance measures.

The complete experimental settings, tables, results, and interpretations are provided in:

**[Supplementary Parameter Sensitivity Analysis](Supplementary_Parameter_Sensitivity_Analysis.md)**

Place `README.md` and `Supplementary_Parameter_Sensitivity_Analysis.md` in the same GitHub directory to keep the link above valid.

## Scope

This work focuses on modeling and comparing the vehicle- and traffic-level consequences of cyberattacks. It does not reproduce low-level intrusion procedures and does not introduce an attack-detection or trajectory-recovery method. The findings are intended to support subsequent research on risk-aware detection, mitigation, and cyber-resilient ACC control.
