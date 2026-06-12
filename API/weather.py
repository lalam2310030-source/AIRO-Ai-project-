import requests

api_key = "b58af70641f0e1c2f2ff6c37b2dbb6d5"
city = "Dhaka"

def get_weather_data():
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        response = requests.get(weather_url)
        weather_data = response.json()

        if response.status_code == 200:
            return {
                'city': weather_data["name"],
                'country': weather_data["sys"]["country"],
                'temperature': weather_data["main"]["temp"],
                'feels_like': weather_data["main"]["feels_like"],
                'humidity': weather_data["main"]["humidity"],
                'pressure': weather_data["main"]["pressure"],
                'weather': weather_data["weather"][0]["main"],
                'description': weather_data["weather"][0]["description"],
                'wind_speed': weather_data["wind"]["speed"]
            }
        else:
            print("Unable to get weather data.")
            print("Reason:", weather_data.get("message"))
            return None

    except Exception as error:
        print("An error occurred while fetching weather data:")
        print(error)
        return None
