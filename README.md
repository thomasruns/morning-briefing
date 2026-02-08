# Morning Briefing System

An automated daily email briefing system that delivers personalized morning updates directly to your inbox. Wake up to a beautiful HTML email containing the weather forecast, today's calendar events, and AI-summarized news articles from your favorite sources.

## Features

- **Weather Forecast**: Current conditions and forecast for your location using OpenWeatherMap API
- **Calendar Integration**: Today's upcoming events from Google Calendar
- **AI-Powered News**: Automatically fetches articles from RSS feeds and generates concise summaries using OpenAI's GPT models
- **Email Delivery**: Professional HTML email delivered via SparkPost
- **Comprehensive Logging**: Detailed logs with automatic rotation and retention management
- **Dry Run Mode**: Test the system without sending emails
- **Flexible Configuration**: YAML-based configuration for easy customization

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure the system
cp config.example.yaml config.yaml
# Edit config.yaml with your API keys and preferences

# 3. Test the system
python morning_briefing.py --dry-run

# 4. Schedule daily briefings
crontab -e
# Add: 30 7 * * * cd /path/to/morning-news-summary && /path/to/venv/bin/python morning_briefing.py
```

## Configuration

The system is configured via a YAML file. See `config.example.yaml` for a template with all available options:

- **API Keys**: OpenWeatherMap, OpenAI, SparkPost
- **Location**: City and country code for weather
- **Email**: Recipient address and sender details
- **News Sources**: List of RSS feeds to monitor
- **Logging**: Log level and retention settings

## Requirements

- Python 3.8 or higher
- API keys for:
  - [OpenWeatherMap](https://openweathermap.org/api) (Free tier available)
  - [OpenAI](https://platform.openai.com/) (GPT-3.5-turbo recommended)
  - [SparkPost](https://www.sparkpost.com/) (Free tier: 500 emails/month)
  - [Google Calendar API](https://developers.google.com/calendar) (Optional, free)

## Cost Estimate

Approximate monthly costs for daily briefings (30 days):

- **OpenWeatherMap**: Free (up to 1,000 calls/day)
- **OpenAI**: ~$0.60-0.90/month (10 articles × 30 days with GPT-3.5-turbo)
- **SparkPost**: Free (500 emails/month tier)
- **Google Calendar**: Free

**Total: ~$0.60-0.90/month**

## Documentation

- [Setup Guide](SETUP.md) - Detailed installation and configuration instructions
- [Design Document](docs/plans/2026-02-06-morning-news-briefing-design.md) - System architecture and design decisions
- [Implementation Plan](docs/plans/2026-02-06-morning-briefing-implementation.md) - Development roadmap

## Project Structure

```
morning-news-summary/
├── morning_briefing.py       # Main orchestrator script
├── modules/                  # Core modules
│   ├── config.py            # Configuration loader
│   ├── logger.py            # Logging setup
│   ├── weather.py           # Weather API integration
│   ├── calendar_events.py   # Google Calendar integration
│   ├── news.py              # RSS feed and article extraction
│   ├── summarizer.py        # OpenAI summarization
│   ├── email_builder.py     # HTML email generation
│   └── email_sender.py      # SparkPost email delivery
├── tests/                   # Unit tests
├── logs/                    # Log files (auto-created)
├── output/                  # Dry-run output (auto-created)
├── config.yaml              # Your configuration (create from example)
└── config.example.yaml      # Configuration template
```

## Usage

```bash
# Run the morning briefing (sends email)
python morning_briefing.py

# Test without sending email (saves to output/ directory)
python morning_briefing.py --dry-run

# Use a custom config file
python morning_briefing.py --config /path/to/config.yaml

# Enable debug logging
python morning_briefing.py --debug

# Combine options
python morning_briefing.py --dry-run --debug
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_weather.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=modules --cov-report=html
```

## License

MIT License - feel free to use and modify for your personal use.

## Contributing

This is a personal automation project, but suggestions and improvements are welcome via issues or pull requests.
