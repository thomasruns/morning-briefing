import pytest
from unittest.mock import patch, Mock, MagicMock
from modules.calendar_events import fetch_calendar_events, CalendarError
from datetime import datetime

def test_fetch_calendar_events_success():
    """Test successful calendar event fetching"""
    mock_service = MagicMock()
    mock_events = {
        'items': [
            {
                'summary': 'Team Meeting',
                'start': {'dateTime': '2024-01-01T09:00:00Z'},
                'end': {'dateTime': '2024-01-01T10:00:00Z'},
                'location': 'Conference Room'
            },
            {
                'summary': 'Lunch',
                'start': {'date': '2024-01-01'},
                'end': {'date': '2024-01-01'}
            }
        ]
    }

    mock_service.events().list().execute.return_value = mock_events

    with patch('modules.calendar_events.authenticate_google_calendar', return_value=mock_service):
        events = fetch_calendar_events('credentials.json')

        assert len(events) == 2
        assert events[0]['title'] == 'Team Meeting'
        assert events[0]['location'] == 'Conference Room'

def test_fetch_calendar_events_no_events():
    """Test when no events are scheduled"""
    mock_service = MagicMock()
    mock_events = {'items': []}
    mock_service.events().list().execute.return_value = mock_events

    with patch('modules.calendar_events.authenticate_google_calendar', return_value=mock_service):
        events = fetch_calendar_events('credentials.json')
        assert len(events) == 0
