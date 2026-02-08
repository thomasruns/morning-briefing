import pytest
from unittest.mock import patch, Mock
from modules.weather import fetch_weather, WeatherError

def test_fetch_weather_success():
    """Test successful weather fetch"""
    mock_response = {
        'main': {
            'temp': 72.5,
            'temp_min': 65.0,
            'temp_max': 78.0
        },
        'weather': [
            {'main': 'Clear', 'description': 'clear sky'}
        ]
    }

    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        weather = fetch_weather('test_key', 'TestCity', 'US')

        assert weather['temperature'] == 72.5
        assert weather['temp_min'] == 65.0
        assert weather['temp_max'] == 78.0
        assert weather['condition'] == 'Clear'
        assert weather['description'] == 'clear sky'

def test_fetch_weather_api_error():
    """Test weather API error handling"""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 401

        with pytest.raises(WeatherError, match="Weather API error"):
            fetch_weather('invalid_key', 'TestCity', 'US')

def test_fetch_weather_timeout():
    """Test weather API timeout handling"""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("Connection timeout")

        with pytest.raises(WeatherError, match="Failed to fetch weather"):
            fetch_weather('test_key', 'TestCity', 'US')
