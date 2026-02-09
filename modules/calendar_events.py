"""Google Calendar integration module for fetching today's events."""

import os
import pickle
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


class CalendarError(Exception):
    """Custom exception for calendar-related errors."""
    pass


def authenticate_google_calendar(credentials_file='credentials.json'):
    """
    Authenticate with Google Calendar API using OAuth 2.0.

    Args:
        credentials_file (str): Path to the credentials JSON file.

    Returns:
        service: Authenticated Google Calendar service object.

    Raises:
        CalendarError: If authentication fails.
    """
    creds = None
    token_file = 'token.pickle'

    # Load token.pickle if it exists
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    # If credentials are invalid or don't exist, refresh or authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh expired credentials
            try:
                creds.refresh(Request())
            except Exception as e:
                raise CalendarError(f"Failed to refresh credentials: {e}")
        else:
            # Run OAuth flow for new credentials
            if not os.path.exists(credentials_file):
                raise CalendarError(f"Credentials file not found: {credentials_file}")

            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, SCOPES)
                # Use run_console() for headless server environments
                # This will print a URL that you visit in a browser, then paste the auth code back
                creds = flow.run_console()
            except Exception as e:
                raise CalendarError(f"Failed to authenticate: {e}")

        # Save the credentials for next run
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        raise CalendarError(f"Failed to build calendar service: {e}")


def fetch_calendar_events(credentials_file='credentials.json'):
    """
    Fetch today's calendar events from Google Calendar.

    Args:
        credentials_file (str): Path to the credentials JSON file.

    Returns:
        list: List of formatted calendar events with fields:
            - title (str): Event title
            - start_time (str): Start time (ISO format or date)
            - end_time (str): End time (ISO format or date)
            - location (str): Event location (if available)
            - all_day (bool): Whether it's an all-day event

    Raises:
        CalendarError: If fetching events fails.
    """
    try:
        service = authenticate_google_calendar(credentials_file)
    except CalendarError:
        raise

    # Get today's date range in local time, then convert to UTC for API
    now = datetime.now()
    start_of_day = datetime(now.year, now.month, now.day, 0, 0, 0)
    end_of_day = start_of_day + timedelta(days=1)

    # Convert local time to UTC for API
    # Calculate UTC offset
    utc_offset = datetime.now() - datetime.utcnow()
    start_of_day_utc = start_of_day - utc_offset
    end_of_day_utc = end_of_day - utc_offset

    # Format times in RFC3339 format (UTC)
    time_min = start_of_day_utc.isoformat() + 'Z'
    time_max = end_of_day_utc.isoformat() + 'Z'

    try:
        # Fetch events from the primary calendar
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        # Format events
        formatted_events = []
        for event in events:
            # Determine if it's an all-day event
            is_all_day = 'date' in event['start']

            formatted_event = {
                'title': event.get('summary', 'No Title'),
                'start_time': event['start'].get('dateTime', event['start'].get('date')),
                'end_time': event['end'].get('dateTime', event['end'].get('date')),
                'location': event.get('location', ''),
                'all_day': is_all_day
            }
            formatted_events.append(formatted_event)

        return formatted_events

    except HttpError as e:
        raise CalendarError(f"Failed to fetch calendar events: {e}")
    except Exception as e:
        raise CalendarError(f"Unexpected error fetching events: {e}")
