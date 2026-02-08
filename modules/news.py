"""
News fetching module for RSS feeds and article content extraction.
"""

import time
import logging
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
from email.utils import parsedate_to_datetime


class NewsError(Exception):
    """Custom exception for news-related errors"""
    pass


def fetch_news(rss_feeds, max_articles=10):
    """
    Fetches articles from multiple RSS feeds.

    Args:
        rss_feeds: Dictionary of RSS feeds with format {feed_key: {title: str, url: str}}
        max_articles: Maximum number of articles to return (default: 10)

    Returns:
        List of article dictionaries with keys: title, link, published, summary, source
        Sorted by published date (newest first)
    """
    all_articles = []

    for idx, (feed_key, feed_data) in enumerate(rss_feeds.items()):
        try:
            # Add delay between feeds (except for the first one)
            if idx > 0:
                time.sleep(0.5)

            # Parse the RSS feed
            feed_url = feed_data['url']
            feed_title = feed_data['title']

            response = requests.get(feed_url, verify=True)
            feed = feedparser.parse(response.text)

            # Extract articles from feed
            for entry in feed.entries:
                article = {
                    'title': getattr(entry, 'title', ''),
                    'link': getattr(entry, 'link', ''),
                    'published': getattr(entry, 'published', ''),
                    'summary': getattr(entry, 'summary', ''),
                    'source': feed_title
                }
                all_articles.append(article)

        except Exception as e:
            # Continue to next feed if one fails
            logging.warning(f"Error fetching feed {feed_url}: {e}")
            continue

    # Sort articles by published date (newest first)
    def parse_date(article):
        try:
            if article['published']:
                return parsedate_to_datetime(article['published'])
        except Exception:
            pass
        return datetime.min

    all_articles.sort(key=parse_date, reverse=True)

    # Limit to max_articles
    return all_articles[:max_articles]


def extract_article_content(url, max_retries=3):
    """
    Extracts content from a URL using web scraping.

    Args:
        url: URL of the article to extract
        max_retries: Number of retry attempts with exponential backoff (default: 3)

    Returns:
        Cleaned article text (limited to 5000 characters)

    Raises:
        NewsError: If content extraction fails after all retries
    """
    for attempt in range(max_retries):
        try:
            # Fetch the page
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0 (compatible; MorningBriefing/1.0)'})
            response.raise_for_status()

            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove unwanted tags
            for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
                tag.decompose()

            # Try to find article tag first
            article_tag = soup.find('article')
            if article_tag:
                content = article_tag.get_text(separator=' ', strip=True)
            else:
                # Fall back to body tag
                body_tag = soup.find('body')
                if body_tag:
                    content = body_tag.get_text(separator=' ', strip=True)
                else:
                    content = soup.get_text(separator=' ', strip=True)

            # Clean up whitespace
            content = ' '.join(content.split())

            # Limit to 5000 characters
            if len(content) > 5000:
                content = content[:5000]

            return content

        except Exception as e:
            if attempt < max_retries - 1:
                # Exponential backoff
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            else:
                raise NewsError(f"Failed to extract content from {url}: {e}")
