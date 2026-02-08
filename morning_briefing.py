#!/usr/bin/env python3
"""
Main orchestrator script for the morning briefing system.

This script coordinates all modules to fetch weather, calendar events, and news,
generate AI summaries, build an HTML email, and send it to the configured recipient.
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path

from modules.config import load_config, ConfigError
from modules.logger import setup_logger
from modules.weather import fetch_weather, fetch_hourly_forecast, WeatherError
from modules.calendar_events import fetch_calendar_events, CalendarError
from modules.news import fetch_news, extract_article_content, NewsError
from modules.summarizer import summarize_articles, SummarizerError
from modules.email_builder import build_email_html
from modules.email_sender import send_email, EmailError


def run_briefing(config_path='config.yaml', dry_run=False):
    """
    Main function that orchestrates the entire morning briefing process.

    Args:
        config_path (str): Path to the configuration YAML file (default: 'config.yaml')
        dry_run (bool): If True, save email to file instead of sending (default: False)

    Returns:
        bool: True if briefing completed successfully, False otherwise
    """
    logger = None

    try:
        # Step 1: Setup logger
        logger = setup_logger()
        logger.info("Starting morning briefing process")

        # Step 2: Load configuration
        try:
            logger.info(f"Loading configuration from {config_path}")
            config = load_config(config_path)
            logger.info("Configuration loaded successfully")
        except ConfigError as e:
            logger.error(f"Configuration error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error loading configuration: {e}")
            return False

        # Step 3: Fetch weather data
        weather = None
        hourly_forecast = []
        try:
            logger.info("Fetching weather data")
            weather = fetch_weather(
                api_key=config['apis']['openweather_key'],
                city=config['location']['city'],
                country_code=config['location']['country_code']
            )
            logger.info(f"Weather fetched: {weather['condition']}, {weather['temperature']}°F")

            # Fetch hourly forecast
            try:
                hourly_forecast = fetch_hourly_forecast(
                    api_key=config['apis']['openweather_key'],
                    city=config['location']['city'],
                    country_code=config['location']['country_code']
                )
                logger.info(f"Hourly forecast fetched: {len(hourly_forecast)} time slots")
            except WeatherError as e:
                logger.warning(f"Hourly forecast fetch failed: {e}")

        except WeatherError as e:
            logger.warning(f"Weather fetch failed: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error fetching weather: {e}")

        # Step 4: Fetch calendar events
        events = []
        try:
            logger.info("Fetching calendar events")
            # Check if credentials file exists
            creds_file = config.get('calendar', {}).get('credentials_file', 'credentials.json')
            if os.path.exists(creds_file):
                events = fetch_calendar_events(credentials_file=creds_file)
                logger.info(f"Found {len(events)} calendar events")
            else:
                logger.warning(f"Calendar credentials file not found: {creds_file}")
        except CalendarError as e:
            logger.warning(f"Calendar fetch failed: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error fetching calendar: {e}")

        # Step 5: Fetch news articles
        articles = []
        try:
            logger.info("Fetching news articles")
            max_articles = config['news'].get('max_articles', 10)
            articles = fetch_news(
                rss_feeds=config['news']['rss_feeds'],
                max_articles=max_articles
            )
            logger.info(f"Fetched {len(articles)} news articles")
        except NewsError as e:
            logger.warning(f"News fetch failed: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error fetching news: {e}")

        # Step 6: Extract article content
        if articles:
            logger.info("Extracting article content")
            for idx, article in enumerate(articles):
                try:
                    logger.debug(f"Extracting content for article {idx + 1}: {article.get('title', 'Unknown')}")
                    content = extract_article_content(article['link'])
                    article['content'] = content
                except NewsError as e:
                    logger.warning(f"Failed to extract content for article {idx + 1}: {e}")
                    article['content'] = article.get('summary', '')
                except Exception as e:
                    logger.warning(f"Unexpected error extracting article {idx + 1}: {e}")
                    article['content'] = article.get('summary', '')

        # Step 7: Generate AI summaries
        if articles:
            try:
                print("AI summary...")
                logger.info("Generating AI summaries")
                num_sentences = config['news'].get('summary_sentences', 3)
                articles = summarize_articles(
                    api_key=config['apis']['openai_key'],
                    articles=articles,
                    num_sentences=num_sentences
                )
                logger.info(f"Generated summaries for {len(articles)} articles")
            except SummarizerError as e:
                logger.warning(f"Summarization failed: {e}")
            except Exception as e:
                logger.warning(f"Unexpected error during summarization: {e}")

        # Step 8: Build email HTML
        try:
            logger.info("Building email HTML")
            html_content = build_email_html(
                weather=weather,
                hourly_forecast=hourly_forecast,
                events=events,
                articles=articles
            )
            logger.info("Email HTML built successfully")
        except Exception as e:
            logger.error(f"Failed to build email HTML: {e}")
            return False

        # Step 9: Send email or save to file
        if dry_run:
            # Save to file instead of sending
            output_dir = Path('output')
            output_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = output_dir / f'briefing_{timestamp}.html'

            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logger.info(f"Dry run: Email saved to {output_file}")
                return True
            except Exception as e:
                logger.error(f"Failed to save email to file: {e}")
                return False
        else:
            # Send email
            try:
                logger.info("Sending email")
                success = send_email(
                    api_key=config['apis']['sparkpost_key'],
                    from_email=config['email']['from_address'],
                    to_email=config['email']['recipient'],
                    subject=config['email']['subject'],
                    html_content=html_content
                )

                if success:
                    logger.info("Email sent successfully")
                    return True
                else:
                    logger.error("Email sending failed")
                    return False

            except EmailError as e:
                logger.error(f"Failed to send email: {e}")
                return False
            except Exception as e:
                logger.error(f"Unexpected error sending email: {e}")
                return False

    except Exception as e:
        if logger:
            logger.error(f"Unexpected error in run_briefing: {e}")
        else:
            print(f"ERROR: {e}", file=sys.stderr)
        return False


def main():
    """
    CLI entry point with argument parsing.
    """
    parser = argparse.ArgumentParser(
        description='Morning Briefing System - Fetch weather, calendar, news and send daily email briefing'
    )

    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration YAML file (default: config.yaml)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Save email to file instead of sending'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )

    args = parser.parse_args()

    # Set log level if debug flag is set
    if args.debug:
        log_level = 'DEBUG'
    else:
        log_level = 'INFO'

    # Setup logger with appropriate level
    logger = setup_logger(level=log_level)

    # Run the briefing
    success = run_briefing(config_path=args.config, dry_run=args.dry_run)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
