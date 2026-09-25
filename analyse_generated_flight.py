import pandas as pd
import matplotlib.pyplot as plt

flight =pd.read_csv("data/full_flight_data.csv")
print(flight.head())


max_altitude = flight["altitude_m"].max()
max_airspeed = flight["airspeed_mps"].max()
max_roll = flight["roll_deg"].abs().max()
max_g = flight["vertical_acceleration_g"].max()
flight_duration = flight["time_s"].max() / 60

print("\nFLIGHT SUMMARY")
print("-------------------------")

print(f"Flight duration: {flight_duration:.1f} min")
print(f"Maximum altitude: {max_altitude:.0f} m")
print(f"Maximum airspeed: {max_airspeed:.1f} m/s")
print(f"Maximum bank angle: {max_roll:.1f} deg")
print(f"Maximum vertical acceleration: {max_g:.2f} g")

# FUEL Consumption

time_interval = flight["time_s"].diff().fillna(0)

fuel_used = flight["fuel_flowrate_kgps"] * time_interval

total_fuel = fuel_used.sum()

print(f"Total fuel consumed: {total_fuel:.1f} kg")


# DETECTING ANOMALIES


high_roll = flight[flight["roll_deg"].abs() > 35 ]

print("\nHIGH BANK ANGLES")
for index, row in high_roll.iterrows():
    time_min = row["time_s"] / 60
    roll_angle = row["roll_deg"]

    print(f"High bank angle at {time_min:.1f} min: {roll_angle:.1f} deg")
    

high_g = flight[flight["vertical_acceleration_g"] > 1.5]

print("\nHIGH VERTICAL ACCELERATION")

for index, row in high_g.iterrows():
    time_min = row["time_s"] / 60
    acceleration = row["vertical_acceleration_g"]

    print(f"High vertical acceleration at {time_min:.1f} min: {acceleration:.2f} g")
    
high_descent = flight[flight["vertical_speed_mps"]< -12]

print("\nHIGH DESCENT RATE")

for index, row in high_descent.iterrows():
    time_min = row["time_s"] / 60
    descent_rate = row["vertical_speed_mps"]

    print(f"High descent rate at {time_min:.1f} min: {descent_rate:.1f} m/s")
    
    
flight["flight_phase"] = "Cruise" # i use + or - 2 m/s because flight data can be a bit noisy even during cruising. leaving room for slight variation

flight.loc[flight["vertical_speed_mps"] > 2, "flight_phase"] = "Climb"
flight.loc[flight["vertical_speed_mps"] < -2, "flight_phase"] = "Descent"

flight["time_interval_min"] = flight["time_s"].diff().shift(-1) / 60


phase_duration = flight.groupby("flight_phase")["time_interval_min"].sum()

for phase, duration in phase_duration.items():
    print(f"{phase}: {duration:.0f} min")
    


time_min = flight["time_s"] / 60

fig, ax1 = plt.subplots()

ax1.plot(time_min, flight["altitude_m"])
ax1.set_xlabel("Time (min)")
ax1.set_ylabel("Altitude (m)")

ax2 = ax1.twinx()

ax2.plot(time_min, flight["airspeed_mps"])
ax2.set_ylabel("Airspeed (m/s)")


line1, = ax1.plot(
    time_min,
    flight["altitude_m"],
    color="blue",
    label="Altitude")
line2, = ax2.plot( time_min,
    flight["airspeed_mps"],
    color="red",
    label="Airspeed")
    
    
    
for index, row in high_roll.iterrows():
    x = row["time_s"] / 60
    ax1.axvline(x, linestyle="--")
    ax1.text(x, 8000, "High Bank", rotation=90)

for index, row in high_g.iterrows():
    x = row["time_s"] / 60
    ax1.axvline(x, linestyle="--")
    ax1.text(x, 8000, "High G", rotation=90)

for index, row in high_descent.iterrows():
    x = row["time_s"] / 60
    ax1.axvline(x, linestyle="--")
    ax1.text(x, 8000, "High Descent", rotation=90)
    
    
plt.title("Flight Profile")
plt.show()


fig, ax1 = plt.subplots()

line1, = ax1.plot(time_min, flight["pitch_deg"], label="Pitch", color="blue")
line2, = ax1.plot(time_min, flight["roll_deg"], label="Roll", color="green")

ax1.set_xlabel("Time (min)")
ax1.set_ylabel("Angle (deg)")

ax2 = ax1.twinx()

line3, = ax2.plot(
    time_min,
    flight["vertical_acceleration_g"],
    label="Vertical Acceleration",
    color="red"
)
ax2.set_ylabel("Vertical Acceleration (g)")

plt.title("Aircraft Attitude and Vertical Acceleration")

lines = [line1, line2, line3]
labels = [line.get_label() for line in lines]
ax1.legend(lines, labels, loc="upper right")



plt.title("Aircraft Attitude and Vertical Acceleration")
plt.show()

    
