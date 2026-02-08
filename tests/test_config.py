import pytest
import yaml
import os
from modules.config import load_config, ConfigError

def test_load_config_success(tmp_path):
    """Test loading valid config file"""
    config_file = tmp_path / "config.yaml"
    config_data = {
        'apis': {
            'openweather_key': 'test_key',
            'openai_key': 'test_key',
            'sparkpost_key': 'test_key'
        },
        'location': {'city': 'TestCity', 'country_code': 'US'},
        'email': {
            'recipient': 'test@test.com',
            'from_address': 'from@test.com',
            'subject': 'Test Subject'
        },
        'news': {
            'rss_feeds': ['http://test.com/feed'],
            'max_articles': 5,
            'summary_sentences': 2
        }
    }
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)

    config = load_config(str(config_file))
    assert config['apis']['openweather_key'] == 'test_key'
    assert config['location']['city'] == 'TestCity'

def test_load_config_missing_file():
    """Test error when config file doesn't exist"""
    with pytest.raises(ConfigError, match="Config file not found"):
        load_config('nonexistent.yaml')

def test_load_config_missing_required_keys(tmp_path):
    """Test error when required keys are missing"""
    config_file = tmp_path / "config.yaml"
    config_data = {'apis': {'openweather_key': 'test'}}
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)

    with pytest.raises(ConfigError, match="Missing required configuration"):
        load_config(str(config_file))
