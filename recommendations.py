"""
Smart Recommendations Engine
Provides recommendations for:
- Smart Home AC (on/off, temperature setting)
- Smart Garden (watering yes/no, amount, sensor status)
- Farmer (field watering, outdoor work safety)
"""

import random
import math
from datetime import datetime

class RecommendationsEngine:
    def __init__(self):
        self.temp_comfort_min = 18
        self.temp_comfort_max = 26
        
    def get_smart_home_recommendation(self, weather_data):
        """
        Recommend AC on/off and temperature setting.
        """
        temp = float(weather_data.get('temperature', 0))
        humidity = float(weather_data.get('humidity', 0))
        weather = weather_data.get('weather', '').lower()
        
        ac_on = False
        ac_temp = 24  # default comfort temp
        reason = ""
        
        # AC ON logic
        if temp > 30:
            ac_on = True
            ac_temp = 22
            reason = f"High temperature ({temp}°C). AC on to maintain comfort."
        elif temp > 28:
            ac_on = True
            ac_temp = 24
            reason = f"Moderate temperature ({temp}°C). AC on for comfort."
        elif temp < 15:
            ac_on = False
            reason = f"Cold temperature ({temp}°C). AC off, use heating if needed."
        else:
            ac_on = False
            reason = f"Temperature {temp}°C is comfortable. AC off."
        
        # Adjust for humidity
        if humidity > 75:
            ac_temp = max(ac_temp - 1, 18)  # lower temp slightly if humid
            reason += " High humidity - reduced temp setting."
        
        return {
            "ac_on": ac_on,
            "ac_temperature": ac_temp,
            "reason": reason,
            "temperature": temp,
            "humidity": humidity
        }
    
    def get_smart_garden_recommendation(self, weather_data, device_type='home'):
        """
        Recommend garden watering.
        device_type: 'home' (small garden) or 'farm' (large field)
        """
        temp = float(weather_data.get('temperature', 0))
        humidity = float(weather_data.get('humidity', 0))
        rainfall = float(weather_data.get('rainfall', 0)) if 'rainfall' in weather_data else 0
        weather = weather_data.get('weather', '').lower()
        
        should_water = False
        water_amount = 0  # in liters per sqm
        reason = ""
        
        # Calculate soil moisture index (simplified)
        # High temp and low humidity = need water
        soil_dryness = ((35 - temp) / 35) * (1 - humidity / 100) if temp < 35 else 0
        
        if 'rain' in weather.lower():
            should_water = False
            water_amount = 0
            reason = "Rain detected. Skip watering, collect rainwater."
        elif temp > 32 and humidity < 40:
            should_water = True
            water_amount = 25 if device_type == 'home' else 50
            reason = f"Very hot ({temp}°C) and dry. Heavy watering needed."
        elif temp > 28 and humidity < 50:
            should_water = True
            water_amount = 15 if device_type == 'home' else 35
            reason = f"Hot ({temp}°C) and moderately dry. Water garden."
        elif temp > 24 and humidity < 60:
            should_water = True
            water_amount = 10 if device_type == 'home' else 20
            reason = f"Warm ({temp}°C). Light watering recommended."
        else:
            should_water = False
            water_amount = 0
            reason = f"Moderate conditions ({temp}°C, {humidity}% humidity). Skip watering."
        
        return {
            "should_water": should_water,
            "water_amount_per_sqm": water_amount,
            "unit": "liters",
            "reason": reason,
            "temperature": temp,
            "humidity": humidity,
            "rainfall": rainfall
        }
    
    def get_farmer_recommendation(self, weather_data):
        """
        Recommend farmer actions: field watering and outdoor work safety.
        """
        temp = float(weather_data.get('temperature', 0))
        humidity = float(weather_data.get('humidity', 0))
        weather = weather_data.get('weather', '').lower()
        wind_speed = float(weather_data.get('wind_speed', 0))
        
        field_water = False
        field_water_reason = ""
        can_work_outside = True
        work_safety_reason = ""
        
        # Field watering logic (larger scale than home garden)
        if 'rain' in weather.lower():
            field_water = False
            field_water_reason = "Rain detected. Field irrigation not needed."
        elif temp > 35 or humidity < 30:
            field_water = True
            field_water_reason = f"Extreme heat ({temp}°C) or very dry ({humidity}%). Irrigate field."
        elif temp > 30 and humidity < 45:
            field_water = True
            field_water_reason = f"Hot ({temp}°C) and dry conditions. Irrigate field."
        else:
            field_water = False
            field_water_reason = f"Conditions acceptable ({temp}°C). Hold irrigation."
        
        # Work safety logic
        if temp > 40:
            can_work_outside = False
            work_safety_reason = f"⚠️ Extreme heat ({temp}°C). DO NOT work outside. Risk of heat stroke."
        elif temp > 35:
            can_work_outside = True
            work_safety_reason = f"⚠️ High temperature ({temp}°C). Work early morning/late evening only. Stay hydrated."
        elif 'heavy rain' in weather.lower() or 'thunder' in weather.lower():
            can_work_outside = False
            work_safety_reason = "⚠️ Severe weather detected. Do not work outside for safety."
        elif 'rain' in weather.lower() and wind_speed > 5:
            can_work_outside = True
            work_safety_reason = "Rain + moderate wind. Work with caution. Wear rain gear."
        elif wind_speed > 8:
            can_work_outside = True
            work_safety_reason = f"Strong wind ({wind_speed} m/s). Be careful, secure any loose items."
        else:
            can_work_outside = True
            work_safety_reason = "✅ Good conditions for outdoor work."
        
        return {
            "should_irrigate_field": field_water,
            "irrigation_reason": field_water_reason,
            "can_work_outside": can_work_outside,
            "work_safety_reason": work_safety_reason,
            "temperature": temp,
            "humidity": humidity,
            "weather": weather,
            "wind_speed": wind_speed
        }
    
    def get_sensor_data(self, seed=None):
        """
        Simulate smart garden sensor data (binary: on/off per sensor).
        Returns dict with binary sensor states.
        """
        if seed is not None:
            random.seed(seed)
        
        # Sensors: soil_moisture, light, temperature, humidity, water_pump
        sensors = {
            "soil_moisture_sensor": random.choice([0, 1]),  # 1 = needs water, 0 = ok
            "light_sensor": random.choice([0, 1]),  # 1 = detecting light, 0 = dark
            "temperature_sensor": random.choice([0, 1]),  # 1 = high temp alert, 0 = ok
            "humidity_sensor": random.choice([0, 1]),  # 1 = high humidity, 0 = ok
            "water_pump_status": random.choice([0, 1]),  # 1 = on, 0 = off
        }
        
        # Logic: pump should be on if soil needs water AND not raining
        if sensors['soil_moisture_sensor'] == 1 and sensors['light_sensor'] == 1:
            sensors['water_pump_status'] = 1
        else:
            sensors['water_pump_status'] = 0
        
        return sensors

    # --- Weather helpers ---
    def _clamp(self, val, lo, hi):
        try:
            v = float(val)
        except Exception:
            return None
        return max(lo, min(hi, v))

    def compute_dew_point(self, temp_c, rh):
        # Magnus formula
        a = 17.27
        b = 237.7
        try:
            alpha = (a * temp_c) / (b + temp_c) + (math.log(rh / 100.0))
            dp = (b * alpha) / (a - alpha)
            return dp
        except Exception:
            return None

    def compute_heat_index(self, temp_c, rh):
        # approximate via conversion to Fahrenheit and NOAA formula
        try:
            t_f = temp_c * 9.0/5.0 + 32.0
            rh_f = rh
            # NOAA heat index coefficients
            hi = -42.379 + 2.04901523*t_f + 10.14333127*rh_f - 0.22475541*t_f*rh_f - 6.83783*(10**-3)*(t_f**2) - 5.481717*(10**-2)*(rh_f**2) + 1.22874*(10**-3)*(t_f**2)*rh_f + 8.5282*(10**-4)*t_f*(rh_f**2) - 1.99*(10**-6)*(t_f**2)*(rh_f**2)
            # adjust
            if rh_f < 13 and (80 <= t_f <= 112):
                adj = ((13 - rh_f)/4)*math.sqrt((17 - abs(t_f-95.))/17)
                hi -= adj
            elif rh_f > 85 and (80 <= t_f <= 87):
                adj = ((rh_f - 85)/10) * ((87 - t_f)/5)
                hi += adj
            # convert back to C
            hi_c = (hi - 32) * 5.0/9.0
            return hi_c
        except Exception:
            return None


