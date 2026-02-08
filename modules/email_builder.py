"""
Email Builder Module

Builds HTML email from weather, calendar, and news data using template rendering.
"""

import os
from datetime import datetime
from pathlib import Path


def get_weather_icon(condition):
    """
    Returns an emoji icon based on weather condition.

    Args:
        condition (str): Weather condition (e.g., 'Clear', 'Rain', 'Clouds')

    Returns:
        str: Weather emoji icon
    """
    condition_lower = condition.lower() if condition else ''

    icon_map = {
        'clear': '☀️',
        'rain': '🌧️',
        'drizzle': '🌧️',
        'clouds': '⛅',
        'cloud': '⛅',
        'partly': '🌤️',
        'thunderstorm': '⛈️',
        'snow': '❄️',
        'mist': '🌫️',
        'fog': '🌫️',
        'haze': '🌫️'
    }

    for key, icon in icon_map.items():
        if key in condition_lower:
            return icon

    return '🌤️'  # Default icon


def format_weather_data(weather):
    """
    Formats weather data for template rendering.

    Args:
        weather (dict or None): Weather data dictionary

    Returns:
        dict: Formatted weather data with weather_available flag
    """
    if weather is None:
        return {
            'weather_available': False
        }

    return {
        'weather_available': True,
        'weather_icon': get_weather_icon(weather.get('condition', '')),
        'temperature': round(weather.get('temperature', 0)),
        'temp_min': round(weather.get('temp_min', 0)),
        'temp_max': round(weather.get('temp_max', 0)),
        'condition': weather.get('condition'),
        'description': weather.get('description', '').capitalize()
    }


def format_hourly_forecast(hourly_forecast):
    """
    Formats hourly forecast data for template rendering.

    Args:
        hourly_forecast (list): List of hourly forecast dictionaries

    Returns:
        dict: Formatted hourly forecast with has_hourly_forecast flag
    """
    if not hourly_forecast or len(hourly_forecast) == 0:
        return {
            'has_hourly_forecast': False,
            'hourly': []
        }

    formatted_hourly = []
    for forecast in hourly_forecast:
        if forecast.get('temperature') is not None:
            formatted_hourly.append({
                'time': forecast['time'],
                'icon': get_weather_icon(forecast.get('condition', '')),
                'rain_chance': forecast.get('rain_chance', 0),
                'temperature': forecast['temperature']
            })

    return {
        'has_hourly_forecast': len(formatted_hourly) > 0,
        'hourly': formatted_hourly
    }


def format_time(time_str, all_day):
    """
    Formats time for display.

    Args:
        time_str (str): ISO format time string
        all_day (bool): Whether event is all-day

    Returns:
        str: Formatted time string
    """
    if all_day:
        return 'All Day'

    try:
        # Parse ISO format time
        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        return dt.strftime('%I:%M %p')
    except (ValueError, AttributeError):
        return time_str


def format_calendar_events(events):
    """
    Formats calendar events for template rendering.

    Args:
        events (list or None): List of calendar event dictionaries

    Returns:
        dict: Formatted events data with has_events flag
    """
    if not events:
        return {
            'has_events': False,
            'events': []
        }

    formatted_events = []
    for event in events:
        formatted_event = {
            'title': event.get('title', 'Untitled Event'),
            'time': format_time(event.get('start_time', ''), event.get('all_day', False)),
            'location': event.get('location', '')
        }
        formatted_events.append(formatted_event)

    return {
        'has_events': True,
        'events': formatted_events
    }


def format_articles(articles):
    """
    Formats news articles for template rendering.

    Args:
        articles (list or None): List of news article dictionaries

    Returns:
        dict: Formatted articles data with has_articles flag
    """
    if not articles:
        return {
            'has_articles': False,
            'articles': []
        }

    return {
        'has_articles': True,
        'articles': articles
    }


def simple_mustache_replace(template, data):
    """
    Simple Mustache-style template replacement.

    Handles:
    - {{variable}} - Simple variable replacement
    - {{#section}}...{{/section}} - Conditional sections (shown if truthy)
    - {{^section}}...{{/section}} - Inverted sections (shown if falsy)
    - Nested loops with {{#array}}...{{/array}}

    Args:
        template (str): Template string with Mustache variables
        data (dict): Data dictionary for replacement

    Returns:
        str: Rendered template
    """
    result = template

    # Handle inverted sections {{^var}}...{{/var}} (shown when falsy)
    import re
    inverted_pattern = r'\{\{\^([^}]+)\}\}(.*?)\{\{/\1\}\}'

    def replace_inverted(match):
        var_name = match.group(1)  # Variable name without ^
        content = match.group(2)
        value = data.get(var_name)
        # Show content if value is falsy
        if not value:
            return simple_mustache_replace(content, data)
        return ''

    result = re.sub(inverted_pattern, replace_inverted, result, flags=re.DOTALL)

    # Handle conditional sections {{#var}}...{{/var}}
    section_pattern = r'\{\{#([^}]+)\}\}(.*?)\{\{/\1\}\}'

    def replace_section(match):
        var_name = match.group(1)
        content = match.group(2)
        value = data.get(var_name)

        if isinstance(value, list):
            # Loop over list
            result_parts = []
            for item in value:
                # For each item, render the content with item data
                item_result = simple_mustache_replace(content, item)
                result_parts.append(item_result)
            return ''.join(result_parts)
        elif value:
            # Conditional - show if truthy
            return simple_mustache_replace(content, data)
        else:
            # Hide if falsy
            return ''

    result = re.sub(section_pattern, replace_section, result, flags=re.DOTALL)

    # Handle simple variable replacements {{var}}
    var_pattern = r'\{\{([^#^/][^}]*)\}\}'

    def replace_var(match):
        var_name = match.group(1)
        value = data.get(var_name, '')
        return str(value) if value is not None else ''

    result = re.sub(var_pattern, replace_var, result)

    return result


def build_email_html(weather, hourly_forecast, events, articles):
    """
    Builds complete HTML email from data.

    Args:
        weather (dict or None): Weather data
        hourly_forecast (list): Hourly forecast data
        events (list or None): Calendar events
        articles (list or None): News articles

    Returns:
        str: Rendered HTML email
    """
    # Load template
    template_path = Path(__file__).parent.parent / 'templates' / 'email_template.html'

    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # Get current date and time
    now = datetime.now()

    # Format all data
    formatted_weather = format_weather_data(weather)
    formatted_hourly = format_hourly_forecast(hourly_forecast)
    formatted_events = format_calendar_events(events)
    formatted_articles = format_articles(articles)

    # Combine all data
    template_data = {
        'date': now.strftime('%A, %B %d, %Y'),
        'time': now.strftime('%I:%M %p'),
        **formatted_weather,
        **formatted_hourly,
        **formatted_events,
        **formatted_articles
    }

    # Render template
    html = simple_mustache_replace(template, template_data)

    return html
