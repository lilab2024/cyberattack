import numpy as np
np.random.seed(42)
import pandas as pd
from scipy.stats import norm
def IDM_Accel(params, v, v_l, s):   
    # Returns the acceleration of the IDM for a particular parameter set and
    # position/speed condition:

    v_0 = params[0]  # Desired Speed Guess 20   
    T = params[1]  # Desired Time-gap  2
    s_0 = params[2]  # Minimum Gap   4
    delta = params[3]  # Acceleration Exponent 2   
    a = params[4]  # max Acceleration rate 2
    b = params[5]  # Comfortable Deceleration 3   
    delta_V = v_l - v

    s_star = s_0 + max([0.0, v*T - (v*delta_V) / (2 * np.sqrt(a * b))])  
    accel = a * (1 - (v / v_0) ** delta - (s_star / max(s,0.1)) ** 2)  

    return accel

import math
omega=0.1
def makeSim_ring_mix_attack(numSteps, numVeh, params_IDM,params_OVRV, delta_T, initVel_Follower, initGap, attacked_Vehicles,attack_start_time, attack_end_time,slope_1, slope_2):#模拟车辆在环形道路上的跟车行为
    spacing_gap_Profile = np.zeros((numSteps, numVeh))
    spacing_gap_Profile[0, :] = np.squeeze(initGap)
    velProfile_Follower = np.zeros((numSteps, numVeh)) 
    velProfile_Follower[0, :] = initVel_Follower
    accelVal = np.zeros((numSteps, numVeh))
    sigma = 0.5
    
    for t in range(1, numSteps):
        for i in range(numVeh):
            noise = norm.rvs(0, sigma)  
            noise_attack = norm.rvs(0, 5)

            if i == 0:  # Leader
                accelVal[t - 1, i] = IDM_Accel(params_IDM[i, :], velProfile_Follower[t - 1, i], velProfile_Follower[t - 1, numVeh - 1], spacing_gap_Profile[t - 1, i]) + noise
                accelVal[t - 1, i] = max(min(accelVal[t - 1, i], 2), -5)
                velProfile_Follower[t, i] = max(velProfile_Follower[t - 1, i] + accelVal[t - 1, i] * delta_T, 0.5)
                spacing_gap_Profile[t, i] = max(spacing_gap_Profile[t - 1, i] + (velProfile_Follower[t - 1, numVeh - 1] - velProfile_Follower[t - 1, i]) * delta_T, 0)#0.5
            elif attacked_Vehicles[0, i] == 2:
                if attack_start_time <= t < attack_end_time:  # Attack Vehicles within specific time 如果在攻击时间之内
                    #print(f"Attack triggered for vehicle {i} at time {t}")
                    # Behavior when the time is within the attack range
                    #accelVal[t - 1, i] = OVRV_Accel_attack(params_OVRV[i, :], velProfile_Follower[t - 1, i], velProfile_Follower[t - 1, i - 1], spacing_gap_Profile[t - 1, i], slope_1, slope_2)
                    #accelVal[t - 1, i] = max(min(accelVal[t - 1, i], 2), -5)
                    #if t>90:
                    theta=omega*(t-attack_start_time)*delta_T
                    accelVal[t - 1, i] = IDM_Accel(params_IDM[i, :], velProfile_Follower[t - 1, i], velProfile_Follower[t - 1, numVeh - 1], spacing_gap_Profile[t - 1, i]) + noise
                    #accelVal[t - 1, i] = OVRV_Accel_attack(params_OVRV[i, :], velProfile_Follower[t - 1, i], velProfile_Follower[t - 1, i - 1], spacing_gap_Profile[t - 1, i], slope_1, slope_2)
                    accelVal[t - 1, i] = max(min(accelVal[t - 1, i], 2), -5)
                    velProfile_Follower[t, i] =max((velProfile_Follower[t - 1, i] + accelVal[t - 1, i] * delta_T)*(1+0.0005*(math.sin(theta))),0.5)
                    #velProfile_Follower[t, i] = max(velProfile_Follower[t - 1, i] + accelVal[t - 1, i] * delta_T, 0.5)# 19 
                    spacing_gap_Profile[t, i] = max(spacing_gap_Profile[t - 1, i] + (velProfile_Follower[t - 1, i - 1] - velProfile_Follower[t - 1, i]) * delta_T, 0)#0.5
                    #spacing_gap_Profile[t, i] =min(max(spacing_gap_Profile[t - 1, i]+spacing_gap_Profile[t - 1, i-1],0),50)
                   
                    #velProfile_Follower[t, i]=velProfile_Follower[t-120, i]
                    #spacing_gap_Profile[t, i]=spacing_gap_Profile[t-120, i]
                                                                 
                    #else:
                    #accelVal[t - 1, i] = OVRV_Accel_attack(params_OVRV[i, :], velProfile_Follower[t - 1, i], velProfile_Follower[t - 1, i - 1], spacing_gap_Profile[t - 1, i], slope_1, slope_2)
                    #accelVal[t - 1, i] = max(min(accelVal[t - 1, i], 2), -5)
                    #velProfile_Follower[t, i] = max(velProfile_Follower[t - 1, i] + accelVal[t - 1, i] * delta_T, 0.5)
                    #spacing_gap_Profile[t, i] = max(spacing_gap_Profile[t - 1, i] + (velProfile_Follower[t - 1, i - 1] - velProfile_Follower[t - 1, i]) * delta_T, 0.5)
                        
                else:
                    # Behavior when the time is outside the attack range - treat as AttackedVeh == 1
                    accelVal[t - 1, i] = IDM_Accel(params_IDM[i, :], velProfile_Follower[t - 1, i], velProfile_Follower[t - 1, numVeh - 1], spacing_gap_Profile[t - 1, i]) + noise
                    #accelVal[t - 1, i] = OVRV_Accel(params_OVRV[i, :], velProfile_Follower[t - 1, i], velProfile_Follower[t - 1, i - 1], spacing_gap_Profile[t - 1, i])
                    accelVal[t - 1, i] = max(min(accelVal[t - 1, i], 2), -5)
                    velProfile_Follower[t, i] = max(velProfile_Follower[t - 1, i] + accelVal[t - 1, i] * delta_T, 0.5)
                    spacing_gap_Profile[t, i] = max(spacing_gap_Profile[t - 1, i] + (velProfile_Follower[t - 1, i - 1] - velProfile_Follower[t - 1, i]) * delta_T, 0)#0.5


            elif attacked_Vehicles[0, i] == 1:
                accelVal[t - 1, i] = IDM_Accel(params_IDM[i, :], velProfile_Follower[t - 1, i], velProfile_Follower[t - 1, numVeh - 1], spacing_gap_Profile[t - 1, i]) + noise
                #accelVal[t - 1, i] = OVRV_Accel(params_OVRV[i, :], velProfile_Follower[t - 1, i], velProfile_Follower[t - 1, i - 1], spacing_gap_Profile[t - 1, i])
                accelVal[t - 1, i] = max(min(accelVal[t - 1, i], 2), -5)
                velProfile_Follower[t, i] = max(velProfile_Follower[t - 1, i] + accelVal[t - 1, i] * delta_T, 0.5)
                spacing_gap_Profile[t, i] = max(spacing_gap_Profile[t - 1, i] + (velProfile_Follower[t - 1, i - 1] - velProfile_Follower[t - 1, i]) * delta_T, 0)#0.5
            
            else:
                accelVal[t - 1, i] = IDM_Accel(params_IDM[i, :], velProfile_Follower[t - 1, i], velProfile_Follower[t - 1, i - 1], spacing_gap_Profile[t - 1, i])
                accelVal[t - 1, i] = max(min(accelVal[t - 1, i], 2), -5)
                velProfile_Follower[t, i] = max(velProfile_Follower[t - 1, i] + accelVal[t - 1, i] * delta_T, 0.5)
                spacing_gap_Profile[t, i] = max(spacing_gap_Profile[t - 1, i] + (velProfile_Follower[t - 1, i - 1] - velProfile_Follower[t - 1, i]) * delta_T, 0)#0.5

    return spacing_gap_Profile, velProfile_Follower, accelVal  