def get_all_recommendations(weather_data):
    """Convenience function to get all recommendations at once."""
    engine = RecommendationsEngine()
    # Normalize and compute derived weather metrics
    temp = engine._clamp(weather_data.get('temperature', None), -50, 60)
    humidity = engine._clamp(weather_data.get('humidity', None), 0, 100)
    feels_like = None
    try:
        feels_like = float(weather_data.get('feels_like'))
    except Exception:
        feels_like = None

    dew_point = None
    heat_index = None
    if temp is not None and humidity is not None:
        dew_point = engine.compute_dew_point(temp, humidity)
        heat_index = engine.compute_heat_index(temp, humidity)

    normalized = {
        'temperature': temp,
        'humidity': humidity,
        'feels_like': feels_like,
        'dew_point': round(dew_point, 2) if dew_point is not None else None,
        'heat_index': round(heat_index, 2) if heat_index is not None else None,
        'weather': weather_data.get('weather'),
        'wind_speed': weather_data.get('wind_speed', 0),
        'rainfall': weather_data.get('rainfall', 0),
        'pressure': weather_data.get('pressure')
    }

    # Use normalized weather for recommendations
    smart_home = engine.get_smart_home_recommendation(normalized)
    smart_garden = engine.get_smart_garden_recommendation(normalized, device_type='home')
    farmer = engine.get_farmer_recommendation(normalized)
    sensors = engine.get_sensor_data()

    return {
        "timestamp": datetime.now().isoformat(),
        "weather": normalized,
        "smart_home": smart_home,
        "smart_garden": smart_garden,
        "farmer": farmer,
        "sensors": sensors
    }


if __name__ == "__main__":
    # Test example
    test_weather = {
        'temperature': 32.5,
        'humidity': 45,
        'weather': 'Sunny',
        'wind_speed': 3.2,
        'rainfall': 0
    }
    
    recommendations = get_all_recommendations(test_weather)
    
    print("\n🏠 SMART HOME RECOMMENDATION:")
    print(recommendations['smart_home'])
    
    print("\n🌱 SMART GARDEN RECOMMENDATION:")
    print(recommendations['smart_garden'])
    
    print("\n👨‍🌾 FARMER RECOMMENDATION:")
    print(recommendations['farmer'])
    
    print("\n📡 GARDEN SENSORS (BINARY):")
    for sensor, status in recommendations['sensors'].items():
        print(f"  {sensor}: {'ON' if status else 'OFF'}")
