import numpy as np
import pandas as pd



# TIME : 1-hour flight, data point each minute
time = np.arange(0,3601,60)


# ALTITUDE : assumptions include 1 hour flight, cruising altitude at 9000 m

altitude = np.zeros(len(time))
for i, t in enumerate(time):
    if t <= 600: 
        altitude[i] = t * 15 #climb phase 

    elif t <= 2700:
        altitude[i] = 9000 #cruise phase

    else:
        altitude[i] = 9000 - (t - 2700) * 10 #descent phase
        
print(altitude)

# AIRSPEED : 
    
airspeed = np.zeros(len(time))

for i, t in enumerate(time):
    if t <= 600:
        airspeed[i] = 70 + t * 0.2

    elif t <= 2700:
        airspeed[i] = 230

    else:
        airspeed[i] = 230 - (t - 2700) * 0.15




# PITCH : 
pitch = np.zeros(len(time))


for i, t in enumerate(time):
    if t <= 600:
        pitch[i] = 8

    elif t <= 2700:
        pitch[i] = 2

    else:
        pitch[i] = -3
        
        
        
        
# ROLL :
roll = np.zeros(len(time))


for i, t in enumerate(time):
    if t < 1200:
        roll[i] = 0

    elif t < 1260:
        roll[i] = 15

    else:
        roll[i] = 0
    
roll[40] = 45 # excessive degree of roll to test bank anomaly function at 40 mins
    
# VERTICAL SPEED:

vertical_speed = np.gradient(altitude,time)

vertical_speed[50]= -12.5 #testing a high descent rate on 50th minute to test high decent anomaly

# VERTICAL ACCELERATION:

vertical_acceleration = np.ones(len(time))

vertical_acceleration[30] = 1.7 # measured in g so 1.7g at minute 30 is an anomaly (inserted on purpose to test this functon). 

# FUEL FLOW

fuel_flowrate = np.zeros(len(time))

for i, t in enumerate(time):
    if t <= 600:
        fuel_flowrate[i] = 1.4 # ofc because take off consums most fue;

    elif t <= 2700:
        fuel_flowrate[i] = 0.9

    else:
        fuel_flowrate[i] = 0.5
    
        fuel_consumed = fuel_flowrate*60
        total_fuel = fuel_consumed.sum()

print(f"Total fuel consumed: {total_fuel:.1f} kg")
        





#FLIGHT TELEMETRY TABLE 


flight = pd.DataFrame({ "time_s": time,
    "altitude_m": altitude,
    "airspeed_mps": airspeed,
    "vertical_speed_mps": vertical_speed,
    "vertical_acceleration_g": vertical_acceleration,
    "pitch_deg": pitch,
    "roll_deg": roll,
    "fuel_flowrate_kgps": fuel_flowrate})

flight.to_csv("data/full_flight_data.csv", index=False)
print("Full flight data saved.")

print(flight)


        