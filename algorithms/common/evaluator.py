def _as_float(row, key, default=0.0):
    try:
        return float(row.get(key, default))
    except (TypeError, ValueError):
        return float(default)


ACTIONS = [
    {"name": "balanced", "e": 1.00, "w": 1.00, "g": 1.00, "irrigation_shift": 0.00},
    {"name": "eco", "e": 0.88, "w": 0.85, "g": 0.93, "irrigation_shift": -0.20},
    {"name": "comfort", "e": 1.08, "w": 1.02, "g": 1.04, "irrigation_shift": 0.05},
    {"name": "farm_priority", "e": 1.03, "w": 1.10, "g": 0.99, "irrigation_shift": 0.20},
    {"name": "rain_mode", "e": 0.94, "w": 0.75, "g": 0.95, "irrigation_shift": -0.40},
]


def evaluate_action(row, action):
    # Unit prices in Bangladeshi Taka (৳).
    c_grid = 8.5
    c_water = 2.5
    c_gas = 3.2

    e = _as_float(row, "electricity_consumption_kwh", _as_float(row, "electricity_consumption"))
    w = _as_float(row, "water_consumption_m3", _as_float(row, "water_consumption"))
    g = _as_float(row, "gas_consumption_m3", _as_float(row, "gas_consumption"))
    rain = _as_float(row, "rainfall_mm", _as_float(row, "rainfall"))
    temp = _as_float(row, "temperature_c", _as_float(row, "temperature"))
    humidity = _as_float(row, "humidity_percent", _as_float(row, "humidity"))
    irrigation = _as_float(row, "irrigation_demand_level", _as_float(row, "irrigation_demand"))
    renewable = _as_float(row, "renewable_energy_kwh", _as_float(row, "renewable_energy_production"))

    adj_e = max(0.1, e * action["e"])
    adj_w = max(0.05, w * action["w"])
    adj_g = max(0.05, g * action["g"])
    adj_irrigation = max(0.0, irrigation + action["irrigation_shift"])

    cost = (c_grid * adj_e) + (c_water * adj_w) + (c_gas * adj_g)

    penalty = 0.0
    if rain > 0.6 and action["irrigation_shift"] > 0:
        penalty += 7.5
    if temp > 36 and action["name"] == "eco":
        penalty += 4.0
    if humidity > 88 and action["name"] == "comfort":
        penalty += 1.2
    if renewable > 10 and action["name"] == "balanced":
        penalty += 0.8

    irrigation_on = 1 if adj_irrigation > 2.0 and rain < 0.8 else 0
    outdoor_risk = 1 if (rain > 8.0 or temp + (0.08 * humidity) > 41) else 0
    efficiency = renewable / max(0.1, (adj_e + adj_w + adj_g))

    return {
        "objective": cost + penalty,
        "cost": cost,
        "efficiency": efficiency,
        "irrigation_on": irrigation_on,
        "outdoor_risk": outdoor_risk,
    }
