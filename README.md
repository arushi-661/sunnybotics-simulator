Sunnybotics Robot Health Simulator
A virtual health monitoring system simulator for a solar panel cleaning robot.

This project simulates a cleaning robot operating a full field session and monitors its health in real time. Every run is different — the robot may encounter a brush stall, an overheating motor, a depleted water tank, low battery, or pump pressure loss, or it may complete the session cleanly. Faults are detected automatically and surfaced as alerts on a live dashboard.

Files
1. simulator.py — generates robot telemetry data, models 5 operating states, and injects faults randomly
2. fault_detection.py — 5 rule-based fault detection checks that run on the telemetry data
3. dashboard.py — live Streamlit dashboard that animates the session and fires alerts in real time
4. telemetry csv - engineered telemetry data for the simulator

How To Run
1. Install dependencies:
   pip3 install pandas numpy streamlit plotly
2. Generate the dataset:
   python3 simulator.py
3. Launch the dashboard:
   python3 -m streamlit run dashboard.py

Then press RUN NEW SIMULATION in the browser. Each run is randomized and generates different fault combinations.


Robot Specs

Based on the Sunnybotics technical datasheet:

Supply voltage: 24V
Battery output: 30A max        
Autonomy per cycle: 4.5 hours       
Cleaning efficiency: 875 m²/h       
Water system: 10 active sprinklers at 3 bar     
Traction: Vulcanized rubber tracks

Faults Detected
Brush Stall: RPM drops below 200 while current exceeds 20A
Water Tank Empty: Tank level drops below 1L during cleaning                        
Motor Overheat: Motor temperature exceeds 80°C         
Low Pump Pressure: Pressure drops below 1 bar with water still in tank     
Low Battery: Battery drops below 20% while not charging