#print(attacked_Vehicles)
#print(velProfile_Follower)


import numpy as np    #实现了一个车辆在环形道路上进行车距和车速跟随的仿真，并模拟了一些攻击

# Configuration Parameters
L = 300  # Length of the ring in meters
numVeh = 10  # Number of vehicles in the ring
numSteps = 30 * 60 * 2  # Number of simulation steps (30 minutes)  两分钟
deltaT = 1 / 30  # Time step in seconds
time_series = np.arange(0, numSteps * deltaT, deltaT)  # Array of time steps，用于记录仿真中的时间
car_length = 5  # Length of each car in meters
ACC_params = [44.1, 2.2, 6.3, 15.5, 0.6, 5.2]# [33.34,1.63,2.02,4.02,2.01,8.97] #medium#   # Parameters for commercial available ACC商用ACC车辆参数，IDM模型参数
Human_params = [30, 1.26, 3.4, 4, 1.06, 2]  # Parameters for human drivers 人工驾驶的
Theoretical_ACC_params =[33.34,1.63,2.02,4.02,2.01,8.97] #[33.33, 1.5, 2, 4, 1.4, 2]
# Car-Following Parameters
  # Theoretical ACC parameters  

# ACC Configuration
eta = 0.5  # ACC-related parameter (adjust as needed)
ACC_indices = [1,3,5,6,7]  # Indices of ACC-equipped vehicles
#Attack_indices = [1]  # Indices of attacked ACC-equipped vehicles 
Attack_indices = [1,5,6] #[1,6]
# Initializing Car Parameters
IDM_parameters = np.tile(Human_params, (numVeh, 1))  # IDM parameters for each vehicle

