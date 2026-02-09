import requests
import time
from datetime import datetime, timedelta


class WeatherError(Exception):
    """Custom exception for weather-related errors"""
    pass


def fetch_weather(api_key, city, country_code, max_retries=3):
    """
    Fetch current weather data from OpenWeatherMap API.

    Args:
        api_key (str): OpenWeatherMap API key
        city (str): City name
        country_code (str): Country code (e.g., 'US')
        max_retries (int): Maximum number of retry attempts

    Returns:
        dict: Weather data with temperature, temp_min, temp_max, condition, description

    Raises:
        WeatherError: If weather fetch fails after retries
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': f"{city},{country_code}",
        'appid': api_key,
        'units': 'imperial'
    }

    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                try:
                    return {
                        'temperature': data['main']['temp'],
                        'temp_min': data['main']['temp_min'],
                        'temp_max': data['main']['temp_max'],
                        'condition': data['weather'][0]['main'],
                        'description': data['weather'][0]['description']
                    }
                except KeyError as e:
                    raise WeatherError(f"Malformed API response: missing expected field {str(e)}")
            elif response.status_code == 401:
                raise WeatherError("Weather API error: Invalid API key")
            else:
                raise WeatherError(f"Weather API error: Status code {response.status_code}")

        except WeatherError:
            # Re-raise WeatherError without retry
            raise
        except Exception as e:
            # Retry on timeout or other exceptions
            if attempt < max_retries - 1:
                backoff_time = 2 ** attempt
                time.sleep(backoff_time)
            else:
                raise WeatherError(f"Failed to fetch weather: {str(e)}")

    raise WeatherError("Failed to fetch weather after maximum retries")


def fetch_hourly_forecast(api_key, city, country_code, max_retries=3):
    """
    Fetch hourly weather forecast from OpenWeatherMap API.
    Returns next 4 available forecast times (approximately 3-hour intervals).

    Args:
        api_key (str): OpenWeatherMap API key
        city (str): City name
        country_code (str): Country code (e.g., 'US')
        max_retries (int): Maximum number of retry attempts

    Returns:
        list: List of next 4 hourly forecasts with time, temp, rain_chance, condition, icon

    Raises:
        WeatherError: If forecast fetch fails
    """
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        'q': f"{city},{country_code}",
        'appid': api_key,
        'units': 'imperial',
        'cnt': 40  # Get enough data points
    }

    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Get the next 4 forecast periods (3-hour intervals)
                hourly_forecasts = []

                for entry in data['list'][:4]:  # Get first 4 forecast entries
                    forecast_dt = datetime.fromtimestamp(entry['dt'])
                    rain_chance = int(entry.get('pop', 0) * 100)  # Probability of precipitation

                    hourly_forecasts.append({
                        'time': forecast_dt.strftime('%I%p').lstrip('0'),  # "12PM", "3PM"
                        'hour': forecast_dt.hour,
                        'temperature': round(entry['main']['temp']),
                        'rain_chance': rain_chance,
                        'condition': entry['weather'][0]['main'],
                        'icon': entry['weather'][0]['icon']
                    })

                return hourly_forecasts

            elif response.status_code == 401:
                raise WeatherError("Weather API error: Invalid API key")
            else:
                raise WeatherError(f"Forecast API error: Status code {response.status_code}")

        except WeatherError:
            raise
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise WeatherError(f"Failed to fetch forecast: {str(e)}")

    raise WeatherError("Failed to fetch forecast after maximum retries")
