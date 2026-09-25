import pandas as pd
import matplotlib.pyplot as plt
import os
from matplotlib.lines import Line2D
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
# CSV PATH 
flight = pd.read_csv(BASE_DIR / "data" / "a320_example_flight.csv.csv")


# Flight-phase thresholds
CLIMB_THRESHOLD = 2.0
DESCENT_THRESHOLD = -2.0

# High vertical-rate event thresholds
HIGH_CLIMB_THRESHOLD = 15.0
HIGH_DESCENT_THRESHOLD = -15.0

#  A320 has two engines so fuel rate multipilied by 2
ENGINE_COUNT = 2

os.makedirs("results", exist_ok=True)




# ============================================================
# CSV DATA RENAMED
# ============================================================

flight = flight.rename(columns={
    "FLIGHT_TIME": "time_s",
    "ALTI_STD_FT": "altitude_ft",
    "GRND_SPD_KT": "ground_speed_kt",
    "VERT_SPD_FTMN": "vertical_speed_ftmin",
    "FUEL_FLOW_KGH": "fuel_flow_kgh",
    "MASS_KG": "mass_kg"})


# ============================================================
# SI CONVERSION
# ============================================================

# Feet -> metres
flight["altitude_m"] = (flight["altitude_ft"] * 0.3048)

# Knots -> metres per second
flight["ground_speed_mps"] = (flight["ground_speed_kt"] * 0.514444)

# Feet per minute -> metres per second
flight["vertical_speed_mps"] = (
    flight["vertical_speed_ftmin"]
    * 0.3048
    / 60)

# Seconds -> minutes
flight["time_min"] = (flight["time_s"] / 60)


# ============================================================
# DATA CHECK FOR MISSING CSV VALUES AND ORDERING
# =========================================================

print("\nDATA CHECK")
print("-------------------------")

print(
    f"Missing values: "
    f"{flight.isnull().sum().sum()}")

print(
    f"Time ordered correctly: "
    f"{flight['time_s'].is_monotonic_increasing}")


# ============================================================
#  FLIGHT SUMMARY
# ============================================================

flight_duration = ( flight["time_s"].max() - flight["time_s"].min()) / 60

max_altitude = (flight["altitude_m"].max())

max_ground_speed = (flight["ground_speed_mps"].max())

max_climb_rate = (flight["vertical_speed_mps"].max())

max_descent_rate = ( flight["vertical_speed_mps"].min())


print("\nFLIGHT SUMMARY")
print("-------------------------")

print(f"Flight duration: "
    f"{flight_duration:.1f} min")

print(f"Maximum altitude: "
    f"{max_altitude:.0f} m")

print( f"Maximum ground speed: "
    f"{max_ground_speed:.1f} m/s")

print( f"Maximum climb rate: "
    f"{max_climb_rate:.1f} m/s")

print(f"Maximum descent rate: "
    f"{max_descent_rate:.1f} m/s")


ground_altitude = (
    flight["altitude_ft"].iloc[0])


# ============================================================
# FLIGHT PHASE 
# ============================================================

#  "Level" by default
flight["flight_phase"] = "Level"


# Climb
flight.loc[flight["vertical_speed_mps"] > CLIMB_THRESHOLD,
    "flight_phase"] = "Climb"


# Descent
flight.loc[flight["vertical_speed_mps"] < DESCENT_THRESHOLD,
    "flight_phase"] = "Descent"


# Cruise:
# almost level AND above 80% of maximum altitude
flight.loc[(flight["vertical_speed_mps"].abs() <= 2) &
    (flight["altitude_m"] > 0.8 * max_altitude),
    "flight_phase"] = "Cruise"


# Ground:
# slow AND close to initial altitude
flight.loc[(flight["ground_speed_kt"] < 40) &
    (
        flight["altitude_ft"]
        < ground_altitude + 100
    ),
    "flight_phase"
] = "Ground"


# ============================================================
# TIME INTERVALS
# ============================================================

flight["time_interval_s"] = (
    flight["time_s"].shift(-1)
    - flight["time_s"])


# ============================================================
#  FLIGHT PHASE DURATIONS
# ============================================================

phase_duration = (flight
    .groupby("flight_phase")["time_interval_s"]
    .sum()
    / 60)


print("\nFLIGHT PHASE DURATIONS")
print("-------------------------")

for phase, duration in phase_duration.items():

    print( f"{phase}: {duration:.1f} min" )


# ============================================================
# FUEL CONSUMPTION
# ============================================================

flight["fuel_used_kg"] = (
    flight["fuel_flow_kgh"]
    * flight["time_interval_s"]
    / 3600)

total_fuel = (
    flight["fuel_used_kg"].sum()
    * ENGINE_COUNT)

print( f"Total fuel consumed: "
    f"{total_fuel:.0f} kg")


# ============================================================
 # TAKEOFF DETECTION
# ============================================================

airborne = flight[
    (flight["ground_speed_kt"] > 100) &
    ( flight["altitude_ft"]
        > ground_altitude + 100)]

takeoff_index = ( airborne.index[0])

# ============================================================
# FUEL and Mass VALIDATION
# ============================================================

takeoff_mass = ( flight.loc[
        takeoff_index,
        "mass_kg"])

ending_mass = (flight["mass_kg"].iloc[-1])

mass_loss = (takeoff_mass
    - ending_mass)


fuel_after_takeoff = (
    flight.loc[
        takeoff_index:,
        "fuel_used_kg"
    ].sum()
    * ENGINE_COUNT)


difference = abs(
    fuel_after_takeoff
    - mass_loss
)

