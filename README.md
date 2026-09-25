# Aircraft Flight Data Analysis

Python project for analysing generated and  A320  example flight trajectory data.

## Features

- Generates synthetic aircraft telemetry
- Reads and analyses CSV flight data
- Converts aviation units to SI units
- Detects climb, cruise, level, descent, and ground phases
- Calculates flight duration, maximum altitude, speed, climb rate, and descent rate
- Integrates fuel flow to estimate total fuel consumption
- Validates fuel consumption against recorded aircraft mass change
- Detects high vertical-rate events
- Produces flight-profile and fuel-flow visualisations

## Project Structure

```text
Aircraft_Flight_Data_Analysis/
├── generate_full_flight.py
├── analyse_generated_flight.py
├── analyse_real_flight.py
├── requirements.txt
├── README.md
└── results/
    ├── real_flight_profile.png
    └── fuel_flow.png
    
    ## Data Source

The real-flight analysis uses an A320 example trajectory dataset from the DGAC Acropole project.

The dataset contains recorded/simulated flight parameters including altitude, ground speed, vertical speed, aircraft mass and fuel flow.

## Assumptions

- Flight phases are identified using heuristic thresholds based on vertical speed, altitude and ground speed.
- Cruise is defined as approximately level flight at more than 80% of the maximum recorded altitude.
- Ground operation is identified using low ground speed and altitude close to the initial airport elevation.
- High vertical-rate events are detected using configurable thresholds rather than aircraft-specific operational limits.
- Fuel-flow values are treated as per-engine values for this A320 dataset and multiplied by two. This interpretation is supported by the close agreement between integrated fuel burn and recorded aircraft mass loss.

## Limitations

- The flight-phase classifier is intentionally simple and is not intended to replace certified flight-data analysis software.
- Phase thresholds may need adjustment for different aircraft types or operating conditions.
- The current real-data analyser is designed around the column structure of the example A320 dataset.
- Roll angle, pitch angle and load-factor analysis are not performed on the real dataset because those parameters are not available in the selected data.
- Detected high vertical-rate events should be interpreted as threshold exceedances, not automatically as unsafe flight conditions.
- The analyser currently processes one flight at a time.

## Validation

Fuel consumption is calculated by integrating fuel flow over the recorded time intervals.

For the analysed A320 trajectory:

- Calculated post-takeoff fuel burn: 5,738 kg
- Recorded aircraft mass reduction: 5,701 kg
- Difference: 36 kg
- Percentage difference: 0.6%

This comparison provides an independent consistency check on the fuel-consumption calculation.