"""Configuration loading and validation module."""

import yaml
import os
from typing import Dict, Any


class ConfigError(Exception):
    """Custom exception for configuration errors."""
    pass


def load_config(config_path: str = 'config.yaml') -> Dict[str, Any]:
    """
    Load and validate configuration from YAML file.

    Args:
        config_path (str): Path to the configuration YAML file

    Returns:
        dict: Validated configuration dictionary

    Raises:
        ConfigError: If config file is missing or invalid
    """
    # Check if file exists
    if not os.path.exists(config_path):
        raise ConfigError(f"Config file not found: {config_path}")

    # Load YAML file
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigError(f"Failed to parse YAML: {e}")
    except Exception as e:
        raise ConfigError(f"Failed to read config file: {e}")

    # Validate required sections
    required_sections = ['apis', 'location', 'email', 'news']
    for section in required_sections:
        if section not in config:
            raise ConfigError(f"Missing required configuration section: {section}")

    # Validate required API keys
    required_api_keys = ['openweather_key', 'openai_key', 'sparkpost_key']
    for key in required_api_keys:
        if key not in config['apis']:
            raise ConfigError(f"Missing required configuration: apis.{key}")

    # Validate required email fields
    required_email_fields = ['recipient', 'from_address', 'subject']
    for field in required_email_fields:
        if field not in config['email']:
            raise ConfigError(f"Missing required configuration: email.{field}")

    # Validate news section
    if 'rss_feeds' not in config['news']:
        raise ConfigError("Missing required configuration: news.rss_feeds")

    if not isinstance(config['news']['rss_feeds'], dict):
        raise ConfigError("Configuration error: news.rss_feeds must be a dictionary")

    if len(config['news']['rss_feeds']) == 0:
        raise ConfigError("Configuration error: news.rss_feeds must have at least one feed")

    # Validate each feed has title and url
    for feed_key, feed_data in config['news']['rss_feeds'].items():
        if not isinstance(feed_data, dict):
            raise ConfigError(f"Configuration error: news.rss_feeds.{feed_key} must be a dictionary")
        if 'title' not in feed_data:
            raise ConfigError(f"Configuration error: news.rss_feeds.{feed_key} missing 'title'")
        if 'url' not in feed_data:
            raise ConfigError(f"Configuration error: news.rss_feeds.{feed_key} missing 'url'")

    return config