percentage_difference = (
    difference
    / mass_loss
) * 100


print("\nFUEL VALIDATION")
print("-------------------------")

print(
    f"Takeoff mass: "
    f"{takeoff_mass:.0f} kg"
)

print(
    f"Ending mass: "
    f"{ending_mass:.0f} kg"
)

print(
    f"Fuel consumed after takeoff: "
    f"{fuel_after_takeoff:.0f} kg"
)

print(
    f"Mass loss after takeoff: "
    f"{mass_loss:.0f} kg"
)

print(
    f"Difference: "
    f"{difference:.0f} kg"
)

print(
    f"Percentage difference: "
    f"{percentage_difference:.1f}%"
)


# ============================================================
# VERTICAL-RATE EVENT CLASSIFICATION
# ============================================================

flight["vertical_event"] = "Normal"


flight.loc[
    (flight["vertical_speed_mps"]
        > HIGH_CLIMB_THRESHOLD ),
    "vertical_event"] = "High Climb"


flight.loc[
    (
        flight["vertical_speed_mps"]
        < HIGH_DESCENT_THRESHOLD
    ),
    "vertical_event"
] = "High Descent"


event_counts = (
    flight["vertical_event"].value_counts()
)


print("\nVERTICAL RATE POINTS")
print("-------------------------")

print(event_counts)


# ============================================================
#   CONSECUTIVE EVENT POINTS
# ============================================================

event_change = (
    flight["vertical_event"]
    != flight["vertical_event"].shift()
)

flight["event_group"] = (
    event_change.cumsum()
)


print("\nHIGH VERTICAL-RATE EVENTS")
print("-------------------------")

for _, group in flight.groupby("event_group"):

    event_type = (
        group["vertical_event"].iloc[0]
    )

    if event_type != "Normal":

        start_time = (
            group["time_min"].iloc[0]
        )

        end_time = (
            group["time_min"].iloc[-1]
        )


        if event_type == "High Climb":

            peak_rate = (
                group["vertical_speed_mps"].max()
            )

        else:

            peak_rate = (
                group["vertical_speed_mps"].min()
            )


        print(
            f"{event_type}: "
            f"{start_time:.2f} - {end_time:.2f} min, "
            f"peak rate = {peak_rate:.1f} m/s"
        )

# ============================================================
# FLIGHT PROFILE GRAPH
# ============================================================

fig, ax1 = plt.subplots(figsize=(10, 6))


# Altitude
line1, = ax1.plot(
    flight["time_min"],
    flight["altitude_m"],
    color="blue",
    label="Altitude"
)

ax1.set_xlabel("Time (min)")
ax1.set_ylabel("Altitude (m)")


# Second y-axis for ground speed
ax2 = ax1.twinx()

line2, = ax2.plot(
    flight["time_min"],
    flight["ground_speed_mps"],
    color="orange",
    label="Ground Speed"
)

ax2.set_ylabel("Ground Speed (m/s)")


# ============================================================
# SHADE CONTINUOUS FLIGHT PHASES
# ============================================================

phase_group = (
    flight["flight_phase"]
    != flight["flight_phase"].shift()
).cumsum()


for _, group in flight.groupby(phase_group):

    phase = group["flight_phase"].iloc[0]

    start = group["time_min"].iloc[0]
    end = group["time_min"].iloc[-1]

    if phase == "Climb":

        ax1.axvspan(
            start,
            end,
            color="green",
            alpha=0.10
        )

    elif phase == "Cruise":

        ax1.axvspan(
            start,
            end,
            color="blue",
            alpha=0.06
        )

    elif phase == "Descent":

        ax1.axvspan(
            start,
            end,
            color="red",
            alpha=0.10
        )


# ============================================================
# MARK HIGH VERTICAL-RATE EVENTS
# ============================================================

for _, group in flight.groupby("event_group"):

    event_type = group["vertical_event"].iloc[0]

    if event_type != "Normal":

        start_time = group["time_min"].iloc[0]
        end_time = group["time_min"].iloc[-1]

        event_time = (
            start_time + end_time
        ) / 2

        if event_type == "High Climb":

            ax1.axvline(
                event_time,
                color="green",
                linestyle="--",
                linewidth=1.2
            )

        elif event_type == "High Descent":

            ax1.axvline(
                event_time,
                color="red",
                linestyle="--",
                linewidth=1.2
            )


# ============================================================
# LEGEND
# ============================================================

high_climb_legend = Line2D(
    [0],
    [0],
    color="green",
    linestyle="--",
    label="High Climb"
)

high_descent_legend = Line2D(
    [0],
    [0],
    color="red",
    linestyle="--",
    label="High Descent"
)


legend_items = [
    line1,
    line2,
    high_climb_legend,
    high_descent_legend
]


ax1.legend(
    handles=legend_items,
    loc="upper right"
)


# ============================================================
# TITLE AND SAVE FLIGHT PROFILE
# ============================================================

ax1.set_title(
    "A320 Real Flight Profile"
)

fig.tight_layout()

fig.savefig(
    "results/real_flight_profile.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# FUEL FLOW GRAPH
# ============================================================

fig2, ax3 = plt.subplots(figsize=(10, 6))


ax3.plot(
    flight["time_min"],
    flight["fuel_flow_kgh"] * ENGINE_COUNT,
    color="purple"
)


ax3.set_xlabel(
    "Time (min)"
)

ax3.set_ylabel(
    "Total Fuel Flow (kg/h)"
)

ax3.set_title(
    "A320 Fuel Flow"
)


fig2.tight_layout()


fig2.savefig(
    "results/fuel_flow.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()