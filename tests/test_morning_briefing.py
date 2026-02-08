import pytest
from unittest.mock import patch, Mock
from morning_briefing import run_briefing

def test_run_briefing_success():
    """Test complete briefing run with all components"""
    mock_config = {
        'apis': {'openweather_key': 'test', 'openai_key': 'test', 'sparkpost_key': 'test'},
        'location': {'city': 'TestCity', 'country_code': 'US'},
        'email': {'recipient': 'test@test.com', 'from_address': 'from@test.com', 'subject': 'Test'},
        'news': {'rss_feeds': ['http://test.com/feed'], 'max_articles': 5, 'summary_sentences': 2}
    }

    with patch('morning_briefing.load_config', return_value=mock_config), \
         patch('morning_briefing.fetch_weather', return_value={'temperature': 72, 'temp_min': 65, 'temp_max': 78, 'condition': 'Clear', 'description': 'sunny'}), \
         patch('morning_briefing.fetch_calendar_events', return_value=[]), \
         patch('morning_briefing.fetch_news', return_value=[{'title': 'Test', 'link': 'http://test.com', 'source': 'Test', 'published': 'Today', 'content': 'Test'}]), \
         patch('morning_briefing.extract_article_content', return_value='Test content'), \
         patch('morning_briefing.summarize_articles', return_value=[]), \
         patch('morning_briefing.build_email_html', return_value='<html></html>'), \
         patch('morning_briefing.send_email', return_value=True), \
         patch('morning_briefing.setup_logger'), \
         patch('os.path.exists', return_value=True):

        result = run_briefing()
        assert result == True
