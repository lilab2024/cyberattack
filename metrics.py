start_idx1 = int(30 / deltaT)  
end_idx1 = int(60 / deltaT)  


selected_velocities = simFollowVel[start_idx1:end_idx1, :]


average_speed = np.mean(selected_velocities)

print(f"30-60s the average speed: {average_speed:.2f} m/s")
selected_velocities = simFollowVel[start_idx1:end_idx1, :]

max_speeds = np.max(selected_velocities, axis=0)  # shape: (numVeh,)
min_speeds = np.min(selected_velocities, axis=0)  # shape: (numVeh,)


speed_differences = max_speeds - min_speeds


average_speed_difference = np.mean(speed_differences)


#print(f"40-60s the difference between the maximum and minimum speed of each vehicle: {speed_differences}")
print(f"30-60s the average intra-vehicle speed variation across all vehicles: {average_speed_difference:.2f} m/s")




#during：

start_idx2 = int(60 / deltaT) 
end_idx2 = int(90 / deltaT)  

selected_velocities = simFollowVel[start_idx2:end_idx2, :]


average_speed = np.mean(selected_velocities)

print(f"60-90s the average speed: {average_speed:.2f} m/s")
selected_velocities = simFollowVel[start_idx2:end_idx2, :]


max_speeds = np.max(selected_velocities, axis=0)  # shape: (numVeh,)
min_speeds = np.min(selected_velocities, axis=0)  # shape: (numVeh,)


speed_differences = max_speeds - min_speeds


average_speed_difference = np.mean(speed_differences)


#print(f"60-90s the difference between the maximum and minimum speed of each vehicle: {speed_differences}")
print(f"60-90s the average intra-vehicle speed variation across all vehicles: {average_speed_difference:.2f} m/s")




#after：

start_idx3 = int(90 / deltaT)  
end_idx3 = int(120 / deltaT)  

selected_velocities = simFollowVel[start_idx3:end_idx3, :]

average_speed = np.mean(selected_velocities)

print(f"90-120s the average speed: {average_speed:.2f} m/s")
selected_velocities = simFollowVel[start_idx3:end_idx3, :]


max_speeds = np.max(selected_velocities, axis=0)  # shape: (numVeh,)
min_speeds = np.min(selected_velocities, axis=0)  # shape: (numVeh,)


speed_differences = max_speeds - min_speeds


average_speed_difference = np.mean(speed_differences)


#print(f"90-120s the difference between the maximum and minimum speed of each vehicle: {speed_differences}")
print(f"90-120s the average intra-vehicle speed variation across all vehicles: {average_speed_difference:.2f} m/s")





#about spacing
#pre
start_idx1 = int(30 / deltaT)  
end_idx1 = int(60 / deltaT)  


selected_spacing = simSpacing[start_idx1:end_idx1, :]


spacing_std = np.std(selected_spacing, axis=0)  


overall_spacing_std = np.mean(spacing_std)  

print(f"30-60s the standard deviation of inter-vehicle spacing：{overall_spacing_std:.2f} 米")


#druing
start_idx2 = int(60 / deltaT)  
end_idx2 = int(90 / deltaT)  


selected_spacing = simSpacing[start_idx2:end_idx2, :]


spacing_std = np.std(selected_spacing, axis=0)  


overall_spacing_std = np.mean(spacing_std)  

print(f"60-90s the standard deviation of inter-vehicle spacing：{overall_spacing_std:.2f} 米")

#after
start_idx3 = int(90 / deltaT) 
end_idx3 = int(120/ deltaT) 


selected_spacing = simSpacing[start_idx3:end_idx3, :]

）
spacing_std = np.std(selected_spacing, axis=0)  


overall_spacing_std = np.mean(spacing_std)  

print(f"90-120s the standard deviation of inter-vehicle spacing：{overall_spacing_std:.2f} 米")





# pre：30-60s

selected_velocity = simFollowVel[start_idx1:end_idx1, :]
velocity_std = np.std(selected_velocity, axis=0)  
overall_velocity_std = np.mean(velocity_std) 
print(f"30-60s the standard deviation of inter-vehicle spacing：{overall_velocity_std:.2f} m/s")

# during：60-90s

selected_velocity = simFollowVel[start_idx2:end_idx2, :]
velocity_std = np.std(selected_velocity, axis=0)
overall_velocity_std = np.mean(velocity_std)
print(f"60-90s the standard deviation of inter-vehicle spacing：{overall_velocity_std:.2f} m/s")

# after：90-120s

selected_velocity = simFollowVel[start_idx3:end_idx3, :]
velocity_std = np.std(selected_velocity, axis=0)
overall_velocity_std = np.mean(velocity_std)
print(f"90-120秒内车辆速度的波动（标准差）：{overall_velocity_std:.2f} m/s")