# Initial States
attacked_Vehicles = np.zeros((1, numVeh)) 
total_vehicle_length = car_length * numVeh 
initial_spacing =(L - total_vehicle_length) / numVeh # Initial spacing between vehicles
S_E = np.full((numVeh, 1), initial_spacing )#
initial_velocity = np.zeros((1, numVeh)) 

# Updating Vehicle States for ACC and Attacked Vehicles 
attacked_Vehicles[0, ACC_indices] = 1  # Mark ACC vehicles
attacked_Vehicles[0, Attack_indices] = 2  # Mark attacked ACC vehicles
IDM_parameters[ACC_indices, :] = ACC_params  # Update IDM parameters for ACC vehicles

# Overriding ACC Parameters
ACC_override_params = [0.08,0.54,1.03,11.88,1.06] #medium   #[0.02, 0.13, 21.51, 1.71]  
OVRV_parameters = np.tile(ACC_override_params, (numVeh, 1))

# Attack Simulation Configuration
attack_start_time = 30 * 60 * 1  # Start time of the attack
attack_end_time = 30 * 60 * 1.5  # End time of the attack

# Attack Slope Parameters
slope_params = [0,-0.1, -0.3, -0.5, -0.7, -0.9, -2, 2, 5, -5, -3, -1.5]
#slope_params = [0,0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
slope_1 = slope_params[0]
slope_2 = slope_params[0]

# Running the Simulation
simSpacing, simFollowVel, simAcc = makeSim_ring_mix_attack(numSteps, numVeh, IDM_parameters, OVRV_parameters, deltaT, initial_velocity, S_E, attacked_Vehicles, attack_start_time, attack_end_time, slope_1, slope_2)

#print(simSpacing)


