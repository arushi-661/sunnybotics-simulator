import pandas as pd

def detect_faults(df):
    df = df.copy()
    df["alert"] = None

    brush_stall = (
        (df["state"] == "CLEANING") &
        (df["brush_rpm"] < 200) &
        (df["current_draw_A"] > 10)
    )
    df.loc[brush_stall, "alert"] = "BRUSH STALL"

    tank_empty = (
        (df["state"] == "CLEANING") &
        (df["tank_level_L"] < 1.0)
    )
    df.loc[tank_empty, "alert"] = "WATER TANK EMPTY"

    overheat = (df["motor_temp_C"] > 80)
    df.loc[overheat, "alert"] = "MOTOR OVERHEAT"

    pressure_loss = (
        (df["state"] == "CLEANING") &
        (df["pump_pressure_bar"] < 1.0) &
        (df["tank_level_L"] > 1.0)
    )
    df.loc[pressure_loss, "alert"] = "LOW PUMP PRESSURE"
    
    low_battery = (
        (df["state"] != "CHARGING") & 
        (df["battery_pct"] < 20)
    )

    df.loc[low_battery, "alert"] = "LOW BATTERY"
    
    
    return df

if __name__ == "__main__":
    df = pd.read_csv("sunnybotics_telemetry.csv")
    df = detect_faults(df)

    alerts = df[df["alert"].notna()]
    print(f"Total alerts fired: {len(alerts)}")
    print()
    print(alerts.groupby("alert").size())