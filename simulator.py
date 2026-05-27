import pandas as pd 
import numpy as np 
from datetime import datetime, timedelta
import random 


def build_state_schedule():
    schedule = [
        ("CHARGING", 60), # 5-sec steps 60*5s = 5 min
        ("NAVIGATING", 9),
        ("CLEANING", 60), 
        ("NAVIGATING", 9),
        ("CLEANING", 60), 
        ("NAVIGATING", 9),
        ("CLEANING", 60),
        ("RETURNING", 18), 
        ("CHARGING", 24),
    ]
    return schedule 

def expand_schedule(schedule): 
    states = []
    for (state, n_steps) in schedule:
        for _ in range(n_steps):
            states.append(state)
    return states

def generate_sensors(state, battery_pct, tank_level, motor_temp):
    sensors = {}

    if state == "CHARGING":
        battery_pct = min(100, battery_pct + 0.15)
    elif state == "CLEANING":
        battery_pct = max(0, battery_pct - 0.08)
    else: 
        battery_pct = max(0, battery_pct - 0.04)

    sensors["battery_pct"] = round(battery_pct + np.random.normal(0, 0.3), 2)

    if state == "CLEANING":
        sensors["brush_rpm"] = round(1000 + np.random.normal(0, 20))
        sensors["pump_pressure_bar"] = round(2.5 + np.random.normal(0, 0.05), 2)
        tank_level = max(0, tank_level - 0.025)
        motor_temp = min(75, motor_temp + 0.05)
    else:
        sensors["brush_rpm"] = 0
        sensors["pump_pressure_bar"] = 0.0
        motor_temp = max(30, motor_temp - 0.1)
    
    sensors["tank_level_L"] = round(tank_level + np.random.normal(0, 0.1), 2)
    sensors["motor_temp_C"] = round(motor_temp + np.random.normal(0, 0.5), 2)

    current_map = {
    "CHARGING":   2.0,
    "NAVIGATING": 8.0,  
    "CLEANING":   18.0,  
    "RETURNING":  7.0,
}
    base_current = current_map.get(state, 3.0)
    sensors["current_draw_A"] = round(base_current + np.random.normal(0,0.2), 2)

    return sensors, battery_pct, tank_level, motor_temp

def inject_fault(df, fault_type):
    df = df.copy()

    cleaning_idx = df[df["state"] == "CLEANING"].index.tolist()

    fault_start = cleaning_idx[int(len(cleaning_idx) * random.uniform(0.1, 0.8))]
    df.loc[fault_start:, "fault_type"] = fault_type
    
    fault_rows = df.index[df.index >= fault_start]

    if fault_type == "BRUSH_STALL":
        decay = 0
        for i in fault_rows:
            if df.at[i, "state"] == "CLEANING":
                decay += 15
                df.at[i, "brush_rpm"] = max(0, 1000 - decay)
                df.at[i, "current_draw_A"] = min(15, df.at[i, "current_draw_A"] + decay * 0.05)
    elif fault_type == "TANK_EMPTY":
        for i in fault_rows:
            df.at[i, "tank_level_L"] = 0.0
            if df.at[i, "state"] == "CLEANING":
                df.at[i, "pump_pressure_bar"] = 0.0
    elif fault_type == "MOTOR_OVERHEAT":
        extra = 0
        for i in fault_rows:
            if df.at[i, "state"] == "CLEANING":
                extra += 0.5
            df.at[i, "motor_temp_C"] = min(110, df.at[i, "motor_temp_C"] + extra)
    
    elif fault_type == "LOW_BATTERY":
        drain = 0
        for i in fault_rows:
            drain += 0.8
            new_val = max(0, df.at[i, "battery_pct"] - drain)
            df.at[i, "battery_pct"] = round(new_val, 2)

    elif fault_type == "PUMP_PRESSURE_LOSS":
        drop = 0
        for i in fault_rows:
            if df.at[i, "state"] == "CLEANING":
                drop += 0.02
                df.at[i, "pump_pressure_bar"] = max(0, 2.5 - drop)
    
    return df

def run_session(session_id, fault_type = None):
    schedule = build_state_schedule()

    states = expand_schedule(schedule)

    battery_pct = 85.0
    tank_level = 20.0
    motor_temp = 30.0 

    start_time = datetime(2026, 5, 1, 7, 0, 0)

    records = []

    #t is step number and state is what the bot is doing @ given step
    for t, state in enumerate(states):
        timestamp = start_time + timedelta(seconds = t*5)

        sensors, battery_pct, tank_level, motor_temp = generate_sensors(state, battery_pct, tank_level, motor_temp)

        record = {
            "session_id": session_id,
            "timestamp": timestamp,
            "state": state,
            "fault_type": None,
            **sensors
        }
        records.append(record)
    
    df = pd.DataFrame(records)

    if fault_type:
        df = inject_fault(df, fault_type)
    
    return df

def run_dynamic_session():
    schedule = build_state_schedule()
    states = expand_schedule(schedule)

    battery_pct = random.uniform(70, 95)
    tank_level  = random.uniform(15, 20)
    motor_temp  = random.uniform(28, 35)

    start_time = datetime.now()

    records = []

    for t, state in enumerate(states):
        timestamp = start_time + timedelta(seconds=t * 5)

        sensors, battery_pct, tank_level, motor_temp = generate_sensors(
            state, battery_pct, tank_level, motor_temp
        )

        record = {
            "session_id": 99,
            "timestamp":  timestamp,
            "state":      state,
            "fault_type": None,
            **sensors
        }
        records.append(record)

    df = pd.DataFrame(records)

    possible_faults = [
        ("BRUSH_STALL",        random.choice([0.1, 0.4, 0.8])),
        ("TANK_EMPTY",         random.choice([0.1, 0.5, 0.9])),
        ("MOTOR_OVERHEAT",     random.choice([0.1, 0.3, 0.8])),
        ("LOW_BATTERY",        random.choice([0.1, 0.4, 0.8])),
        ("PUMP_PRESSURE_LOSS", random.choice([0.1, 0.35, 0.8])),
    ]

    for fault_type, probability in possible_faults:
        if random.random() < probability:
            df = inject_fault(df, fault_type)

    return df

if __name__ == "__main__":
    sessions = [
        (1, None),
        (2, None),
        (3, None),
        (4, "BRUSH_STALL"),
        (5, "TANK_EMPTY"),
        (6, "MOTOR_OVERHEAT"),
        (7, "LOW_BATTERY"),
        (8, "PUMP_PRESSURE_LOSS"),
    ]

    all_sessions = []
    for session_id, fault_type in sessions:
        df = run_session(session_id, fault_type=fault_type)
        all_sessions.append(df)
        print(f"Session {session_id} done — {fault_type or 'CLEAN'}")

    full_dataset = pd.concat(all_sessions, ignore_index=True)
    full_dataset.to_csv("sunnybotics_telemetry.csv", index=False)
    print(f"\n✅ Saved! Total rows: {len(full_dataset)}")