# Reshaping and accumulating spacing data   
last_vehicle_spacing = simSpacing[:, numVeh - 1]  # Extract spacing for the last vehicle
remaining_vehicle_spacing = simSpacing[:, :numVeh - 1]  # Extract spacing for all but the last vehicle
# Rearrange spacing data so that the last vehicle's data comes first
simSpacing_reshaped = np.hstack((last_vehicle_spacing[:, None], remaining_vehicle_spacing))
# Cumulative sum of the rearranged spacing data
cumulative_spacing = np.cumsum(simSpacing_reshaped, axis=1)

# Ensure all following velocities are non-negative
non_negative_follow_vel = np.maximum(simFollowVel, 0)
# Extract first vehicle's velocity and calculate its travel distance
first_vehicle_vel = non_negative_follow_vel[:, 0]
first_vehicle_travel_dist = first_vehicle_vel * deltaT
cumulative_first_vehicle_dist = np.cumsum(first_vehicle_travel_dist)
# Replicate this distance for all vehicles
all_vehicle_cumulative_dist = np.tile(cumulative_first_vehicle_dist, (numVeh, 1)).T

# Calculate positions for vehicles 2 to N(e.g., 20) based on distances and spacing
position_vehicles_2_to_20 = all_vehicle_cumulative_dist - cumulative_spacing
first_vehicle_position = position_vehicles_2_to_20[:, numVeh - 1]
remaining_vehicles_position = position_vehicles_2_to_20[:, :numVeh - 1]
# Combine the positions of the first vehicle and remaining vehicles
combined_positions = np.hstack((first_vehicle_position[:, None], remaining_vehicles_position))
# Calculate travel distance based on velocity for all vehicles
travel_distance_all_vehicles = simFollowVel * deltaT
cumulative_travel_distance_all_vehicles = np.cumsum(travel_distance_all_vehicles, axis=0)


# Initialize parameters for position calculation
initial_position = L  # starting number
spacing_step_length = S_E[0]  # step length (s_e from the above code)
number_of_vehicles = numVeh  # number of vehicles
# Calculate initial position for each vehicle
initial_vehicle_positions = initial_position - spacing_step_length * np.arange(number_of_vehicles)
# Replicate initial positions for each time step
initial_positions_all_steps = np.tile(initial_vehicle_positions, (numSteps, 1))

# Calculate new positions by adding travel distances to initial positions
pos_new = cumulative_travel_distance_all_vehicles + initial_positions_all_steps

import matplotlib.pyplot as plt
a=60
b=90
#marker_size=1
fig, ax = plt.subplots(figsize=(10, 9))

ax.plot(time_series, pos_new, 'orange',marker='.', markersize=0.3, alpha=0.5, label='Human-driven vehicles') 
ax.plot(time_series, pos_new[:,ACC_indices], 'b', markersize=0.3, alpha=0.5, label='ACC vehicles') 
ax.plot(time_series, pos_new[:,Attack_indices], 'r', markersize=0.3, alpha=0.5, label='ACC vehicles') # Add label

ax.set_xlabel("Time (sec)", fontsize=28)
ax.set_ylabel("Position (m)", fontsize=28)
ax.grid(True)
# ax.legend() # Add legend
#ax.set_title("Vehicle Trajectories Over Time", fontsize=20)  # Increase title font size
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], color='orange', marker='.', linestyle='None', markersize=10, label='Human-driven vehicles'),
     Line2D([0], [0], color='b', marker='.', linestyle='None', markersize=10, label='ACC vehicles'),
        Line2D([0], [0], color='r', marker='.', linestyle='None', markersize=10, label="Attacked Vehicles"),

]
ax.legend(handles=legend_elements, fontsize=16, loc='lower right', markerscale=2)  # Adjust legend position, font size, and marker scale

ax.axvspan(a, b, color='grey', alpha=0.3)

plt.show()


import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(12, 9))

# Set the start (a) and end (b) times for the shaded area
a = 60# Example start time
b = 90 # Example end time

