import pytest
from unittest.mock import patch, Mock
from modules.news import fetch_news, extract_article_content, NewsError
import feedparser

def test_fetch_news_success():
    """Test successful RSS feed parsing"""
    mock_feed = Mock()
    mock_feed.entries = [
        Mock(
            title='Test Article 1',
            link='http://example.com/article1',
            published='Mon, 01 Jan 2024 12:00:00 GMT',
            summary='Test summary 1'
        ),
        Mock(
            title='Test Article 2',
            link='http://example.com/article2',
            published='Mon, 01 Jan 2024 11:00:00 GMT',
            summary='Test summary 2'
        )
    ]

    with patch('requests.get') as mock_get, patch('feedparser.parse', return_value=mock_feed):
        mock_get.return_value.text = '<rss></rss>'
        articles = fetch_news([{'title': 'Test Feed', 'url': 'http://test.com/feed'}], max_articles=2)

        assert len(articles) == 2
        assert articles[0]['title'] == 'Test Article 1'
        assert articles[0]['link'] == 'http://example.com/article1'

def test_fetch_news_multiple_feeds():
    """Test fetching from multiple RSS feeds"""
    mock_feed1 = Mock()
    mock_feed1.entries = [
        Mock(title='Article 1', link='http://example.com/1',
             published='Mon, 01 Jan 2024 12:00:00 GMT', summary='Summary 1')
    ]

    mock_feed2 = Mock()
    mock_feed2.entries = [
        Mock(title='Article 2', link='http://example.com/2',
             published='Mon, 01 Jan 2024 11:00:00 GMT', summary='Summary 2')
    ]

    with patch('requests.get') as mock_get, patch('feedparser.parse', side_effect=[mock_feed1, mock_feed2]):
        mock_get.return_value.text = '<rss></rss>'
        articles = fetch_news([
            {'title': 'NPR', 'url': 'https://feeds.npr.org/1001/rss.xml'},
            {'title': 'The Verge', 'url': 'https://www.theverge.com/tech'}
        ], max_articles=5)

        assert len(articles) == 2

def test_extract_article_content_success():
    """Test article content extraction"""
    mock_html = """
    <html>
        <body>
            <article>
                <p>This is the article content.</p>
                <p>It has multiple paragraphs.</p>
            </article>
        </body>
    </html>
    """

    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = mock_html

        content = extract_article_content('http://example.com/article')

        assert 'article content' in content.lower()
