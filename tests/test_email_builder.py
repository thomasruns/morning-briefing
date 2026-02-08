import pytest
from modules.email_builder import build_email_html, format_weather_data, format_calendar_events

def test_format_weather_data():
    """Test weather data formatting"""
    weather = {
        'temperature': 72.5,
        'temp_min': 65.0,
        'temp_max': 78.0,
        'condition': 'Clear',
        'description': 'clear sky'
    }

    formatted = format_weather_data(weather)

    assert formatted['weather_available'] == True
    assert formatted['temperature'] == 72  # Rounded from 72.5
    assert formatted['temp_min'] == 65
    assert formatted['temp_max'] == 78
    assert formatted['weather_icon'] in ['☀️', '🌧️', '⛅', '🌤️', '⛈️', '❄️', '🌫️']

def test_format_weather_data_none():
    """Test weather formatting when unavailable"""
    formatted = format_weather_data(None)
    assert formatted['weather_available'] == False

def test_format_calendar_events():
    """Test calendar events formatting"""
    events = [
        {
            'title': 'Meeting',
            'start_time': '2024-01-01T09:00:00Z',
            'end_time': '2024-01-01T10:00:00Z',
            'location': 'Office',
            'all_day': False
        }
    ]

    formatted = format_calendar_events(events)

    assert formatted['has_events'] == True
    assert len(formatted['events']) == 1
    assert formatted['events'][0]['title'] == 'Meeting'
