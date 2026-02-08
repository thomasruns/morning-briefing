"""
AI-powered article summarization using OpenAI's GPT API.
"""

import time
import openai
from typing import List, Dict, Any


class SummarizerError(Exception):
    """Exception raised for errors during article summarization."""
    pass


def summarize_article(
    api_key: str,
    article_text: str,
    num_sentences: int = 3,
    max_retries: int = 3
) -> str:
    """
    Summarize an article using OpenAI's GPT API.

    Args:
        api_key: OpenAI API key
        article_text: The article text to summarize
        num_sentences: Number of sentences in the summary (default: 3)
        max_retries: Maximum number of retry attempts (default: 3)

    Returns:
        str: The generated summary text

    Raises:
        SummarizerError: If summarization fails after all retries
    """
    client = openai.OpenAI(api_key=api_key)

    prompt = f"Summarize the following article in exactly {num_sentences} sentences:\n\n{article_text}"

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise article summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )

            summary = response.choices[0].message.content.strip()

            # Add 1 second delay to respect rate limits
            time.sleep(1)

            return summary

        except Exception as e:
            if attempt < max_retries - 1:
                # Exponential backoff: 2^attempt seconds
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            else:
                raise SummarizerError(f"Failed to summarize article after {max_retries} attempts: {str(e)}")

    # This should never be reached, but added for safety
    raise SummarizerError("Failed to summarize article")


def summarize_articles(
    api_key: str,
    articles: List[Dict[str, Any]],
    num_sentences: int = 3
) -> List[Dict[str, Any]]:
    """
    Summarize multiple articles in batch.

    Args:
        api_key: OpenAI API key
        articles: List of article dictionaries
        num_sentences: Number of sentences in each summary (default: 3)

    Returns:
        List[Dict[str, Any]]: Articles with 'ai_summary' field added
    """
    summarized_articles = []

    for article in articles:
        try:
            # Get the article text (could be from different fields)
            article_text = article.get('content') or article.get('description') or article.get('title', '')

            if article_text:
                summary = summarize_article(api_key, article_text, num_sentences)
                article['ai_summary'] = summary
            else:
                article['ai_summary'] = "No content available for summarization."

        except SummarizerError as e:
            # Log error but continue with other articles
            article['ai_summary'] = f"Error: {str(e)}"
        except Exception as e:
            article['ai_summary'] = f"Unexpected error: {str(e)}"

        summarized_articles.append(article)

    return summarized_articles