# Increase marker size for better visibility in the plot
marker_size = 1

# Use a darker shade of green for better visibility and less brightness 
ax.plot(time_series, pos_new % L, '.', color='orange', markersize=marker_size, label='Human-driven vehicles')
ax.plot(time_series, pos_new[:, ACC_indices] %L, 'b.', markersize=marker_size, label='ACC vehicles')
ax.plot(time_series, pos_new[:, Attack_indices] %L,'.', color='r', markersize=1, alpha=0.5, label="Attacked Vehicles")

# The attacked vehicles are not labeled and hence not in the legend

ax.set_xlabel("Time (sec)", fontsize=28)  # Increase font size for the axis label
ax.set_ylabel("Position (m)", fontsize=28)  # Increase font size for the axis label

# Increase font size of the numbers on the axes
ax.tick_params(axis='both', labelsize=16)  # Increase font size for the ticks 

# Add gridlines to the plot
ax.grid(True)  

# Set the legend to show with a larger font, and only for human-driven and ACC vehicles
# Since we have multiple HDVs but want them to appear only once in the legend,
# we can create custom legend entries:
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], color='orange', marker='.', linestyle='None', markersize=10, label='Human-driven vehicles'),
     Line2D([0], [0], color='b', marker='.', linestyle='None', markersize=10, label='ACC vehicles'),
        Line2D([0], [0], color='r', marker='.', linestyle='None', markersize=10, label="Attacked Vehicles"),

]
ax.legend(handles=legend_elements, fontsize=16, loc='lower right', markerscale=2)  # Adjust legend position, font size, and marker scale

# Add a title to the plot
#ax.set_title("Vehicle Trajectories Over Time", fontsize=20)  # Increase title font size
ax.axvspan(a, b, color='grey', alpha=0.3)


plt.show()

print("Attack_indices:", Attack_indices)

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
fig, ax = plt.subplots(figsize=(12, 9))
# Set figure size
#plt.figure(figsize=(12, 9))
# Set the start (a) and end (b) times for the shaded area
a = 60# Example start time
b = 90 # Example end time

# Plot all vehicles in green with alpha for transparency
ax.plot(time_series, simSpacing, '.',color='orange', markersize=1, alpha=0.5, label="Human-driven Vehicles") 

# Plot ACC vehicles in blue with alpha for transparency
ax.plot(time_series, simSpacing[:, ACC_indices], 'b.', markersize=1, alpha=0.5, label="ACC Vehicles")
ax.plot(time_series, simSpacing[:, Attack_indices], '.',color='r', markersize=1, alpha=0.5, label="Attacked Vehicles")


ax.set_xlabel("Time (sec)", fontsize=28)
ax.set_ylabel("Spacing (m)", fontsize=28)

# Increase font size for the tick labels
ax.tick_params(axis='both', labelsize=16)

# Add gridlines to the plot for better readability
ax.grid(True)

# Make top and right spines visible to emulate Matlab's box on
ax = plt.gca() 
ax.spines['top'].set_visible(True)
ax.spines['right'].set_visible(True)

# Create custom legend entries with increased marker size
legend_elements = [
    Line2D([0], [0], color='orange', marker='.', linestyle='None', markersize=10, label="Human-driven Vehicles"),
     Line2D([0], [0], color='b', marker='.', linestyle='None', markersize=10, label="ACC Vehicles"),
    Line2D([0], [0], color='r', marker='.', linestyle='None', markersize=10, label="Attacked Vehicles"),
]
ax.axvspan(a, b, color='grey', alpha=0.3)

# Add a legend to the plot with custom markers
ax.legend(handles=legend_elements, fontsize=16, loc='lower right', markerscale=2)  # Adjust legend position, font size, and marker scale


# Display the plot
plt.show()


