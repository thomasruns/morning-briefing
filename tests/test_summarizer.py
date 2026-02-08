import pytest
from unittest.mock import patch, Mock
from modules.summarizer import summarize_article, SummarizerError

def test_summarize_article_success():
    """Test successful article summarization"""
    mock_response = Mock()
    mock_response.choices = [
        Mock(message=Mock(content="This is a concise summary. It has two sentences."))
    ]

    with patch('openai.OpenAI') as mock_openai:
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        summary = summarize_article(
            "test_api_key",
            "Long article content here...",
            num_sentences=2
        )

        assert "summary" in summary.lower()
        assert len(summary) > 0

def test_summarize_article_api_error():
    """Test OpenAI API error handling"""
    with patch('openai.OpenAI') as mock_openai:
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client

        with pytest.raises(SummarizerError, match="Failed to summarize"):
            summarize_article("test_key", "Article content")