import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
fig, ax = plt.subplots(figsize=(12, 9))
# Set figure size
#plt.figure(figsize=(12, 9))
# Set the start (a) and end (b) times for the shaded area
a = 60# Example start time
b = 90 # Example end time #突发事件的时间

# Plot all vehicles in green with alpha for transparency
ax.plot(time_series, simAcc[:,0], '.',color='orange', markersize=2, alpha=1, label="Human Vehicles") #绘制人为驾驶车辆的加速度数据 simacc：加速度数据

# Plot ACC vehicles in blue with alpha for transparency
ax.plot(time_series, simAcc[:, ACC_indices[1]], 'b.', markersize=2, alpha=1, label="ACC Vehicles")

# Plot attacked vehicles in red with alpha for transparency
ax.plot(time_series, simAcc[:, Attack_indices[0]], '.',color='r', markersize=2, alpha=1, label="Attack Vehicles")

# Set labels with increased font size
ax.set_xlabel("Time (sec)", fontsize=28)
ax.set_ylabel("Acceleration (m/s²)", fontsize=28)

# Increase font size for the tick labels
ax.tick_params(axis='both', labelsize=16)

# Add gridlines to the plot for better readability
ax.grid(True)

# Make top and right spines visible to emulate Matlab's box on
ax = plt.gca()
ax.spines['top'].set_visible(True)
ax.spines['right'].set_visible(True)

# Create custom legend entries with increased marker size
legend_elements = [
    Line2D([0], [0], color='orange', marker='.', linestyle='None', markersize=10, label="Human Vehicles"),
    Line2D([0], [0], color='b', marker='.', linestyle='None', markersize=10, label="ACC Vehicles"),
    Line2D([0], [0], color='r', marker='.', linestyle='None', markersize=10, label="Attacked Vehicles"),
]
ax.axvspan(a, b, color='grey', alpha=0.3)


# Add a legend to the plot with custom markers
ax.legend(handles=legend_elements, fontsize=16, loc='lower right', markerscale=2)  # Adjust legend position, font size, and marker scale



# Display the plot
plt.show()


import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# Set figure size
plt.figure(figsize=(12, 9))

# Set the start (a) and end (b) times for the shaded area
a = 60# Example start time
b = 90 # Example end time

# Plot all vehicles in green with alpha for transparency
plt.plot(time_series, simFollowVel, 'orange', markersize=1, alpha=0.5, label="Human-driven Vehicles")

# Plot ACC vehicles in blue with alpha for transparency
plt.plot(time_series, simFollowVel[:, ACC_indices], 'b.', markersize=1, alpha=0.5, label="ACC Vehicles")

# Plot attacked vehicles in red with alpha for transparency
plt.plot(time_series, simFollowVel[:, Attack_indices], 'r.', markersize=1, alpha=0.5, label="Attacked Vehicles")

# Set labels with increased font size
plt.xlabel("Time (sec)", fontsize=28)
plt.ylabel("Speed (m/s)", fontsize=28)

# Increase font size for the tick labels
plt.tick_params(axis='both', labelsize=16)

# Add gridlines to the plot for better readability
plt.grid(True)

# Make top and right spines visible to emulate Matlab's box on
ax = plt.gca()
ax.spines['top'].set_visible(True)
ax.spines['right'].set_visible(True)

# Create custom legend entries with increased marker size
legend_elements = [
    Line2D([0], [0], color='orange', marker='.', linestyle='None', markersize=10, label="Human-driven Vehicles"),
    Line2D([0], [0], color='b', marker='.', linestyle='None', markersize=10, label="ACC Vehicles"),
     Line2D([0], [0], color='r', marker='.', linestyle='None', markersize=10, label="Attacked Vehicles"),
]
ax.axvspan(a, b, color='grey', alpha=0.3)

# Add a legend to the plot with custom markers
ax.legend(handles=legend_elements, fontsize=16, loc='lower right', markerscale=2)  # Adjust legend position, font size, and marker scale

# Display the plot
plt.show()
